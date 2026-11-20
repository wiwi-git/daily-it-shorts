"""Builds assets/narration.mp3, index.html and examples.txt from vo.json (run gen_vo.py first)."""
import json, re, subprocess, html, os, tempfile, shutil

# SPEED: tempo vs. the earlier episodes (TTS rate +12% → +34%); gaps and motion shrink by the same factor
SPEED = 1.2
LEAD, GAP, TAIL = round(0.3 / SPEED, 3), round(0.45 / SPEED, 3), 1.0
XF = round(0.15 / SPEED, 3)  # scene change this long before the next narration
# scenes built so far: each ticket adds its scene ids, and the last one removes this filter
READY = {"hook", "write"}
vo = [s for s in json.load(open("vo.json")) if s["id"] in READY]

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
      "for while do continue true false null this return extends super final abstract interface implements instanceof long "
      "try catch finally throw throws").split()
TOK = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//.*|\d+(?:\.\d+)?[LfF]?\b|@\w+|->|::|\w+|.')
def hl(line):
    out = []
    for m in TOK.finditer(line):
        x = m.group()
        if x in ("->", "::"):
            out.append(f'<span class="ar">{html.escape(x)}</span>')
        elif x[0] in "\"'":
            body = re.sub(r"(\\.)", r'<span class="es">\1</span>', html.escape(x, quote=False))
            out.append(f'<span class="st">{body}</span>')
        elif x.startswith("//"):
            out.append(f'<span class="cm">{html.escape(x)}</span>')
        elif x[0].isdigit():
            out.append(f'<span class="nu">{x}</span>')
        elif x == "throws":  # the one letter that tells it from throw
            out.append('<span class="kw">throw<span class="s">s</span></span>')
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
# Each program runs with its own temp folder as the working directory, so `new FileWriter("scores.txt")`
# writes there (never into the repo, never shared between examples). After the run that folder's
# scores.txt is read into LAST["file"] (None if the program made none); `file=` on the helpers is the
# exact content the script expects there, and fterm() draws what is really in it. A scene that needs
# an earlier scene's file runs that scene's code first as invisible `pre=` in the same program.
TMP = tempfile.mkdtemp(prefix="java-shorts-")
EXAMPLES, LAST = [], {"out": "", "rt": "", "file": None}
FILE = "scores.txt"
IMPORTS = ["import java.io.*;", "import java.nio.file.*;", "import java.util.*;", ""]
HELLO = ["public class Main {",
         "  public static void main(String[] args) {",
         '    System.out.println("Hello World");',
         "  }",
         "}"]
# File code must handle IOException (a checked exception), so by default main declares it; the scenes
# say so on screen. Set MAIN_THROWS = "" around an example that must show what happens without it.
MAIN_THROWS = "IOException"

def wrap(lines, top=(), members=()):
    """Statements shown alone run inside main of a Main.java; `top` (e.g. a class) goes above class Main,
    `members` (e.g. a static method) inside class Main, above main (`main ... throws MAIN_THROWS`)."""
    main = HELLO[1].replace(") {", f") throws {MAIN_THROWS} {{") if MAIN_THROWS else HELLO[1]
    return "\n".join(IMPORTS + list(top) + ([""] if top else []) + HELLO[:1] + ["  " + l for l in members]
                     + ([""] if members else []) + [main] + ["    " + l for l in lines] + HELLO[3:] + [""])

def shown(lines, top, members, show_top, show_members):
    """What a code block draws: the shown declarations (`top`, then `members`) above the statements."""
    return (list(top) if show_top else []) + (list(members) if show_members else []) + list(lines)

def jok(sid, lines, top=(), pre=(), members=(), file=None):
    """Snippet that has to compile (and run without output or error); nothing is drawn."""
    check(sid, wrap(list(pre) + list(lines), top, members), "", label="컴파일 확인 (출력 없음)", file=file)

