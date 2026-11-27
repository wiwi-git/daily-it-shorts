"""Builds assets/narration.mp3, index.html and examples.txt from vo.json (run gen_vo.py first).
Shared steps and helpers live in ../tools/javashorts.py; this file holds only this video's scenes."""
import os, sys, html, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import javashorts as J
J.load(speed=1.2)
from javashorts import *
# main sleeps one second before asking the worker to stop, so every example's main declares
# `throws InterruptedException`; the worker's own sleep is caught inside the lambda (22편's reason:
# Runnable.run() cannot throw it).
J.MAIN_THROWS = "InterruptedException"

EXEC = ["stop()은 쓰지 않기\n→ 멈춰 달라고 요청", "멈춤 신호에는 volatile", "interrupt()는\n자는 스레드도 깨운다",
        "예외를 삼키지 말고\ninterrupt()로 되살리기", "데몬 스레드는\n일반 스레드와 함께 끝난다"]
EXEC_SAID = ["스탑은", "멈춤", "인터럽트는", "예외를", "데몬"]
EXEC_END = "구독과"

# --- example: one worker thread for the whole video. It prints 작업 중 every 0.2 s; main waits one second
# and asks it to stop; only the way of asking changes from STEP to STEP ---
BRAND = "자바 <em>스레드 멈추기</em> 정리"
WORKING = "작업 중"

def lines_of(out):
    return out.rstrip("\n").split("\n") if out.endswith("\n") else None

def stops_with(last):
    """each= check: one or more 작업 중 lines (how many depends on timing), then `last` as the final line."""
    def ok(out):
        ls = lines_of(out)
        return bool(ls) and len(ls) >= 2 and ls[-1] == last and all(l == WORKING for l in ls[:-1])
    return ok

def daemon_ends(out):
    """each= check for the daemon example: exactly one main 끝, at least one 작업 중, never 작업 끝
    (a 6th 작업 중 may land right around main 끝, so its position is not fixed)."""
    ls = lines_of(out)
    return bool(ls) and ls.count("main 끝") == 1 and ls.count(WORKING) >= 1 and set(ls) <= {WORKING, "main 끝"}

def kept_working(never=None):
    """jhang each= check: in 3 s it kept printing 작업 중 well past the 1 s mark (5 by then, 8 or more in
    all) and never printed `never` — so it really did not stop, rather than hanging for another reason."""
    return lambda out: out.count(WORKING) >= 8 and (never is None or never not in out)

SHOWN_END =(WORKING + "\n") * 5 + "작업 끝\n"
SHOWN_MAIN = (WORKING + "\n") * 5 + "main 끝\n"

def worker(cond, end=True):
    """The worker thread: `try` around the loop, so InterruptedException ends it (22편's `catch (` break)."""
    return (["Thread t = new Thread(() -> {",
             "  try {",
             f"    while ({cond}) {{",
             f'      System.out.println("{WORKING}");',
             "      Thread.sleep(200);",
             "    }",
             "  } catch (",
             "    InterruptedException e) {}"]
            + (['  System.out.println("작업 끝");'] if end else [])
            + ["});"])

ASK = ["t.start();", "Thread.sleep(1000);"]
STOP_DECL = ["static volatile boolean stop;"]

def duo(main_block, label="이어서 main"):
    """main's last lines (left) next to the console box of the run (right)."""
    return (f'<div class="duo in"><div class="side">{lab(label)}{main_block}</div>'
            + term(cls="term") + "</div>")

def hook_scene():
    # the warning is a fact checked on this JDK: Thread.stop() now only throws
    jrt("hook", ["Thread t = new Thread(() -> {});", "t.stop();"], "UnsupportedOperationException")
    return ('<div class="hook">'
            '<div class="pill in">JAVA 입문 · 스물다섯 번째</div>'
            '<h1 class="big in">스레드<br/><em>멈추기</em></h1>'
            '<div class="warn in"><code>t.stop()</code>은 이제 <b>예외만</b> 던져요'
            "<br/><small>UnsupportedOperationException</small></div>"
            '<div class="vs in">'
            '<div class="card"><b>① 요청</b><span>멈춰 달라고<br/>알리기</span></div>'
            '<div class="card on"><b>② 스스로</b><span>스레드가 확인하고<br/>끝내기</span></div></div>'
            "</div>")

def run_split(sid, body, main, shown_out, each, mark_body=(), mark_main=(), members=(), show_members=False):
    """One program drawn as two blocks: the worker (full width) and main's last lines next to the
    console box. Checked as one program with jmulti."""
    jmulti(sid, body + main, shown_out, each=each, members=members)
    top = code(shown(body, (), members, False, show_members), mark=mark_body, sm=True)
    bottom = code(main, mark=mark_main, sm=True)
    return top, bottom

def flag_scene():
    top, bottom = run_split("flag", worker("!stop"), ASK + ["stop = true;"], SHOWN_END, stops_with("작업 끝"),
                            mark_body=(0, 3), mark_main=(2,), members=STOP_DECL, show_members=True)
    return (head("STEP 1 · 멈춤 신호", "volatile boolean",
                 "<b>volatile</b> = 다른 스레드가 바꾼 값을 보게<br/><small>없으면 못 보고 계속 돌 수도 있어요</small>")
            + top + duo(bottom))

def interrupt_scene():
    top, bottom = run_split("interrupt", worker("true"), ASK + ["t.interrupt();"], SHOWN_END,
                            stops_with("작업 끝"), mark_body=(2,), mark_main=(2,))
    return (head("STEP 2 · 인터럽트", "interrupt()",
                 "자고 있으면 <b>InterruptedException</b>으로 깨운다")
            + top + duo(bottom))

