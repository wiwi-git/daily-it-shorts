# 03: STEP 4 풀 닫기 + 가상 스레드 비교

**What to build:** 02에서 이미 본 try-with-resources 괄호의 의미를 풀고, 가상 스레드를 한 줄로 비교하는 장면을 대본 → 음성 → 화면까지 만든다.

- future 장면의 코드를 다시 보여 주고 `try (` … `) {` 줄을 주황 강조(`mark`). 메모: "괄호가 끝나면 → 작업이 다 끝날 때까지 기다렸다 닫기 = `join` 대신". 21편 파일 닫기와 같은 문법이라고 말한다
- `.warn` "닫지 않으면 프로그램이 끝나지 않아요". 실행 예제는 만들지 않는다(검증 도구에 시간 제한을 새로 만들지 않음)
- 가상 스레드: 코드 블록이 아닌 비교 상자에 메소드 이름만 위아래로 `newFixedThreadPool(2)` ↓ `newVirtualThreadPerTaskExecutor()`. 나레이션 "풀을 만드는 줄만 바꾸면, 작업마다 가벼운 가상 스레드를 하나씩 만들어요. 자바 21부터예요". "가상 스레드 풀"이라고 말하지 않는다
- 가상 스레드 버전 전체 프로그램(future 코드에서 풀 만드는 줄만 바꾼 것)은 화면에 그리지 않고, 기존 `check`/`wrap`으로 실행해 `177`인지 확인한다. 새 헬퍼는 만들지 않는다
- 나레이션이 "try-with-resources로 풀을 닫는 건 예전부터 됐다"처럼 들리지 않게 한다(자바 19부터)

자세한 결정은 [../spec.md](../spec.md).

**Blocked by:** 02

**Status:** resolved

- [x] 가상 스레드 버전이 빌드에서 실행되어 `177`이고, 기대값을 일부러 틀리게 바꾸면 빌드가 멈춘다
- [x] `newVirtualThreadPerTaskExecutor()`가 390px 폭 시트에서 줄바꿈·넘침 없이 보인다
- [x] 닫지 않으면 안 끝난다는 경고가 `.warn`으로 보이고, 이를 실행하는 예제는 없다
- [x] 나레이션이 "사실 표현 주의"(가상 스레드는 풀이 아님, 자바 21부터)를 지킨다
- [x] `tools/verify-video.sh java-pool-shorts --no-render` 통과, close 장면을 390px 폭 시트에서 확인

## Comments

- 화면 코드는 future 전체를 다시 그리지 않고 `// submit · get` 한 줄로 줄인 모양(try·`) {`·`}` 강조). 이 모양도 `jok("close")`로 컴파일·실행 확인.
- 가상 스레드 버전: STEP 3 프로그램에서 풀 줄만 바꿔 `check("close-virtual", …, "177\n")`. 기대값을 176으로 바꾸면 `close-virtual: prints '177\n', but the script expects '176\n'`로 멈춤.
- 비교 상자 `.swap`(build.py 지역 CSS): "풀을 만드는 줄만 바꾸면 · 자바 21부터" / `newFixedThreadPool(2)` ↓ `newVirtualThreadPerTaskExecutor()`(38px, 한 줄) / "풀이 아니라 작업마다 가벼운 가상 스레드 · 결과는 똑같이 177".
- "닫지 않으면 안 끝남"은 `.warn`만. 메모 줄이 넘쳐 "} 블록이 끝나면<br/>작업이 다 끝날 때까지 기다렸다 닫기" 두 줄로 나눔.
