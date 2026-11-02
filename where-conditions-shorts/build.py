"""Builds assets/narration.mp3, index.html and queries.sql from vo.json (run gen_vo.py first)."""
import json, re, subprocess, html, sqlite3

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
      "LIMIT IS NULL BETWEEN NOT").split()
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

# One colour per category, used for that category's rows everywhere: book=k1, pen=k2, note=k3.
CAT = {"book": "k1", "pen": "k2", "note": "k3"}
P = {1: ("SQL 입문서", "book", 18000), 2: ("볼펜", "pen", 1500), 3: ("SQL 문제집", "book", 9000),
     4: ("노트", "note", 3000), 5: ("만년필", "pen", 45000), 6: ("형광펜", "pen", 2000)}

def rows(ids, cols=("name", "price")):
    idx = {"id": None, "name": 0, "category": 1, "price": 2}
    return [(CAT[P[i][1]], tuple(i if c == "id" else P[i][idx[c]] for c in cols)) for i in ids]

def filtered(keep, cols=("name", "category", "price")):
    """All six products; the ones the condition drops are struck through."""
    return [(rc if i in keep else "out", v) for i, (rc, v) in zip(range(1, 7), rows(range(1, 7), cols))]

def res(ids, bad=()):
    """One-line result: product names as chips in their category colour; `bad` ones flagged."""
    chips = "".join(f'<span class="{CAT[P[i][1]]}{" bad" if i in bad else ""}">{P[i][0]}{" ⚠" if i in bad else ""}</span>' for i in ids)
    return f'<div class="res in"><i>결과 →</i>{chips}</div>'

# --- example queries: every query on screen runs on P before anything is drawn ---
# Each must return what the narration says (`expect`), the result chips/tables are drawn from what
# it actually returns (got()), and all of them are saved to queries.sql to run in sqlite3 or MySQL.
SCHEMA = "CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(50), category VARCHAR(20), price INT);"
DB = sqlite3.connect(":memory:")
DB.execute(SCHEMA)
DB.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", [(i, *v) for i, v in P.items()])
QUERIES, LAST = [], []

def qcode(sid, lines, *expect, mark=()):
    """Code block of one or more statements; statement k must return the ids in expect[k]."""
    stmts = [x.strip() for x in "\n".join(lines).split(";") if x.strip()]
    if len(stmts) != len(expect):
        raise ValueError(f"{sid}: {len(stmts)} statements but {len(expect)} expected results")
    for st, want in zip(stmts, expect):
        full = st if st.upper().startswith("SELECT") else "SELECT name, category, price\nFROM products\n" + st
        DB.execute(full).fetchall()  # the statement as shown must run
        ids = [r[0] for r in DB.execute("SELECT id FROM products " + full[full.upper().index("WHERE"):] + " ORDER BY id")]
        if ids != sorted(want):
            raise ValueError(f"{sid}: {st!r} returns {ids}, but the script expects {sorted(want)}")
        QUERIES.append((sid, full, ids))
        LAST[:] = ids
    return code(lines, mark)

def got():
    """Ids the last qcode() statement returned."""
    return list(LAST)

def lab(text):
    return f'<div class="tlabel in">{text}</div>'

EXEC = ["비교 · BETWEEN", "AND · OR", "( ) 괄호", "IN · NOT IN", "LIKE  %  _", "IS NULL"]
EXEC_SAID = ["비교", "앤드", "괄호", "인", "라이크", "이즈"]
EXEC_END = "이것만"

