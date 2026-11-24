"""Builds assets/narration.mp3, index.html and examples.txt from vo.json (run gen_vo.py first).
Shared steps and helpers live in ../tools/javashorts.py; this file holds only this video's scenes."""
import os, sys, html, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import javashorts as J
J.load(speed=1.2)
from javashorts import *
J.KW.append("synchronized")  # the keyword this video is about: highlight it like the others
# Every example runs two threads, so each goes through jmulti (run 20 times, checked by a rule) and
# its console box draws a fixed example the rule accepts.

EXEC = ["메소드 전체 → 사실상 차례로", "synchronized (lock)\n필요한 줄만", "같은 잠금 객체를 써야",
        "incrementAndGet() 원자적 연산", "ArrayList는 스레드 안전 X", "synchronizedList로 감싸기"]
EXEC_SAID = ["메소드", "싱크로나이즈드", "같은", "아토믹", "어레이", "싱크로나이즈드"]
EXEC_END = "구독과"

# --- example data: 22편's shared counter `count`, two threads × 10000 (STEP 4: a shared list instead) ---
BRAND = "자바 입문 <em>동기화</em> 정리"
ALWAYS = dict(each=lambda o: o == "20000\n", label="실행 결과 · 20회 모두",
              note="출력 (20회 실행해 매번 같음 확인):")

def threads(m="inc"):
    """main's statements: two threads run Main::<m>, main waits for both (the print line comes after)."""
    return [f"Thread a = new Thread(Main::{m});", f"Thread b = new Thread(Main::{m});",
            "a.start(); b.start();", "a.join(); b.join();"]

def hook_scene():
    return ('<div class="hook">'
            '<div class="pill in">JAVA 입문 · 스물세 번째</div>'
            '<h1 class="big in">동기화<br/><em>더 깊이</em></h1>'
            '<p class="sub in">지난 편 <b>synchronized</b>의 문제</p>'
            '<div class="vs in">'
            '<div class="card"><b>지난 편</b><span>메소드 전체에<br/>synchronized</span></div>'
            '<div class="card on"><b>오늘</b><span>필요한 줄만 ·<br/>AtomicInteger</span></div></div>'
            "</div>")

SYNC_INC = ["static int count = 0;",
            "static synchronized void inc() {",
            "  for (int i = 0; i < 10000; i++)",
            "    count++;",
            "}"]

def scope_scene():
    J.MAIN_THROWS = "InterruptedException"  # join() throws it; main declares it in every example
    block = jmulti("scope", [], "20000\n", hidden=threads() + ["System.out.println(count);"],
                   members=SYNC_INC, show_members=True, mark=(1,), sm=True, **ALWAYS)
    return (head("STEP 1 · 메소드 전체를 잠그면", "지난 편 코드", "<b>synchronized</b>가 만 번 도는 메소드 전체에")
            + block
            + '<div class="tline in"><i>시간 →</i>'
              '<div class="tr"><span>스레드 1</span><div class="trk"><b class="b1">inc() 만 번</b></div></div>'
              '<div class="tr"><span>스레드 2</span><div class="trk"><b class="wt">기다림</b><b class="b2">inc() 만 번</b></div></div></div>'
            + '<div class="duo in">' + term(cls="term ok")
            + '<div class="warn">결과는 맞지만<br/><small>사실상 차례로 실행</small></div></div>')

BLOCK_INC = ["static int count = 0;",
             "static final Object lock =",
             "    new Object();",
             "static void inc() {",
             "  for (int i = 0; i < 10000; i++)",
             "    synchronized (lock) {",
             "      count++;",
             "    }",
             "}"]

def block_scene():
    block = jmulti("block", [], "20000\n", hidden=threads() + ["System.out.println(count);"],
                   members=BLOCK_INC, show_members=True, mark=(1, 2, 5, 6, 7), sm=True, **ALWAYS)
    return (head("STEP 2 · 동기화 블록", "필요한 줄만", "<b>synchronized (잠금 객체)</b> { 이 줄만 }")
            + block
            + '<div class="duo in">' + term(cls="term ok")
            + '<div class="note"><b>같은</b> 잠금 객체<br/><small>두 스레드가 함께 쓰는\nstatic 필드</small></div></div>'
            + '<div class="note in">잠그는 범위는 <b>필요한 만큼만</b></div>')

ATOMIC_INC = ["static AtomicInteger count =",
              "    new AtomicInteger();",
              "static void inc() {",
              "  for (int i = 0; i < 10000; i++)",
              "    count.incrementAndGet();",
              "}"]

def atomic_scene():
    J.IMPORTS = ["import java.util.concurrent.atomic.*;", ""]
    block = jmulti("atomic", ["// main에서: a·b start·join 뒤", "System.out.println(count.get());"], "20000\n",
                   pre=threads(), members=ATOMIC_INC, show_members=True, mark=(0, 1, 4, 7), sm=True, **ALWAYS)
    J.IMPORTS = []
    return (head("STEP 3 · AtomicInteger", "한 번에 끝내기", "<b>incrementAndGet()</b> · 값은 <b>get()</b>")
            + lab("<code>import java.util.concurrent.atomic.*;</code>")
            + block
            + '<div class="duo in">' + term(cls="term ok")
            + '<div class="note steps">읽기→더하기→쓰기\n<b>한 번에</b>\n'
              "<small>원자적 연산\n(쪼개지지 않는)</small></div></div>"
            + '<div class="chips in"><span><code>synchronized</code> 없이</span><span>끼어들기 불가</span></div>')

