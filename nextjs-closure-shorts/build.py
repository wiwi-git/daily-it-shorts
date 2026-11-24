"""Builds assets/narration.mp3, index.html and examples.txt from vo.json (run gen_vo.py first).
Shared steps and helpers live in ../tools/javashorts.py; this file holds only this video's scenes."""
import os, sys, html, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import javashorts as J
J.load(speed=1.2)
from javashorts import *
# JavaScript examples run with node (jscode), Java ones with javac (jcode / jce); React·Next.js code
# cannot run here and is only drawn (xshow). JavaScript is always blue, Java always green.

J.IMPORTS = ["import java.util.*;", "import java.util.function.*;", ""]
BRAND = "Next.js <em>클로저</em> 정리"
ERR = "effectively final"   # javac: local variables referenced from a lambda expression must be final or effectively final

EXEC = ["클로저 = 함수 + 바깥 변수", "JS는 변수 자체를 붙잡음", "자바는 사실상 final만 (동시성)",
        "반복문은 let", "React 상태는 스냅샷\n서버 액션 값은 브라우저를 오감"]
EXEC_SAID = ["클로저는", "자바스크립트는", "자바는", "반복문에서는", "리액트"]
EXEC_END = "구독과"

def bare(block):
    """A code block placed inside an animated card: the card is what slides in."""
    return block.replace('class="code in', 'class="code', 1)

def chip(text, cls="ok"):
    return f'<span class="{cls}">{html.escape(text)}</span>'

def out_chip(label="", cls="ok"):
    """The last run's real output on one line (each printed line → space)."""
    return chip((label + " → " if label else "") + LAST["out"].rstrip("\n").replace("\n", " "), cls)

def err_chip(label=""):
    return chip((label + " → " if label else "") + "컴파일 오류", "ng")

def lang(cls, name, chips, block, foot=""):
    """One language's card in a top-to-bottom comparison (JavaScript above, Java below)."""
    return (f'<div class="lang {cls} in"><div class="lh"><b>{name}</b>{"".join(chips)}</div>{bare(block)}'
            + (f'<div class="why">{foot}</div>' if foot else "") + "</div>")

def ce_foot():
    """javac's real message for the last jce(), shortened to the part that names the rule."""
    msg = LAST["ce"]
    i = msg.find("must be")
    return html.escape("… " + msg[i:] if i > 0 else msg)

# --- hook ---
def hook_scene():
    return ('<div class="hook">'
            '<div class="pill in">Next.js</div>'
            '<h1 class="big in"><em>클로저</em></h1>'
            '<p class="sub in">같은 코드, <b>다른 결과</b></p>'
            '<div class="vs in">'
            '<div class="card js"><b>JavaScript</b><span>2 출력</span></div>'
            '<div class="card java"><b>Java</b><span class="ng">컴파일 오류</span></div></div>'
            "</div>")

# --- STEP 1: the counter (the example used through the whole video) ---
COUNTER = ["function makeCounter() {",
           "  let count = 0;",
           "  return () => ++count;",
           "}",
           "const c1 = makeCounter();",
           "const c2 = makeCounter();",
           "console.log(c1(), c1(), c2());"]

def counter_scene():
    block = jscode("counter", COUNTER, "1 2 1\n", mark=(1, 2), sm=True)
    return (head("STEP 1 · 클로저란", "함수 + 바깥 변수", "함수가 끝나도 <b>붙잡은(캡처)</b> 변수는 살아 있다")
            + lang("js", "JavaScript", [out_chip()], block)
            + '<div class="note in"><code>() =&gt; x</code> = 자바의 <code>() -&gt; x</code><br/>'
              "<small>let · const = 변수 선언</small></div>"
            + '<div class="note in">c1·c2는 <b>각자의 count</b><br/><small>makeCounter()를 부를 때마다 새로 생김</small></div>')

# --- STEP 2: JavaScript holds the variable itself; Java refuses ---
CAP_JS = ["let x = 1;",
          "const f = () => x;",
          "x = 2;",
          "console.log(f());"]
CAP_JAVA = ["int x = 1;",
            "Supplier<Integer> f = () -> x;",
            "x = 2;",
            "System.out.println(f.get());"]

