"""Builds assets/narration.mp3, index.html and examples.txt from vo.json (run gen_vo.py first).
Shared steps and helpers live in ../tools/javashorts.py; this file holds only this video's scenes."""
import os, sys, html
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import javashorts as J
J.load(speed=1.2)
from javashorts import *
# Each example runs in its own temp folder; scores.txt left there is checked (`file=`) and drawn (fterm).
# File code must handle IOException (a checked exception), so by default main declares it; the scenes
# say so on screen.
J.FILE = "scores.txt"
J.IMPORTS = ["import java.io.*;", "import java.nio.file.*;", "import java.util.*;", ""]
J.MAIN_THROWS = "IOException"

EXEC = ["BufferedWriter · newLine()", "try-with-resources 자동 닫기", "true 이어쓰기 · 없으면 덮어쓰기",
        "readLine() 끝이면 null", "IOException 처리 필수", "짧게: Files"]
EXEC_SAID = ["버퍼드", "트라이", "트루를", "리드", "파일", "짧게"]
EXEC_END = "구독과"

# --- example data: scores.txt, one `이름,점수` per line: 민수,85 (k1) · 서준,92 (k2) · 지우,78 (k3); wrong name score.txt ---
BRAND = "자바 입문 <em>파일</em> 읽기·쓰기 정리"
J.K = K = {"민수": "k1", "서준": "k2", "지우": "k3", "85": "k1", "92": "k2", "78": "k3"}

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

APPEND = open_writer("true") + put("지우,78") + ["}"]  # STEP 1-1; read/sum reuse it as `pre=`
THREE = "민수,85\n서준,92\n지우,78\n"

def append_scene():
    block = jcode("append", APPEND, "", mark=(3,), sm=True, pre=WRITE, file=THREE)
    ok = fterm(label="scores.txt · true", cls="term file")
    jok("append-trap", open_writer() + put("지우,78") + ["}"], pre=WRITE, file="지우,78\n")
    bad = fterm(label="scores.txt · true 없음", cls="term file bad")
    return (head("STEP 1-1 · 이어쓰기", "뒤에 덧붙이기", "<b>FileWriter</b>에 <b>true</b> → 이어쓰기")
            + block
            + '<div class="duo in">' + ok + bad + "</div>"
            + '<div class="warn in">함정! <code>true</code>를 빼면 <b>덮어쓰기</b><br/>'
              "<small>기존 두 줄이 지워지고 지우만 남음 · 덮어쓰기가 기본</small></div>")

def reader(name="scores.txt"):
    return ["try (BufferedReader r =", "  new BufferedReader(", "    new FileReader(", f'      "{name}"))) {{']

LOOP = ["  String line;", "  while ((line = r.readLine())", "         != null) {"]
READ = reader() + LOOP + ["    System.out.println(line);", "  }", "}"]

def read_scene():
    block = jcode("read", READ, THREE, mark=(5, 6), sm=True, pre=WRITE + APPEND, file=THREE)
    return (head("STEP 2 · 읽기", "한 줄씩 읽기", "<b>readLine()</b> · 끝이면 <b>null</b>")
            + block
            + '<div class="duo in">' + fterm(cls="term file") + term(cls="term") + "</div>")

SUM = (["int sum = 0;"] + reader() + LOOP
       + ['    String[] p = line.split(",");', "    sum += Integer.parseInt(", "      p[1]);", "  }", "}",
          "System.out.println(sum);"])

def sum_scene():
    block = jcode("sum", SUM, "255\n", mark=(8, 9, 10), sm=True, pre=WRITE + APPEND, file=THREE)
    return (head("STEP 3 · 읽어서 계산", "합계 구하기", "<b>split</b>으로 나누고 <b>parseInt</b>로 숫자로")
            + block
            + '<div class="duo in"><div class="note split"><code>"민수,85"</code><br/><small>.split(",")</small><br/><small>→ [민수, 85]</small></div>'
            + term(cls="term") + "</div>")

EXCEPT = reader("score.txt") + ["  System.out.println(", "    r.readLine());", "} catch (IOException e) {",
                                "  System.out.println(e);", "}"]

def except_scene():
    block = jcode("except", EXCEPT, "java.io.FileNotFoundException: score.txt (No such file or directory)\n",
                  mark=(3, 6), sm=True)
    out = term(cls="term wrap")
    J.MAIN_THROWS = ""  # without try-catch or throws, file code does not even compile
    jce("except-unhandled", reader() + ["  System.out.println(", "    r.readLine());", "}"],
        "unreported exception FileNotFoundException")
    J.MAIN_THROWS = "IOException"
    return (head("STEP 4 · 파일 예외", "없는 파일 읽기", "<b>IOException</b>으로 잡기")
            + block + out
            + '<div class="warn in">IOException = <b>체크 예외</b> (처리 강제)<br/>'
              "<small>try-catch 또는 throws 없으면 → 컴파일 오류</small></div>")

FILES = ['Path p = Path.of("scores.txt");', "Files.writeString(p,", '  "민수,85\\n서준,92\\n지우,78\\n");',
         "System.out.println(", "  Files.readAllLines(p));"]

def files_scene():
    LAST["out"], _ = check("files", wrap(FILES), "[민수,85, 서준,92, 지우,78]\n", file=THREE)
    shown_ = (["public static void main(", "    String[] args)", "    throws IOException {"]
              + ["  " + l for l in FILES] + ["}"])
    return (head("STEP 5 · 짧게 쓰기", "Files 한 줄", "<b>writeString</b>으로 쓰고 <b>readAllLines</b>로 읽기")
            + code(shown_, mark=(2, 5, 8), sm=True)
            + '<div class="duo in">' + fterm(cls="term file")
            + '<div class="note">readAllLines<br/><small>→ 모든 줄을 List로</small></div></div>'
            + term())

scenes = {
 "hook": hook_scene(),
 "write": write_scene(),
 "append": append_scene(),
 "read": read_scene(),
 "sum": sum_scene(),
 "except": except_scene(),
 "files": files_scene(),
 "outro": '<div class="pill in">정리</div><h2 class="title in">파일 읽기·쓰기</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{html.escape(c)}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="note in">한글이 깨지면 → <b>UTF-8</b> 확인</div><div class="cta in">👍 구독 · 좋아요</div>',
}
PROG = {"write": 1, "append": 1, "read": 2, "sum": 3, "except": 4, "files": 5}

CSS = """
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
.term.file.bad { border-color: rgba(255,93,93,.5); }
.term.wrap { white-space: normal; font-size: 34px; word-break: break-all; }
.warn code { font-size: 40px; }
.note.split small { white-space: nowrap; }
"""

J.build(scenes, PROG, BRAND, CSS, outro=(EXEC, EXEC_SAID, EXEC_END),
        examples_header=["각 예제를 빈 폴더에 파일 이름대로 저장한 뒤: javac -g -encoding UTF-8 Main.java && java Main", "(scores.txt는 실행한 폴더에 생긴다. 앞 장면의 파일 상태는 각 예제 안에서 먼저 만든다)"])
