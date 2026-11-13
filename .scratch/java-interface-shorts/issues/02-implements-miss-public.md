# 02: STEP 2 implements·빠뜨리면?·public 필수

**What to build:** STEP 2의 세 장면을 대본 → 음성 → 화면까지 만든다.
- impl: `class Student extends Person implements Studyable`이 `@Override public void study()`를 구현한다. 실행하면 `민수 공부 중`이 출력된다. `extends` 뒤에 `implements`가 오는 순서를 보여 준다.
- miss: Student가 `study()`를 빠뜨리면 컴파일 오류가 난다. 추상 메소드와 같은 강제라는 점을 연결한다.
- pub: `public`을 뺀 `void study()`는 컴파일 오류다. 오류 아래에 "인터페이스 메소드 = 자동 public" 메모를 두고, 더 좁힐 수 없다는 이유를 말한다.

진행 표시는 세 장면 모두 2번째 칸이다.

**Blocked by:** 01

**Status:** resolved

- [x] impl 예제가 빌드 중 실행되고, 출력 `민수 공부 중`과 대조되어 통과한다
- [x] miss 오류가 javac의 `Student is not abstract and does not override abstract method study() in Studyable`과 대조되어 통과한다
- [x] pub 오류가 javac의 `study() in Student cannot implement study() in Studyable`과 대조되어 통과한다
- [x] 나레이션에서 말한 오류·이유(자동 public)가 모두 화면에 보인다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 세 장면을 확인한다

## Comments

- 2026-11-13: Opus가 메인 세션에서 직접 구현(워크트리·서브에이전트 없음). 첫 빌드에서 예제 대조 9건 통과(출력 4·컴파일 오류 4·컴파일 성공 1), check 오류 0건(line_unread 경고 1건), 자막 공백 0초, 렌더링 1:56.8.
