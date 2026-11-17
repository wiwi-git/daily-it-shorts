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
      "for while do continue true false null this return extends super final abstract interface implements instanceof package import private protected").split()
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
# Every example is a set of files laid out in their package folders (school/…, app/…), compiled
# together and run as app.Main. Each must print what the narration says (`expect`) or fail to
# compile with the error it names (`error=`, and `detail=` for javac's explanation line under the
# caret); the console boxes and the access table are drawn from what actually happened, and all
# of it is saved to examples.txt.
TMP = tempfile.mkdtemp(prefix="java-shorts-")
EXAMPLES, LAST = [], {"out": "", "ce": "", "detail": ""}

def person(extra=()):
    return "\n".join(["package school;", "", "public abstract class Person {",
                      "  public String name;", "  protected int age;", "  String phone;", "  private String password;",
                      "  public Person(String name, int age,", "      String phone, String password) {",
                      "    this.name = name;", "    this.age = age;", "    this.phone = phone;",
                      "    this.password = password;", "  }",
                      "  public boolean check(String p) {", "    return password.equals(p);", "  }",
                      "  public abstract void hello();", *extra, "}", ""])

def student(extra=()):
    return "\n".join(["package school;", "", "public class Student extends Person {",
                      "  private int score;", "  public Student(String name, int score) {",
                      '    super(name, 17, "010-1234", "1234");', "    this.score = score;", "  }",
                      "  public int getScore() { return score; }",
                      "  public void setScore(int v) {", "    if (v >= 0 && v <= 100)", "      score = v;", "  }",
                      "  public void printPhone() {", "    System.out.println(phone);", "  }",
                      "  @Override", "  public void hello() {", '    System.out.println("학생 " + name + " 안녕");', "  }",
                      *extra, "}", ""])

def teacher(hello_pub=True, extra=()):
    return "\n".join(["package school;", "", "public class Teacher extends Person {",
                      "  public Teacher(String name) {", '    super(name, 40, "010-0000", "0000");', "  }",
                      "  @Override", ("  public " if hello_pub else "  ") + "void hello() {",
                      '    System.out.println(name + " 선생님 안녕");', "  }", *extra, "}", ""])

def tutor(extra=()):
    return "\n".join(["package app;", "", "import school.Person;", "", "public class Tutor extends Person {",
                      "  public Tutor(String name) {", '    super(name, 20, "010-5678", "5678");', "  }",
                      "  @Override", "  public void hello() {",
                      '    System.out.println("튜터 " + name + " " + age + "살");', "  }", *extra, "}", ""])

BASE = {"school/Person.java": person(), "school/Student.java": student(), "school/Teacher.java": teacher(),
        "app/Tutor.java": tutor()}
S_PRE = 'Student s = new Student("민수", 85);'

def main_src(stmts, imports=("import school.Student;",), pre=(S_PRE,)):
    """app/Main.java: `imports`, then `pre` + `stmts` inside main."""
    return "\n".join(["package app;", ""] + list(imports) + ([""] if imports else [])
                     + ["public class Main {", "  public static void main(String[] args) {"]
                     + ["    " + l for l in [*pre, *stmts]] + ["  }", "}", ""])

def run_files(files):
    """Write the files in their package folders, compile them all, run app.Main.
    (stdout, javac's first error or None, that error's whole message block, runtime error or None)."""
    d = tempfile.mkdtemp(dir=TMP)
    for path, src in files.items():
        os.makedirs(os.path.join(d, os.path.dirname(path)), exist_ok=True)
        open(os.path.join(d, path), "w").write(src)
    c = subprocess.run(["javac", "-J-Duser.language=en", "-encoding", "UTF-8", "-d", "out", *sorted(files)],
                       cwd=d, capture_output=True, text=True)
    if c.returncode:
        block = re.split(r"\n(?=\S+\.java:\d+: )|\n\d+ errors?\n", c.stderr)[0]
        return None, re.search(r"error: (.*)", block).group(1), block, None
    r = subprocess.run(["java", "-Duser.language=en", "-cp", os.path.join(d, "out"), "app.Main"],
                       capture_output=True, text=True)
    return r.stdout, None, None, (r.stderr.split("\n")[0] if r.returncode else None)

