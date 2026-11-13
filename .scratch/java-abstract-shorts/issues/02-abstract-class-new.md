# 02: STEP 2 추상 클래스·new 불가

**What to build:** STEP 2의 두 장면을 대본 → 음성 → 화면까지 만든다.
- aclass: 추상 메소드 `hello()`가 있는데 `class` 앞의 `abstract`를 빼면 컴파일 오류가 난다. `abstract class Person`으로 고치면 통과한다.
- anew: 추상 클래스로 `new Person("서준")`을 하면 컴파일 오류가 난다. 이 오류가 why 장면의 "어중간한 객체" 문제를 막아 준다고 연결한다.

진행 표시는 두 장면 모두 2번째 칸이다.

**Blocked by:** 01

**Status:** resolved

- [x] aclass 오류 예제가 javac의 `Person is not abstract and does not override abstract method hello() in Person`과 대조되어 통과한다
- [x] anew 오류 예제가 javac의 `Person is abstract; cannot be instantiated`와 대조되어 통과한다
- [x] 고친 `abstract class Person` 코드는 컴파일 성공으로 확인된다
- [x] 나레이션에서 말한 오류·해결 방법이 모두 화면에 보인다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-13: Opus가 메인 세션에서 직접 구현(워크트리·서브에이전트 없음). 전체 빌드에서 예제 대조 통과, check 0건, 렌더링 1:56.8.
