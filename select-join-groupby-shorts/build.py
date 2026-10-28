"""Builds assets/narration.mp3 and index.html from vo.json (run gen_vo.py first)."""
import json, re, subprocess, html

LEAD, GAP, TAIL = 0.3, 0.45, 1.2
vo = json.load(open("vo.json"))

# --- timing + concatenated narration ---
t = LEAD
for s in vo:
    s["start"] = round(t, 3)
    t += s["dur"] + GAP
TOTAL = round(t - GAP + TAIL, 2)

inputs, filt = [], []
for i, s in enumerate(vo):
    inputs += ["-i", f"assets/vo/{s['id']}.mp3"]
    filt.append(f"[{i}]adelay={int(s['start']*1000)}:all=1[a{i}]")
mix = "".join(f"[a{i}]" for i in range(len(vo)))
filt.append(f"{mix}amix=inputs={len(vo)}:normalize=0,apad,atrim=0:{TOTAL}[out]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
                "-map", "[out]", "-ar", "48000", "-b:a", "192k", "assets/narration.mp3"], check=True)

S = {s["id"]: s for s in vo}

def norm(x):
    return re.sub(r"[^\w]", "", x)

def word_time(sid, token, after=0.0):
    """Absolute time of the first word in scene `sid` starting with `token`, spoken after `after`."""
    s = S[sid]
    for w in s["words"]:
        at = s["start"] + w["t"]
        if at >= after and norm(w["text"]).startswith(norm(token)):
            return round(at, 3)
    raise ValueError(f"{token!r} not found in {sid}")

# --- SQL highlighting ---
KW = ("SELECT FROM WHERE ORDER BY DESC ASC JOIN INNER LEFT ON GROUP HAVING COUNT SUM AVG AS AND OR IN LIKE "
      "LIMIT IS NULL").split()
def hl(line):
    out = html.escape(line)
    out = re.sub(r"(--.*)$", r'<span class="cm">\1</span>', out)
    out = re.sub(r"(&#x27;[^&]*&#x27;)", r'<span class="st">\1</span>', out)
    out = re.sub(r"\b(" + "|".join(KW) + r")\b", r'<span class="kw">\1</span>', out)
    out = re.sub(r"(?<![\w>])(\d+)\b", r'<span class="nu">\1</span>', out)
    return out

def code(lines, mark=()):
    """`mark`: indexes of lines to tint as the point of the scene."""
    return '<div class="code in">' + "".join(
        f'<div class="ln{" mk" if i in mark else ""}">{hl(l) or "&nbsp;"}</div>' for i, l in enumerate(lines)) + "</div>"

def head(step, title, desc):
    return f'<div class="pill in">{step}</div><h2 class="title in">{title}</h2><p class="desc in">{desc}</p>'

def table(cols, rows, label="", cls=""):
    """rows: (row_class, values); a None value renders as a highlighted NULL."""
    th = "".join(f"<th>{c}</th>" for c in cols)
    tr = "".join(f'<tr class="{rc}">' + "".join(
        '<td class="nl">NULL</td>' if v is None else f"<td>{v}</td>" for v in vals) + "</tr>" for rc, vals in rows)
    lab = f'<div class="tlabel">{label}</div>' if label else ""
    return f'<div class="tbl in {cls}">{lab}<table><tr>{th}</tr>{tr}</table></div>'

# One colour per member, used for that member's rows everywhere: kim=k1, lee=k2, park=k3.
USERS = [("k1", (1, "kim")), ("k2", (2, "lee")), ("k3", (3, "park"))]
ORDERS = [("k1", (1, 1, "12000")), ("k1", (2, 1, "8000")), ("k2", (3, 2, "5000"))]
JOINED = [("k1", ("kim", "12000")), ("k1", ("kim", "8000")), ("k2", ("lee", "5000"))]
EXEC = ["FROM · JOIN", "WHERE", "GROUP BY", "HAVING", "SELECT", "ORDER BY", "LIMIT"]
EXEC_SAID = ["프롬", "웨어", "그룹", "해빙", "셀렉트", "오더", "리밋"]

