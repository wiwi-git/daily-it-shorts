"""Builds assets/narration.mp3, index.html and examples.txt from vo.json (run gen_vo.py first).
Shared steps and helpers live in ../tools/javashorts.py; this file holds only this video's scenes."""
import os, sys, html, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import javashorts as J
J.load(speed=1.2)
from javashorts import *
# Every example runs in main, which declares `throws Exception` (Future.get() throws checked exceptions)
# and imports java.util.concurrent; the pool is always closed by try-with-resources, so each shown
# program runs to the end when typed in as it is.
J.MAIN_THROWS = "Exception"
J.IMPORTS = ["import java.util.concurrent.*;", ""]

EXEC = ["스레드 풀 = 스레드 돌려 쓰기\n남은 작업은 대기 줄에서", "newFixedThreadPool(2)\n+ submit(작업)",
        "값을 돌려주면 → Future", "get()은 끝날 때까지 기다림", "try-with-resources로 닫기",
        "가상 스레드\nnewVirtualThreadPerTaskExecutor()"]
EXEC_SAID = ["만든", "픽스드", "퓨처로", "겟은", "트라이", "가상"]
EXEC_END = "구독과"

# --- example data: 22편's 민수 85 (k1) · 서준 92 (k2); tasks print them (STEP 2), then return them (STEP 3) ---
BRAND = "자바 입문 <em>스레드 풀</em> 정리"

def hook_scene():
    return ('<div class="hook">'
            '<div class="pill in">JAVA 입문 · 스물네 번째</div>'
            '<h1 class="big in">스레드 <em>풀</em></h1>'
            '<p class="sub in">만든 스레드를 <b>돌려 쓰기</b></p>'
            '<div class="vs in">'
            '<div class="card"><b>22편</b><span>작업마다<br/>new Thread</span></div>'
            '<div class="card on"><b>오늘</b><span>몇 개만 만들어<br/>돌려 쓰기 · 결과 받기</span></div></div>'
            "</div>")

def why_scene():
    return (head("STEP 1 · 왜 스레드 풀?", "만들고 버리면", "스레드도 <b>만들고 없애는 데</b> 시간이 든다")
            + '<div class="vs in">'
              '<div class="card"><b>작업마다 new</b><span>작업 1000개<br/>→ 스레드 1000개</span></div>'
              '<div class="card on"><b>스레드 풀</b><span>정해 둔 2개를<br/>돌려 쓰기</span></div></div>'
            + '<div class="pool in"><i>작업 3개 · 스레드 2개</i>'
              '<div class="tr"><span>대기 줄</span><div class="trk"><b class="t q">작업 3</b><b class="arr">↓ 꺼내 감</b></div></div>'
              '<div class="tr"><span>스레드 1</span><div class="trk"><b class="t">작업 1</b><b class="t t3">작업 3</b></div></div>'
              '<div class="tr"><span>스레드 2</span><div class="trk"><b class="t t2">작업 2</b></div></div></div>'
            + '<div class="note in">먼저 끝난 스레드가 <b>대기 줄</b>에서 꺼내 간다</div>')

K = {"민수": "k1", "서준": "k2"}

def kterm(cls="term in"):
    """Console box of the last example, each line in its person's colour (term() draws plain lines)."""
    label = LAST.get("label") or "실행 결과"
    body = "".join(f'<div class="{K.get(l.split(" ")[0], "")}">{html.escape(l)}</div>'
                   for l in LAST["out"].rstrip("\n").split("\n"))
    return f'<div class="{cls}"><i>{label}</i>{body}</div>'

def pool(body, make="newFixedThreadPool(2)"):
    """The shown program: a pool opened by try-with-resources around `body` (closed when the block ends)."""
    return ["try (ExecutorService pool =", f"  Executors.{make}", ") {"] + ["  " + l for l in body] + ["}"]

SUBMIT = pool(["pool.submit(() ->", '  System.out.println("민수 85"));',
               "pool.submit(() ->", '  System.out.println("서준 92"));'])
FUT_BODY = ["Future<Integer> f1 =", "  pool.submit(() -> 85);",
            "Future<Integer> f2 =", "  pool.submit(() -> 92);",
            "int sum = f1.get() + f2.get();", "System.out.println(sum);"]
ALWAYS = dict(each=lambda o: o == "177\n", label="실행 결과 · 20회 모두", note="출력 (20회 실행해 매번 같음 확인):")
IMPORT = lab("<code>import java.util.concurrent.*;</code>")

def submit_scene():
    block = jmulti("submit", SUBMIT, "민수 85\n서준 92\n", each=same_lines("민수 85", "서준 92"),
                   mark=(1, 3, 5), sm=True)
    return (head("STEP 2 · 작업 맡기기", "submit()", "스레드 <b>2개</b>짜리 풀에 <b>작업</b>을 맡긴다")
            + IMPORT + block
            + '<div class="duo in">' + kterm(cls="term")
            + '<div class="stack"><div class="note cmp"><small>22편</small>new Thread(…)\n.start()'
              '<small>오늘</small><b>pool.submit(…)</b></div></div></div>'
            + '<div class="note in">람다식은 그대로 · <b>start()</b> 없이 실행</div>')

def future_scene():
    block = jmulti("future", pool(FUT_BODY), "177\n", mark=(3, 4, 5, 6, 7), sm=True, **ALWAYS)
    return (head("STEP 3 · 값 돌려받기", "Future · get()", "값을 <b>돌려주는</b> 작업 = <code>Callable</code>")
            + lab("<code>main(…) throws Exception</code> <small>get()도 예외를 던질 수 있어서</small>")
            + block
            + '<div class="duo in">' + term(cls="term ok")
            + '<div class="note steps"><b>퓨처</b>\n<small>(나중에 결과를\n꺼내는 상자)</small></div></div>'
            + '<div class="note in"><code>get()</code> = 작업이 <b>끝날 때까지 기다렸다</b> 꺼내기</div>')

