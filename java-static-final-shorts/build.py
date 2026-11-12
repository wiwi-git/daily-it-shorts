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
      "for while do continue true false null this return extends super final").split()
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
# Each must print what the narration says (`expect`) or stop with the runtime error it names
# (`runtime=`); the console boxes are drawn from what actually happened, and all of them are
# saved to examples.txt.
TMP = tempfile.mkdtemp(prefix="java-shorts-")
EXAMPLES, LAST = [], {"out": "", "rt": ""}
HELLO = ["public class Main {",
         "  public static void main(String[] args) {",
         '    System.out.println("Hello World");',
         "  }",
         "}"]

def wrap(lines, cls=None):
    """Statements shown alone run inside main of the program above; class Student sits below it
    in the same Main.java."""
    return "\n".join(HELLO[:2] + ["    " + l for l in lines] + HELLO[3:] + [""] + (cls or STUDENT))

STUDENT = ["class Student {", "}"]

def run(src, fname="Main.java"):
    """(stdout, javac's first error or None, first line of the runtime error or None)."""
    d = tempfile.mkdtemp(dir=TMP)
    open(os.path.join(d, fname), "w").write(src)
    c = subprocess.run(["javac", "-J-Duser.language=en", "-encoding", "UTF-8", fname], cwd=d, capture_output=True, text=True)
    if c.returncode:
        return None, re.search(r"error: (.*)", c.stderr).group(1), None
    r = subprocess.run(["java", "-Duser.language=en", "-cp", d, "Main"], capture_output=True, text=True)
    return r.stdout, None, (r.stderr.split("\n")[0] if r.returncode else None)

def check(sid, src, expect=None, runtime=None, fname="Main.java"):
    out, ce, rt = run(src, fname)
    if ce is not None:
        raise ValueError(f"{sid}: does not compile: {ce}")
    if runtime is not None:
        if rt is None or runtime not in rt:
            raise ValueError(f"{sid}: expected runtime error {runtime!r}, got {rt!r} / output {out!r}")
    elif out != expect or rt:
        raise ValueError(f"{sid}: prints {out!r}, but the script expects {expect!r} ({rt or 'no error'})")
    EXAMPLES.append((sid, fname, src, out, rt))
    return out, rt

def comments(lines):
    """The `// value` written at the end of each shown line, in order."""
    return "".join(l.split("// ")[1].strip() + "\n" for l in lines if "// " in l)

def jcode(sid, lines, expect, mark=(), hidden=(), pre=(), sm=False, cls=None):
    """Code block; the statements (between invisible `pre` setup and `hidden` prints, run inside main)
    must print `expect`."""
    LAST["out"], _ = check(sid, wrap(list(pre) + list(lines) + list(hidden), cls), expect)
    return code(lines, mark, sm)

def jcmt(sid, lines, hidden, mark=(), pre=()):
    """Code block whose `// value` comments are the result: the `hidden` prints must print exactly them."""
    return jcode(sid, lines, comments(lines), mark, hidden, pre)

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
    """The last jrt() block's runtime error, broken before 'java.lang.' and after the exception name."""
    msg = LAST["rt"].replace(' java.lang.', '\njava.lang.').replace('Exception: ', 'Exception:\n')
    return '<div class="term err in"><i>실행 오류</i>' + "".join(f"<div>{html.escape(l)}</div>" for l in msg.split("\n")) + "</div>"

def jce(sid, lines, error, mark=(), pre=(), cls=None, sm=False):
    """Code block that must NOT compile: javac's first error has to contain `error`."""
    src = wrap(list(pre) + list(lines), cls)
    out, ce, rt = run(src)
    if ce is None or error not in ce:
        raise ValueError(f"{sid}: expected compile error {error!r}, got {ce!r} / output {out!r}")
    LAST["ce"] = ce
    EXAMPLES.append((sid, "Main.java", src, "", f"컴파일 오류: {ce}"))
    return code(lines, mark, sm)

def cterm():
    """The last jce() block's compile error."""
    return f'<div class="term err in"><i>컴파일 오류</i><div>{html.escape(LAST["ce"])}</div></div>'

