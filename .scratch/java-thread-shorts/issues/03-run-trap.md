# 03: STEP 1-1 `run()` 함정

**What to build:** `start()` 대신 `run()`을 직접 부르면 새 스레드 없이 그냥 메소드 호출이 된다는 것을 보여 주는 장면.

- 스레드 안에서 `Thread.currentThread().getName()`을 출력한다(33자 제한 때문에 변수에 담거나 줄을 나눈다)
- `start()` 쪽은 `Thread-0`, `run()` 쪽은 `main` — 항상 같으므로 기존 `jcode`로 대조한다
- 함정 쪽은 경고 색으로 구분한다. "오류가 아니라 그냥 메소드 호출"이라고 정확히 말한다

진행 표시는 1번째 칸.

**Blocked by:** 02

**Status:** resolved

- [x] 두 출력(`Thread-0` / `main`)이 빌드에서 대조된다
- [x] 390px 폭에서도 읽힌다
- [x] 나레이션이 화면 결과와 같은지 직접 확인했다

## Comments

- 공유 람다 코드(`getName()` 줄 강조) 아래에 `t.start();` → `Thread-0`(초록 테두리) / `t.run();` → `main`(빨간 테두리) 카드 두 장, 그 아래 경고 메모. 두 출력은 각각 `jcode`로 대조(`run-trap`, `run-trap-run`).
- 공용 헬퍼 수정: 장면 id에 `-`가 있으면 `examples.txt` 섹션 찾기가 실패해서(`run-trap-run` → `run`), 가장 긴 장면 id 접두어로 찾게 바꿨다. 21편 재빌드 diff 없음. `docs/java-helpers.md` 갱신.
- 검증: check 오류 0건, 자막 공백 0초, 휴대폰 폭 시트 확인.
