"""Builds assets/narration.mp3, index.html and examples.txt from vo.json (run gen_vo.py first).
Shared steps and helpers live in ../tools/javashorts.py; this file holds only this video's scenes."""
import os, sys, html
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import javashorts as J
J.load(speed=1.2)
from javashorts import *
# Thread output can change from run to run: those examples go through jmulti (run 20 times, checked
# by a rule) and their console box draws a fixed example the rule accepts.

EXEC = ["new Thread(람다) · start()", "run()은 그냥 메소드 호출", "출력 순서는 보장 안 됨",
        "join() 끝날 때까지 기다리기", "같은 변수 → 경쟁 조건", "synchronized 한 번에 하나"]
EXEC_SAID = ["뉴", "런을", "출력", "조인은", "같은", "싱크로나이즈드로"]
EXEC_END = "구독과"

# --- example data: 민수 85 (k1) · 서준 92 (k2) printed by two threads; shared counter `count` (STEP 3·4) ---
BRAND = "자바 입문 <em>스레드</em> 정리"
K = {"민수": "k1", "서준": "k2"}

def kterm(cls="term in"):
    """Console box of the last example, each line in its person's colour (term() draws plain lines)."""
    label = LAST.get("label") or "실행 결과"
    body = "".join(f'<div class="{K.get(l.split(" ")[0], "")}">{html.escape(l)}</div>'
                   for l in LAST["out"].rstrip("\n").split("\n"))
    return f'<div class="{cls}"><i>{label}</i>{body}</div>'

def hook_scene():
    return ('<div class="hook">'
            '<div class="pill in">JAVA 입문 · 스물두 번째</div>'
            '<h1 class="big in"><em>스레드</em></h1>'
            '<p class="sub in">코드를 실행하는 <b>흐름</b></p>'
            '<div class="vs in">'
            '<div class="card"><b>지금까지</b><span>main 스레드<br/>하나</span></div>'
            '<div class="card on"><b>오늘</b><span>스레드 여러 개<br/>→ 번갈아 실행</span></div></div>'
            "</div>")

START = ["Thread a = new Thread(() ->",
         '  System.out.println("민수 85"));',
         "Thread b = new Thread(() ->",
         '  System.out.println("서준 92"));',
         "a.start();",
         "b.start();",
         'System.out.println("main 끝");']

def start_scene():
    block = jmulti("start", START, "민수 85\nmain 끝\n서준 92\n",
                   each=same_lines("민수 85", "서준 92", "main 끝"), mark=(0, 4, 5))
    return (head("STEP 1 · 스레드 만들기", "new Thread + start()", "<b>람다식</b>으로 할 일을 넘기고 <b>start()</b>")
            + block
            + '<div class="duo in">' + kterm(cls="term")
            + '<div class="stack"><div class="note">main은<br/><small>기다리지 않음</small></div>'
              '<div class="warn">출력 순서<br/><small>보장 안 됨</small></div></div></div>'
            + '<div class="note in">다른 방법: <code>extends Thread</code><br/><small>Thread 클래스를 물려받기</small></div>')

NAME = ["Thread t = new Thread(() ->",
        "  System.out.println(",
        "    Thread.currentThread()",
        "      .getName()));"]

def run_trap_scene():
    jcode("run-trap", NAME + ["t.start();"], "Thread-0\n")
    jcode("run-trap-run", NAME + ["t.run();"], "main\n")
    return (head("STEP 1-1 · run() 함정", "start() 대신 run()?", "<b>getName()</b>으로 실행 중인 스레드 이름 보기")
            + code(NAME, mark=(2, 3))
            + '<div class="vs in">'
              '<div class="card on"><small>t.start();</small><b class="ok">Thread-0</b><span>새 스레드에서 실행</span></div>'
              '<div class="card bad"><small>t.run();</small><b class="ng">main</b><span>main 스레드가<br/>그냥 메소드 호출</span></div></div>'
            + '<div class="warn in">함정! <code>run()</code>은 <b>오류가 아니라</b> 그냥 메소드 호출<br/>'
              "<small>새 스레드를 만들려면 반드시 start()</small></div>")

WORK = ["Thread t = new Thread(() -> {",
        "  try {",
        "    Thread.sleep(1000);",
        "  } catch (",
        "    InterruptedException e) {}",
        '  System.out.println("민수 85");',
        "});",
        "t.start();"]
JOIN = WORK + ["t.join();", 'System.out.println("채점 끝");']