def pcheck(sid, main=None, expect=None, error=None, detail=None, changed=None, label=None, record=True):
    """Run BASE + `changed` files + app/Main.java (`main`, default: just the hidden `s`). With
    `error`, javac's first error must contain it (and its message block `detail`); otherwise the
    program must print exactly `expect`."""
    changed = dict(changed or {})
    changed["app/Main.java"] = main or main_src([])
    out, ce, block, rt = run_files({**BASE, **changed})
    if error is not None:
        if ce is None or error not in ce or (detail and detail not in block):
            raise ValueError(f"{sid}: expected compile error {error!r} / {detail!r}, got {block!r} / output {out!r}")
        LAST["ce"], LAST["detail"] = ce, (detail and next(l.strip() for l in block.split("\n") if detail in l))
        if record:
            EXAMPLES.append((sid, changed, f"컴파일 오류: {ce}" + (f"\n//   {LAST['detail']}" if detail else "")))
        return ""
    if ce is not None:
        raise ValueError(f"{sid}: does not compile: {ce}")
    if out != expect or rt:
        raise ValueError(f"{sid}: prints {out!r}, but the script expects {expect!r} ({rt or 'no error'})")
    LAST["out"] = out
    if record:
        EXAMPLES.append((sid, changed, label or ("출력:\n" + "".join(f"//   {l}\n" for l in out.rstrip("\n").split("\n"))
                                                  if out else "출력 없음 (컴파일·실행 성공)")))
    return ""

def mrun(sid, stmts, expect=None, error=None, **kw):
    """Run statements in app.Main after the hidden `Student s = new Student("민수", 85);`."""
    return pcheck(sid, main_src(stmts), expect, error, **kw)

def pcode(sid, shown, expect=None, error=None, mark=(), sm=True, **kw):
    """Code block of statements in app.Main, compiled and run exactly as shown (after the hidden `s`)."""
    mrun(sid, shown, expect, error, **kw)
    return code(shown, mark, sm)

def term(label="실행 결과", out=None, k=""):
    out = LAST["out"] if out is None else out
    return f'<div class="term in"><i>{label}</i>' + "".join(f'<div class="{k}">{html.escape(l)}</div>' for l in out.rstrip("\n").split("\n")) + "</div>"

def cterm():
    """The last pcheck() compile error (and its explanation line, if one was checked)."""
    d = f'<div class="dt">{html.escape(LAST["detail"])}</div>' if LAST["detail"] else ""
    return f'<div class="term err in"><i>컴파일 오류</i><div>{html.escape(LAST["ce"])}</div>{d}</div>'

def flab(path, note=""):
    """File name label above a code block."""
    return f'<div class="flab in">📄 {path}{f" <small>{note}</small>" if note else ""}</div>'

# --- the access table: each modifier's field, touched from four places, compiled for real ---
MODS = [("public", "name"), ("protected", "age"), ("기본", "phone"), ("private", "password")]
PLACES = ["같은<br/>클래스", "같은<br/>패키지", "다른 패키지<br/>자식", "다른<br/>패키지"]
EXPECT_ACCESS = {"public": [1, 1, 1, 1], "protected": [1, 1, 1, 0], "기본": [1, 1, 0, 0], "private": [1, 0, 0, 0]}

def probe(field, place):
    """Does `field` compile when used from `place` (0 Person itself, 1 a non-child class in school,
    2 app.Tutor (child, other package), 3 app.Main (other package)?"""
    use = f"Object x = {'this' if place in (0, 2) else 's'}.{field};"
    changed = [{"school/Person.java": person([f"  void probe() {{ {use} }}"])},
               {"school/Desk.java": f"package school;\n\nclass Desk {{\n  void probe(Student s) {{ {use} }}\n}}\n"},
               {"app/Tutor.java": tutor([f"  void probe() {{ {use} }}"])},
               {"app/Main.java": main_src([use])}][place]
    out, ce, _, _ = run_files({**BASE, "app/Main.java": main_src([]), **changed})
    return ce is None

ACCESS = {m: [probe(f, p) for p in range(4)] for m, f in MODS}
for m, _ in MODS:
    if [int(x) for x in ACCESS[m]] != EXPECT_ACCESS[m]:
        raise ValueError(f"access table: {m} compiles as {ACCESS[m]}, the script says {EXPECT_ACCESS[m]}")
EXAMPLES.append(("table", {}, "접근 표 (필드를 같은 클래스 · school의 다른 클래스 · app.Tutor · app.Main 에서 사용, 실제 컴파일):\n"
                 + "".join(f"//   {m:9} {' '.join('O' if x else 'X' for x in ACCESS[m])}\n" for m, _ in MODS)))

def scope(mod):
    """The four places as chips, from the compiled access table."""
    return '<div class="scope in">' + "".join(
        f'<div class="{"ok" if x else "ng"}"><small>{p}</small><b>{"✅" if x else "❌"}</b></div>'
        for p, x in zip(PLACES, ACCESS[mod])) + "</div>"

def acc_table():
    head_ = '<div class="h"></div>' + "".join(f'<div class="h">{p}</div>' for p in PLACES)
    rows = "".join(f'<div class="m">{m}</div>' + "".join(f'<div class="{"ok" if x else "ng"}">{"✅" if x else "❌"}</div>'
                                                          for x in ACCESS[m]) for m, _ in MODS)
    return f'<div class="acc in">{head_}{rows}</div>'

