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
IMPORTS = ["import java.util.ArrayList;", "import java.util.List;", "import java.util.function.Predicate;", ""]
HELLO = ["public class Main {",
         "  public static void main(String[] args) {",
         '    System.out.println("Hello World");',
         "  }",
         "}"]

def wrap(lines, top=()):
    """Statements shown alone run inside main of a Main.java that imports ArrayList, List and
    Predicate; `top` (e.g. an interface) goes above class Main."""
    return "\n".join(IMPORTS + list(top) + ([""] if top else []) + HELLO[:2] + ["    " + l for l in lines] + HELLO[3:] + [""])

CHECKER = ["interface Checker {", "  boolean check(int s);", "}"]

def jok(sid, lines, top=CHECKER, pre=()):
    """Snippet that has to compile (and run without output or error); nothing is drawn."""
    check(sid, wrap(list(pre) + list(lines), top), "", label="컴파일 확인 (출력 없음)")

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

def jcode(sid, lines, expect, mark=(), hidden=(), pre=(), sm=False, top=()):
    """Code block; the statements (between invisible `pre` setup and `hidden` prints, run inside main)
    must print `expect`."""
    LAST["out"], _ = check(sid, wrap(list(pre) + list(lines) + list(hidden), top), expect)
    return code(lines, mark, sm)

SHOW = re.compile(r"^// (\w+) → (.*)$")
def jshow(sid, lines, mark=(), pre=(), sm=False, top=()):
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
    LAST["out"], _ = check(sid, wrap(list(pre) + run_, top), "".join(w + "\n" for w in want))
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

def jce(sid, lines, error, detail="", mark=(), pre=(), sm=False, top=(), show_top=False):
    """Code block that must NOT compile: javac's first error has to contain `error`, and, if given,
    one of the lines under it (the caret's explanation) has to contain `detail`. With `show_top`
    the `top` declarations are drawn above the statements (marks count from the first drawn line)."""
    src = wrap(list(pre) + list(lines), top)
    out, ce, rt = run(src)
    if ce is None or error not in ce:
        raise ValueError(f"{sid}: expected compile error {error!r}, got {ce!r} / output {out!r}")
    if detail and not any(detail in l for l in LAST["ce2"]):
        raise ValueError(f"{sid}: expected error detail {detail!r}, got {LAST['ce2']!r}")
    LAST["ce"], LAST["cd"] = ce, detail
    EXAMPLES.append((sid, "Main.java", src, "", f"컴파일 오류: {ce}" + (f" / {detail}" if detail else "")))
    return code((list(top) if show_top else []) + list(lines), mark, sm)

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

EXEC = ["(매개변수) -> 몸체", "타입·괄호·return 생략", "함수형 = 추상 메소드 1개", "Predicate · test()",
        "forEach · removeIf · sort", "지역 변수 다시 대입 ✗", ":: = 메소드 참조"]
EXEC_SAID = ["람다식은", "타입", "함수형", "프레디케이트는", "리스트는", "바깥", "마지막으로"]
EXEC_END = "구독과"

# --- example data: 민수 (k1) · 서준 (k2) · 지우 (k3); scores 85 (k1) · 92 (k2) · 78 (k3) ---
BRAND = "자바 입문 <em>람다식</em> 정리"
K = {"민수": "k1", "서준": "k2", "지우": "k3", "85": "k1", "92": "k2", "78": "k3"}

NEW_NAMES = ["List<String> names =", "    new ArrayList<>();"]
ADD3 = ['names.add("민수");', 'names.add("서준");', 'names.add("지우");']
NEW_SCORES = ["List<Integer> scores =", "    new ArrayList<>();"]
ADD_SC = ["scores.add(85);", "scores.add(92);", "scores.add(78);"]
LAMBDA = "s -> s >= 80"
PRINT2 = ['System.out.println(c.check(85) + " " + c.check(78));']
PASS_CLASS = ["class Pass implements Checker {", "  public boolean check(int s) {", "    return s >= 80;", "  }", "}",
              "Checker c = new Pass();"]
STAGES = ["(int s) -> { return s >= 80; }", "(s) -> { return s >= 80; }", "s -> { return s >= 80; }", LAMBDA]
CHECKER2 = ["interface Checker {", "  boolean check(int s);", "  boolean ok(int s);  // 추가", "}"]

