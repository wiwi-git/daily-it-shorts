"""Builds assets/narration.mp3, index.html and queries.sql from vo.json (run gen_vo.py first,
and ../tools/mysql-sandbox.sh start so the example queries can run)."""
import json, re, subprocess, html

LEAD, GAP, TAIL = 0.3, 0.45, 1.2
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

# --- SQL highlighting ---
KW = ("SELECT FROM WHERE ORDER BY DESC ASC JOIN INNER LEFT ON GROUP HAVING COUNT SUM AVG AS AND OR IN LIKE "
      "LIMIT IS NULL BETWEEN NOT CREATE TABLE ALTER ADD COLUMN MODIFY RENAME TO DROP TRUNCATE INDEX PRIMARY KEY "
      "INT VARCHAR DEFAULT START TRANSACTION COMMIT ROLLBACK SAVEPOINT UPDATE SET DELETE INSERT INTO VALUES "
      "USER IDENTIFIED GRANT REVOKE SHOW GRANTS TABLES USAGE").split()
def hl(line):
    out = html.escape(line)
    out = re.sub(r"(--.*)$", r'<span class="cm">\1</span>', out)
    out = re.sub(r"(&#x27;[^&]*&#x27;)", r'<span class="st">\1</span>', out)
    out = re.sub(r"\b(" + "|".join(KW) + r")\b", r'<span class="kw">\1</span>', out)
    out = re.sub(r"(?<![\w>])(\d+)\b", r'<span class="nu">\1</span>', out)
    return out

def code(lines, mark=()):
    """`mark`: indexes of lines to tint as the point of the scene."""
    return '<div class="code in">' + "".join(
        f'<div class="ln{" mk" if i in mark else ""}">{hl(l) or "&nbsp;"}</div>' for i, l in enumerate(lines)) + "</div>"

def head(step, title, desc):
    return f'<div class="pill in">{step}</div><h2 class="title in">{title}</h2><p class="desc in">{desc}</p>'

def table(cols, rows, label="", cls=""):
    """rows: (row_class, values); a None value renders as a highlighted NULL."""
    th = "".join(f"<th>{c}</th>" for c in cols)
    tr = "".join(f'<tr class="{rc}">' + "".join(
        '<td class="nl">NULL</td>' if v is None else f"<td>{v}</td>" for v in vals) + "</tr>" for rc, vals in rows)
    lab = f'<div class="tlabel">{label}</div>' if label else ""
    return f'<div class="tbl in {cls}">{lab}<table><tr>{th}</tr>{tr}</table></div>'

# Same two accounts in every example: kim=k1 (sender), lee=k2 (receiver).
WHO = {"kim": "k1", "lee": "k2"}
ACCOUNTS = {"root": "sandbox"}

# --- example queries: every query on screen runs on a throwaway MySQL (../tools/mysql-sandbox.sh)
# before anything is drawn. Each must give what the narration says (`expect`), result tables are
# drawn from what it actually returned (got()), and all of them are saved to queries.sql.
SANDBOX = ["docker", "exec", "-i", "shorts-mysql", "mysql", "--batch", "--skip-column-names"]
QUERIES, LAST = [], []

def mysql(sql, user="root", db="shop"):
    """Run `sql` in the sandbox as `user`: (rows, error) where error is "" or "ERROR nnnn: message"."""
    cmd = SANDBOX + [f"-u{user}", f"-p{ACCOUNTS[user]}"] + ([db] if db else [])
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    if "No such container" in r.stderr or "is not running" in r.stderr:
        raise SystemExit("MySQL 샌드박스가 꺼져 있음 → ../tools/mysql-sandbox.sh start")
    err = next((re.sub(r" \(\w+\) at line \d+", "", l) for l in r.stderr.splitlines() if l.startswith("ERROR")), "")
    return [tuple(l.split("\t")) for l in r.stdout.splitlines()], err