def run(src, fname="Main.java"):
    """(stdout, javac's first error or None, first line of the runtime error or None); the program
    runs inside its own temp folder, and that folder's scores.txt ends up in LAST["file"]."""
    d = tempfile.mkdtemp(dir=TMP)
    open(os.path.join(d, fname), "w").write(src)
    LAST["file"] = None
    c = subprocess.run(["javac", "-g", "-J-Duser.language=en", "-encoding", "UTF-8", fname], cwd=d, capture_output=True, text=True)
    if c.returncode:
        LAST["ce2"] = [l.strip() for l in c.stderr.split("\n")[1:]]
        return None, re.search(r"error: (.*)", c.stderr).group(1), None
    r = subprocess.run(["java", "-Duser.language=en", "-Dfile.encoding=UTF-8", "-cp", ".", "Main"], cwd=d,
                       capture_output=True, text=True)
    p = os.path.join(d, FILE)
    if os.path.exists(p):
        LAST["file"] = open(p, encoding="utf-8").read()
    return r.stdout, None, (r.stderr.split("\n")[0] if r.returncode else None)

def check(sid, src, expect=None, runtime=None, fname="Main.java", label=None, file=None):
    """Runs `src`; stops the build unless it prints `expect` (or stops with `runtime`) and, when `file`
    is given, leaves exactly that text in scores.txt."""
    out, ce, rt = run(src, fname)
    if ce is not None:
        raise ValueError(f"{sid}: does not compile: {ce}")
    if runtime is not None:
        if rt is None or runtime not in rt:
            raise ValueError(f"{sid}: expected runtime error {runtime!r}, got {rt!r} / output {out!r}")
    elif out != expect or rt:
        raise ValueError(f"{sid}: prints {out!r}, but the script expects {expect!r} ({rt or 'no error'})")
    if file is not None and LAST["file"] != file:
        raise ValueError(f"{sid}: leaves {FILE} = {LAST['file']!r}, but the script expects {file!r}")
    EXAMPLES.append((sid, fname, src, out, rt or label, LAST["file"]))
    return out, rt

def jcode(sid, lines, expect, mark=(), hidden=(), pre=(), sm=False, top=(), members=(),
          show_top=False, show_members=False, file=None):
    """Code block; the statements (between invisible `pre` setup and `hidden` prints, run inside main)
    must print `expect` and, with `file`, leave that exact text in scores.txt. `show_top`/`show_members`
    draw those declarations above the statements (marks count from the first drawn line)."""
    LAST["out"], _ = check(sid, wrap(list(pre) + list(lines) + list(hidden), top, members), expect, file=file)
    return code(shown(lines, top, members, show_top, show_members), mark, sm)

SHOW = re.compile(r"^// (\w+) → (.*)$")
def jshow(sid, lines, mark=(), pre=(), sm=False, top=(), members=(), file=None):
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
    LAST["out"], _ = check(sid, wrap(list(pre) + run_, top, members), "".join(w + "\n" for w in want), file=file)
    return code(lines, mark, sm)

def jrt(sid, lines, runtime, before="", mark=(), pre=(), sm=False, top=(), members=(), file=None):
    """Code block that compiles, prints `before`, then stops at run time with an error containing `runtime`."""
    LAST["out"], LAST["rt"] = check(sid, wrap(list(pre) + list(lines), top, members), runtime=runtime, file=file)
    if LAST["out"] != before:
        raise ValueError(f"{sid}: prints {LAST['out']!r} before the error, but the script expects {before!r}")
    return code(lines, mark, sm)

def term(cmds=(), label="실행 결과", out=None, cls="term in"):
    """Console box: optional shell commands, then what the last jcode() printed (or `out`)."""
    out = LAST["out"] if out is None else out
    body = "".join(f'<div class="cmd">$ {html.escape(c)}</div>' for c in cmds)
    if out:
        body += "".join(f"<div>{html.escape(l) or '&nbsp;'}</div>" for l in out.rstrip("\n").split("\n"))
    else:
        body += '<div class="z">(출력 없음)</div>'
    return f'<div class="{cls}"><i>{label}</i>{body}</div>'

def fterm(label=FILE, cls="term file in"):
    """File box: what the last run really left in scores.txt, each line in its person's colour."""
    if LAST["file"] is None:
        raise ValueError(f"fterm: the last example made no {FILE}")
    lines = LAST["file"].split("\n")
    if lines[-1] == "":
        lines.pop()
    body = "".join(f'<div class="{K.get(l.split(",")[0], "")}">{html.escape(l) or "&nbsp;"}</div>' for l in lines)
    body = body or '<div class="z">(빈 파일)</div>'
    return f'<div class="{cls}"><i>📄 {html.escape(label)}</i>{body}</div>'