def jcomp(sid, lines, why, mark=(), pre=()):
    """Code block that compiles but is not run (it would never stop): `why` says so in examples.txt."""
    src = wrap(list(pre) + list(lines))
    d = tempfile.mkdtemp(dir=TMP)
    open(os.path.join(d, "Main.java"), "w").write(src)
    c = subprocess.run(["javac", "-J-Duser.language=en", "-encoding", "UTF-8", "Main.java"], cwd=d, capture_output=True, text=True)
    if c.returncode:
        raise ValueError(f"{sid}: does not compile: {c.stderr}")
    EXAMPLES.append((sid, "Main.java", src, "", f"컴파일만 확인 (실행하지 않음: {why})"))
    return code(lines, mark)


def table(cols, rows, label):
    head_ = "".join(f"<th>{c}</th>" for c in cols)
    body = "".join(f'<tr class="{k}">' + "".join(f"<td>{html.escape(v)}</td>" for v in cells) + "</tr>" for k, cells in rows)
    return f'<div class="tbl in">{lab(label)}<table><tr>{head_}</tr>{body}</table></div>'

def cerr(sid, error, cls, main, shown, mark=()):
    """Code block (class code shown) whose full program must NOT compile: javac's first error contains `error`."""
    src = wrap(main, cls)
    out, ce, rt = run(src)
    if ce is None or error not in ce:
        raise ValueError(f"{sid}: expected compile error {error!r}, got {ce!r} / output {out!r}")
    LAST["ce"] = ce
    EXAMPLES.append((sid, "Main.java", src, "", f"컴파일 오류: {ce}"))
    return code(shown, mark, True)

def ok(sid, main, cls, expect=""):
    """Checked program, nothing drawn."""
    LAST["out"], _ = check(sid, wrap(main, cls), expect)
    return ""

def C(*blocks):
    out = []
    for b in blocks:
        out += ([""] if out else []) + list(b)
    return out

def kc(lines, k, mark=()):
    """Class code block in the class's colour (Person k1 · Student k2 · Teacher k3)."""
    return code(lines, mark, True).replace('class="code in sm"', f'class="code in sm {k}"')

# --- example data: Student 민수 85 · 지영 92 (k2) ---
BRAND = "자바 입문 <em>static·final</em> 정리"
STUDENT_CLS = ["class Student {", "  String name;", "  int score;", "  static int count;",
               "  Student(String name,", "          int score) {", "    this.name = name;",
               "    this.score = score;", "    count++;", "  }", "}"]
STUDENT_CLS_F = [l.replace("  String name;", "  final String name;") for l in STUDENT_CLS]  # STEP 3부터: name은 final
FERR = "cannot assign a value to final variable"
GETCOUNT = ["static int getCount() {", "  return count;", "}"]
GETSCORE = ["static int getScore() {", "  return score;", "}"]
STUDENT_CLS2 = STUDENT_CLS[:-1] + ["  " + l for l in GETCOUNT] + ["}"]
STUDENT_CLS3 = STUDENT_CLS[:-1] + ["  " + l for l in GETSCORE] + ["}"]
S_NEW = ["Student s1 = new Student(", '    "민수", 85);', "Student s2 = new Student(", '    "지영", 92);']

# --- STEP 4~5: Person (k1) · Student (k2) ---
def cfail(sid, error, cls, main=()):
    """Checked program that must NOT compile (javac's first error contains `error`); nothing drawn, cterm() shows the error."""
    cerr(sid, error, cls, list(main), ["x"])
    return ""

HELLO_PRINT = ["    System.out.println(", '        "안녕하세요");']
P_FINAL = ["class Person {", "  String name;", "  final void hello() {"] + HELLO_PRINT + ["  }", "}"]
S_OVR = ["class Student extends Person {", "  void hello() {"] + HELLO_PRINT + ["  }", "}"]
P_FCLS = ["final class Person {", "  void hello() { }", "}"]
S_EXT = ["class Student extends Person {", "}"]
PASS_CLS = ["class Student {", "  static final int", "      PASS_SCORE = 60;", "  String name;", "  int score;",
            "  Student(String name,", "          int score) {", "    this.name = name;", "    this.score = score;", "  }",
            "  boolean isPass() {", "    return score >= PASS_SCORE;", "  }", "}"]
PASS_SHOW = ["class Student {", "  static final int", "      PASS_SCORE = 60;", "  int score;", "  boolean isPass() {",
             "    return score >= PASS_SCORE;", "  }", "}"]