def capture_scene():
    js = jscode("capture", CAP_JS, "2\n", mark=(2,), sm=True)
    js_card = lang("js", "JavaScript", [out_chip()], js)
    java = jce("capture-java", CAP_JAVA, ERR, mark=(2,), sm=True)
    return (head("STEP 2 · 변수를 붙잡는다", "값이 아니라 변수", "자바스크립트는 <b>바뀐 값</b>까지 본다")
            + js_card
            + lang("java", "Java", [err_chip()], java, ce_foot())
            + '<div class="note in">자바는 "클로저" 대신 <b>람다식의 캡처</b><br/><small>사실상 final만 캡처 · 19편 람다식 참고</small></div>')

# --- STEP 3: why Java forbids it, and the workaround ---
BAD = ["static IntSupplier",
       "    makeCounter() {",
       "  int count = 0;",
       "  return () -> ++count;",
       "}"]
GOOD = ["static IntSupplier",
        "    makeCounter() {",
        "  int[] count = {0};",
        "  return () -> ++count[0];",
        "}"]
CALLS = ["IntSupplier c1 = makeCounter();",
         "IntSupplier c2 = makeCounter();",
         'System.out.println(c1.getAsInt() + " " + c1.getAsInt() + " " + c2.getAsInt());']

def why_scene():
    bad = jce("why", [], ERR, members=BAD, show_members=True, mark=(3,), sm=True)
    bad_card = lang("java", "Java · int", [err_chip("++count")], bad)
    good = jcode("why-array", [], "1 2 1\n", hidden=CALLS, members=GOOD, show_members=True, mark=(2, 3), sm=True)
    return (head("STEP 3 · 자바는 왜?", "바뀌는 변수는 금지", "<b>동시성 문제</b>를 막으려고 (자바 언어 명세)")
            + bad_card
            + lang("java", "Java · int 배열", [out_chip("c1, c1, c2")], good)
            + '<div class="note in">배열을 가리키는 변수는 그대로<br/>'
              "<small>실무에서는 AtomicInteger · 22편 스레드 참고</small></div>")

# --- STEP 4: loops ---
LOOP_JS = ["const a = [];",
           "for (var i = 0; i < 3; i++)",
           "  a.push(() => console.log(i));",
           "a.forEach(f => f());"]
LIST = ["List<IntSupplier> list = new ArrayList<>();"]
LOOP_JAVA_FOR = ["for (int i = 0; i < 3; i++)",
                 "  list.add(() -> i);"]
LOOP_JAVA_EACH = ["for (int n : new int[]{0, 1, 2})",
                  "  list.add(() -> n);"]
PRINT = ["for (IntSupplier s : list) System.out.println(s.getAsInt());"]

def loop_scene():
    js = jscode("loop", LOOP_JS, "3\n3\n3\n", mark=(1,), sm=True)
    var = out_chip("var", "ng")
    jscode("loop-let", [l.replace("var", "let") for l in LOOP_JS], "0\n1\n2\n")
    let = out_chip("let")
    jce("loop-java", LOOP_JAVA_FOR, ERR, pre=LIST)
    jcode("loop-java-each", LOOP_JAVA_EACH, "0\n1\n2\n", pre=LIST, hidden=PRINT)
    each = out_chip("향상된 for")
    java = code(["// list: IntSupplier 리스트"] + LOOP_JAVA_FOR + LOOP_JAVA_EACH, mark=(2,), sm=True)
    return (head("STEP 4 · 반복문 함정", "모두 3이 나온다?", "<b>var</b>는 하나를 함께 · <b>let</b>은 반복마다 새로")
            + lang("js", "JavaScript", [var, let], js)
            + lang("java", "Java", [err_chip("일반 for"), each], java))

# --- STEP 5: where Next.js code meets closures ---
SNAP = ["const [number, setNumber] =",
        "  useState(0);",
        "<button onClick={() => {",
        "  setNumber(number + 5);",
        "  setTimeout(() => {",
        "    alert(number);",
        "  }, 3000);",
        "}}>+5</button>"]

def snapshot_scene():
    block = xshow("snapshot", SNAP, mark=(5,), sm=True)
    return (head("STEP 5 · React 스냅샷", "알림은 0?", "핸들러는 <b>그 렌더링의 값</b>을 붙잡는다")
            + block
            + '<div class="res in"><i>클릭 3초 뒤</i><span>화면 5</span><span class="bad">알림 0</span></div>')

# react.dev "Queueing a Series of State Updates": +3 in one click (before 1, with updater 3)
UPD_BEFORE = ["// 클릭 한 번에 +3?",
              "setNumber(number + 1);",
              "setNumber(number + 1);",
              "setNumber(number + 1);"]
