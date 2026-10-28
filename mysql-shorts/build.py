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

# --- SQL highlighting ---
KW = ("SELECT FROM WHERE ORDER BY DESC JOIN ON GROUP COUNT AS INSERT INTO VALUES UPDATE SET DELETE "
      "CREATE TABLE ALTER ADD DROP INDEX PRIMARY KEY AUTO_INCREMENT INT VARCHAR START TRANSACTION "
      "COMMIT ROLLBACK GRANT REVOKE TO").split()
def hl(line):
    out = html.escape(line)
    out = re.sub(r"(--.*)$", r'<span class="cm">\1</span>', out)
    out = re.sub(r"(&#x27;[^&]*&#x27;)", r'<span class="st">\1</span>', out)
    out = re.sub(r"\b(" + "|".join(KW) + r")\b", r'<span class="kw">\1</span>', out)
    out = re.sub(r"(?<![\w>])(\d+)\b", r'<span class="nu">\1</span>', out)
    return out

def code(lines):
    return '<div class="code in">' + "".join(f'<div class="ln">{hl(l) or "&nbsp;"}</div>' for l in lines) + "</div>"

RANK = [("DQL", "SELECT", "조회"), ("DML", "INSERT·UPDATE·DELETE", "변경"),
        ("DDL", "CREATE·ALTER·DROP", "구조"), ("TCL", "COMMIT·ROLLBACK", "트랜잭션"),
        ("DCL", "GRANT·REVOKE", "권한")]

def rank_head(n, cat, title, desc):
    return (f'<div class="rank in"><span class="no">{n}</span><span class="wi">위</span>'
            f'<span class="cat">{cat}</span></div>'
            f'<h2 class="title in">{title}</h2><p class="desc in">{desc}</p>')

scenes = {
 "hook": '''<div class="hook">
   <div class="pill in">MySQL · SQL 핵심 정리</div>
   <h1 class="big in">SQL,<br/><em>뭐부터</em><br/>배워야 할까?</h1>
   <div class="sub in">가성비 순위 <b>TOP 5</b></div>
 </div>''',
 "intro": '<div class="pill in">SQL = 데이터베이스에게 일을 시키는 언어</div><h2 class="title in">SQL의 5가지 종류</h2><div class="grid">'
    + "".join(f'<div class="card in"><b>{c}</b><span>{k}</span><i>{t}</i></div>'
              for c, t, k in [("DQL","SELECT","조회"),("DML","INSERT · UPDATE · DELETE","데이터 변경"),
                              ("DDL","CREATE · ALTER · DROP","구조 정의"),("TCL","COMMIT · ROLLBACK","트랜잭션"),
                              ("DCL","GRANT · REVOKE","권한")])
    + '</div><div class="note in">중요도는 <b>전혀 같지 않다!</b></div>',
 "r1": rank_head(1, "DQL", "SELECT", "실무 쿼리의 대부분은 <b>조회</b>")
    + code(["SELECT name, price", "FROM products", "WHERE price > 10000", "ORDER BY price DESC;"])
    + '<div class="chips in"><span>데이터 확인</span><span>리포트</span><span>장애 분석</span></div>',
 "r1b": rank_head(1, "DQL+", "JOIN · GROUP BY", "여러 테이블 연결 + 집계")
    + code(["SELECT u.name, COUNT(o.id) AS cnt", "FROM users u", "JOIN orders o ON o.user_id = u.id", "GROUP BY u.name;"])
    + '<div class="chips in"><span>일별 매출</span><span>회원별 주문 수</span></div>',
 "r2": rank_head(2, "DML", "INSERT · UPDATE · DELETE", "데이터를 <b>추가 · 수정 · 삭제</b>")
    + code(["INSERT INTO users (name)", "  VALUES ('kim');", "UPDATE users SET name = 'lee'", "  WHERE id = 1;", "DELETE FROM users WHERE id = 1;"])
    + '<div class="warn in">⚠ WHERE 빠뜨리면 <b>테이블 전체</b>가 바뀜<br/><small>실행 전 같은 조건으로 SELECT 먼저!</small></div>',
 "r3": rank_head(3, "DDL", "CREATE · ALTER · DROP", "테이블 <b>구조</b>를 정의")
    + code(["CREATE TABLE users (", "  id INT PRIMARY KEY AUTO_INCREMENT,", "  name VARCHAR(50)", ");",
            "ALTER TABLE users", "  ADD email VARCHAR(100);", "CREATE INDEX idx_name ON users(name);", "DROP TABLE users;"])
    + '<div class="warn in">⚠ 잘못 쓰면 <b>되돌리기 어려움</b></div>',
 "r4": rank_head(4, "TCL", "COMMIT · ROLLBACK", "전부 성공 or 전부 취소")
    + code(["START TRANSACTION;", "UPDATE acct SET bal = bal - 1000", "  WHERE id = 1;",
            "UPDATE acct SET bal = bal + 1000", "  WHERE id = 2;", "COMMIT;  -- 실패 시 ROLLBACK;"])
    + '<div class="note in">MySQL 기본값 <code>autocommit = 1</code><br/><small>롤백하려면 트랜잭션부터 열기</small></div>',
 "r5": rank_head(5, "DCL", "GRANT · REVOKE", "사용자 <b>권한</b> 관리")
    + code(["GRANT SELECT, INSERT ON shop.*", "  TO 'dev'@'%';", "REVOKE INSERT ON shop.*", "  FROM 'dev'@'%';"])
    + '<div class="chips in"><span>주로 DBA · 인프라 담당</span><span>개발자는 마지막에</span></div>',
 "outro": '<h2 class="title in">가성비 학습 순서</h2><div class="list">'
    + "".join(f'<div class="row in"><span class="no">{i}</span><b>{c}</b><span>{t}</span></div>'
              for i, (c, t, _) in enumerate(RANK, 1))
    + '</div><div class="cta in">오늘은 <b>SELECT</b>부터! 👍 구독 · 좋아요</div>',
}

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