def rterm():
    """The last jrt() block's runtime error: exception name on its own line, then the message."""
    msg = LAST["rt"].replace('Exception in thread "main" ', "").replace("Exception: ", "Exception:\n")
    return '<div class="term err in"><i>실행 오류</i>' + "".join(f"<div>{html.escape(l)}</div>" for l in msg.split("\n")) + "</div>"

def jce(sid, lines, error, detail="", mark=(), pre=(), sm=False, top=(), show_top=False, members=(),
        show_members=False):
    """Code block that must NOT compile: javac's first error has to contain `error`, and, if given,
    one of the lines under it (the caret's explanation) has to contain `detail`. With `show_top`
    the `top` declarations are drawn above the statements, with `show_members` the `members` (marks
    count from the first drawn line)."""
    src = wrap(list(pre) + list(lines), top, members)
    out, ce, rt = run(src)
    if ce is None or error not in ce:
        raise ValueError(f"{sid}: expected compile error {error!r}, got {ce!r} / output {out!r}")
    if detail and not any(detail in l for l in LAST["ce2"]):
        raise ValueError(f"{sid}: expected error detail {detail!r}, got {LAST['ce2']!r}")
    LAST["ce"], LAST["cd"] = ce, detail
    EXAMPLES.append((sid, "Main.java", src, "", f"컴파일 오류: {ce}" + (f" / {detail}" if detail else ""), None))
    return code(shown(lines, top, members, show_top, show_members), mark, sm)

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
.code .ar, code.ar { color: var(--orange); font-weight: 800; }
.code.hero { font-size: 84px; align-self: flex-start; padding: 30px 50px; }
.res span.out { color: #5b6782; text-decoration: line-through; box-shadow: inset 0 0 0 3px var(--red); }
.parts { display: flex; gap: 18px; align-items: flex-start; }
.parts div { display: flex; flex-direction: column; align-items: center; gap: 10px; }
.parts code { font-size: 44px; font-weight: 800; background: var(--panel); padding: 22px 22px; border-radius: 18px; white-space: pre; }
.parts small { font-size: 34px; font-weight: 700; color: var(--mute); }
.warn small, .note small { white-space: pre-wrap; }
"""

EXEC = ["BufferedWriter 로 쓰기 · newLine()", "try-with-resources 자동 닫기", "true 이어쓰기 · 없으면 덮어쓰기",
        "readLine() 끝이면 null", "IOException 처리 필수", "짧게: Files"]
EXEC_SAID = ["버퍼드", "트라이", "트루를", "리드", "파일", "짧게"]
EXEC_END = "구독과"

# --- example data: scores.txt, one `이름,점수` per line: 민수,85 (k1) · 서준,92 (k2) · 지우,78 (k3); wrong name score.txt ---
BRAND = "자바 입문 <em>파일</em> 읽기·쓰기 정리"
K = {"민수": "k1", "서준": "k2", "지우": "k3", "85": "k1", "92": "k2", "78": "k3"}

def open_writer(*args):
    """try-with-resources header opening scores.txt for writing; `args` are extra FileWriter arguments."""
    return ["try (BufferedWriter w =", "  new BufferedWriter(", "    new FileWriter(",
            '      "scores.txt"' + "".join(f", {a}" for a in args) + "))) {"]

def put(*rows):
    """write + newLine per row, inside the try block."""
    return [l for r in rows for l in (f'  w.write("{r}");', "  w.newLine();")]

WRITE = open_writer() + put("민수,85", "서준,92") + ["}"]  # STEP 1; append/read/sum reuse it as `pre=`

def hook_scene():
    return ('<div class="hook">'
            '<div class="pill in">JAVA 입문 · 스물한 번째</div>'
            '<h1 class="big in"><em>파일</em></h1>'
            '<p class="sub in">텍스트 파일 <b>읽기·쓰기</b></p>'
            '<div class="vs in">'
            '<div class="card"><b>List</b><span class="ng">프로그램 끝<br/>→ 사라짐</span></div>'
            '<div class="card on"><b>scores.txt</b><span class="ok">프로그램 끝<br/>→ 남음</span></div></div>'
            "</div>")

def write_scene():
    return (head("STEP 1 · 쓰기", "파일에 쓰기", "<b>FileWriter</b>로 열고 <b>BufferedWriter</b>로 감싸기")
            + lab("<small>main 에 <code>throws IOException</code> · 이유는 STEP 4</small>")
            + jcode("write", WRITE, "", mark=(0, 4, 5), sm=True, file="민수,85\n서준,92\n")
            + '<div class="duo in">' + fterm(cls="term file")
            + '<div class="stack"><div class="note"><b>try-with-resources</b><br/><small>블록 끝 → 자동으로 닫힘</small></div>'
            '<div class="note">이름만 쓰면<br/><small>→ 실행한 폴더에 생김</small></div></div></div>')

scenes = {
 "hook": hook_scene(),
 "write": write_scene(),
 "outro": '<div class="pill in">정리</div><h2 class="title in">파일 읽기·쓰기</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"write": 1, "append": 1, "read": 2, "sum": 3, "except": 4, "files": 5}

CSS_EXTRA += """
.tlabel small { font-size: 30px; }
.hook { gap: 44px; }
.hook .vs .card span { font-family: var(--font); font-size: 40px; line-height: 1.3; }
.chips code { color: var(--blue); }
.note code { font-size: 40px; }
.pill em, .title em { font-style: normal; color: var(--orange); }
.term i code { font-size: 28px; }
.term.file { border-color: rgba(63,167,214,.5); }
.duo { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
.duo .term { font-size: 40px; }
.note b { color: var(--orange); }
.stack { display: flex; flex-direction: column; gap: 22px; }
.stack .note { font-size: 36px; padding: 20px 28px; }
.stack .note small { font-size: 32px; font-family: var(--font); }
"""

JDK = subprocess.run(["java", "-version"], capture_output=True, text=True).stderr.split("\n")[0]
SECTION = {s["id"]: s["section"] for s in json.load(open("script.json"))}
with open("examples.txt", "w") as f:
    f.write("// 영상에 나오는 예제 프로그램 (build.py가 생성 · 직접 고치지 말 것)\n"
            "// 각 예제를 빈 폴더에 파일 이름대로 저장한 뒤: javac -g -encoding UTF-8 Main.java && java Main\n"
            "// (scores.txt는 실행한 폴더에 생긴다. 앞 장면의 파일 상태는 각 예제 안에서 먼저 만든다)\n"
            "// 확인한 JDK: " + JDK + "\n")
    for sid, fname, src, out, rt, fc in EXAMPLES:
        res = (rt if rt.startswith("컴파일") else f"실행 오류: {rt}") if rt else "출력 없음 (컴파일·실행 성공)" if not out else "출력:\n" + "".join(f"//   {l}\n" for l in out.rstrip("\n").split("\n"))
        if fc is not None:
            res = res.rstrip() + f"\n// 실행 뒤 {FILE}:\n" + "".join(f"//   {l}\n" for l in fc.rstrip("\n").split("\n"))
        f.write(f"\n// [{SECTION[sid]}] {fname} → {res.rstrip()}\n{src}\n")
shutil.rmtree(TMP)
for d in (".", ".."):  # every example ran in its own temp folder: none may have written into the repo
    if os.path.exists(os.path.join(d, FILE)):
        raise ValueError(f"{os.path.abspath(os.path.join(d, FILE))} exists: an example wrote outside its temp folder")



def bad_cut(x, i):
    """True if a caption break at space `i` would split an amount or orphan a dependent word."""
    prev, nxt = x[:i].split()[-1], x[i + 1:].split()[0]
    return bool(re.search(r"\d[천만백]?$|^[A-Z]+$|^(한|그)$", prev)) or nxt.startswith(("원", "이상", "이하", "미만", "않", "있어도", "중", "오류", "줄"))

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

# outro: light up each summary line as the narration names it
if "outro" in S:  # READY filter: the outro is built in a later ticket
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
.row b {{ font-family: var(--mono); color: var(--blue); white-space: pre-line; }}
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