scenes = {
 "hook": '''<div class="hook">
   <div class="pill in">MySQL · DQL 핵심 정리</div>
   <h1 class="big in"><em>SELECT</em><br/>JOIN<br/>GROUP BY</h1>
   <div class="sub in">기본 문법부터 <b>3분 정리</b></div>
 </div>''',
 "basic": head("STEP 1 · 기본 구조", "SELECT … FROM", "무엇을 · 어디서 가져올지")
    + code(["SELECT name, price", "FROM products;"])
    + table(["name", "price"], [("", ("SQL 입문서", "18000")), ("", ("볼펜", "1500")), ("", ("노트", "3000"))], "결과")
    + '<div class="warn in">⚠ <code>SELECT *</code> 대신 <b>필요한 컬럼만</b></div>',
 "where": head("STEP 2 · 조건", "WHERE", "원하는 <b>행</b>만 고르기")
    + code(["SELECT name, price", "FROM products", "WHERE price >= 10000", "  AND category IN ('book', 'pen')", "  AND name LIKE '%SQL%';"], mark=(2, 3, 4))
    + '<div class="chips in"><span>= &gt; &lt;=</span><span>AND · OR</span><span>IN (…)</span><span>LIKE \'%글자%\'</span></div>',
 "order": head("STEP 3 · 정렬", "ORDER BY · LIMIT", "정렬하고 <b>상위 N개</b>만")
    + code(["SELECT name, price", "FROM products", "ORDER BY price DESC", "LIMIT 5;"], mark=(2, 3))
    + '<div class="chips in"><span>ASC 오름차순 (기본)</span><span>DESC 내림차순</span><span>LIMIT 개수</span></div>',
 "join": head("STEP 4 · 연결", "JOIN 이란?", "공통 키로 <b>두 테이블을 연결</b>")
    + table(["<u>id</u>", "name"], USERS, "users · 회원")
    + '<div class="link in">orders.<b>user_id</b> = users.<b>id</b></div>'
    + table(["id", "<u>user_id</u>", "amount"], ORDERS, "orders · 주문"),
 "inner": head("STEP 4-1", "INNER JOIN", "양쪽 모두 <b>짝이 있는 행</b>만")
    + code(["SELECT u.name, o.amount", "FROM users AS u", "INNER JOIN orders AS o", "  ON o.user_id = u.id;"], mark=(2, 3))
    + table(["name", "amount"], JOINED + [("out", ("park", "—"))], "결과 · park는 주문이 없어 제외")
    + '<div class="note in"><code>AS</code>는 생략 가능 · <small>FROM users u</small></div>',
 "left": head("STEP 4-2", "LEFT JOIN", "왼쪽 테이블은 <b>전부</b> 남김")
    + code(["SELECT u.name, o.amount", "FROM users AS u", "LEFT JOIN orders AS o", "  ON o.user_id = u.id;"], mark=(2,))
    + table(["name", "amount"], JOINED + [("k3", ("park", None))], "결과 · 짝이 없으면 NULL"),
 "left2": head("STEP 4-3", "LEFT JOIN + IS NULL", "주문하지 않은 <b>회원 찾기</b>")
    + code(["SELECT u.name", "FROM users AS u", "LEFT JOIN orders AS o", "  ON o.user_id = u.id", "WHERE o.id IS NULL;"], mark=(4,))
    + table(["name"], [("k3", ("park",))], "결과 · park만 남음"),
 "group": head("STEP 5 · 집계", "GROUP BY", "같은 값끼리 <b>묶어서 계산</b>")
    + code(["SELECT u.name,", "  COUNT(*)      AS cnt,", "  SUM(o.amount) AS total,", "  AVG(o.amount) AS avg",
            "FROM users AS u", "JOIN orders AS o", "  ON o.user_id = u.id", "GROUP BY u.id, u.name;"], mark=(1, 2, 3, 7))
    + '<div class="note in">집계 안 하는 컬럼은 <b>GROUP BY에 함께</b></div>',
 "group2": head("STEP 5-1", "묶이는 과정", "kim의 주문 2건 → <b>1줄</b>")
    + table(["name", "amount"], JOINED, "JOIN 결과 · 3행")
    + '<div class="arrow in">▼ GROUP BY u.id, u.name</div>'
    + table(["name", "cnt", "total", "avg"], [("k1", ("kim", "2", "20000", "10000")), ("k2", ("lee", "1", "5000", "5000"))], "집계 결과 · 2행"),
 "having": head("STEP 5-2", "HAVING", "묶은 <b>그룹</b>을 다시 거르기")
    + code(["SELECT user_id, COUNT(*) AS cnt", "FROM orders", "GROUP BY user_id", "HAVING COUNT(*) >= 2;"], mark=(3,))
    + table(["user_id", "cnt"], [("k1", ("1", "2"))], "결과 · kim(1)만 남음")
    + '<div class="vs"><div class="card in"><b>WHERE</b><span>묶기 <em>전</em> 행</span></div>'
      '<div class="card in"><b>HAVING</b><span>묶은 <em>후</em> 그룹</span></div></div>',
 "outro": '<div class="pill in">정리</div><h2 class="title in">SQL 논리적 처리 순서</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{c}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"basic": 1, "where": 2, "order": 3, "join": 4, "inner": 4, "left": 4, "left2": 4,
        "group": 5, "group2": 5, "having": 5}

