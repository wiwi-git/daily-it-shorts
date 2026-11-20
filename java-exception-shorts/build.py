"""Builds assets/narration.mp3, index.html and examples.txt from vo.json (run gen_vo.py first).
Shared steps and helpers live in ../tools/javashorts.py; this file holds only this video's scenes."""
import os, sys, html
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import javashorts as J
J.load(speed=1.2)
from javashorts import *

EXEC = ["try-catch 로 잡으면 계속 실행", "catch 는 구체적인 예외부터", "finally 는 항상 실행",
        "throw 던지기 · throws 넘기기", "체크 예외는 처리 필수", "커스텀: extends Exception\n강제 안 하면 RuntimeException"]
EXEC_SAID = ["트라이", "캐치는", "파이널리는", "쓰로우는", "체크", "커스텀"]
EXEC_END = "구독과"

# --- example data: 민수 (k1) · 서준 (k2) · 지우 (k3); scores 85 (k1) · 92 (k2) · 78 (k3); wrong score 120 ---
BRAND = "자바 입문 <em>예외</em> 정리"
K = {"민수": "k1", "서준": "k2", "지우": "k3", "85": "k1", "92": "k2", "78": "k3"}

DIV = ["int a = 10 / 0;", "System.out.println(a);"]  # hook stops here; trycatch puts it in try
END = ['System.out.println("끝");']

def hook_scene():
    return ('<div class="hook">'
            '<div class="pill in">JAVA 입문 · 스무 번째</div>'
            '<h1 class="big in"><em>예외</em></h1>'
            + jrt("hook", DIV + END, "java.lang.ArithmeticException: / by zero", before="", mark=(0,))
            + rterm()
            + '<div class="chips in"><span>실행 중 오류 = <em>예외</em></span></div>'
            + "</div>")

def trycatch_scene():
    lines = ["try {"] + ["  " + l for l in DIV] + ["} catch (ArithmeticException e) {", "  System.out.println(",
                                                    '      "0으로 나눌 수 없어요");', "}"] + END
    return (head("STEP 1 · try-catch", "예외 잡기", "<b>catch</b>로 잡으면 끝까지 실행")
            + jcode("trycatch", lines, "0으로 나눌 수 없어요\n끝\n", mark=(1, 3))
            + term(label="실행 결과")
            + '<div class="note in"><code>catch (ArithmeticException e)</code><br/><small>괄호 안 타입 = 잡을 예외\n'
            '예외가 난 줄 아래는 건너뜀</small></div>')

SCORES = ["int[] scores = {85, 92, 78};"]
MSG = ["  System.out.println(", "    e.getMessage());", "}"]

def kinds_scene():
    lines = (["try {", '  Integer.parseInt("abc");', "} catch (", "  NumberFormatException e) {"] + MSG
             + ["try {", "  int n = scores[3];", "} catch (", "  ArrayIndexOutOfBoundsException", "    e) {"] + MSG)
    return (head("STEP 2 · 여러 catch", "예외 종류별로 잡기", "종류마다 <b>catch</b> · <code>scores = {85, 92, 78}</code>")
            + jcode("kinds", lines, 'For input string: "abc"\nIndex 3 out of bounds for length 3\n',
                    mark=(1, 3, 8, 10), pre=SCORES, sm=True)
            + term(label="실행 결과 · e.getMessage()"))

def order_scene():
    lines = (["try {", "  " + DIV[0], "} catch (Exception e) {", '  System.out.println("예외");',
              "} catch (ArithmeticException e) {", '  System.out.println("0 나누기");', "}"])
    return (head("STEP 2 · catch 순서", "catch 순서 함정", "<b>Exception</b>을 위에 쓰면 컴파일 오류")
            + jce("order", lines, "exception ArithmeticException has already been caught", mark=(2, 4))
            + cterm()
            + '<div class="warn in"><b>Exception</b> = 예외 클래스들의 부모<br/><small>구체적인 예외부터 위에</small></div>')

FIN = ["try {", "  int n = Integer.parseInt(s);", "  System.out.println(n);",
       "} catch (", "  NumberFormatException e) {", '  System.out.println("숫자 아님");',
       "} finally {", '  System.out.println("끝");', "}"]

def finally_scene():
    """The same try-catch-finally run twice: "85" converts, "abc" throws; both print 끝 last."""
    shown = jcode("finally", FIN, "85\n끝\n", mark=(6, 7), pre=['String s = "85";'])
    ok = term(label='s = "85"', cls="term")
    jcode("finally", FIN, "숫자 아님\n끝\n", pre=['String s = "abc";'])
    ng = term(label='s = "abc"', cls="term")
    return (head("STEP 3 · finally", "항상 실행", "예외가 나든 안 나든 <b>finally</b>")
            + shown + f'<div class="duo in">{ok}{ng}</div>'
            + '<div class="note in">두 번 모두 마지막에 <b>끝</b></div>')

# STEP 4: one checkScore grows across the scenes (static method inside Main, via `members=`)
DECL = "static void checkScore(int s)"  # first line identical in throw · throws · custom
RANGE = "  if (s < 0 || s > 100)"
SCORE_MSG = '        "점수 오류: " + s);'
CHECK_THROW = [DECL + " {", RANGE,
               "    throw new", "      IllegalArgumentException(", SCORE_MSG, "}"]
