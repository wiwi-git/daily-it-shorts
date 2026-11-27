# 03: STEP 2 인터럽트 + STEP 3 예외 삼키지 않기

**What to build:** 시청자가 인터럽트로 자고 있는 스레드를 깨워 멈추는 방법을 보고, 이어서 반복 안에서 `InterruptedException`을 삼키면 왜 스레드가 끝나지 않는지와 고치는 법을 본다. 두 장면 모두 STEP 1의 코드 뼈대를 그대로 이어 쓴다.

- interrupt: flag 코드에서 두 줄만 바꾼다 — `while (!stop)` → `while (true)`, `stop = true;` → `t.interrupt();`. 바뀐 두 줄은 주황 강조한다. 자고 있던 `sleep`이 `InterruptedException`을 던지고, 반복 바깥의 `catch`로 빠져나와 `작업 끝`을 출력한다. `jmulti` 20회, 화면 예시는 STEP 1과 같다
- swallow(문제 버전): 반복 조건을 `while (!Thread.currentThread()` / `.isInterrupted()) {` 두 줄로 쓰고, `try { Thread.sleep(200); }`와 빈 `catch`를 반복 안에 둔다. 01의 `jhang`으로 "끝나지 않음"을 검증한다. 출력 상자 대신 `.warn`("끝나지 않아요")을 둔다. 나레이션: 예외가 나는 순간 인터럽트 상태가 지워져서, 반복 조건이 계속 참이 된다
- swallow(고친 카드): 화면에는 `catch` 부분만 다시 그린다 — `InterruptedException e) {` / `Thread.currentThread()` / `.interrupt();` / `}`. 빌드는 고친 전체 프로그램을 `jmulti`로 실행한다(`작업 중` 1줄 이상 + `작업 끝`)
- 나레이션은 STEP 1·2의 빈 `catch`(반복 바깥, 예외가 나면 끝남)와 이번 빈 `catch`(반복 안, 계속 돎)를 구분한다. "빈 `catch`는 무조건 나쁘다"처럼 단정하지 않는다

자세한 결정은 [../spec.md](../spec.md).

**Blocked by:** 01 (`jhang` 헬퍼), 02 (프로젝트 골격·대본·flag 코드 뼈대)

**Status:** resolved

- [x] interrupt 코드가 flag 코드와 정확히 두 줄만 다르고, 그 두 줄이 강조된다
- [x] interrupt 예제와 swallow 고친 버전이 `jmulti` 20회를 통과한다
- [x] swallow 문제 버전이 `jhang`을 통과한다(제한 시간 안에 끝나지 않음)
- [x] 모든 코드 줄이 33자 이하이고, swallow 장면(가장 빽빽한 장면 후보)이 자막·하단 300px과 겹치지 않는다
- [x] 나레이션이 "인터럽트는 요청", "예외가 나면 인터럽트 상태가 지워진다"를 정확히 말하고, 빈 `catch`를 단정적으로 금지하지 않는다
- [x] 나레이션이 화면과 같은지 직접 확인했다
- [x] `tools/verify-video.sh java-stop-shorts --no-render` 통과

## Comments

- interrupt: flag와 다른 두 줄(`while (true) {`, `t.interrupt();`)만 강조.
- swallow: 빈 catch 버전은 그리는 코드(작업 스레드만) + main(STEP 2와 같음)을 합쳐 `jhang`으로 확인, 고친 버전 전체는 `jmulti`로 확인. 화면은 문제 코드 아래에 "고치면" catch 카드 + 오른쪽 "빈 catch면 안 끝나요" 경고 / "고치면 마지막 줄 작업 끝" 상자.