def split_caption(text, limit=24):
    """Comma-first split; long pieces halved at a space; short fragments merged."""
    pieces = [x.strip() + "," for x in text.split(",")]
    pieces[-1] = pieces[-1][:-1]
    out = []
    for x in pieces:
        while len(x) > limit and " " in x:
            mid = len(x) // 2
            cut = min((i for i, c in enumerate(x) if c == " "), key=lambda i: abs(i - mid))
            out.append(x[:cut]); x = x[cut + 1:]
        out.append(x)
    merged = []
    for x in out:
        if merged and (len(x) < 9 or len(merged[-1]) < 9) and len(merged[-1]) + len(x) <= limit + 8:
            merged[-1] += " " + x
        else:
            merged.append(x)
    return merged

def word_marks(s):
    """(char offset in norm(script), time) per TTS word. Edge TTS sometimes glues a neighbour's
    syllables onto a word ('바이. 기'), so each token of the word is tried near the cursor."""
    ntext, cur, marks = norm(s["text"]), 0, []
    for w in s["words"]:
        for tok in filter(None, map(norm, re.split(r"[\s.,?!]+", w["text"]))):
            pos = ntext.find(tok, cur, cur + len(tok) + 3)
            if pos >= 0:
                marks.append((pos, w["t"])); cur = pos + len(tok)
                break
    if cur < len(ntext) - 2:
        raise ValueError(f"{s['id']}: TTS words cover only {cur}/{len(ntext)} chars of the script")
    return marks

def caption_chunks(s):
    """Caption pieces timed to the TTS word boundaries: each piece starts on its first spoken
    word and stays up until the next piece starts (the last one until the scene's audio ends)."""
    marks, pos, pieces = word_marks(s), 0, []
    for sentence in re.split(r"(?<=[.?!])\s+", s["text"].strip()):
        for part in split_caption(sentence):
            pieces.append((part, next(t for p, t in marks if p >= pos)))
            pos += len(norm(part))
    out = []
    for k, (txt, a) in enumerate(pieces):
        b = pieces[k + 1][1] if k + 1 < len(pieces) else s["dur"]
        a = 0.0 if k == 0 else a
        out.append((s["start"] + a, b - a, txt))
    return out

clips, caps, js = [], [], []
for s in vo:
    st = s["start"]
    vis_start = 0 if s is vo[0] else st - 0.15
    vis_end = TOTAL if s is vo[-1] else vo[vo.index(s) + 1]["start"] - 0.15
    vis_dur = round(vis_end - vis_start, 3)
    clips.append(f'<section id="sc-{s["id"]}" class="clip scene" data-start="{vis_start:.3f}" data-duration="{vis_dur}" data-track-index="1">{scenes[s["id"]]}</section>')
    js.append(f'enter("#sc-{s["id"]}", {st}, {s["dur"]});')
    rk = PROG.get(s["id"], 0)
    js.append(f'tl.set(".prog i", {{backgroundColor: "#26324a"}}, {vis_start});')
    if rk:
        js.append(f'tl.set(".prog i:nth-child({rk})", {{backgroundColor: "#f29111"}}, {vis_start});')
    for j, (a, d, txt) in enumerate(caption_chunks(s)):
        caps.append(f'<div id="cap-{s["id"]}-{j}" class="clip cap" data-start="{a:.3f}" data-duration="{d:.3f}" data-track-index="2"><span>{html.escape(txt)}</span></div>')

