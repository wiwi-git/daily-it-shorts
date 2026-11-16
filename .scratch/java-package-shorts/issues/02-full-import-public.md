# 02: STEP 2 전체 이름·import + STEP 3 public 필요

**What to build:** 세 장면을 대본 → 음성 → 화면까지 만든다.
- full(STEP 2): `app/Main.java`에서 `school.Student s = new school.Student("민수", 85);` → `s.hello()` → `학생 민수 안녕`. `school.Student` 부분을 주황으로 강조하고, 화면에 처음 한 번 "전체 이름 (패키지 이름 + 클래스 이름)"을 표시한다.
- imp(2-1): `import school.Student;` 후 `Student`만으로 같은 결과 `학생 민수 안녕`이 나온다. `import` 줄을 `mark`로 강조한다. full과 같은 모양으로 배치해 결과가 같다는 것이 보이게 한다. import는 클래스를 복사하거나 포함하는 것이 아니라, 이름을 줄여 쓰게 해 줄 뿐이라고 설명한다.
- pub(STEP 3): `public`이 없는 `class Student`를 쓰면 다른 패키지에서 컴파일 오류가 난다. 실제 오류 문구와 `.warn`을 보여 준다. 이어서 생성자·메소드도 다른 패키지에서 쓰려면 `public`이 필요하다는 것을 한 문장으로 말하고, 코드에서 `public` 생성자·메소드 줄을 `mark`로 강조한다. `public`이 없을 때의 범위(같은 패키지에서만)는 한 문장으로 언급하고, 자세한 내용은 다음 편(접근 제어자)으로 넘긴다. `.note` 한 줄: public 클래스는 파일 이름과 같아야 한다(`Student.java`).

진행 표시는 full·imp가 2번째 칸, pub가 3번째 칸이다.

**Blocked by:** 01

**Status:** resolved

- [x] full 예제가 빌드 중 실행되고, 출력 `학생 민수 안녕`과 대조되어 통과한다
- [x] imp 예제가 빌드 중 실행되고, 출력 `학생 민수 안녕`과 대조되어 통과한다
- [x] pub 오류가 javac의 `Student is not public in school; cannot be accessed from outside package`와 대조되어 통과한다
- [x] 나레이션에서 말한 전체 이름·import·public·파일 이름 규칙이 모두 화면에 보인다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 세 장면을 확인한다(pub는 390px 폭으로도 확인)

## Comments

- 2026-11-16: Opus가 메인 세션에서 01~04를 한 번에 구현(워크트리·서브에이전트 없음). Java 헬퍼를 파일 묶음(school/·app/ 폴더) 컴파일로 바꿈. 예제 대조 8건 통과(컴파일 성공 1·출력 5·컴파일 오류 2), 기대값을 틀리게 바꾸면 빌드가 멈추는 것 확인(std 출력·clash 오류). check 오류 0건(line_unread 1건 허용), pub 장면 넘침을 줄 수 축소로 해결, 자막 공백 0초, 렌더링 2:04.4, 1080×1920·오디오 확인.