CSS_EXTRA = """
.code.k1 { border-color: var(--orange); } .code.k2 { border-color: var(--green); } .code.k3 { border-color: var(--violet); }
.vs .card span.big2 { font-size: 52px; }
.vs .card small { font-size: 34px; color: var(--mute); font-weight: 700; }
.vs .card.k1 b, .vs .card.k2 b, .vs .card.k3 b { color: inherit; }
.vs .card.k2 b { color: var(--green); } .vs .card.k3 b { color: var(--violet); }
.vs .card span { font-size: 38px; }
.note small.t { font-family: var(--mono); }
"""

EXEC = ["static 필드 = 모든 객체가 함께 쓰는 하나", "static 메소드 = 객체 없이 클래스이름.메소드()", "static 메소드에서 인스턴스 필드 사용 불가", "final 변수·필드 = 한 번만 대입", "final 메소드 = 오버라이딩 금지 · final 클래스 = 상속 금지", "static final = 상수 (이름은 대문자)"]
EXEC_SAID = ["스태틱", "메소드는", "메소드에서는", "파이널", "메소드는", "스태틱"]
EXEC_END = "구독과"

scenes = {
 "hook": '''<div class="hook">
   <div class="pill in">JAVA 입문 · 열한 번째</div>
   <h1 class="big in"><em>static</em>과<br/><em>final</em></h1>
   <div class="sub in">static · final · <b>상수</b></div>
 </div>''',
 "sfield": head("STEP 1 · static 필드", "객체마다? 모두 함께?", "<b>static</b> 을 붙이면 클래스에 하나")
    + '<div class="vs in"><div class="card k2"><b>score</b><span>인스턴스 필드</span><small>(객체마다 따로)</small></div>'
      '<div class="card k2"><b>count</b><span>static 필드</span><small>클래스에 하나 · 모두 함께</small></div></div>'
    + ok("sfield", S_NEW, STUDENT_CLS)
    + kc(STUDENT_CLS, "k2", mark=(3, 8)),
 "sfrun": head("STEP 1 · 함께 쓰는 필드", "만들 때마다 count 증가", "객체가 아니라 <b>클래스 이름</b>으로 사용")
    + jcode("sfrun", S_NEW + ["System.out.println(", "    Student.count);"], "2\n", mark=(4, 5), cls=STUDENT_CLS)
    + term(label="실행 결과")
    + '<div class="note in"><b>Student.count</b> 처럼 클래스 이름으로</div>',
 "smethod": head("STEP 2 · static 메소드", "객체 없이 호출", "<b>static</b> 메소드는 클래스 이름으로 부른다")
    + code(GETCOUNT, mark=(0,))
    + jcode("smethod", ["System.out.println(", "    Student.getCount());"] + S_NEW
            + ["System.out.println(", "    Student.getCount());"], "0\n2\n", mark=(0, 1, 6, 7), cls=STUDENT_CLS2, sm=True)
    + term(label="실행 결과 (객체를 만들기 전 · 만든 후)"),
 "sme": head("STEP 2-1 · 주의", "static에서는 score 불가", "객체 없이 실행되니 <b>누구의 score?</b>")
    + cerr("sme", "non-static variable score cannot be referenced from a static context", STUDENT_CLS3, [], GETSCORE, mark=(1,))
    + cterm()
    + '<div class="note in"><b>main</b> 도 static이라<br/>객체를 만들어 점으로 사용</div>',

 "fvar": head("STEP 3 · final 변수", "한 번 넣으면 끝", "<b>final</b> 변수는 다시 대입할 수 없다")
    + jce("fvar", ["final int x = 10;", "x = 20;"], FERR, mark=(1,))
    + cterm()
    + '<div class="note in">값을 <b>한 번만</b> 넣을 수 있다</div>',
 "ffield": head("STEP 3 · final 필드", "생성자에서 한 번만", "<b>final</b> 필드는 한 번만 대입")
    + ok("ffield", S_NEW, STUDENT_CLS_F)
    + kc([l for l in STUDENT_CLS_F if "count" not in l], "k2", mark=(1, 5))
    + cerr("ffield", FERR, STUDENT_CLS_F, S_NEW + ['s1.name = "철수";'], ['s1.name = "철수";'], mark=(0,))
    + cterm()
    + '<div class="note in">이름은 <b>그대로</b> · 점수는 계속 변함</div>',
 "fref": head("STEP 3-1 · 주의", "final Student s", "<b>변수</b>를 막을 뿐, 객체는 막지 않는다")
    + jcode("fref", ["final Student s = new Student(", '    "민수", 85);', "s.score = 100;", "System.out.println(s.score);"], "100\n", mark=(2,), cls=STUDENT_CLS_F, sm=True)
    + term(label="실행 결과")
    + jce("fref", ["s = new Student(", '    "지영", 92);'], FERR, mark=(0,), pre=["final Student s = new Student(", '    "민수", 85);'], cls=STUDENT_CLS_F, sm=True)
    + cterm()
    + '<div class="warn in">final은 <b>변수</b>를 고정 · 객체 내용은 변경 가능</div>',
 "fmc": head("STEP 4 · final 메소드", "오버라이딩 금지", "<b>final</b> 메소드는 자식이 고칠 수 없다")
    + kc(["class Person {", "  final void hello() { … }", "}"], "k1", mark=(1,))
    + kc(["class Student extends Person {", "  void hello() { … }", "}"], "k2", mark=(1,))
    + cfail("fmc", "hello() in Student cannot override hello() in Person", C(P_FINAL, S_OVR))
    + cterm()
    + '<div class="note in"><b>부모 클래스</b>의 final 메소드는 <b>오버라이딩</b> 불가</div>',
 "fcls": head("STEP 4-1 · final 클래스", "상속 금지", "<b>final</b> 클래스는 상속할 수 없다")
    + kc(["final class Person { … }"], "k1", mark=(0,))
    + kc(S_EXT, "k2", mark=(0,))
    + cfail("fcls", "cannot inherit from final Person", C(P_FCLS, S_EXT))
    + cterm()
    + '<div class="note in">자바의 <b>String</b> 도 final 클래스<br/><small class="t">public final class String</small></div>',
 "const": head("STEP 5 · static final 상수", "60을 이름으로", "<b>static final</b> 로 상수를 만든다")
    + kc(PASS_SHOW, "k2", mark=(1, 2, 5))
    + ok("const", ["Student s = new Student(", '    "민수", 85);', "System.out.println(", "    s.isPass());"], PASS_CLS, "true\n")
    + term(label="민수(85) 의 isPass() 결과")
    + '<div class="note in">상수 이름은 <b>대문자와 _</b> 로 쓴다</div>',
 "cre": head("STEP 5-1 · 상수 재대입", "상수는 못 바꾼다", "<b>final</b> 이라 다시 대입하면 오류")
    + jce("cre", ["Student.PASS_SCORE = 70;"], "cannot assign a value to static final variable PASS_SCORE", mark=(0,), cls=PASS_CLS)
    + cterm()
    + '<div class="note in">기준 점수는 <b>한 곳</b>에서만 정한다</div>',
 "outro": '<div class="pill in">정리</div><h2 class="title in">static · final 6가지</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"sfield": 1, "sfrun": 1, "smethod": 2, "sme": 2, "fvar": 3, "ffield": 3, "fref": 3, "fmc": 4, "fcls": 4, "const": 5, "cre": 5}


SECTION = {s["id"]: s["section"] for s in json.load(open("script.json"))}
with open("examples.txt", "w") as f:
    f.write("// 영상에 나오는 예제 프로그램 (build.py가 생성 · 직접 고치지 말 것)\n"
            "// 각 예제를 파일 이름대로 저장한 뒤: javac -encoding UTF-8 Main.java && java Main\n")
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
after = S["outro"]["start"] if "outro" in S else 0
for i, token in enumerate(EXEC_SAID, 1):
    at = word_time("outro", token, after)
    after = at
    if i > 1:
        js.append(f'tl.to("#ex{i - 1}", {{backgroundColor: "#131c2e", scale: 1, duration: 0.2}}, {at});')
    js.append(f'tl.to("#ex{i}", {{backgroundColor: "#3a2a12", scale: 1.04, duration: 0.2}}, {at});')
if EXEC: js.append(f'tl.to("#ex{len(EXEC)}", {{backgroundColor: "#131c2e", scale: 1, duration: 0.3}}, {word_time("outro", EXEC_END)} + 0.6);')

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
