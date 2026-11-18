"""Builds assets/narration.mp3, index.html and examples.txt from vo.json (run gen_vo.py first)."""
import json, re, subprocess, html, os, tempfile

# SPEED: tempo vs. the earlier episodes (TTS rate +12% → +34%); gaps and motion shrink by the same factor
SPEED = 1.2
LEAD, GAP, TAIL = round(0.3 / SPEED, 3), round(0.45 / SPEED, 3), 1.0
XF = round(0.15 / SPEED, 3)  # scene change this long before the next narration
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

# --- Java highlighting ---
KW = ("public class static void String int double boolean new if else switch case default break "
      "for while do continue true false null this return extends super final abstract interface implements instanceof").split()
TOK = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//.*|\d+(?:\.\d+)?[LfF]?\b|@\w+|\w+|.')
def hl(line):
    out = []
    for m in TOK.finditer(line):
        x = m.group()
        if x[0] in "\"'":
            body = re.sub(r"(\\.)", r'<span class="es">\1</span>', html.escape(x, quote=False))
            out.append(f'<span class="st">{body}</span>')
        elif x.startswith("//"):
            out.append(f'<span class="cm">{html.escape(x)}</span>')
        elif x[0].isdigit():
            out.append(f'<span class="nu">{x}</span>')
        elif x in KW or x[0] == "@":
            out.append(f'<span class="kw">{x}</span>')
        else:
            out.append(html.escape(x, quote=False))
    return "".join(out)

def code(lines, mark=(), sm=False):
    """`mark`: indexes of lines to tint as the point of the scene. `sm`: smaller font for whole programs."""
    for l in lines:
        assert len(l) <= 33, f"code line over 33 chars: {l!r}"
    return f'<div class="code in{" sm" if sm else ""}">' + "".join(
        f'<div class="ln{" mk" if i in mark else ""}">{hl(l) or "&nbsp;"}</div>' for i, l in enumerate(lines)) + "</div>"

def head(step, title, desc):
    return f'<div class="pill in">{step}</div><h2 class="title in">{title}</h2><p class="desc in">{desc}</p>'

def lab(text):
    return f'<div class="tlabel in">{text}</div>'

# --- example programs: every snippet on screen is compiled and run before anything is drawn ---
# Each must print what the narration says (`expect`, or the `// …` results written on the shown
# lines), fail to compile with the error it names, or stop with the runtime error it names
# (`runtime=`); the console boxes are drawn from what actually happened, and all of them are
# saved to examples.txt. Compiled with -g so a NullPointerException names the variable.
TMP = tempfile.mkdtemp(prefix="java-shorts-")
EXAMPLES, LAST = [], {"out": "", "rt": ""}
IMPORTS = ["import java.util.ArrayList;", "import java.util.List;", ""]
HELLO = ["public class Main {",
         "  public static void main(String[] args) {",
         '    System.out.println("Hello World");',
         "  }",
         "}"]

def wrap(lines):
    """Statements shown alone run inside main of a Main.java that imports ArrayList and List."""
    return "\n".join(IMPORTS + HELLO[:2] + ["    " + l for l in lines] + HELLO[3:] + [""])

def run(src, fname="Main.java"):
    """(stdout, javac's first error or None, first line of the runtime error or None)."""
    d = tempfile.mkdtemp(dir=TMP)
    open(os.path.join(d, fname), "w").write(src)
    c = subprocess.run(["javac", "-g", "-J-Duser.language=en", "-encoding", "UTF-8", fname], cwd=d, capture_output=True, text=True)
    if c.returncode:
        LAST["ce2"] = [l.strip() for l in c.stderr.split("\n")[1:]]
        return None, re.search(r"error: (.*)", c.stderr).group(1), None
    r = subprocess.run(["java", "-Duser.language=en", "-cp", d, "Main"], capture_output=True, text=True)
    return r.stdout, None, (r.stderr.split("\n")[0] if r.returncode else None)

