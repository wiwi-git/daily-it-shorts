# 05: STEP 5 커스텀 예외

**What to build:** 예외 클래스를 직접 만들어 쓰는 장면. 04의 `checkScore`가 이어서 발전한다.
- custom: `class ScoreException extends Exception`, 생성자에서 `super(message)`로 메시지를 부모 클래스에 넘김. `checkScore`가 `throws ScoreException`으로 `ScoreException`을 던지고, 부르는 쪽이 `catch (ScoreException e)`로 잡아 `e.getMessage()` → `점수 오류: 120`. 장점: 예외 이름만 봐도 무슨 문제인지 알 수 있음

`ScoreException`은 `Main` 바깥(클래스 위쪽)에 둔다. 진행 표시는 5번째 칸.

**Blocked by:** 04

**Status:** resolved

- [x] custom의 출력이 빌드에서 대조되고, 화면 상자는 실제 출력으로 그린다
- [x] 커스텀 예외에 화면 처음 한 번 "(직접 만든 예외 클래스)"를 덧붙인다
- [x] `super(message)`와 `getMessage()`의 연결을 화면과 나레이션 모두에서 보여 준다
- [x] 클래스 선언·메소드·호출이 한 화면에 들어가고 390px 폭에서도 읽힌다
- [x] 나레이션이 화면 결과와 같은지 직접 확인했다
