# 03: STEP 3 여러 개 구현 + STEP 4 상수와 new

**What to build:** 두 장면을 대본 → 음성 → 화면까지 만든다.
- multi(STEP 3): `class Teacher extends Person implements Teachable, Studyable`이 `teach()`와 `study()`를 구현한다. 실행하면 `서준 수업 중`, `서준 공부 중`이 출력된다. "extends 하나 · implements 여럿" 칩을 함께 보여 준다.
- rules(STEP 4): 인터페이스의 `int MAX_HOURS = 8;`은 자동으로 `public static final` 상수다. `Studyable.MAX_HOURS`를 출력하면 `8`이 나오고, `Studyable.MAX_HOURS = 9;`는 컴파일 오류다. `new Studyable()`도 컴파일 오류다. 두 오류를 한 장면에 담으므로 코드를 짧게 줄이고, 공간이 부족하면 결과 칩으로 대체한다.

**Blocked by:** 02

**Status:** resolved

- [x] multi 예제가 빌드 중 실행되고, 출력 `서준 수업 중` / `서준 공부 중` 두 줄과 대조되어 통과한다
- [x] rules 예제가 빌드 중 실행되고, 출력 `8`과 대조되어 통과한다
- [x] 재대입 오류가 javac의 `cannot assign a value to static final variable MAX_HOURS`와 대조되어 통과한다(11편의 `final variable` 문구와 다름)
- [x] `new Studyable()` 오류가 javac의 `Studyable is abstract; cannot be instantiated`와 대조되어 통과한다
- [x] 나레이션 문장이 화면의 기대 결과와 같은지 직접 확인한다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다(multi·rules는 390px 폭으로도 확인)

## Comments

- 2026-11-13: Opus가 메인 세션에서 직접 구현(워크트리·서브에이전트 없음). 첫 빌드에서 예제 대조 9건 통과(출력 4·컴파일 오류 4·컴파일 성공 1), check 오류 0건(line_unread 경고 1건), 자막 공백 0초, 렌더링 1:56.8.