def setup(sid, sql):
    """Reset the sandbox to the state a scene starts from (run as root, also written to queries.sql)."""
    rows, err = mysql(sql, db=None)
    if err:
        raise ValueError(f"{sid} setup: {err}")
    QUERIES.append((sid, "root", sql, None))

def qsql(sid, lines, expect, check="", user="root", mark=(), pre=""):
    """Code block run as `user`, then the unseen `check` query in the same session. Its rows — or the
    ERROR the code raised — must equal `expect` (a list of row tuples, or an "ERROR nnnn" prefix).
    `pre` is run first in the same session, for a block that continues the previous one."""
    shown = "\n".join(lines)
    rows, err = mysql(pre + shown + ("\n" + check if check else ""), user)
    out = err or rows
    ok = out.startswith(expect) if isinstance(expect, str) else (not err and rows == [tuple(map(str, r)) for r in expect])
    if not ok:
        raise ValueError(f"{sid}: {shown!r} gave {out!r}, but the script expects {expect!r}")
    QUERIES.append((sid, user, shown + ("\n" + check if check else ""), out))
    LAST[:] = [out] if err else rows
    return code(lines, mark)

def got():
    """Rows (or the error) the last qsql() produced."""
    return list(LAST)

def write_queries(title):
    section = {s["id"]: s["section"] for s in json.load(open("script.json"))}
    with open("queries.sql", "w") as f:
        f.write(f"-- {title} · 영상에 나오는 예제 쿼리 (build.py가 생성 · 직접 고치지 말 것)\n"
                "-- MySQL에서 위에서부터 차례로 실행. '계정:' 표시가 있는 블록은 그 계정으로 접속해서 실행\n"
                "-- 검증 환경: MySQL %s · 기본 엔진 %s · 격리 수준 %s · autocommit=%s (../tools/mysql-sandbox.sh)\n"
                % mysql("SELECT VERSION(), @@default_storage_engine, @@transaction_isolation, @@autocommit;", db=None)[0][0])
        for sid, user, sql, out in QUERIES:
            who = "" if user == "root" else f" ({user})" if user.startswith(("세션", "앞 블록")) else f" (계정: {user})"
            if out is None:
                f.write(f"\n-- [{section[sid]}]{who or ' 준비'}\n{sql}\n")
            else:
                res = out if isinstance(out, str) else " / ".join(", ".join(r) for r in out) or "결과 없음"
                f.write(f"\n-- [{section[sid]}]{who} → {res}\n{sql}\n")

def lab(text):
    return f'<div class="tlabel in">{text}</div>'

def line(label, items):
    """One-line result: (text, class) chips after a muted label; class k1/k2/k3/ok/bad."""
    return f'<div class="res in"><i>{label}</i>' + "".join(f'<span class="{c}">{t}</span>' for t, c in items) + "</div>"

BASE = ("DROP DATABASE IF EXISTS shop;\nCREATE DATABASE shop;\nUSE shop;\n"
        "CREATE TABLE accounts (id INT PRIMARY KEY, name VARCHAR(20), balance INT) ENGINE=InnoDB;\n"
        "INSERT INTO accounts VALUES (1, 'kim', 50000), (2, 'lee', 10000);")
BAL = "SELECT name, balance FROM accounts ORDER BY id;"
KIM_OUT = ["UPDATE accounts", "  SET balance = balance - 10000", "  WHERE name = 'kim';"]
LEE_IN = ["UPDATE accounts", "  SET balance = balance + 10000", "  WHERE name = 'lee';"]

def balances(label, warn=False):
    return table(["name", "balance"], [(WHO[n], (n, b)) for n, b in got()], label)