def list_members(sync):
    """Main's members: the shared list (plain ArrayList, or wrapped by synchronizedList) and add()."""
    decl = (["static List<Integer> list =", "    Collections.synchronizedList(", "        new ArrayList<>());"]
            if sync else ["static List<Integer> list =", "    new ArrayList<>();"])
    return decl + ["static void add() {", "  for (int i = 0; i < 10000; i++)", "    list.add(i);", "}"]

SIZE = threads("add") + ["System.out.println(list.size());"]

def list_scene():
    J.IMPORTS = ["import java.util.*;", ""]  # shown above the code as a label, like atomic
    # Some runs end a worker thread with ArrayIndexOutOfBoundsException; the program still exits 0 and
    # prints the size, so jmulti checks only that printed size.
    block = jmulti("list", [], "14302\n", hidden=SIZE, members=list_members(False), show_members=True,
                   each=lambda o: int(o) <= 20000, all_=lambda outs: any(int(o) < 20000 for o in outs),
                   label="실행 결과 예시 · 매번 다름", mark=(1,), sm=True)
    bad = term(cls="term bad")
    jmulti("list-sync", [], "20000\n", hidden=SIZE, members=list_members(True), **ALWAYS)
    J.IMPORTS = []
    return (head("STEP 4 · 스레드 안전 리스트", "ArrayList도?", "두 스레드가 만 번씩 <b>add</b>")
            + lab("<code>import java.util.*;</code>")
            + block
            + '<div class="duo in">' + bad
            + '<div class="warn">값이 빠지거나<br/><small>예외가 나기도</small></div></div>'
            + code(list_members(True)[:3], mark=(1, 2), sm=True)
            + '<div class="duo in">' + term(cls="term ok")
            + '<div class="note"><b>스레드 안전</b><br/><small>여러 스레드가 함께 써도\n올바른 결과</small></div></div>')

def todo(step, title):
    return head(step, title, "(준비 중)")

scenes = {
 "hook": hook_scene(),
 "scope": scope_scene(),
 "block": block_scene(),
 "atomic": atomic_scene(),
 "list": list_scene(),
 "outro": '<div class="pill in">정리</div><h2 class="title in">동기화 더 깊이</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"scope": 1, "block": 2, "atomic": 3, "list": 4}

CSS = """
.hook { gap: 44px; }
.hook .vs .card span { font-family: var(--font); font-size: 40px; line-height: 1.3; color: var(--ink); }
.hook .vs .card.on span { color: var(--orange); }
.duo { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
.term.ok { border-color: rgba(126,224,138,.5); }
.term.bad { border-color: rgba(255,93,93,.5); }
.term.ok div, .term.bad div { font-size: 64px; font-weight: 800; }
.term.ok div { color: var(--green); } .term.bad div { color: var(--red); }
.duo .warn, .duo .note { font-size: 40px; padding: 22px 30px; }
.duo small { font-size: 34px; font-family: var(--font); }
.tline { display: flex; flex-direction: column; gap: 14px; }
.tline > i { align-self: flex-end; font-style: normal; font-size: 30px; font-weight: 700; color: var(--mute); }
.tr { display: grid; grid-template-columns: 150px 1fr; align-items: center; gap: 18px; }
.tr span { font-size: 32px; font-weight: 700; color: var(--mute); }
.trk { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; height: 76px; }
.trk b { border-radius: 14px; display: flex; align-items: center; justify-content: center;
  font-size: 32px; font-weight: 800; color: var(--ground); }
.trk .b1 { grid-column: 1; background: var(--orange); }
.trk .b2 { grid-column: 2; background: var(--green); }
.trk .wt { grid-column: 1; border: 3px dashed #26324a; color: var(--mute); }
.note.steps { font-size: 38px; padding: 20px 28px; white-space: pre-line; }
.note.steps small { font-size: 32px; font-family: var(--font); }
.note small { font-family: var(--font); }
.tlabel code { font-size: 32px; }
#sc-list { gap: 20px; }
#sc-list .term div { font-size: 54px; }
#sc-list .duo .warn, #sc-list .duo .note { padding: 16px 28px; font-size: 38px; }
#sc-list .duo small { font-size: 32px; }
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
    <div class="pill">JAVA 입문 · 23편</div>
    <h1 class="big">동기화<br/><em>더 깊이</em></h1>
    <p class="sub">지난 편 <b>synchronized</b>의 문제</p>
    <div class="chips"><span>synchronized 블록</span><span>AtomicInteger</span><span>synchronizedList</span></div>
  </div>
</div></body></html>
''')