UPD_AFTER = ["// n = 바로 전 값",
             "setNumber(n => n + 1);",
             "setNumber(n => n + 1);",
             "setNumber(n => n + 1);"]

def updater_scene():
    before = xshow("updater-before", UPD_BEFORE, sm=True)
    after = xshow("updater-after", UPD_AFTER, mark=(1, 2, 3), sm=True)
    return (head("STEP 5 · 업데이터 함수", "세 번 더해도 1?", "붙잡은 값 대신 <b>함수</b>를 넘긴다")
            + lang("before", "붙잡은 값", [chip("→ 1", "ng")], before)
            + lang("after", "업데이터 함수", [chip("→ 3")], after)
            + '<div class="note in">업데이터는 <b>다음 렌더링 값</b>을 계산<br/>'
              "<small>붙잡은 number는 그대로 → 알림은 여전히 0</small></div>")

ACTION = ["async function Page() {",
          "  const version =",
          "    await getVersion();",
          "  async function publish() {",
          '    "use server";',
          "    // version 사용",
          "  }",
          "  return <button",
          "    formAction={publish} />;",
          "}"]

def action_scene():
    block = xshow("action", ACTION, mark=(1, 5), sm=True, fname="app/page.jsx")
    return (head("STEP 5 · 서버 액션", "붙잡은 값이 오간다", "<b>\"use server\"</b> 함수도 클로저")
            + block
            + '<div class="chips in"><span>서버</span><span class="gt">→</span><span>🔒 브라우저</span>'
              '<span class="gt">→</span><span>서버</span></div>'
            + '<div class="warn in">자동 암호화되지만 <b>암호화만 믿지 말 것</b><br/>'
              "<small>비밀값은 붙잡지 않기</small></div>")

scenes = {
 "hook": hook_scene(),
 "counter": counter_scene(),
 "capture": capture_scene(),
 "why": why_scene(),
 "loop": loop_scene(),
 "snapshot": snapshot_scene(),
 "updater": updater_scene(),
 "action": action_scene(),
 "outro": '<div class="pill in">정리</div><h2 class="title in">클로저</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"counter": 1, "capture": 2, "why": 3, "loop": 4, "snapshot": 5, "updater": 5, "action": 5}

CSS = """
.hook { gap: 44px; }
.hook .vs .card b { font-family: var(--font); font-size: 44px; }
.hook .vs .card span { font-family: var(--mono); font-size: 52px; color: var(--ink); }
.hook .vs .card.js b { color: var(--blue); } .hook .vs .card.java b { color: var(--green); }
.hook .vs .card span.ng { color: var(--red); font-family: var(--font); }
.note code, .warn code { font-size: 40px; }
.lang { background: var(--panel); border-radius: 26px; padding: 18px 22px 22px; border-left: 10px solid; display: flex; flex-direction: column; gap: 14px; }
.lang.js { border-color: var(--blue); } .lang.java { border-color: var(--green); }
.lang.before { border-color: var(--red); } .lang.after { border-color: var(--orange); }
.lang.before .lh b { color: var(--red); } .lang.after .lh b { color: var(--orange); }
.lh { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.lh b { font-size: 36px; font-weight: 800; margin-right: 6px; }
.lang.js .lh b { color: var(--blue); } .lang.java .lh b { color: var(--green); }
.lh span { font-family: var(--mono); font-size: 34px; font-weight: 800; padding: 6px 18px; border-radius: 12px; background: #0a0f1a; color: var(--ink); }
.lh span.ng { color: var(--red); box-shadow: inset 0 0 0 3px var(--red); background: rgba(255,93,93,.1); font-family: var(--font); }
.lang .code { box-shadow: none; }
.lang .why { font-family: var(--mono); font-size: 28px; color: var(--red); white-space: normal; }
.chips .gt { font-size: 42px; }
.note small { font-family: var(--font); }
#sc-why { gap: 20px; } #sc-why .lang { gap: 10px; padding: 14px 22px 16px; } #sc-why .code.sm { font-size: 32px; padding: 16px 24px; }
#sc-outro .row b { font-family: var(--font); font-weight: 800; }
"""

NODE = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
J.build(scenes, PROG, BRAND, CSS, outro=(EXEC, EXEC_SAID, EXEC_END),
        examples_header=["자바(Main.java): javac -g -encoding UTF-8 Main.java && java Main",
                         f"자바스크립트(main.js): node main.js  (확인한 Node.js: {NODE})",
                         "React·Next.js 코드(.jsx): 화면에만 나오고 실행하지 않음"])
