# 자바 영상 빌드 헬퍼 (`tools/javashorts.py`)

자바 입문 영상의 `build.py`는 장면만 담고, 타이밍·나레이션 합치기·예제 실행·자막·`index.html` 출력은 공용 모듈 `tools/javashorts.py`가 한다. 새 영상은 가장 최근 자바 영상의 `build.py`를 복사해 장면만 바꾼다. 헬퍼를 고치면 모든 영상에 반영되므로, 고친 뒤 기존 영상 두 편 이상을 다시 빌드해 `index.html`·`examples.txt`가 그대로인지(`git diff`) 확인한다.

## build.py 골격

```python
import javashorts as J
J.load(speed=1.2)          # vo.json → 장면 시작 시각 + assets/narration.mp3
from javashorts import *
J.FILE = "scores.txt"      # 필요할 때만: 예제가 남기는 파일 (fterm·file= 대조)
J.IMPORTS = ["import java.util.*;", ""]
J.MAIN_THROWS = "IOException"
scenes = {"hook": ..., ...}; PROG = {"write": 1, ...}   # PROG: 장면 id → 진행 칸(1~5)
J.build(scenes, PROG, BRAND, CSS, outro=(EXEC, EXEC_SAID, EXEC_END))
```

장면 도중 설정을 바꿀 때는 `J.MAIN_THROWS = ""`처럼 모듈을 거친다(`*`로 가져온 이름을 바꾸면 반영되지 않는다).

## 예제 실행·대조

화면의 자바 코드는 모두 컴파일·실행되고, 결과가 대본과 다르면 빌드가 멈춘다. 결과 상자는 실제 결과로 그린다. 모든 예제는 `examples.txt`에 남는다.

| 헬퍼 | 대조하는 것 |
|---|---|
| `jcode(sid, lines, expect, mark=, pre=, hidden=, file=)` | 출력이 `expect`와 같음. `pre`·`hidden`은 보이지 않게 앞뒤로 실행 |
| `jshow(sid, lines)` | 줄 끝 `// 결과` 주석이 그 줄의 출력과 같음 |
| `jrt(sid, lines, runtime, before=)` | 실행 중 예외 문구에 `runtime`이 들어 있음 |
| `jce(sid, lines, error, detail=)` | 컴파일 오류 문구에 `error`가 들어 있음 |
| `jok(sid, lines)` | 컴파일·실행만 되면 됨 (그리지 않음) |
| `jmulti(sid, lines, shown_out, each=, all_=, runs=20, label=, note=)` | 실행할 때마다 다른 출력(스레드). 한 번 컴파일해 `runs`번 실행하고, 매 출력이 `each(out)`, 전체 목록이 `all_(outs)`를 만족해야 함. 화면 상자는 고정 예시 `shown_out`(그 자체도 `each` 통과 필수) |

- `jmulti`: 순서만 다른 출력은 `each=same_lines("민수 85", "서준 92", "main 끝")`. 다음 `term()`의 라벨은 `label`(기본 "실행 결과 예시")이 되고, 다른 헬퍼를 부르면 "실행 결과"로 돌아간다. `examples.txt`에는 고정 예시와 "실행할 때마다 다를 수 있음" 주석이 남는다(관찰한 출력은 남기지 않아 다시 빌드해도 같다)

- 코드는 `main` 안에서 실행된다. `top=`은 `class Main` 위(다른 클래스), `members=`는 `Main` 안(`static` 메소드). `show_top`·`show_members`로 화면에 그릴지 정한다
- `file=`: 실행 뒤 `J.FILE` 내용이 정확히 이 문자열이어야 한다. 예제마다 임시 폴더에서 실행되므로 앞 장면의 파일 상태는 `pre=`로 다시 만든다
- 결과 상자: `term()`(출력), `fterm()`(파일 내용), `rterm()`(실행 중 예외), `cterm()`(컴파일 오류)
- 예제 id에 `-`를 붙이면(`append-trap`) `examples.txt`에서 그 앞부분과 같은 장면 id 중 가장 긴 것의 섹션 이름을 쓴다(장면 id에도 `-`가 들어갈 수 있다: `run-trap-run` → `run-trap`)

## 화면 조각

- `head(step, title, desc)`: STEP 라벨 + 제목 + 설명(`<b>`는 주황)
- `code(lines, mark=(), sm=False)`: 코드 블록 42px(`sm`은 34px), 한 줄 33자 넘으면 빌드 중단, `mark`는 핵심 줄 주황 배경
- `lab(text)`, `table(cols, rows, label)`, `card(small, big, span, k)`
- 정리 장면: `outro=(EXEC, EXEC_SAID, EXEC_END)`를 넘기면 나레이션이 `EXEC_SAID[i]`로 시작하는 단어를 말하는 순간 `#ex{i}` 줄을 강조한다. 단어를 못 찾으면 빌드 중단
- `word_time(sid, token)`: 장면 안에서 `token`으로 시작하는 단어의 절대 시각
- 공통 CSS는 `BASE_CSS`, 영상별 CSS는 `build()`의 `css` 인자