def norm(x):
    return re.sub(r"[^\w]", "", x)

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
    st, du = s["start"], round(s["dur"] + GAP, 3)
    if s is vo[-1]:
        du = round(TOTAL - st, 3)
    vis_start = 0 if s is vo[0] else st - 0.15
    vis_end = TOTAL if s is vo[-1] else vo[vo.index(s) + 1]["start"] - 0.15
    vis_dur = round(vis_end - vis_start, 3)
    clips.append(f'<section id="sc-{s["id"]}" class="clip scene" data-start="{vis_start:.3f}" data-duration="{vis_dur}" data-track-index="1">{scenes[s["id"]]}</section>')
    js.append(f'enter("#sc-{s["id"]}", {st}, {s["dur"]});')
    rk = {"r1": 1, "r1b": 1, "r2": 2, "r3": 3, "r4": 4, "r5": 5}.get(s["id"], 0)
    js.append(f'tl.set(".prog i", {{backgroundColor: "#26324a"}}, {vis_start});')
    if rk:
        js.append(f'tl.set(".prog i:nth-child({rk})", {{backgroundColor: "#f29111"}}, {vis_start});')
    for j, (a, d, txt) in enumerate(caption_chunks(s)):
        caps.append(f'<div id="cap-{s["id"]}-{j}" class="clip cap" data-start="{a:.3f}" data-duration="{d:.3f}" data-track-index="2"><span>{html.escape(txt)}</span></div>')