scenes = {
 "hook": '''<div class="hook">
   <div class="pill in">MySQL · WHERE 핵심 정리</div>
   <h1 class="big in"><em>WHERE</em><br/>AND · OR<br/>IN · LIKE</h1>
   <div class="sub in">원하는 행만 <b>골라내기</b></div>
 </div>''',
 "intro": head("WHERE의 역할", "WHERE", "조건이 <b>참인 행</b>만 남김")
    + code(["SELECT name, price", "FROM products", "WHERE 조건;"], mark=(2,))
    + table(["id", "name", "category", "price"], rows(range(1, 7), ("id", "name", "category", "price")), "products · 상품 6개"),
 "compare": head("STEP 1 · 비교", "비교 연산자", "같다 · 다르다 · 크다 · 작다")
    + '<div class="chips in"><span>= 같다</span><span>&lt;&gt;  != 다르다</span><span>&gt;  &gt;=  &lt;  &lt;=</span></div>'
    + qcode("compare", ["SELECT name, price", "FROM products", "WHERE price >= 10000;"], [1, 5], mark=(2,))
    + table(["name", "price"], rows(got()), "결과 · 1만 원 이상"),
 "string": head("STEP 1-1", "문자열 비교", "값은 <b>작은따옴표</b>로 감싸기")
    + qcode("string", ["SELECT name, category", "FROM products", "WHERE category = 'book';"], [1, 3], mark=(2,))
    + table(["name", "category"], rows(got(), ("name", "category")), "결과"),
 "between": head("STEP 1-2", "BETWEEN", "범위 조건 · <b>양 끝 값 포함</b>")
    + qcode("between", ["SELECT name, price", "FROM products", "WHERE price", "  BETWEEN 3000 AND 10000;"], [3, 4], mark=(2, 3))
    + table(["name", "price"], rows(got()), "결과 · 노트(3000)도 포함")
    + '<div class="note in">같은 뜻 <code><br/>price &gt;= 3000 AND price &lt;= 10000</code></div>',
 "and": head("STEP 2 · AND", "AND", "두 조건이 <b>모두</b> 참")
    + qcode("and", ["SELECT name, category, price", "FROM products", "WHERE category = 'book'", "  AND price < 10000;"], [3], mark=(2, 3))
    + table(["name", "category", "price"], filtered(got()), "결과 · 책이면서 1만 원 미만 → 1개"),
 "or": head("STEP 2-1", "OR", "둘 중 <b>하나만</b> 참이어도 통과")
    + qcode("or", ["SELECT name, category, price", "FROM products", "WHERE category = 'pen'", "   OR price >= 18000;"], [1, 2, 5, 6], mark=(2, 3))
    + table(["name", "category", "price"], filtered(got()), "결과 · 펜이거나 18000원 이상 → 4개"),
 "paren": head("STEP 2-2", "AND가 먼저!", "책이나 펜 중 <b>1만 원 이상</b>")
    + lab("✗ 괄호 없음 → AND부터 묶임")
    + qcode("paren", ["WHERE category = 'book'", "   OR category = 'pen'", "  AND price >= 10000;"], [1, 3, 5], mark=(1, 2))
    + res(got(), bad=(3,))
    + lab("✓ 괄호로 의도 고정")
    + qcode("paren", ["WHERE (category = 'book'", "    OR category = 'pen')", "  AND price >= 10000;"], [1, 5], mark=(0, 1))
    + res(got()),
 "in": head("STEP 3 · IN", "IN · NOT IN", "<b>OR 여러 개</b>를 짧게")
    + qcode("in", ["WHERE category", "  IN ('book', 'pen');"], [1, 2, 3, 5, 6], mark=(1,))
    + res(got())
    + qcode("in", ["WHERE category", "  NOT IN ('book', 'pen');"], [4], mark=(1,))
    + res(got())
    + '<div class="note in">IN = <code>category = \'book\' OR …</code></div>',
 "like": head("STEP 4 · LIKE", "LIKE 패턴", "<b>%</b> 0글자 이상 · <b>_</b> 정확히 1글자")
    + qcode("like", ["WHERE name LIKE '%펜';"], [2, 6], mark=(0,))
    + res(got())
    + qcode("like", ["WHERE name LIKE '_펜';"], [2], mark=(0,))
    + res(got())
    + '<div class="chips in"><span>% = 아무 글자 0개 이상</span><span>_ = 아무 글자 1개</span></div>',
 "like2": head("STEP 4-1", "LIKE 주의점", "<b>%로 시작</b>하면 범위 검색 불가")
    + '<div class="vs"><div class="card in"><b>\'SQL%\'</b><span>앞부분 고정</span><span class="ok">범위 검색 ✓</span></div>'
      '<div class="card in"><b>\'%펜\'</b><span>앞부분 미정</span><span class="ng">범위 검색 ✗</span></div></div>'
    + '<div class="warn in">⚠ 인덱스로 범위를 좁힐 수 없어<br/>데이터가 많으면 <b>느려질 수 있음</b><br/><small>앞부분을 안다면 고정한 패턴으로</small></div>',
 "null": head("STEP 5 · NULL", "IS NULL", "NULL은 <b>=로 비교 불가</b>")
    + lab("✗ 항상 결과 없음")
    + qcode("null", ["WHERE category = NULL;"], [], mark=(0,))
    + lab("✓ NULL 찾기 · 제외하기")
    + qcode("null", ["WHERE category IS NULL;", "WHERE category IS NOT NULL;"], [], [1, 2, 3, 4, 5, 6], mark=(0, 1))
    + lab("⚠ NOT IN 목록에 NULL → 결과 없음")
    + qcode("null", ["WHERE category", "  NOT IN ('book', NULL);"], [], mark=(1,)),
 "outro": '<div class="pill in">정리</div><h2 class="title in">WHERE 핵심 6가지</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{c}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
SECTION = {s["id"]: s["section"] for s in json.load(open("script.json"))}
with open("queries.sql", "w") as f:
    f.write("-- 영상에 나오는 예제 쿼리 (build.py가 생성 · 직접 고치지 말 것)\n"
            "-- 실행: sqlite3 :memory: < queries.sql   (MySQL에서도 그대로 실행 가능)\n\n"
            + SCHEMA + "\nINSERT INTO products VALUES\n"
            + ",\n".join(f"  ({i}, '{n}', '{c}', {pr})" for i, (n, c, pr) in P.items()) + ";\n")
    for sid, full, ids in QUERIES:
        f.write(f"\n-- [{SECTION[sid]}] 결과: {', '.join(P[i][0] for i in ids) or '없음'}\n{full};\n")

PROG = {"compare": 1, "string": 1, "between": 1, "and": 2, "or": 2, "paren": 2, "in": 3,
        "like": 4, "like2": 4, "null": 5}

def bad_cut(x, i):
    """True if a caption break at space `i` would split an amount or orphan a dependent word."""
    prev, nxt = x[:i].split()[-1], x[i + 1:].split()[0]
    return bool(re.search(r"\d[천만백]?$|^[A-Z]+$", prev)) or nxt.startswith(("원", "이상", "이하", "미만", "않", "있어도"))

def split_caption(text, limit=24):
    """Comma-first split; long pieces halved at a space; short fragments merged."""
    pieces = [x.strip() + "," for x in text.split(",")]
    pieces[-1] = pieces[-1][:-1]
    out = []
    for x in pieces:
        while len(x) > limit and " " in x:
            mid = len(x) // 2
            cut = min((i for i, c in enumerate(x) if c == " "), key=lambda i: abs(i - mid) + 100 * bad_cut(x, i))
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
js.append(f'tl.to("#ex{len(EXEC)}", {{backgroundColor: "#131c2e", scale: 1, duration: 0.3}}, {word_time("outro", EXEC_END)} + 0.6);')

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
#root {{ position: relative; width: 100%; height: 100%; font-variant-ligatures: none; font-family: var(--font); color: var(--ink); overflow: hidden;
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
.vs .card span {{ font-size: 44px; font-weight: 800; }} .vs .card .ok {{ color: var(--green); }} .vs .card .ng {{ color: var(--red); }}
.res {{ display: flex; flex-wrap: wrap; align-items: center; gap: 14px; margin-top: -6px; }}
.res i {{ font-style: normal; font-size: 34px; color: var(--mute); font-weight: 700; }}
.res span {{ padding: 8px 22px; border-radius: 14px; background: var(--panel); font-size: 40px; font-weight: 700; }}
.res span.k1 {{ color: var(--orange); }} .res span.k2 {{ color: var(--green); }} .res span.k3 {{ color: var(--violet); }}
.res span.bad {{ color: var(--red); background: rgba(255,93,93,.14); box-shadow: inset 0 0 0 3px var(--red); }} .vs .card em {{ font-style: normal; color: var(--orange); }}
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
  <div class="brand"><b>SQL <em>WHERE</em> 정리</b><div class="prog"><i></i><i></i><i></i><i></i><i></i></div></div>
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
    const at = Math.max(0, t - 0.1) + i * step;
    tl.fromTo(el, {{ opacity: 0, y: 50 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, at);
    el.querySelectorAll(".ln").forEach((ln, j) => {{
      tl.fromTo(ln, {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power2.out" }}, at + 0.15 + j * 0.3);
    }});
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