BRAND = "자바 입문 <em>접근 제어자</em> 정리"

CSS_EXTRA = """
.flab { font-family: var(--mono); font-size: 30px; font-weight: 700; color: var(--mute); margin-bottom: -14px; }
.flab small { font-family: var(--font); font-size: 28px; color: #6f7d98; margin-left: 10px; }
.term .k2 { color: var(--green); } .term .k3 { color: var(--violet); } .term .k4 { color: var(--blue); }
.term.err .dt { color: #ffb0b0; font-size: 30px; margin-top: 6px; }
.scene { gap: 20px; }
.scope { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.scope div { background: var(--panel); border-radius: 18px; padding: 10px 6px 12px; display: flex; flex-direction: column; align-items: center; gap: 2px; }
.scope small { font-size: 28px; font-weight: 700; color: var(--mute); text-align: center; line-height: 1.2; }
.scope b { font-size: 40px; }
.scope .ok { box-shadow: inset 0 0 0 3px rgba(126,224,138,.5); } .scope .ng { opacity: .6; }
.acc { display: grid; grid-template-columns: 1.35fr repeat(4, 1fr); gap: 10px; }
.acc div { background: var(--panel); border-radius: 16px; display: flex; align-items: center; justify-content: center; height: 118px; font-size: 52px; }
.acc .h { background: #1a2640; color: var(--blue); font-size: 29px; font-weight: 700; text-align: center; line-height: 1.2; height: 104px; }
.acc .h:first-child { background: none; }
.acc .m { font-family: var(--mono); font-size: 40px; font-weight: 800; color: var(--orange); justify-content: flex-start; padding-left: 22px; }
.acc .ng { opacity: .55; }
.hook .chips span { font-family: var(--mono); font-size: 44px; }
.hook .chips span.kr { font-family: var(--font); }
.row b { font-size: 44px; }
"""

EXEC = ["private → 같은 클래스만", "기본 → 같은 패키지까지", "protected → +다른 패키지 자식", "public → 어디서나",
        "필드는 private + getter·setter", "오버라이딩: 범위 좁히기 ❌"]
EXEC_SAID = ["프라이빗은", "기본", "프로텍티드는", "퍼블릭은", "필드는", "오버라이딩은"]
EXEC_END = "구독과"