def check(sid, src, expect=None, runtime=None, fname="Main.java", label=None):
    out, ce, rt = run(src, fname)
    if ce is not None:
        raise ValueError(f"{sid}: does not compile: {ce}")
    if runtime is not None:
        if rt is None or runtime not in rt:
            raise ValueError(f"{sid}: expected runtime error {runtime!r}, got {rt!r} / output {out!r}")
    elif out != expect or rt:
        raise ValueError(f"{sid}: prints {out!r}, but the script expects {expect!r} ({rt or 'no error'})")
    EXAMPLES.append((sid, fname, src, out, rt or label))
    return out, rt

def jcode(sid, lines, expect, mark=(), hidden=(), pre=(), sm=False):
    """Code block; the statements (between invisible `pre` setup and `hidden` prints, run inside main)
    must print `expect`."""
    LAST["out"], _ = check(sid, wrap(list(pre) + list(lines) + list(hidden)), expect)
    return code(lines, mark, sm)

SHOW = re.compile(r"^// (\w+) → (.*)$")
def jshow(sid, lines, mark=(), pre=(), sm=False):
    """Code block whose `// …` comments are the results, each checked where it stands:
    `x.get(0);  // 민수` prints that call, and a whole line `// names → [...]` prints `names`."""
    run_, want = [], []
    for l in lines:
        m = SHOW.match(l.strip())
        if m:
            run_.append(f"System.out.println({m.group(1)});"); want.append(m.group(2))
        elif "// " in l:
            stmt, res = l.split("// ")
            run_.append(f"System.out.println({stmt.strip().rstrip(';')});"); want.append(res.strip())
        elif not l.startswith("import "):  # imports are already at the top of every program
            run_.append(l)
    LAST["out"], _ = check(sid, wrap(list(pre) + run_), "".join(w + "\n" for w in want))
    return code(lines, mark, sm)

def jrt(sid, lines, runtime, mark=(), pre=()):
    """Code block that compiles but stops at run time with an error containing `runtime`."""
    _, LAST["rt"] = check(sid, wrap(list(pre) + list(lines)), runtime=runtime)
    return code(lines, mark)

def term(cmds=(), label="실행 결과", out=None, cls="term in"):
    """Console box: optional shell commands, then what the last jcode() printed (or `out`)."""
    out = LAST["out"] if out is None else out
    body = "".join(f'<div class="cmd">$ {html.escape(c)}</div>' for c in cmds)
    if out:
        body += "".join(f"<div>{html.escape(l) or '&nbsp;'}</div>" for l in out.rstrip("\n").split("\n"))
    else:
        body += '<div class="z">(출력 없음)</div>'
    return f'<div class="{cls}"><i>{label}</i>{body}</div>'

def rterm():
    """The last jrt() block's runtime error: exception name on its own line, then the message."""
    msg = LAST["rt"].replace('Exception in thread "main" ', "").replace("Exception: ", "Exception:\n")
    return '<div class="term err in"><i>실행 오류</i>' + "".join(f"<div>{html.escape(l)}</div>" for l in msg.split("\n")) + "</div>"

def jce(sid, lines, error, detail="", mark=(), pre=(), sm=False):
    """Code block that must NOT compile: javac's first error has to contain `error`, and, if given,
    one of the lines under it (the caret's explanation) has to contain `detail`."""
    src = wrap(list(pre) + list(lines))
    out, ce, rt = run(src)
    if ce is None or error not in ce:
        raise ValueError(f"{sid}: expected compile error {error!r}, got {ce!r} / output {out!r}")
    if detail and not any(detail in l for l in LAST["ce2"]):
        raise ValueError(f"{sid}: expected error detail {detail!r}, got {LAST['ce2']!r}")
    LAST["ce"], LAST["cd"] = ce, detail
    EXAMPLES.append((sid, "Main.java", src, "", f"컴파일 오류: {ce}" + (f" / {detail}" if detail else "")))
    return code(lines, mark, sm)