CLOSE = pool(["// submit · get"])

def close_scene():
    jok("close", CLOSE)
    # the virtual-thread version is only named on screen (the method names below), but it still has to
    # run: STEP 3's program with the pool line swapped must print 177 too
    check("close-virtual", wrap(pool(FUT_BODY, "newVirtualThreadPerTaskExecutor()")), "177\n")
    return (head("STEP 4 · 풀 닫기", "try-with-resources", "파일을 닫을 때 쓴 <b>그 문법</b>")
            + code(CLOSE, mark=(0, 1, 2, 4), sm=True)
            + '<div class="note in"><code>}</code> 블록이 끝나면<br/>작업이 <b>다 끝날 때까지</b> 기다렸다 닫기'
              "<br/><small><code>join()</code>을 따로 안 불러도 된다 · 자바 19부터</small></div>"
            + '<div class="warn in">고정 풀은 안 닫으면 <b>프로그램이 끝나지 않아요</b></div>'
            + '<div class="swap in"><i>풀을 만드는 줄만 바꾸면 · 자바 21부터</i>'
              "<code>newFixedThreadPool(2)</code><em>↓</em>"
              '<code class="v">newVirtualThreadPerTaskExecutor()</code>'
              "<small>풀이 아니라 작업마다 <b>가벼운 가상 스레드</b> · 결과는 똑같이 177</small></div>")

scenes = {
 "hook": hook_scene(),
 "why": why_scene(),
 "submit": submit_scene(),
 "future": future_scene(),
 "close": close_scene(),
 "outro": '<div class="pill in">정리</div><h2 class="title in">스레드 풀</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"why": 1, "submit": 2, "future": 3, "close": 4}

CSS = """
.hook { gap: 44px; }
.hook .vs .card span { font-family: var(--font); font-size: 40px; line-height: 1.3; color: var(--ink); }
.hook .vs .card.on span { color: var(--orange); }
#sc-why .vs .card span { font-family: var(--font); font-size: 40px; line-height: 1.3; color: var(--ink); }
#sc-why .vs .card.on span { color: var(--orange); }
#sc-why .vs .card b { font-family: var(--font); font-size: 46px; font-weight: 800; }
.pool { display: flex; flex-direction: column; gap: 16px; background: var(--panel); border-radius: 26px;
  padding: 28px 30px; }
.pool > i { font-style: normal; font-size: 32px; font-weight: 700; color: var(--mute); }
.tr { display: grid; grid-template-columns: 150px 1fr; align-items: center; gap: 18px; }
.tr span { font-size: 32px; font-weight: 700; color: var(--mute); }
.trk { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; height: 84px; }
.trk b { border-radius: 14px; display: flex; align-items: center; justify-content: center;
  font-size: 34px; font-weight: 800; border: 3px solid #26324a; color: var(--ink); }
.trk .t2 { grid-column: 1 / span 2; }
.trk .q { border-style: dashed; color: var(--orange); }
.trk .arr { border: 0; font-size: 30px; color: var(--mute); }
.duo { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
.stack { display: flex; flex-direction: column; gap: 22px; }
.term .k1 { color: var(--orange); } .term .k2 { color: var(--green); }
.term.ok { border-color: rgba(126,224,138,.5); }
.term.ok div { font-size: 64px; font-weight: 800; color: var(--green); }
.note.cmp { font-family: var(--mono); font-size: 34px; padding: 18px 26px; white-space: pre-line; line-height: 1.3; }
.note.cmp small { display: block; font-family: var(--font); font-size: 28px; color: var(--mute); margin-top: 6px; }
.note.steps { font-size: 40px; padding: 20px 28px; white-space: pre-line; }
.note small, .warn small { font-size: 34px; font-family: var(--font); }
.note code, .warn code, .tlabel code { font-size: 36px; }
.tlabel small { font-size: 28px; margin-left: 10px; }
.swap { display: flex; flex-direction: column; gap: 8px; background: var(--panel); border-radius: 26px; padding: 24px 30px; }
.swap i { font-style: normal; font-size: 30px; font-weight: 700; color: var(--mute); }
.swap code { font-family: var(--mono); font-size: 38px; font-weight: 800; color: var(--blue); }
.swap code.v { color: var(--orange); }
.swap em { font-style: normal; font-size: 34px; color: var(--mute); }
.swap small { font-size: 32px; font-weight: 700; color: var(--ink); margin-top: 6px; }
.swap small b { color: var(--orange); }
#ex6 b { font-size: 38px; }
.trk .t3 { border-color: var(--orange); color: var(--orange); background: rgba(242,145,17,.13); }
"""

J.build(scenes, PROG, BRAND, CSS, outro=(EXEC, EXEC_SAID, EXEC_END))

# --- thumbnail: one still in the video's own CSS (tokens, Pretendard, background), rendered to PNG by
# headless Chrome (command in the 04 ticket); the bottom 300px stays empty for the Shorts UI ---
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
    <div class="pill">JAVA 입문 · 24편</div>
    <h1 class="big">스레드<br/><em>풀</em></h1>
    <p class="sub">만든 스레드를 <b>돌려 쓰기</b></p>
    <div class="chips"><span>submit</span><span>Future</span><span>get</span></div>
  </div>
</div></body></html>
''')
