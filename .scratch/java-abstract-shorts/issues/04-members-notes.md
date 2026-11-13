# 04: STEP 4 추상 클래스의 구성 + STEP 5 주의

**What to build:** 두 장면을 대본 → 음성 → 화면까지 만든다.
- members(STEP 4): 추상 클래스 `Person`도 필드 `name`, 생성자 `Person(String name)`, 일반 메소드 `bye()`(`name + " 잘 가"`)를 가질 수 있다. 자식은 `super(name)`으로 부모 생성자를 호출한다. `s.bye()`를 실행하면 `민수 잘 가`가 출력된다. 생성자와 `bye()`는 이 장면에서 처음 화면에 보여 준다.
- notes(STEP 5): 메모(`.note`) "추상 메소드 없는 추상 클래스도 가능"과 경고(`.warn`) "`abstract final class`는 컴파일 오류"를 보여 준다. 이유는 "abstract는 물려받아 완성하라, final은 물려받지 마라"로 설명한다.

**Blocked by:** 03

**Status:** resolved

- [x] members 예제가 빌드 중 실행되고, 출력 `민수 잘 가`와 대조되어 통과한다
- [x] 추상 메소드 없는 추상 클래스 예제는 컴파일 성공으로 확인된다
- [x] `abstract final` 예제가 javac의 `illegal combination of modifiers: abstract and final`과 대조되어 통과한다
- [x] 나레이션에서 말한 필드·생성자·일반 메소드·`super(name)`이 모두 화면에 보인다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다(members는 390px 폭으로도 확인)

## Comments

- 2026-11-13: Opus가 메인 세션에서 직접 구현(워크트리·서브에이전트 없음). 전체 빌드에서 예제 대조 통과, check 0건, 렌더링 1:56.8.
