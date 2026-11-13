# 03: STEP 3 자식이 완성·빠뜨리면?

**What to build:** STEP 3의 두 장면을 대본 → 음성 → 화면까지 만든다.
- override: `Student`(민수·85)와 `Teacher`(서준)가 `@Override hello()`로 추상 메소드를 완성한다. 실행하면 `학생 민수 안녕`, `서준 선생님 안녕`이 출력된다.
- omiss: Teacher가 `hello()`를 빠뜨리면 컴파일 오류가 난다. 해결 방법 두 가지(오버라이딩하기 / `abstract class Teacher`로 미루기)를 번호 목록 또는 비교 카드로 보여 준다. `abstract class Teacher`는 통과하지만, 그 Teacher를 `new` 하면 컴파일 오류가 난다.

Teacher는 상속 편의 `subject` 필드를 쓰지 않는다. 진행 표시는 두 장면 모두 3번째 칸이다.

**Blocked by:** 02

**Status:** resolved

- [x] override 예제가 빌드 중 실행되고, 출력 `학생 민수 안녕` / `서준 선생님 안녕` 두 줄과 대조되어 통과한다
- [x] omiss(빠뜨림) 오류가 javac의 `Teacher is not abstract and does not override abstract method hello() in Person`과 대조되어 통과한다
- [x] `abstract class Teacher` 코드는 컴파일 성공으로 확인된다
- [x] abstract Teacher를 `new` 하는 예제가 javac의 `Teacher is abstract; cannot be instantiated`와 대조되어 통과한다
- [x] 나레이션 문장이 화면의 기대 결과와 같은지 직접 확인한다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다(omiss는 390px 폭으로도 확인)

## Comments

- 2026-11-13: Opus가 메인 세션에서 직접 구현(워크트리·서브에이전트 없음). 전체 빌드에서 예제 대조 통과, check 0건, 렌더링 1:56.8.
