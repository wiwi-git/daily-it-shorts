# 01: `jhang` 헬퍼 + 실행 시간 제한

**What to build:** 자바 영상 빌드가 "이 프로그램은 끝나지 않는다"는 나레이션의 주장도 실제로 검증할 수 있게 한다. 지금 공용 빌드 모듈은 프로그램을 시간 제한 없이 실행하기 때문에, 끝나지 않는 예제를 넣으면 빌드가 끝나지 않는다.

- 프로그램 실행 함수에 선택 인자 `timeout`을 추가한다. 기본값은 지금처럼 제한 없음이어서, 기존 헬퍼(`jcode`·`jshow`·`jrt`·`jmulti` 등)의 동작은 바뀌지 않는다
- 새 헬퍼 `jhang(sid, lines, secs=3, …)`
  - 한 번 컴파일해 `secs`초 동안 실행한다
  - 제한 시간 안에 끝나지 않으면 프로세스를 종료하고 통과한다
  - 제한 시간 안에 끝나거나 실행 오류가 나면 빌드를 멈춘다
  - `examples.txt`에는 "N초 안에 끝나지 않음(의도)"과, 그 사이 출력이 있었다면 그 일부를 남긴다
  - 다른 헬퍼처럼 코드 블록을 돌려준다. 다른 헬퍼와 같은 인자(`mark`·`pre`·`hidden`·`top`·`members` 등)를 받고, 그리지 않고 검증만 하는 용도로도 쓸 수 있다
- `docs/java-helpers.md` 헬퍼 표에 `jhang` 행을 추가한다

이 티켓은 새 영상과 상관없이 끝낼 수 있다. 검증용으로 25편 swallow(빈 `catch`)·daemon(`setDaemon` 없음) 프로그램을 임시로 돌려 본다. 자세한 결정은 [../spec.md](../spec.md)의 "공용 모듈 변경".

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] 실행 함수의 `timeout` 기본값이 "제한 없음"이고, 기존 헬퍼 호출 코드는 하나도 바꾸지 않았다
- [x] 끝나지 않는 프로그램(반복 안의 빈 `catch` + `isInterrupted()` 조건)을 `jhang`에 넣으면 약 3초 뒤 통과한다
- [x] 곧 끝나는 프로그램을 `jhang`에 넣으면 빌드가 이유와 함께 멈춘다
- [x] 컴파일 오류·실행 오류도 빌드를 멈춘다
- [x] `jhang` 검증 뒤 `java` 프로세스가 남지 않는다(`pgrep`·`ps`로 확인)
- [x] `java-pool-shorts`와 `java-thread-shorts`를 다시 빌드해도 두 편의 `index.html`·`examples.txt`에 `git diff`가 없다
- [x] `docs/java-helpers.md`에 `jhang` 사용법(통과 조건·`secs`·`examples.txt` 기록 방식)이 적혀 있다

## Comments

- 실행 함수에 `timeout`(기본 None = 제한 없음)을 넣었다. 시간이 지나면 `subprocess.run`이 자식 프로세스를 kill하고 `TimeoutExpired`를 던진다.
- `jhang`: 시간 초과 → 통과, `examples.txt`에는 "N초 안에 끝나지 않음 (의도 · 빌드가 강제로 종료)"과 그 사이 출력 처음 3줄(+ "…"). 곧 끝남·실행 오류·컴파일 오류는 모두 빌드 중단을 확인함.
- 임시 스크립트로 swallow 빈 `catch` 프로그램을 돌려 3.3초 뒤 통과, 뒤에 남은 `java` 프로세스 없음(`pgrep`).
- `java-pool-shorts`, `java-thread-shorts` 재빌드 → `index.html`·`examples.txt` diff 없음.
