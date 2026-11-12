# 04: STEP 4 final 메소드·클래스 + STEP 5 static final 상수

**What to build:**
- fmc(STEP 4): 부모 클래스 `Person`(k1)의 final `hello()`를 자식 클래스 `Student`가 오버라이딩하면 컴파일 오류가 난다. final 클래스 `Person`을 `extends`해도 컴파일 오류가 난다. 자바의 `String`도 final 클래스라는 메모(`public final class String`)를 넣는다.
- const(STEP 5): 메소드 편 `isPass()`의 숫자 60을 `static final int PASS_SCORE = 60`으로 바꾼다. 민수(85)의 `isPass()`는 true다. 상수는 `static final`로 만들고 이름은 대문자와 `_`로 쓴다는 규칙을 보여 주고, 상수에 다시 대입하면 컴파일 오류가 나는 것을 보여 준다.

**Blocked by:** 03

**Status:** resolved

- [x] final 메소드 예제가 빌드 중 컴파일되고, 오류에 `hello() in Student cannot override hello() in Person`이 포함되어야 통과한다
- [x] final 클래스 예제가 빌드 중 컴파일되고, 오류에 `cannot inherit from final Person`이 포함되어야 통과한다
- [x] const 예제가 빌드 중 실행되고, 출력 `true`와 대조되어 통과한다
- [x] 상수 재대입 예제는 오류에 `cannot assign a value to static final variable`이 포함되어야 통과한다
- [x] 나레이션에서 말한 `String` 내용이 화면 메모로 보인다
- [x] fmc 장면을 390px 폭으로 줄여 모바일 가독성을 확인한다
- [x] `hyperframes check` 오류 0건이고, snapshot으로 새 장면을 확인한다

## Comments

- 2026-11-12: 병합(be085f7, 1b59919, 6d89ff2). 장면을 fmc·fcls, const·cre로 나눔. 상수 재대입 오류는 실제 javac 문구(`static final variable`)로 대조. 길이 조정을 위해 전 장면 나레이션을 줄임.