SWALLOW = ["Thread t = new Thread(() -> {",
           "  while (!Thread.currentThread()",
           "      .isInterrupted()) {",
           f'    System.out.println("{WORKING}");',
           "    try { Thread.sleep(200); }",
           "    catch (",
           "      InterruptedException e) {}",
           "  }",
           '  System.out.println("작업 끝");',
           "});"]
FIXED_CATCH = ["catch (",
               "  InterruptedException e) {",
               "  Thread.currentThread()",
               "      .interrupt();",
               "}"]
FIXED = SWALLOW[:5] + ["    " + l for l in FIXED_CATCH] + SWALLOW[7:]
STOP_IT = ASK + ["t.interrupt();"]

def swallow_scene():
    # main is STEP 2's (start, sleep 1 s, interrupt); only the worker is drawn
    jhang("swallow", SWALLOW + STOP_IT, each=kept_working("작업 끝"))
    jmulti("swallow-fixed", FIXED + STOP_IT, SHOWN_END, each=stops_with("작업 끝"))
    return (head("STEP 3 · 예외 삼키지 않기", "빈 catch {}", "예외가 나면 <b>인터럽트 상태</b>가 지워진다")
            + lab("main은 STEP 2와 같음 · <code>t.interrupt()</code>")
            + code(SWALLOW, mark=(5, 6), sm=True)
            + '<div class="duo fix in"><div class="side">' + lab("고치면 · 상태를 다시 켜기")
            + code(FIXED_CATCH, mark=(2, 3), sm=True) + "</div>"
            + '<div class="stack"><div class="warn">빈 catch면<br/><b>안 끝나요</b></div>'
              '<div class="term ok"><i>고치면 마지막 줄</i><div>작업 끝</div></div></div></div>')

def daemon_scene():
    body = worker("true", end=False)
    main = ["t.setDaemon(true);"] + ASK + ['System.out.println("main 끝");']
    # the same program without setDaemon: main ends, yet the worker keeps the program alive
    jhang("daemon-none", body + main[1:], each=lambda o: "main 끝" in o and kept_working()(o))
    top, bottom = run_split("daemon", body, main, SHOWN_MAIN, daemon_ends, mark_body=(2,), mark_main=(0,))
    return (head("STEP 4 · 데몬 스레드", "setDaemon(true)", "<b>일반 스레드</b>가 모두 끝나면 함께 끝나는 스레드")
            + top + duo(bottom, "이어서 main · start() 전에")
            + '<div class="note in">일반 스레드가 남으면 <b>프로그램이 안 끝나요</b>'
              "<br/><small>22편 main 끝 뒤의 출력 · 24편 풀 닫기</small></div>")

scenes = {
 "hook": hook_scene(),
 "flag": flag_scene(),
 "interrupt": interrupt_scene(),
 "swallow": swallow_scene(),
 "daemon": daemon_scene(),
 "outro": '<div class="pill in">정리</div><h2 class="title in">스레드 멈추기</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"flag": 1, "interrupt": 2, "swallow": 3, "daemon": 4}

CSS = """
.hook { gap: 44px; }
.hook .vs .card b { font-family: var(--font); font-size: 46px; font-weight: 800; }
.hook .vs .card span { font-family: var(--font); font-size: 40px; line-height: 1.3; color: var(--ink); }
.hook .vs .card.on span, .hook .vs .card.on b { color: var(--orange); }
.desc small { display: block; font-size: 36px; margin-top: 6px; }
.code.sm { line-height: 1.4; }
.duo { display: grid; grid-template-columns: auto 1fr; gap: 22px; align-items: start; }
.side { display: flex; flex-direction: column; gap: 12px; }
.side .tlabel { margin-bottom: 0; }
.duo .term { font-size: 32px; line-height: 1.3; padding: 16px 26px 20px; }
.stack { display: flex; flex-direction: column; gap: 18px; justify-content: space-between; align-self: stretch; }
.note small, .warn small { font-size: 32px; font-family: var(--font); }
.warn small { font-family: var(--mono); }
.note code, .warn code, .tlabel code { font-size: 36px; }
.warn { font-size: 40px; padding: 22px 32px; }
.term.ok { border-color: rgba(126,224,138,.5); }
.term.ok div { font-size: 48px; font-weight: 800; color: var(--green); }
"""

J.build(scenes, PROG, BRAND, CSS, outro=(EXEC, EXEC_SAID, EXEC_END))

# --- thumbnail: one still in the video's own CSS (tokens, Pretendard, background), rendered to PNG by
# headless Chrome (command in the 05 ticket); the bottom 300px stays empty for the Shorts UI ---
style = re.search(r"<style>.*?</style>", open("index.html").read(), re.S).group(0)
THUMB_CSS = """<style>
.thumb { position: absolute; inset: 0 0 300px; display: flex; flex-direction: column; justify-content: center;
  gap: 56px; padding: 0 80px; }
.thumb .pill { font-size: 52px; padding: 16px 40px; }
.thumb .big { font-size: 220px; line-height: 1.08; }
.thumb .sub { font-size: 60px; }
.thumb .chips span { font-family: var(--mono); font-size: 46px; color: var(--blue); }
</style>"""
open("thumbnail.html", "w").write(f'''<!doctype html>
<html lang="ko"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
{style}
{THUMB_CSS}
</head><body><div id="root">
  <div class="brand"><b>{BRAND}</b></div>
  <div class="thumb">
    <div class="pill">JAVA 입문 · 25편</div>
    <h1 class="big">스레드<br/><em>멈추기</em></h1>
    <p class="sub">멈춰 달라고 <b>요청</b>하기</p>
    <div class="chips"><span>volatile</span><span>interrupt</span><span>데몬</span></div>
  </div>
</div></body></html>
''')
