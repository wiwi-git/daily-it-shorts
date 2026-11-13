# 04: STEP 5 default 메소드·추상 클래스와 비교

**What to build:** STEP 5의 두 장면을 대본 → 음성 → 화면까지 만든다.
- dflt: `Studyable`에 몸체 있는 `default void rest()`(`"쉬는 중"` 출력)를 둔다. Student가 `rest()`를 구현하지 않아도 `s.rest()`를 실행하면 `쉬는 중`이 출력된다. default 메소드는 구현이 강제되지 않는다.
- vs: 추상 클래스와 인터페이스를 비교 카드 세 줄로 보여 준다. `extends` 하나 vs `implements` 여럿 / 필드·생성자 가능 vs 상수만 / 일반 메소드 vs `default` 메소드.

진행 표시는 두 장면 모두 5번째 칸이다.

**Blocked by:** 03

**Status:** resolved

- [x] dflt 예제가 빌드 중 실행되고, 출력 `쉬는 중`과 대조되어 통과한다
- [x] dflt의 Student 코드에 `rest()` 구현이 없다
- [x] vs 카드 세 줄이 모두 화면에 보이고, 나레이션이 말한 차이와 같다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-13: Opus가 메인 세션에서 직접 구현(워크트리·서브에이전트 없음). 첫 빌드에서 예제 대조 9건 통과(출력 4·컴파일 오류 4·컴파일 성공 1), check 오류 0건(line_unread 경고 1건), 자막 공백 0초, 렌더링 1:56.8.