def check_ex(decl, ex="Exception"):  # throws/custom: the same method throwing `ex`, `decl` = its declaration lines
    return decl + [RANGE, f"    throw new {ex}(", SCORE_MSG, "}"]
CALL = lambda catch: ["try {", "  checkScore(120);", "} catch (", f"  {catch} e) {{",
                      "  System.out.println(", "      e.getMessage());", "}"]

def throw_scene():
    return (head("STEP 4 · throw", "예외 던지기", "<b>throw</b>로 직접 던지기")
            + jcode("throw", [""] + CALL("IllegalArgumentException"), "점수 오류: 120\n", members=CHECK_THROW,
                    show_members=True, mark=(2, 3, 8), sm=True)
            + '<div class="duo in">' + term(label="실행 결과", cls="term")
            + '<div class="note"><code>throw<span class="s">s</span></code> 없이도<br/>컴파일 OK</div></div>')

def throws_scene():
    vs = ('<div class="vs in">'
          '<div class="card on"><b>체크 예외</b><small>(처리 강제)</small><span>IOException</span></div>'
          '<div class="card"><b>언체크 예외</b><small>(처리 선택)</small><span>ArithmeticException</span></div></div>')
    jce("throws", CALL("Exception"), "unreported exception Exception; must be caught or declared to be thrown", members=check_ex([DECL + " {"]))
    return (head("STEP 4 · throw<em>s</em>", "처리 넘기기 throw<em>s</em>", "<b>try-catch</b>로 잡거나 <b>throw<span class=\"s\">s</span></b>로 넘기기")
            + cterm().replace("<i>컴파일 오류</i>", "<i>Exception을 던지면 · throws 없음 → 컴파일 오류</i>")
            + jcode("throws", [], "점수 오류: 120\n", hidden=CALL("Exception"), members=check_ex([DECL, "    throws Exception {"]),
                    show_members=True, mark=(1, 3), sm=True)
            + term(label='부르는 쪽 <code>catch (Exception e)</code> → 실행 결과')
            + vs)

# STEP 5: checkScore now throws a class of its own; ScoreException sits above class Main (`top=`)
SCORE_EX = ["class ScoreException", "    extends Exception {", "  ScoreException(", "      String message) {",
            "    super(message);", "  }", "}"]
CUSTOM_CALL = ["try {", "  checkScore(120);", "} catch (ScoreException e) {", "  System.out.println(",
               "      e.getMessage());", "}"]

def custom_scene():
    """Class, method and call on one screen: the whole program is compiled and run as one, then drawn as
    two blocks (class + method, then the call beside its result) so it fits above the captions.
    super(message) and e.getMessage() are marked on both ends."""
    method = check_ex([DECL, "    throws ScoreException {"], "ScoreException")
    jcode("custom", CUSTOM_CALL, "점수 오류: 120\n", top=SCORE_EX, members=method)
    gap = lambda h: h.replace('<div class="ln">&nbsp;</div>', '<div class="ln gap"></div>')
    return (head("STEP 5 · 커스텀 예외", "예외 클래스 만들기", "<b>커스텀 예외</b> (직접 만든 예외 클래스)")
            + gap(code(SCORE_EX + [""] + method, mark=(1, 4, 11), sm=True))
            + '<div class="pair">' + code(CUSTOM_CALL, mark=(2, 4), sm=True)
            + '<div class="side in">' + term(label="실행 결과", cls="term")
            + '<div class="note"><code>super(message)</code><br/>→ <code>getMessage()</code></div></div></div>')

scenes = {
 "hook": hook_scene(),
 "trycatch": trycatch_scene(),
 "kinds": kinds_scene(),
 "order": order_scene(),
 "finally": finally_scene(),
 "throw": throw_scene(),
 "throws": throws_scene(),
 "custom": custom_scene(),
 "outro": '<div class="pill in">정리</div><h2 class="title in">예외</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"trycatch": 1, "kinds": 2, "order": 2, "finally": 3, "throw": 4, "throws": 4, "custom": 5}

CSS = """
.tlabel small { font-size: 30px; }
.hook { gap: 44px; }
.hook .chips span { font-size: 52px; }
.chips code { color: var(--blue); }
.note code { font-size: 40px; }
.s, .kw .s { color: var(--orange); font-weight: 800; }
.pill em, .title em { font-style: normal; color: var(--orange); }
.term i code { font-size: 28px; }
#sc-throws .vs .card small { font-size: 34px; color: var(--ink); }
#sc-throws .vs .card span { font-size: 32px; }
#sc-throws .vs .card b { font-family: var(--font); font-weight: 800; }
#sc-custom .code.sm { font-size: 30px; padding: 22px 26px; }
#sc-custom .code .ln.gap { height: 16px; }
#sc-custom .pair { display: flex; gap: 22px; align-items: stretch; }
#sc-custom .side { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 22px; }
#sc-custom .side .term { font-size: 32px; }
#sc-custom .side .note code { font-size: 28px; }
.duo { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
.duo .term { font-size: 40px; }
.note b { color: var(--orange); }
"""

J.build(scenes, PROG, BRAND, CSS, outro=(EXEC, EXEC_SAID, EXEC_END))
