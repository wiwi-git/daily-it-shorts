# 04: STEP 2 `sleep`과 `join`

**What to build:** 스레드가 끝날 때까지 기다리는 법을 보여 주는 장면.

- 스레드가 `Thread.sleep(1000)` 뒤 `민수 85`를 출력한다
- `join`이 없는 버전: `main 끝` → `민수 85`
- `t.join()` 한 줄을 넣은 버전: `민수 85` → `채점 끝`. 추가된 줄은 `mark`로 강조한다
- 두 버전 모두 `jmulti`로 여러 번 실행해 매번 이 순서인지 확인한다(1초 `sleep`으로 사실상 고정이지만 스레드 예제라서)
- `sleep`·`join`은 체크 예외 `InterruptedException`을 던져서 `main`에 `throws InterruptedException`을 붙인다(`J.MAIN_THROWS`). 20편 체크 예외와 한 문장으로 연결한다

진행 표시는 2번째 칸.

**Blocked by:** 02

**Status:** resolved

- [x] 두 버전의 출력 순서가 빌드에서 반복 검증된다
- [x] 화면에 `throws InterruptedException`이 보이고, 나레이션은 "인터럽티드 익셉션"으로 읽는다
- [x] 두 버전 비교가 한 화면에 들어가고 390px 폭에서도 읽힌다(가장 빽빽한 장면 후보)
- [x] 나레이션이 화면 결과와 같은지 직접 확인했다

## Comments

- (02에서 확정) `sleep`은 람다 안이라 `try { Thread.sleep(1000); } catch (InterruptedException e) {}`로 감싸야 한다(33자 제한: `} catch (` 뒤에서 줄바꿈). `main`의 `throws InterruptedException`은 `join` 때문. 대본은 이미 이렇게 말한다.
- 구현: 코드 한 벌(`t.join()` 줄 강조, sm 34px) 아래에 결과 상자 두 개(`join 없음`: 채점 끝→민수 85 / `t.join() 있음`: 민수 85→채점 끝), 그 아래 체크 예외 메모. 두 버전 모두 `jmulti`로 대조.
- 반복 횟수: 예제마다 1초 `sleep`이 있어 20회면 빌드가 40초 늘어나므로 `runs=5`로 했다.
- 대본 수정: "조인이 없으면 메인 끝이 먼저" → "채점 끝이 먼저"(코드의 출력 문구와 맞춤), 음성 재생성.
- 화면 수정: 처음엔 `throws` 라벨 + 3줄 메모가 하단 자막 영역을 침범해서, 라벨을 빼고 메모를 두 줄(`체크 예외 InterruptedException` / `sleep → 스레드 안 try-catch · join → main에 throws`)로 줄였다. 코드 블록에는 `main` 선언이 보이지 않고 `throws`는 메모로 보여 준다.
- 검증: check 오류 0건, 자막 공백 0초, 휴대폰 폭 시트에서 자막과 겹치지 않음 확인.