def cterm():
    """The last jce() block's compile error."""
    extra = f'<div class="z">{html.escape(LAST["cd"])}</div>' if LAST.get("cd") else ""
    return f'<div class="term err in"><i>컴파일 오류</i><div>{html.escape(LAST["ce"])}</div>{extra}</div>'

def table(cols, rows, label):
    head_ = "".join(f"<th>{c}</th>" for c in cols)
    body = "".join(f'<tr class="{k}">' + "".join(f"<td>{html.escape(v)}</td>" for v in cells) + "</tr>" for k, cells in rows)
    return f'<div class="tbl in">{lab(label)}<table><tr>{head_}</tr>{body}</table></div>'

def card(small, big, span="", k=""):
    return (f'<div class="card"><small>{small}</small><b{f" class={chr(34)}{k}{chr(34)}" if k else ""}>{big}</b>'
            + (f"<span>{span}</span>" if span else "") + "</div>")

# --- example data: 민수 (k1) · 서준 (k2) · 지우 (k3) · 하은 (no colour); scores 85 · 92 · 78 ---
BRAND = "자바 입문 <em>래퍼 클래스와 List</em> 정리"
K = {"민수": "k1", "서준": "k2", "지우": "k3", "하은": "k0"}

NEW_NAMES = ["ArrayList<String> names =", "    new ArrayList<>();"]
ADD3 = ['names.add("민수");', 'names.add("서준");', 'names.add("지우");']
NEW_SCORES = ["List<Integer> scores =", "    new ArrayList<>();"]
ADD_SC = ["scores.add(85);", "scores.add(92);", "scores.add(78);"]

def listed(s):
    """'[민수, 서준]' → ['민수', '서준']"""
    return [x.strip() for x in s.strip()[1:-1].split(",") if x.strip()]

def idxgrid(rows):
    """Index table: one row per (label, names, removed index or None); each name keeps its person's
    colour wherever it moves, a removed one is struck out."""
    width = max(len(n) for _, n, _ in rows)
    head_ = '<i></i>' + "".join(f"<i>[{j}]</i>" for j in range(width))
    body = ""
    for label, names, gone in rows:
        body += f"<i>{label}</i>" + "".join(
            f'<b class="{K[n]}{" out" if j == gone else ""}">{n}</b>' for j, n in enumerate(names))
        body += "<b class=\"z\"></b>" * (width - len(names))
    return (f'<div class="ig in" style="grid-template-columns: 170px repeat({width}, 1fr)">{head_}{body}</div>')

def edit_grid():
    """Before/after table of remove(0), drawn from what the edit scene actually printed."""
    out = LAST["out"].split("\n")
    return idxgrid([("remove 전", listed(out[0]), 0), ("remove 후", listed(out[1]), None)])

CSS_EXTRA = """
.chips em { font-style: normal; color: var(--orange); }
.chips .k1 { color: var(--orange); font-family: var(--mono); } .chips .k2 { color: var(--green); font-family: var(--mono); }
.chips .r { color: var(--red); }
.vs .card small { font-size: 32px; color: var(--mute); font-weight: 700; }
.vs .card span { font-family: var(--mono); font-size: 44px; color: var(--blue); font-weight: 800; }
.vs .card.on b, .vs .card.on span { color: var(--orange); }
.flow { display: flex; flex-direction: column; gap: 14px; }
.flow div { display: flex; align-items: center; gap: 18px; font-size: 40px; font-weight: 700; }
.flow code { background: var(--panel); padding: 8px 20px; border-radius: 14px; }
.flow em { font-style: normal; color: var(--mute); }
.ig { display: grid; gap: 10px; align-items: center; }
.ig i { font-style: normal; font-family: var(--mono); font-size: 32px; font-weight: 700; color: var(--mute); text-align: center; }
.ig b { height: 92px; background: var(--panel); border-radius: 16px; display: flex; align-items: center; justify-content: center;
  font-size: 44px; font-weight: 800; }
.ig b.out { color: #5b6782; text-decoration: line-through; box-shadow: inset 0 0 0 3px var(--red); }
.ig b.z { background: none; border: 3px dashed #26324a; }
.k0 { color: var(--ink); }
.tbl tr.hi td { color: var(--orange); }
"""