def join_scene():
    # join() can throw the checked InterruptedException, so main declares it from here on; sleep() inside
    # the lambda cannot pass it on (Runnable.run() throws nothing) and catches it instead.
    J.MAIN_THROWS = "InterruptedException"
    jmulti("join-none", WORK + ['System.out.println("채점 끝");'], "채점 끝\n민수 85\n",
           each=lambda o: o == "채점 끝\n민수 85\n", runs=5, label="join 없음")
    none = kterm(cls="term")
    block = jmulti("join", JOIN, "민수 85\n채점 끝\n", each=lambda o: o == "민수 85\n채점 끝\n", runs=5,
                   label="t.join() 있음", mark=(2, 8), sm=True)
    return (head("STEP 2 · sleep과 join", "끝날 때까지 기다리기", "<b>sleep(1000)</b> 1초 쉬기 · <b>join()</b> 기다리기")
            + block
            + '<div class="duo in">' + none + kterm(cls="term ok") + "</div>"
            + '<div class="note in jn"><b>체크 예외</b> InterruptedException<br/>'
              "<small>sleep → 스레드 안 try-catch · join → main에 throws</small></div>")

def inc(sync=""):
    """Main's members: the shared counter and the method each thread runs (STEP 3; STEP 4 adds `synchronized`)."""
    return ["static int count = 0;", f"static {sync}void inc() {{", "  for (int i = 0; i < 10000; i++)",
            "    count++;", "}", ""]  # blank line: where main's statements start on screen

TWO = ["Thread a = new Thread(Main::inc);",
       "Thread b = new Thread(Main::inc);",
       "a.start(); b.start();",
       "a.join(); b.join();",
       "System.out.println(count);"]

def race_scene():
    block = jmulti("race", TWO, "13426\n", each=lambda o: int(o) <= 20000,
                   all_=lambda outs: any(int(o) < 20000 for o in outs),
                   label="실행 결과 예시 · 매번 다름", members=inc(), show_members=True, mark=(3,), sm=True)
    return (head("STEP 3 · 경쟁 조건", "같은 변수를 함께", "만 번씩 두 번 → <b>20000</b>이 아니다?")
            + block
            + '<div class="duo in">' + term(cls="term bad")
            + '<div class="note steps"><code>count++</code>\n읽기→더하기→쓰기\n'
              "<small>같은 값을 읽고 각자 쓰면\n→ 하나 사라짐</small></div></div>"
            + '<div class="warn in"><b>경쟁 조건</b> (레이스 컨디션)</div>')

def sync_scene():
    block = jmulti("sync", TWO, "20000\n", each=lambda o: o == "20000\n", label="실행 결과 · 20회 모두",
                   note="출력 (20회 실행해 매번 같음 확인):",
                   members=inc("synchronized "), show_members=True, mark=(1,), sm=True)
    return (head("STEP 4 · synchronized", "한 번에 하나씩", "메소드에 <b>synchronized</b> → 동기화")
            + block
            + '<div class="duo in">' + term(cls="term ok")
            + '<div class="note">한 번에 <b>한 스레드만</b><br/><small>inc() 안에 들어감</small></div></div>')

scenes = {
 "hook": hook_scene(),
 "start": start_scene(),
 "run-trap": run_trap_scene(),
 "join": join_scene(),
 "race": race_scene(),
 "sync": sync_scene(),
 "outro": '<div class="pill in">정리</div><h2 class="title in">스레드</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"start": 1, "run-trap": 1, "join": 2, "race": 3, "sync": 4}

CSS = """
.hook { gap: 44px; }
.hook .vs .card span { font-family: var(--font); font-size: 40px; line-height: 1.3; color: var(--ink); }
.hook .vs .card.on span { color: var(--orange); }
.note code, .warn code { font-size: 40px; }
.duo { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
.stack { display: flex; flex-direction: column; gap: 22px; }
.stack .note, .stack .warn { font-size: 38px; padding: 20px 28px; }
.stack small { font-size: 34px; font-family: var(--font); }
.tlabel small { font-size: 30px; }
.note.jn small { font-size: 32px; font-family: var(--font); }
.term.bad { border-color: rgba(255,93,93,.5); }
#sc-race .term.bad div, #sc-sync .term.ok div { font-size: 64px; font-weight: 800; }
#sc-race .term.bad div { color: var(--red); } #sc-sync .term.ok div { color: var(--green); }
.note.steps { font-size: 36px; padding: 20px 28px; white-space: pre-line; }
.note.steps small { font-size: 32px; font-family: var(--font); }
.term.ok { border-color: rgba(126,224,138,.5); }
#sc-run-trap .vs .card small { font-family: var(--mono); font-size: 38px; color: var(--blue); }
#sc-run-trap .vs .card b { font-size: 64px; }
#sc-run-trap .vs .card span { font-family: var(--font); font-size: 36px; font-weight: 700; color: var(--mute); line-height: 1.3; }
#sc-run-trap .vs .card.on { box-shadow: inset 0 0 0 3px var(--green); }
#sc-run-trap .vs .card.bad { box-shadow: inset 0 0 0 3px var(--red); }
"""

J.build(scenes, PROG, BRAND, CSS, outro=(EXEC, EXEC_SAID, EXEC_END))