scenes = {
 "hook": '''<div class="hook">
   <div class="pill in">JAVA 입문 · 열여섯 번째</div>
   <h1 class="big in"><em>접근<br/>제어자</em></h1>
   <div class="chips in"><span>public</span><span>protected</span><span class="kr">기본</span><span>private</span></div>
 </div>''',
 "priv": head("STEP 1 · private", "private", "<b>같은 클래스</b> 안에서만")
    + flab("school/Person.java")
    + code(["private String password;", "public boolean check(String p) {", "  return password.equals(p);", "}"], mark=(0, 2), sm=True)
    + mrun("priv", ['System.out.println(s.check("1234"));'], "true\n")
    + term('s.check("1234")  · s = 민수')
    + flab("school/Student.java", "자식 클래스")
    + code(["System.out.println(password);"], sm=True)
    + pcheck("priv", error="password has private access in Person",
             changed={"school/Student.java": student(["  public void leak() {", "    System.out.println(password);", "  }"])})
    + cterm()
    + scope("private"),
 "dflt": head("STEP 2 · 기본 접근", "아무것도 안 붙이면", "(아무것도 안 붙임 = <b>같은 패키지</b> 전용)")
    + flab("school/Person.java")
    + code(["String phone;"], mark=(0,), sm=True)
    + flab("school/Student.java", "같은 패키지")
    + code(["System.out.println(phone);"], sm=True)
    + mrun("dflt", ["s.printPhone();"], "010-1234\n")
    + term("s.printPhone()")
    + flab("app/Main.java", "다른 패키지")
    + pcode("dflt", ["System.out.println(s.phone);"], error="phone is not public in Person; cannot be accessed from outside package")
    + cterm()
    + scope("기본"),
 "prot": head("STEP 3 · protected", "protected", "같은 패키지 + <b>다른 패키지의 자식</b>")
    + flab("school/Person.java")
    + code(["protected int age;"], mark=(0,), sm=True)
    + flab("app/Tutor.java", "다른 패키지의 자식")
    + code(["class Tutor extends Person {", '  ... + age + "살");'], mark=(1,), sm=True)
    + mrun("prot", ['new Tutor("지우").hello();'], "튜터 지우 20살\n")
    + term('new Tutor("지우").hello()', k="k4")
    + flab("app/Main.java", "다른 패키지 · 자식 아님")
    + pcode("prot", ["System.out.println(s.age);"], error="age has protected access in Person")
    + cterm()
    + scope("protected"),
 "pub": head("STEP 4 · public", "public", "<b>어디서나</b> 쓸 수 있다")
    + flab("school/Person.java")
    + code(["public String name;"], mark=(0,), sm=True)
    + flab("app/Main.java", "다른 패키지")
    + pcode("pub", ["System.out.println(s.name);"], "민수\n")
    + term(k="k2")
    + '<div class="note in">지난 편: 다른 패키지에서 쓰려고<br/>클래스 · 생성자 · 메소드에 붙인 <b>public</b></div>'
    + scope("public"),
 "table": head("STEP 4-1 · 한눈에", "네 단계 정리", "아래로 갈수록 <b>좁아진다</b>")
    + acc_table()
    + '<div class="note in">기본 = 아무것도 안 붙임</div>',
 "cls": head("STEP 4-2 · 클래스", "클래스에는 둘만", "파일에 바로 쓰는 클래스: <b>public · 기본</b>")
    + pcheck("cls", label="컴파일 성공 확인 (public class Student · class Desk)",
             changed={"school/Desk.java": "package school;\n\nclass Desk {\n}\n"}, expect="")
    + code(["public class Student { }", "class Desk { }", "private class Club { }"], mark=(2,))
    + pcheck("cls", error="modifier private not allowed here",
             changed={"school/Club.java": "package school;\n\nprivate class Club {\n}\n"})
    + cterm()
    + '<div class="res in"><i>결과</i><span class="k2">public ✅</span><span class="k2">기본 ✅</span><span class="bad">private ❌</span></div>',
 "enc": head("STEP 5 · 캡슐화", "왜 private 으로 숨길까?", "잘못된 값을 <b>막는다</b>")
    + flab("school/Student.java")
    + code(["private int score;", "public int getScore() { ... }", "public void setScore(int v) {",
            "  if (v >= 0 && v <= 100)", "    score = v;", "}"], mark=(0, 3), sm=True)
    + mrun("enc", ["s.setScore(-5);", "System.out.println(s.getScore());"], "85\n")
    + term("s.setScore(-5) → s.getScore()", k="k2")
    + flab("app/Main.java")
    + pcode("enc", ["s.score = -5;"], error="score has private access in Student")
    + cterm()
    + '<div class="note in"><b>캡슐화</b> = private + getter · setter</div>',
 "ovr": head("STEP 5-1 · 오버라이딩", "범위를 좁힐 수 없다", "public → 기본 <b>오류</b> · 넓히기는 OK")
    + flab("school/Teacher.java")
    + code(["public class Teacher", "    extends Person {", "  @Override", "  void hello() { ... }", "}"], mark=(3,), sm=True)
    + pcheck("ovr", error="hello() in Teacher cannot override hello() in Person",
             detail="attempting to assign weaker access privileges; was public",
             changed={"school/Teacher.java": teacher(hello_pub=False)})
    + cterm()
    + pcheck("ovr", label="컴파일 성공 확인 (protected → public 으로 넓히기)", expect="",
             changed={"school/Person.java": person(["  protected void rest() { }"]),
                      "school/Teacher.java": teacher(extra=["  @Override", "  public void rest() { }"])})
    + '<div class="res in"><i>좁히기</i><span class="bad">public → 기본 ❌</span></div><div class="res in"><i>넓히기</i><span class="k2">protected → public ✅</span></div>'
    + '<div class="note in">그래서 인터페이스 메소드를 구현할 때<br/><b>public</b> 이 필수였다 <small>(13편)</small></div>',
 "outro": '<div class="pill in">정리</div><h2 class="title in">접근 제어자 6가지</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"priv": 1, "dflt": 2, "prot": 3, "pub": 4, "table": 4, "cls": 4, "enc": 5, "ovr": 5}


SECTION = {s["id"]: s["section"] for s in json.load(open("script.json"))}
with open("examples.txt", "w") as f:
    f.write("// 영상에 나오는 예제 프로그램 (build.py가 생성 · 직접 고치지 말 것)\n"
            "// 기본 파일(school 패키지 3개 + app/Tutor.java)을 폴더대로 저장하고, 예제마다 바뀐 파일을 덮어쓴 뒤:\n"
            "// javac -encoding UTF-8 -d out school/*.java app/*.java && java -cp out app.Main\n")
    f.write("\n// ===== 기본 파일 =====\n")
    for path, src in BASE.items():
        f.write(f"\n// --- {path}\n{src}")
    for sid, changed, res in EXAMPLES:
        f.write(f"\n// ===== [{SECTION[sid]}] → {res.rstrip()}\n")
        for path, src in changed.items():
            f.write(f"\n// --- {path}\n{src}")



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