EXEC = ["래퍼 = 기본 타입을 객체로", "오토박싱·언박싱 (null 주의)", "add · get · size()", "remove → 뒤 칸이 당겨짐",
        "< > 안엔 기본 타입 ✗ → Integer", "변수는 기본적으로 List 타입", "remove(1) = 1번 칸"]
EXEC_SAID = ["래퍼", "오토박싱과", "어레이리스트는", "리무브하면", "꺾쇠", "변수는", "마지막으로"]
EXEC_END = "구독과"

scenes = {
 "hook": '''<div class="hook">
   <div class="pill in">JAVA 입문 · 열일곱 번째</div>
   <h1 class="big in">래퍼 클래스와<br/><em>List</em></h1>
   <div class="chips in"><span>배열은 <em>크기 고정</em></span><span><code>&lt;int&gt;</code> 는 <em class="r">안 됨</em></span></div>
 </div>''',
 "wrap": head("STEP 1 · 래퍼 클래스", "기본 타입을 객체로", "기본 타입 값을 <b>감싼 클래스</b>")
    + table(["기본 타입", "래퍼 클래스"], [("hi", ["int", "Integer"]), ("hi", ["char", "Character"]),
                                      ("", ["double", "Double"]), ("", ["boolean", "Boolean"]),
                                      ("", ["long …", "Long … (첫 글자 대문자)"])], "이름이 바뀌는 건 둘뿐")
    + jcode("wrap", ["Integer a = 85;", "Character c = 'A';", "Double d = 3.5;", "Boolean b = true;"],
            "85 A 3.5 true\n", hidden=['System.out.println(a + " " + c + " " + d + " " + b);'], sm=True)
    + term(label="네 값 출력"),
 "box": head("STEP 2 · 오토박싱·언박싱", "자동으로 바뀐다", "넣을 때 감싸고, 쓸 때 풀고")
    + jcode("box", ["Integer n = 85;  // 오토박싱", "int m = n + 1;   // 언박싱", "System.out.println(m);",
                    'int k = Integer.parseInt("92");', "System.out.println(k + 1);"], "86\n93\n", mark=(0, 1, 3), sm=True)
    + term()
    + '<div class="flow in"><div><code>int</code><em>→</em><code>Integer</code> <b class="k1">오토박싱</b></div>'
      '<div><code>Integer</code><em>→</em><code>int</code> <b class="k1">언박싱</b></div></div>'
    + '<div class="note in"><b>parseInt</b> : 문자열 → 숫자</div>',
 "npe": head("STEP 2-1 · null 언박싱", "null 은 풀 수 없다", "래퍼는 객체라서 <b>null</b> 가능")
    + jrt("npe", ["Integer n = null;  // OK", "int m = n;  // 언박싱"], 'java.lang.NullPointerException: Cannot invoke "java.lang.Integer.intValue()" because "n" is null', mark=(1,))
    + rterm()
    + '<div class="warn in">컴파일은 되고 <b>실행 중 오류</b><br/>null 이 들어올 수 있으면 조심!</div>',
 "list": head("STEP 3 · ArrayList", "크기를 안 정한다", "꺾쇠로 <b>담을 타입</b> 정하기 = 제네릭")
    + lab("// 뒤 주석 = 그 줄을 실행한 결과 값")
    + jshow("list", ["import java.util.ArrayList;"] + NEW_NAMES + ADD3 + ["// names → [민수, 서준, 지우]", "names.size();   // 3", "names.get(0);   // 민수"],
            mark=(1, 7, 8))
    + '<div class="note in"><b>&lt;String&gt;</b> → 문자열만 들어간다<br/><small>오른쪽 &lt;&gt; 는 비워도 OK</small></div>',
 "idx": head("STEP 3-1 · 범위 밖", "인덱스는 0부터", "배열과 같다 → <b>get(3)</b> 은 오류")
    + jrt("idx", ["names.get(3);"], "java.lang.IndexOutOfBoundsException: Index 3 out of bounds for length 3",
          mark=(0,), pre=NEW_NAMES + ADD3)
    + rterm()
    + '<div class="vs in">' + card("배열", "arr[0]", "arr.length") + card("ArrayList", "get(0)", "size()").replace('class="card"', 'class="card on"') + "</div>",
 "edit": head("STEP 4 · set · remove · contains", "지우면 당겨진다", "뒤 칸이 <b>한 칸씩 앞으로</b>")
    + jshow("edit", ['names.add("하은");', "// names → [민수, 서준, 지우, 하은]", "names.remove(0);", "// names → [서준, 지우, 하은]",
                     "names.get(0);  // 서준", 'names.contains("민수"); // false', 'names.set(0, "민수");',
                     "// names → [민수, 지우, 하은]"], mark=(2, 4, 6), pre=NEW_NAMES + ADD3, sm=True)
    + edit_grid()
    + '<div class="note in"><b>set</b> = 덮어쓰기 (서준 → 민수)<br/><small>끼워 넣는 게 아님</small></div>',
 "nums": head("STEP 5 · List&lt;Integer&gt;", "점수는 Integer 로", "&lt; &gt; 안엔 <b>기본 타입 ✗</b>")
    + jce("nums", ["ArrayList<int> scores;"], "unexpected type", detail="required: reference", sm=True)
    + cterm()
    + jshow("nums", ["import java.util.List;"] + NEW_SCORES + ADD_SC + ["int sum = 0;", "for (int s : scores) sum += s;", "// sum → 255"],
            mark=(1, 7), sm=True)
    + '<div class="note in">변수는 <b>List</b> 타입 <small>(업캐스팅)</small></div>',
 "rm": head("STEP 5-1 · remove(1) 의 함정", "1 은 값? 칸?", "<b>인덱스</b>를 받는 remove 가 먼저")
    + jshow("rm", ["// scores → [85, 92, 78]", "scores.remove(1);", "// scores → [85, 78]"],
            mark=(1,), pre=NEW_SCORES + ADD_SC, sm=True)
    + '<div class="warn in">값 1 이 아니라 <b>1번 칸</b>(92)을 지운다</div>'
    + jshow("rm", ["scores.remove(", "    Integer.valueOf(85));", "// scores → [92, 78]"],
            mark=(0, 1), pre=NEW_SCORES + ADD_SC, sm=True),
 "outro": '<div class="pill in">정리</div><h2 class="title in">래퍼 클래스와 List</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"wrap": 1, "box": 2, "npe": 2, "list": 3, "idx": 3, "edit": 4, "nums": 5, "rm": 5}


SECTION = {s["id"]: s["section"] for s in json.load(open("script.json"))}
with open("examples.txt", "w") as f:
    f.write("// 영상에 나오는 예제 프로그램 (build.py가 생성 · 직접 고치지 말 것)\n"
            "// 각 예제를 파일 이름대로 저장한 뒤: javac -g -encoding UTF-8 Main.java && java Main\n")
    for sid, fname, src, out, rt in EXAMPLES:
        res = (rt if rt.startswith("컴파일") else f"실행 오류: {rt}") if rt else "출력 없음 (컴파일·실행 성공)" if not out else "출력:\n" + "".join(f"//   {l}\n" for l in out.rstrip("\n").split("\n"))
        f.write(f"\n// [{SECTION[sid]}] {fname} → {res.rstrip()}\n{src}\n")



def bad_cut(x, i):
    """True if a caption break at space `i` would split an amount or orphan a dependent word."""
    prev, nxt = x[:i].split()[-1], x[i + 1:].split()[0]
    return bool(re.search(r"\d[천만백]?$|^[A-Z]+$|^한$", prev)) or nxt.startswith(("원", "이상", "이하", "미만", "않", "있어도"))

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
    vis_start = 0 if s is vo[0] else st - XF
    vis_end = TOTAL if s is vo[-1] else vo[vo.index(s) + 1]["start"] - XF
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
.code.sm {{ font-size: 34px; padding: 26px 28px; }}
.code .ln {{ margin: 0 -14px; padding: 0 14px; border-radius: 10px; }}
.code .ln.mk {{ background: rgba(242,145,17,.13); }}
.kw {{ color: var(--blue); font-weight: 700; }} .st {{ color: var(--green); }} .nu {{ color: var(--orange); }} .cm {{ color: #6f7d98; }} .es {{ color: var(--orange); font-weight: 700; }}
.term {{ background: #05080f; border: 2px solid #26324a; border-radius: 22px; padding: 18px 32px 22px; font-family: var(--mono);
  font-size: 40px; line-height: 1.4; color: var(--ink); white-space: pre; tab-size: 8; }}
.term i {{ display: block; font-style: normal; font-family: var(--font); font-size: 28px; font-weight: 700; color: var(--mute); margin-bottom: 6px; }}
.term .cmd {{ color: var(--blue); }}
.term.err {{ border-color: rgba(255,93,93,.5); color: var(--red); font-size: 34px; white-space: normal; }}
.warn small {{ font-size: 36px; color: var(--mute); font-weight: 600; }}
.nest > div, .nest > div div {{ border: 3px solid; border-radius: 22px; padding: 16px 26px 20px; display: flex; flex-direction: column; gap: 12px; }}
.nest b {{ font-size: 38px; font-weight: 800; font-family: var(--mono); }}
.nest .k1 {{ border-color: var(--orange); }} .nest .k1 > b {{ color: var(--orange); }}
.nest .k2 {{ border-color: var(--green); }} .nest .k2 > b {{ color: var(--green); }}
.nest .k3 {{ border-color: var(--violet); }} .nest .k3 > b {{ color: var(--violet); }}
.chips {{ display: flex; flex-wrap: wrap; gap: 18px; }}
.chips span {{ padding: 16px 30px; background: var(--panel); border-radius: 18px; font-size: 42px; font-weight: 700; }}
.warn, .note {{ padding: 26px 36px; border-radius: 24px; font-size: 44px; font-weight: 700; line-height: 1.45; }}
.warn {{ background: rgba(255,93,93,.12); border-left: 10px solid var(--red); }} .warn b {{ color: var(--red); }}
.note {{ background: rgba(63,167,214,.12); border-left: 10px solid var(--blue); }} .note b {{ color: var(--orange); }}
.note small {{ font-size: 38px; color: var(--mute); font-weight: 600; font-family: var(--mono); }}
code {{ font-family: var(--mono); color: var(--orange); }}
.var {{ display: grid; grid-template-columns: 1fr 1.3fr 1fr; gap: 18px; }}
.var div {{ background: var(--panel); border-radius: 24px; padding: 20px 30px 24px; display: flex; flex-direction: column; gap: 4px; }}
.var small {{ font-size: 32px; font-weight: 700; color: var(--mute); }}
.var b {{ font-family: var(--mono); font-size: 64px; }}
.var .v {{ border: 4px dashed var(--orange); }} .var .v b {{ color: var(--orange); }}
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
.arr {{ display: flex; align-items: flex-start; gap: 14px; }}
.arr .nm {{ font-family: var(--mono); font-size: 38px; font-weight: 700; color: var(--mute); padding-top: 34px; margin-right: 6px; }}
.arr .nm.tn {{ margin-left: 30px; color: var(--blue); }}
.cw {{ display: flex; flex-direction: column; align-items: center; gap: 6px; }}
.cw small {{ font-family: var(--mono); font-size: 32px; font-weight: 700; color: var(--mute); height: 40px; }}
.box {{ position: relative; width: 150px; height: 110px; background: var(--panel); border: 3px solid #26324a; border-radius: 18px; }}
.box b {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 56px; font-weight: 800; }}
.box.ghost {{ border: 3px dashed var(--red); background: rgba(255,93,93,.08); }} .box.ghost b {{ color: var(--red); }}
.k1 {{ color: var(--orange); }} .k2 {{ color: var(--green); }} .k3 {{ color: var(--violet); }} .z {{ color: var(--mute); }}
#sc-swap .arr .cw:last-child .box {{ border-style: dashed; border-color: var(--blue); }}
.gridw {{ display: flex; flex-direction: column; gap: 22px; }}
.grid {{ display: grid; gap: 12px; align-items: center; }}
.grid i {{ font-style: normal; font-family: var(--mono); font-size: 32px; font-weight: 700; color: var(--mute); text-align: center; }}
.grid b {{ height: 96px; background: var(--panel); border-radius: 16px; display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 52px; font-weight: 800; }}
.grid b.k1 {{ box-shadow: inset 0 0 0 4px var(--orange); }}
.dims {{ display: flex; flex-wrap: wrap; gap: 16px; }}
.dims span {{ padding: 12px 26px; background: var(--panel); border-radius: 16px; font-size: 40px; font-weight: 700; }}
.dims em {{ font-style: normal; color: var(--orange); }}
.share {{ display: flex; gap: 12px; }}
.pp {{ width: 140px; display: flex; flex-direction: column; align-items: center; gap: 6px; }}
.pp .cd {{ width: 140px; height: 190px; background: var(--panel); border: 3px solid var(--orange); border-radius: 18px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 46px; line-height: 1.15; }}
.pp.left .cd {{ border: 3px dashed var(--green); background: rgba(126,224,138,.08); }}
.pp small {{ font-size: 30px; font-weight: 700; color: var(--mute); }} .pp.left small {{ color: var(--green); }}
.chips .gt {{ background: none; padding: 16px 0; color: var(--mute); }}
.cap {{ top: auto; bottom: 260px; height: auto; display: flex; justify-content: center; padding: 0 60px; }}
.cap span {{ background: rgba(0,0,0,.78); color: #fff; font-size: 48px; font-weight: 700; line-height: 1.4; padding: 16px 30px;
  border-radius: 18px; text-align: center; word-break: keep-all; }}
.bar {{ position: absolute; left: 0; bottom: 0; height: 10px; width: 1080px; background: var(--orange); transform-origin: left center; }}
{CSS_EXTRA}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
  <div class="brand"><b>{BRAND}</b><div class="prog"><i></i><i></i><i></i><i></i><i></i></div></div>
  {chr(10).join(clips)}
  {chr(10).join(caps)}
  <div class="bar"></div>
  <audio id="vo" src="assets/narration.mp3" data-start="0" data-duration="{TOTAL}" data-track-index="0"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const SP = {SPEED};
function enter(sel, t, dur) {{
  const items = document.querySelectorAll(sel + " .in");
  const step = Math.min(0.9 / SP, (dur * 0.5) / Math.max(1, items.length));
  items.forEach((el, i) => {{
    const at = Math.max(0, t - 0.1 / SP) + i * step;
    tl.fromTo(el, {{ opacity: 0, y: 50 }}, {{ opacity: 1, y: 0, duration: 0.5 / SP, ease: "power3.out" }}, at);
    el.querySelectorAll(".ln").forEach((ln, j) => {{
      tl.fromTo(ln, {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.35 / SP, ease: "power2.out" }}, at + (0.15 + j * 0.3) / SP);
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