def listed(s):
    """'[85, 92]' → ['85', '92']"""
    return [x.strip() for x in s.strip()[1:-1].split(",") if x.strip()]

def chips(label, values, gone=()):
    """One row of value chips, each in its person's colour; values in `gone` are struck out."""
    return (f'<div class="res in"><i>{label}</i>'
            + "".join(f'<span class="{K[v]}{" out" if v in gone else ""}">{v}</span>' for v in values) + "</div>")

def last_list():
    return listed(LAST["out"].strip().split("\n")[-1])

def parts():
    """The three parts of a lambda, each with its name underneath."""
    return ('<div class="parts in"><div><code class="k1">(int s)</code><small>매개변수</small></div>'
            '<div><code class="ar">-&gt;</code><small>화살표</small></div>'
            '<div><code class="k2">{ return s &gt;= 80; }</code><small>몸체</small></div></div>')

# every snippet drawn without a jcode/jshow/jce of its own still has to compile
jok("hook", [f"Checker c = {LAMBDA};"])
jok("syntax", [f"Checker c = {STAGES[0]};"])
for i, st in enumerate(STAGES):
    jok("short", [f"Checker c{i} = {st};"])
jok("short", ["java.util.function.Supplier<Integer> z = () -> 80;",
              "java.util.Comparator<Integer> t = (a, b) -> b - a;"], top=())
check("sort", wrap(NEW_SCORES + ADD_SC + ["scores.sort((a, b) -> a - b);", "System.out.println(scores);"]),
      "[78, 85, 92]\n")  # the narration's "a - b is the small-first order"
check("sort", wrap(NEW_SCORES + ADD_SC + ["scores.sort((a, b) -> Integer.compare(b, a));", "System.out.println(scores);"]),
      "[92, 85, 78]\n")  # the on-screen tip for large numbers
jok("final", ["int pass = 80;", "Checker c = s -> s >= pass;"])  # unchanged → fine

def fi_scene():
    a = jce("fi", [f"Checker c = {LAMBDA};"], "incompatible types: Checker is not a functional interface",
            detail="multiple non-overriding abstract methods found in interface Checker",
            mark=(2, 4), top=CHECKER2, show_top=True, sm=True) + cterm()
    jce("fi", [], "Unexpected @FunctionalInterface annotation", detail="Checker is not a functional interface",
        top=["@FunctionalInterface"] + CHECKER2)
    return (a + '<div class="note in">추상 메소드가 <b>딱 하나</b> = 함수형 인터페이스</div>'
            + f'<div class="warn in"><code>@FunctionalInterface</code> 를 붙이면<br/><b>인터페이스 선언</b>에서 바로 오류<br/><small>{html.escape(LAST["ce"])}</small></div>')