def two_sessions(sid, a_lines, a_expect, b_lines, expect):
    """Session A runs `a_lines` and must read `a_expect` itself; only then does session B run `b_lines`
    (checked against `expect`) while A's transaction is still open. A is rolled back afterwards."""
    a = subprocess.Popen(SANDBOX + ["--unbuffered", "-uroot", f"-p{ACCOUNTS['root']}", "shop"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        a.stdin.write("\n".join(a_lines) + "\n" + A_CHECK + "\n"); a.stdin.flush()
        seen = a.stdout.readline().strip()  # blocks until A has run its UPDATE and read the value back
        if seen != str(a_expect):
            raise ValueError(f"{sid}: session A read {seen!r}, expected {a_expect!r}")
        out = qsql(sid, b_lines, expect, mark=(0, 1))
        a.stdin.write("ROLLBACK;\n"); a.stdin.close()
        err = a.stderr.read()
        if a.wait(timeout=10) or "ERROR" in err:
            raise ValueError(f"{sid}: session A failed: {err.strip()}")
    finally:
        if a.poll() is None:
            a.kill()
    b = QUERIES.pop()
    QUERIES.extend([(sid, "세션 A · 창 1", "\n".join(a_lines) + "\n" + A_CHECK, [(str(a_expect),)]),
                    (sid, "세션 B · 창 2, A를 커밋하기 전에", b[2], b[3]),
                    (sid, "세션 A · 창 1", "ROLLBACK;", None)])
    return out

A_CHECK = "SELECT balance FROM accounts WHERE name = 'kim';"

EXEC = ["START TRANSACTION", "COMMIT · 확정", "ROLLBACK · 취소", "autocommit = 1", "SAVEPOINT", "DDL → 자동 커밋"]
EXEC_SAID = ["스타트", "커밋으로", "롤백", "오토", "세이브", "DDL"]
EXEC_END = "이것만"

scenes = {
 "hook": '''<div class="hook">
   <div class="pill in">MySQL · 트랜잭션 핵심 정리</div>
   <h1 class="big in"><em>COMMIT</em><br/>ROLLBACK</h1>
   <div class="sub in">전부 성공 or <b>전부 취소</b></div>
 </div>''',
}
setup("intro", BASE)
scenes["intro"] = (head("SQL 4위 · TCL", "이체 중 멈추면?", "kim → lee <b>10000원</b> 송금")
    + qsql("intro", KIM_OUT + ["-- 여기서 멈추면?"], [("kim", 40000), ("lee", 10000)], check=BAL, mark=(3,))
    + balances("")
    + f'<div class="warn in">⚠ 합계 60000 → <b>{sum(int(b) for _, b in got())}</b> · 1만 원 증발</div>')
scenes["concept"] = (head("STEP 1 · 트랜잭션", "트랜잭션", "여러 작업을 <b>하나로</b> 묶기")
    + '<div class="vs"><div class="card in"><b>COMMIT</b><span>전부 반영</span><span class="ok">출금 ✓ 입금 ✓</span></div>'
      '<div class="card in"><b>ROLLBACK</b><span>전부 취소</span><span class="ng">출금 ✗ 입금 ✗</span></div></div>'
    + '<div class="note in">원자성 (Atomicity)<br/><small>전부 되거나, 전부 안 되거나</small></div>'
    + '<div class="warn in">⚠ 오류가 나도 <b>자동으로</b> 전부 취소 ✗<br/><small>ROLLBACK을 직접 실행</small></div>')
setup("commit", BASE)
scenes["commit"] = (head("STEP 1-1", "COMMIT", "커밋하는 순간 <b>한꺼번에 확정</b>")
    + qsql("commit", ["START TRANSACTION;", *KIM_OUT, *LEE_IN, "COMMIT;"], [("kim", 40000), ("lee", 20000)],
           check=BAL, mark=(0, 7))
    + balances("결과 · 합계 60000 그대로"))
setup("rollback", BASE)
scenes["rollback"] = (head("STEP 2 · ROLLBACK", "ROLLBACK", "시작 전 상태로 <b>되돌리기</b>")
    + qsql("rollback", ["START TRANSACTION;", *KIM_OUT, "-- 문제 발생!", "ROLLBACK;"], [("kim", 50000), ("lee", 10000)],
           check=BAL, mark=(4, 5))
    + balances("결과 · 출금 취소 → 처음 그대로"))
setup("isolation", BASE)
scenes["isolation"] = (head("STEP 3 · 격리", "커밋 전 변경", "다른 세션엔 <b>보이지 않음</b>")
    + lab("세션 A · 아직 커밋 전")
    + code(["START TRANSACTION;", *KIM_OUT])
    + lab("세션 B · 동시에 조회")
    + two_sessions("isolation", ["START TRANSACTION;", *KIM_OUT], 40000,
                   ["SELECT balance FROM accounts", "  WHERE name = 'kim';"], [(50000,)])
    + line("B가 보는 값 →", [(f"{got()[0][0]} (변경 전)", "k1")]))
qsql("isolation", ["SELECT @@transaction_isolation;"], [("REPEATABLE-READ",)])
scenes["isolation"] += f'<div class="note in">MySQL 기본 격리 수준<br/><small>{got()[0][0].replace("-", " ")}</small></div>'
setup("autocommit", BASE)
scenes["autocommit"] = (head("STEP 4 · 주의", "autocommit", "기본은 <b>문장마다 바로 확정</b>")
    + qsql("autocommit", ["SELECT @@autocommit;"], [(1,)], mark=(0,))
    + line("결과 →", [(f"{got()[0][0]} (켜짐)", "bad")])
    + qsql("autocommit", [*KIM_OUT, "ROLLBACK;"], [("kim", 40000), ("lee", 10000)], check=BAL, mark=(3,))
    + balances("ROLLBACK 했지만 이미 반영 ⚠"))
setup("savepoint", BASE)
SAVEPOINT = ["START TRANSACTION;", *KIM_OUT, "SAVEPOINT sent;", "UPDATE accounts",
             "  SET balance = balance + 100000", "  WHERE name = 'lee';", "ROLLBACK TO sent;"]
scenes["savepoint"] = (head("STEP 5 · SAVEPOINT", "SAVEPOINT", "<b>일부만</b> 되돌리기")
    + qsql("savepoint", SAVEPOINT, [("kim", 40000), ("lee", 10000)], check=BAL, mark=(4, 8))
    + balances("ROLLBACK TO 직후 · 아직 커밋 전"))
# ROLLBACK TO keeps the transaction open, so the transfer is finished in the same session
scenes["finish"] = (head("STEP 5-1 · 마무리", "끝은 COMMIT", "ROLLBACK TO는 트랜잭션을 <b>끝내지 않음</b>")
    + lab("이어서 · 리에게 제대로 입금")
    + qsql("finish", [*LEE_IN, "COMMIT;"], [("kim", 40000), ("lee", 20000)], check=BAL, mark=(3,),
           pre="\n".join(SAVEPOINT) + "\n")
    + balances("COMMIT 후 · 합계 60000 그대로"))
QUERIES[-1] = ("finish", "앞 블록에 이어서 같은 세션", *QUERIES[-1][2:])
setup("caution", BASE)
scenes["caution"] = (head("STEP 5-2 · 주의", "DDL은 자동 커밋", "트랜잭션 도중이라도 <b>확정</b>")
    + qsql("caution", ["START TRANSACTION;", *KIM_OUT, "ALTER TABLE accounts", "  ADD COLUMN memo VARCHAR(20);", "ROLLBACK;"],
           [("kim", 40000), ("lee", 10000)], check=BAL, mark=(4, 5))
    + balances("ROLLBACK 했지만 출금은 확정 ⚠")
    + '<div class="warn in">⚠ 길게 열면 다른 작업이 <b>대기</b></div>')
scenes["outro"] = ('<div class="pill in">정리</div><h2 class="title in">트랜잭션 핵심 6가지</h2><div class="list in">'
    + "".join(f'<div class="row" id="ex{i}"><span class="no">{i}</span><b>{c}</b></div>' for i, c in enumerate(EXEC, 1))
    + '</div><div class="cta in">👍 구독 · 좋아요</div>')
write_queries("TCL: START TRANSACTION · COMMIT · ROLLBACK · SAVEPOINT")

PROG = {"concept": 1, "commit": 1, "rollback": 2, "isolation": 3, "autocommit": 4, "savepoint": 5, "finish": 5, "caution": 5}
BRAND = "MySQL <em>트랜잭션</em> 정리"

def bad_cut(x, i):
    """True if a caption break at space `i` would split an amount or orphan a dependent word."""
    prev, nxt = x[:i].split()[-1], x[i + 1:].split()[0]
    return bool(re.search(r"\d[천만백]?$|^[A-Z]+$", prev)) or nxt.startswith(("원", "이상", "이하", "미만", "않", "있어도"))

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
    vis_start = 0 if s is vo[0] else st - 0.15
    vis_end = TOTAL if s is vo[-1] else vo[vo.index(s) + 1]["start"] - 0.15
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
.code .ln {{ margin: 0 -14px; padding: 0 14px; border-radius: 10px; }}
.code .ln.mk {{ background: rgba(242,145,17,.13); }}
.kw {{ color: var(--blue); font-weight: 700; }} .st {{ color: var(--green); }} .nu {{ color: var(--orange); }} .cm {{ color: #6f7d98; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 18px; }}
.chips span {{ padding: 16px 30px; background: var(--panel); border-radius: 18px; font-size: 42px; font-weight: 700; }}
.warn, .note {{ padding: 26px 36px; border-radius: 24px; font-size: 44px; font-weight: 700; line-height: 1.45; }}
.warn {{ background: rgba(255,93,93,.12); border-left: 10px solid var(--red); }} .warn b {{ color: var(--red); }}
.note {{ background: rgba(63,167,214,.12); border-left: 10px solid var(--blue); }} .note b {{ color: var(--orange); }}
.note small {{ font-size: 38px; color: var(--mute); font-weight: 600; font-family: var(--mono); }}
code {{ font-family: var(--mono); color: var(--orange); }}
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
.res span.ok {{ color: var(--green); }}
.res span.bad {{ color: var(--red); background: rgba(255,93,93,.14); box-shadow: inset 0 0 0 3px var(--red); }} .vs .card em {{ font-style: normal; color: var(--orange); }}
.list {{ display: flex; flex-direction: column; gap: 16px; }}
.row {{ display: flex; align-items: center; gap: 30px; background: var(--panel); border-radius: 22px; padding: 14px 36px; font-size: 48px;
  transform-origin: left center; }}
.row .no {{ font-size: 52px; font-weight: 900; color: var(--orange); width: 50px; }}
.row b {{ font-family: var(--mono); color: var(--blue); }}
.cta {{ margin-top: 20px; font-size: 54px; font-weight: 800; text-align: center; }}
.cap {{ top: auto; bottom: 260px; height: auto; display: flex; justify-content: center; padding: 0 60px; }}
.cap span {{ background: rgba(0,0,0,.78); color: #fff; font-size: 48px; font-weight: 700; line-height: 1.4; padding: 16px 30px;
  border-radius: 18px; text-align: center; word-break: keep-all; }}
.bar {{ position: absolute; left: 0; bottom: 0; height: 10px; width: 1080px; background: var(--orange); transform-origin: left center; }}
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
function enter(sel, t, dur) {{
  const items = document.querySelectorAll(sel + " .in");
  const step = Math.min(0.9, (dur * 0.5) / Math.max(1, items.length));
  items.forEach((el, i) => {{
    const at = Math.max(0, t - 0.1) + i * step;
    tl.fromTo(el, {{ opacity: 0, y: 50 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, at);
    el.querySelectorAll(".ln").forEach((ln, j) => {{
      tl.fromTo(ln, {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power2.out" }}, at + 0.15 + j * 0.3);
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