progress_end = vo[-1]["start"] - 0.15
page = f'''<!doctype html>
<html lang="ko" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
:root {{
  --ground: #0b1220; --panel: #131c2e; --ink: #f4f6fb; --mute: #9aa6bd;
  --blue: #3fa7d6; --orange: #f29111; --red: #ff5d5d; --green: #7ee08a;
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
.brand {{ position: absolute; top: 120px; left: 80px; right: 80px; display: flex; justify-content: space-between; align-items: center;
  font-size: 34px; font-weight: 700; color: var(--mute); letter-spacing: 0.02em; }}
.brand b {{ color: var(--blue); }} .brand b em {{ color: var(--orange); font-style: normal; }}
.prog {{ display: flex; gap: 12px; }}
.prog i {{ display: block; width: 56px; height: 12px; border-radius: 6px; background: #26324a; }}
.prog i.on {{ background: var(--orange); }}
.scene {{ padding: 250px 80px 0; display: flex; flex-direction: column; gap: 34px; }}
.pill {{ align-self: flex-start; padding: 14px 28px; border-radius: 999px; background: #1d2a44; color: var(--blue);
  font-size: 36px; font-weight: 700; }}
.hook {{ display: flex; flex-direction: column; gap: 50px; padding-top: 120px; }}
.big {{ font-size: 150px; line-height: 1.12; font-weight: 800; letter-spacing: -0.04em; }}
.big em {{ font-style: normal; color: var(--orange); }}
.sub {{ font-size: 64px; font-weight: 700; color: var(--mute); }} .sub b {{ color: var(--ink); }}
.title {{ font-size: 92px; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; }}
.desc {{ font-size: 50px; color: var(--mute); font-weight: 600; }} .desc b {{ color: var(--orange); }}
.rank {{ display: flex; align-items: baseline; gap: 10px; }}
.rank .no {{ font-size: 170px; font-weight: 900; color: var(--orange); line-height: 0.9; letter-spacing: -0.05em; }}
.rank .wi {{ font-size: 64px; font-weight: 800; color: var(--orange); }}
.rank .cat {{ margin-left: 24px; padding: 10px 26px; border: 4px solid var(--blue); border-radius: 18px; color: var(--blue);
  font-size: 52px; font-weight: 800; font-family: var(--mono); align-self: center; }}
.code {{ background: #0a0f1a; border: 2px solid #26324a; border-radius: 28px; padding: 40px 40px; font-family: var(--mono);
  font-size: 36px; line-height: 1.55; color: #d9e1f2; white-space: pre; box-shadow: 0 30px 60px rgba(0,0,0,.35); }}
.kw {{ color: var(--blue); font-weight: 700; }} .st {{ color: var(--green); }} .nu {{ color: var(--orange); }} .cm {{ color: #6f7d98; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 18px; }}
.chips span {{ padding: 16px 30px; background: var(--panel); border-radius: 18px; font-size: 40px; font-weight: 700; }}
.warn, .note {{ padding: 30px 38px; border-radius: 24px; font-size: 46px; font-weight: 700; line-height: 1.45; }}
.warn {{ background: rgba(255,93,93,.12); border-left: 10px solid var(--red); }} .warn b {{ color: var(--red); }}
.note {{ background: rgba(63,167,214,.12); border-left: 10px solid var(--blue); }} .note b {{ color: var(--orange); }}
.warn small, .note small {{ font-size: 36px; color: var(--mute); font-weight: 600; }}
code {{ font-family: var(--mono); color: var(--orange); }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }}
.card {{ background: var(--panel); border-radius: 26px; padding: 30px 32px; display: flex; flex-direction: column; gap: 6px; }}
.card b {{ font-family: var(--mono); font-size: 58px; color: var(--blue); }}
.card span {{ font-size: 44px; font-weight: 800; }} .card i {{ font-style: normal; font-size: 28px; color: var(--mute); font-family: var(--mono); }}
.list {{ display: flex; flex-direction: column; gap: 22px; }}
.row {{ display: flex; align-items: center; gap: 30px; background: var(--panel); border-radius: 24px; padding: 26px 36px; font-size: 50px; }}
.row .no {{ font-size: 64px; font-weight: 900; color: var(--orange); width: 50px; }}
.row b {{ font-family: var(--mono); color: var(--blue); width: 160px; }} .row span:last-child {{ font-weight: 700; font-size: 40px; }}
.cta {{ margin-top: 20px; font-size: 54px; font-weight: 800; text-align: center; }} .cta b {{ color: var(--orange); }}
.cap {{ top: auto; bottom: 300px; height: auto; display: flex; justify-content: center; padding: 0 70px; }}
.cap span {{ background: rgba(0,0,0,.72); color: #fff; font-size: 48px; font-weight: 700; line-height: 1.4; padding: 18px 30px;
  border-radius: 18px; text-align: center; word-break: keep-all; }}
.bar {{ position: absolute; left: 0; bottom: 0; height: 10px; width: 1080px; background: var(--orange); transform-origin: left center; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
  <div class="brand"><b>My<em>SQL</em> 핵심</b><div class="prog"><i></i><i></i><i></i><i></i><i></i></div></div>
  {chr(10).join(clips)}
  {chr(10).join(caps)}
  <div class="bar"></div>
  <audio id="vo" src="assets/narration.mp3" data-start="0" data-duration="{TOTAL}" data-track-index="0"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
function enter(sel, t, dur) {{
  const items = document.querySelectorAll(sel + " .in");
  const step = Math.min(0.9, (dur * 0.55) / Math.max(1, items.length));
  items.forEach((el, i) => {{
    tl.fromTo(el, {{ opacity: 0, y: 50 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, Math.max(0, t - 0.1) + i * step);
  }});
  document.querySelectorAll(sel + " .code .ln").forEach((el, i, all) => {{
    tl.fromTo(el, {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power2.out" }}, t + 0.6 + i * Math.min(0.8, dur * 0.4 / all.length));
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