# outro: light up each processing step as the narration names it
after = S["outro"]["start"]
for i, token in enumerate(EXEC_SAID, 1):
    at = word_time("outro", token, after)
    after = at
    if i > 1:
        js.append(f'tl.to("#ex{i - 1}", {{backgroundColor: "#131c2e", scale: 1, duration: 0.2}}, {at});')
    js.append(f'tl.to("#ex{i}", {{backgroundColor: "#3a2a12", scale: 1.04, duration: 0.2}}, {at});')
js.append(f'tl.to("#ex{len(EXEC)}", {{backgroundColor: "#131c2e", scale: 1, duration: 0.3}}, {word_time("outro", "순입니다")} + 0.6);')

page = f'''<!doctype html>
<html lang="ko" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
:root {{
  --ground: #0b1220; --panel: #131c2e; --ink: #f4f6fb; --mute: #9aa6bd;
  --blue: #3fa7d6; --orange: #f29111; --red: #ff5d5d; --green: #7ee08a; --violet: #c3a6ff;
  --font: "Pretendard", sans-serif;
  --mono: "Menlo", "SF Mono", monospace;
}}
@font-face {{ font-family: "Pretendard"; src: url("assets/fonts/PretendardVariable.woff2") format("woff2"); font-weight: 45 920; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }}
#root {{ position: relative; width: 100%; height: 100%; font-family: var(--font); color: var(--ink); overflow: hidden;
  background: radial-gradient(1200px 900px at 80% -10%, #16365a 0%, transparent 60%),
              radial-gradient(900px 900px at -10% 110%, #3a2410 0%, transparent 55%), var(--ground); }}
.clip {{ position: absolute; inset: 0; }}
.brand {{ position: absolute; top: 110px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: center;
  font-size: 34px; font-weight: 700; color: var(--mute); letter-spacing: 0.02em; }}
.brand b {{ color: var(--blue); }} .brand b em {{ color: var(--orange); font-style: normal; }}
.prog {{ display: flex; gap: 12px; }}
.prog i {{ display: block; width: 56px; height: 12px; border-radius: 6px; background: #26324a; }}
.scene {{ padding: 210px 70px 0; display: flex; flex-direction: column; gap: 26px; }}
.pill {{ align-self: flex-start; padding: 12px 26px; border-radius: 999px; background: #1d2a44; color: var(--blue);
  font-size: 34px; font-weight: 700; }}
.hook {{ display: flex; flex-direction: column; gap: 50px; padding-top: 140px; }}
.big {{ font-size: 150px; line-height: 1.12; font-weight: 800; letter-spacing: -0.04em; }}
.big em {{ font-style: normal; color: var(--orange); }}
.sub {{ font-size: 64px; font-weight: 700; color: var(--mute); }} .sub b {{ color: var(--ink); }}
.title {{ font-size: 80px; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; }}
.desc {{ font-size: 46px; color: var(--mute); font-weight: 600; margin-top: -8px; }} .desc b {{ color: var(--orange); }}
.code {{ background: #0a0f1a; border: 2px solid #26324a; border-radius: 26px; padding: 30px 32px; font-family: var(--mono);
  font-size: 42px; line-height: 1.5; color: #d9e1f2; white-space: pre; box-shadow: 0 30px 60px rgba(0,0,0,.35);
  font-variant-ligatures: none; font-feature-settings: "liga" 0, "calt" 0; }}
.code .ln {{ margin: 0 -14px; padding: 0 14px; border-radius: 10px; }}
.code .ln.mk {{ background: rgba(242,145,17,.13); }}
.kw {{ color: var(--blue); font-weight: 700; }} .st {{ color: var(--green); }} .nu {{ color: var(--orange); }} .cm {{ color: #6f7d98; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 18px; }}
.chips span {{ padding: 16px 30px; background: var(--panel); border-radius: 18px; font-size: 42px; font-weight: 700; }}
.warn, .note {{ padding: 26px 36px; border-radius: 24px; font-size: 44px; font-weight: 700; line-height: 1.45; }}
.warn {{ background: rgba(255,93,93,.12); border-left: 10px solid var(--red); }} .warn b {{ color: var(--red); }}
.note {{ background: rgba(63,167,214,.12); border-left: 10px solid var(--blue); }} .note b {{ color: var(--orange); }}
.note small {{ font-size: 38px; color: var(--mute); font-weight: 600; font-family: var(--mono); }}
code {{ font-family: var(--mono); color: var(--orange); }}
.tbl {{ align-self: flex-start; }}
.tlabel {{ font-size: 34px; font-weight: 700; color: var(--mute); margin-bottom: 10px; }}
.tbl table {{ border-collapse: collapse; font-family: var(--mono); font-size: 40px; background: var(--panel); border-radius: 18px; overflow: hidden; }}
.tbl th {{ color: var(--blue); text-align: left; padding: 12px 32px; background: #1a2640; }}
.tbl th u {{ text-decoration: none; color: var(--orange); }}
.tbl td {{ padding: 10px 32px; border-top: 1px solid #26324a; }}
.tbl tr.k1 td {{ color: var(--orange); }} .tbl tr.k2 td {{ color: var(--green); }} .tbl tr.k3 td {{ color: var(--violet); }}
.tbl tr.out td {{ color: #5b6782; text-decoration: line-through; }}
.tbl td.nl {{ color: var(--red) !important; font-style: italic; font-weight: 700; background: rgba(255,93,93,.12); }}
.link {{ align-self: flex-start; font-family: var(--mono); font-size: 38px; color: var(--mute); padding: 6px 0 6px 26px;
  border-left: 8px solid var(--orange); }}
.link b {{ color: var(--orange); }}
.arrow {{ font-family: var(--mono); font-size: 38px; color: var(--orange); font-weight: 700; }}
.vs {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }}
.card {{ background: var(--panel); border-radius: 26px; padding: 26px 32px; display: flex; flex-direction: column; gap: 6px; }}
.card b {{ font-family: var(--mono); font-size: 52px; color: var(--blue); }}
.vs .card span {{ font-size: 44px; font-weight: 800; }} .vs .card em {{ font-style: normal; color: var(--orange); }}
.list {{ display: flex; flex-direction: column; gap: 16px; }}
.row {{ display: flex; align-items: center; gap: 30px; background: var(--panel); border-radius: 22px; padding: 14px 36px; font-size: 48px;
  transform-origin: left center; }}
.row .no {{ font-size: 52px; font-weight: 900; color: var(--orange); width: 50px; }}
.row b {{ font-family: var(--mono); color: var(--blue); }}
.cta {{ margin-top: 20px; font-size: 54px; font-weight: 800; text-align: center; }}
.cap {{ top: auto; bottom: 260px; height: auto; display: flex; justify-content: center; padding: 0 60px; }}
.cap span {{ background: rgba(0,0,0,.78); color: #fff; font-size: 48px; font-weight: 700; line-height: 1.4; padding: 16px 30px;
  border-radius: 18px; text-align: center; word-break: keep-all; }}
.bar {{ position: absolute; left: 0; bottom: 0; height: 10px; width: 1080px; background: var(--orange); transform-origin: left center; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
  <div class="brand"><b>SQL <em>SELECT</em> 정리</b><div class="prog"><i></i><i></i><i></i><i></i><i></i></div></div>
  {chr(10).join(clips)}
  {chr(10).join(caps)}
  <div class="bar"></div>
  <audio id="vo" src="assets/narration.mp3" data-start="0" data-duration="{TOTAL}" data-track-index="0"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
function enter(sel, t, dur) {{
  const items = document.querySelectorAll(sel + " .in");
  const step = Math.min(0.9, (dur * 0.5) / Math.max(1, items.length));
  items.forEach((el, i) => {{
    tl.fromTo(el, {{ opacity: 0, y: 50 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, Math.max(0, t - 0.1) + i * step);
  }});
  document.querySelectorAll(sel + " .code .ln").forEach((el, i, all) => {{
    tl.fromTo(el, {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power2.out" }}, t + 0.6 + i * Math.min(0.6, dur * 0.35 / all.length));
  }});
}}
{chr(10).join(js)}
tl.fromTo(".bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {TOTAL}, ease: "none" }}, 0);
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
'''
open("index.html", "w").write(page)
print("total", TOTAL, "s; scenes", [(s["id"], s["start"]) for s in vo])
