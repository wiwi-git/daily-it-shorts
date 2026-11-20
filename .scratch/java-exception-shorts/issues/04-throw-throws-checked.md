# 04: STEP 4 throw · throws · 체크 예외

**What to build:** 예외를 직접 던지고(throw), 처리를 부르는 쪽에 넘기는(throws) 두 장면. 같은 `checkScore` 메소드가 장면을 따라 바뀐다.

먼저 헬퍼를 확장한다: `checkScore` 같은 `static` 메소드를 `Main` 클래스 안(`main` 바깥)에 두고 실행할 수 있게 한다. 기존 장면의 결과는 바뀌지 않아야 한다.

- throw: `static void checkScore(int score)`가 0 미만·100 초과면 `throw new IllegalArgumentException("점수 오류: " + score)`. `checkScore(120)`을 `try-catch`로 불러 `점수 오류: 120` 출력. `throws` 없이 컴파일된다(언체크 예외)
- throws: 던지는 예외를 `Exception`으로 바꾸면 컴파일 오류(`unreported exception Exception; must be caught or declared to be thrown`) → 선언에 `throws Exception`을 붙이고 부르는 쪽이 `try-catch`로 처리하면 `점수 오류: 120`. 체크 예외(처리 강제)와 언체크 예외(처리 선택)를 `.vs` 카드로 비교, 체크 예외의 대표로 `IOException`(다음 편 예고 없이 사실만)

진행 표시는 둘 다 4번째 칸. 화면에서 `throws`의 `s`를 주황으로 강조한다. 선언 줄은 33자를 넘으면 `throws` 앞에서 줄을 바꾼다.

**Blocked by:** 01

**Status:** resolved

- [x] `Main` 안 `static` 메소드가 컴파일·실행되고, 01~03 장면의 대조가 그대로 통과한다
- [x] throw의 출력, throws의 컴파일 오류(처리 전)와 출력(처리 뒤)이 빌드에서 대조된다
- [x] 체크 예외·언체크 예외에 화면 처음 한 번 "(처리 강제)" "(처리 선택)"을 덧붙인다
- [x] 체크 예외 처리는 "try-catch로 잡거나 throws로 넘긴다" 두 가지를 함께 말한다
- [x] 코드 한 줄은 33자 이하다
- [x] 나레이션이 화면 결과와 같은지 직접 확인했다