scenes = {
 "hook": '''<div class="hook">
   <div class="pill in">JAVA 입문 · 열여덟 번째</div>
   <h1 class="big in"><em>람다식</em></h1>
 ''' + code([LAMBDA]).replace('class="code in"', 'class="code in hero"') + '''
   <div class="chips in"><span>매개변수 <em>→</em> 몸체</span><span>클래스 없이 <em>한 줄</em></span></div>
 </div>''',
 "why": head("STEP 1 · 왜 필요한가", "클래스 대신 한 줄", "구현 클래스 → <b>람다식</b>")
    + lab("<code>interface Checker { boolean check(int s); }</code>")
    + jcode("why", PASS_CLASS, "true false\n", hidden=PRINT2, top=CHECKER, sm=True)
    + jcode("why", [f"Checker c = {LAMBDA};"], "true false\n", hidden=PRINT2, top=CHECKER, mark=(0,))
    + term(label="c.check(85) · c.check(78)"),
 "syntax": head("STEP 2 · 문법", "세 부분으로 읽기", "매개변수 <b>-&gt;</b> 몸체")
    + parts()
    + '<div class="note in"><code>-&gt;</code> 는 <b>화살표</b><br/><small>화살표 switch 와 기호만 같고 뜻은 다르다</small></div>',
 "short": head("STEP 2-1 · 줄여 쓰기", "더 짧게", "타입 · 괄호 · <b>{ return ; }</b> 생략")
    + lab("모두 같은 람다식")
    + code(STAGES, mark=(3,))
    + '<div class="flow in"><div><code>s</code><em>←</em>매개변수가 하나면 괄호 생략</div></div>'
    + '<div class="warn in">매개변수 0개 · 2개면 괄호 <b>필수</b><br/><code>() -&gt; 80</code>  ·  <code>(a, b) -&gt; b - a</code></div>',
 "fi": head("STEP 3 · 함수형 인터페이스", "추상 메소드는 하나만", "두 개면 <b>람다식 불가</b>") + fi_scene(),
 "pred": head("STEP 3-1 · Predicate", "자바가 만들어 둔 것", "<b>Predicate</b> = 검사용 함수형 인터페이스")
    + lab("<code>import java.util.function.Predicate;</code>")
    + jshow("pred", ["Predicate<Integer> p =", f"    {LAMBDA};", "p.test(85);  // true"], mark=(0, 1, 2))
    + '<div class="vs in">' + card("직접 만든", "Checker", "check()")
    + card("자바가 만든", "Predicate", "test()").replace('class="card"', 'class="card on"') + "</div>",
 "each": head("STEP 4 · forEach", "하나씩 꺼내 실행", "값마다 <b>람다식</b>을 실행")
    + jcode("each", NEW_NAMES + ADD3 + ["names.forEach(n ->", "    System.out.println(n));"],
            "민수\n서준\n지우\n", mark=(5, 6), sm=True)
    + term(),
 "rmif": head("STEP 4-1 · removeIf", "조건으로 지우기", "람다식 = <b>지울 조건</b>")
    + jshow("rmif", NEW_SCORES + ADD_SC + ["scores.removeIf(s -> s < 80);", "// scores → [85, 92]"], mark=(5,), sm=True)
    + chips("지우기 전", ["85", "92", "78"], gone=[v for v in ["85", "92", "78"] if v not in last_list()])
    + chips("지운 뒤", last_list()),
 "sort": head("STEP 4-2 · sort", "람다식으로 정렬", "두 값을 비교 → <b>괄호 필수</b>")
    + jshow("sort", NEW_SCORES + ADD_SC + ["scores.sort((a, b) -> b - a);", "// scores → [92, 85, 78]"], mark=(5,), sm=True)
    + chips("정렬 뒤", last_list())
    + '<div class="note in"><code>b - a</code> → 큰 순서<br/><small>a - b → 작은 순서</small></div>'
    + lab("아주 큰 수까지 안전하게: <code>Integer.compare(b, a)</code>"),
 "final": head("STEP 5 · 사실상 final", "람다식 안에서 더하기?", "람다식에서 쓰는 <b>지역 변수</b>는 다시 대입 ✗")
    + jce("final", ["// scores = [85, 92, 78]", "int sum = 0;", "scores.forEach(s -> sum += s);"],
          "local variables referenced from a lambda expression must be final or effectively final", mark=(2,),
          pre=NEW_SCORES + ADD_SC)
    + cterm()
    + '<div class="note in">한 번도 다시 대입 안 하는 변수<br/><small>= 사실상 final → 람다식에서 OK</small></div>'
    + lab("합계는 향상된 for 로")
    + jshow("final", ["int sum = 0;", "for (int s : scores) sum += s;", "// sum → 255"], mark=(1,), pre=NEW_SCORES + ADD_SC, sm=True),
 "ref": head("STEP 5-1 · 메소드 참조", "더 짧게 :: ", "받은 값을 <b>그대로 넘길 때</b>")
    + lab("람다식")
    + jcode("ref", ["names.forEach(n ->", "    System.out.println(n));"], "민수\n서준\n지우\n", pre=NEW_NAMES + ADD3)
    + lab("메소드 참조")
    + jcode("ref", ["names.forEach(", "    System.out::println);"], "민수\n서준\n지우\n", pre=NEW_NAMES + ADD3, mark=(1,))
    + term(label="둘 다 같은 결과"),
 "outro": '<div class="pill in">정리</div><h2 class="title in">람다식</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"why": 1, "syntax": 2, "short": 2, "fi": 3, "pred": 3, "each": 4, "rmif": 4, "sort": 4, "final": 5, "ref": 5}


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
