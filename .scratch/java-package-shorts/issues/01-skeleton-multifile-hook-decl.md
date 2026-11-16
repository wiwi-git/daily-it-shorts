# 01: 프로젝트 골격 + 여러 파일 컴파일 헬퍼 + 도입·STEP 1 package 선언

**What to build:** 다형성 편(14편)과 같은 방식·템포(1.2배)로 패키지 영상 프로젝트를 만든다. 상단 바 브랜드는 "자바 입문 패키지 정리"로 하고, "패키지"를 주황으로 강조한다.

빌드의 Java 실행 헬퍼를 넓힌다. 지금은 `Main.java` 한 파일만 받는데, "경로 → 소스"로 된 파일 묶음을 받도록 바꾼다. 묶음을 폴더 구조 그대로 임시 디렉터리에 쓰고, 한 번에 컴파일한 뒤 `app.Main`을 실행한다. 출력 대조, 컴파일 오류 대조, 예제 기록의 인터페이스는 기존 헬퍼와 같은 모양으로 유지한다. 예제 기록은 파일별로 남긴다. 기본 묶음은 다음 네 파일이고, 장면마다 바뀐 파일만 넘긴다.
- `school/Person.java`: `public abstract class Person`, `String name`, `public` 생성자, `public abstract void hello()`
- `school/Student.java`: `public class Student extends Person`, `int score`, `public` 생성자, `public void hello()` → `"학생 " + name + " 안녕"`
- `school/Teacher.java`: `public class Teacher extends Person`, `public void hello()` → `name + " 선생님 안녕"`
- `app/Main.java`: `public class Main`, 예제 문장은 이 클래스의 `main` 안에서 실행된다

도입("자바 입문 열다섯 번째, 패키지")과 STEP 1을 대본 → 음성 → 화면까지 만든다.
- decl: `package school;` 한 줄과 파일 트리(`school/Person.java`·`Student.java`·`Teacher.java`, `app/Main.java`)를 함께 보여 준다. 패키지는 클래스를 묶는 이름이고, 패키지 이름과 폴더를 맞춰 둔다(자바가 클래스를 찾는 기준). 컴파일러가 강제하는 절대 규칙처럼 말하지 않는다. `.note` 한 줄: 실무 관례 `com.example.school`(소문자, 도메인을 거꾸로).

대본은 이 티켓에서 영상 전체를 먼저 쓰고 길이(3분 이하)를 확인한다. 이 장면들만으로 볼 수 있는 빌드가 나와야 한다.

**Blocked by:** 없음 (다형성 편 04 완료)

**Status:** resolved

- [x] 새 영상 프로젝트가 14편의 음성 생성·빌드 스크립트를 기반으로 만들어지고, 디자인 토큰·글꼴·모션은 그대로다
- [x] Java 헬퍼가 파일 묶음을 폴더 구조로 컴파일·실행하고, 기대와 다르면 빌드가 멈춘다(기대값을 일부러 틀리게 바꿔 확인)
- [x] decl의 기본 묶음 전체가 컴파일 성공으로 확인되고, 예제 목록 파일에 파일별로 기록된다
- [x] 파일 트리와 패키지 이름이 대상별 색(Person k1 · Student k2 · Teacher k3)을 쓴다
- [x] 대본 전체가 GLOSSARY 표기(패키지·import·전체 이름)를 쓰고, "풀 네임·정규화된 이름·불러오기(단독 표기)"를 쓰지 않는다. 영어 키워드는 한글 발음으로 쓴다
- [x] 대본 전체 길이가 3분 이하임을 음성 생성 전에 확인한다
- [x] 코드 한 줄이 33자 이하이고, 하단 약 300px에 본문이 없다
- [x] `hyperframes check` 오류 0건이고, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-16: Opus가 메인 세션에서 01~04를 한 번에 구현(워크트리·서브에이전트 없음). Java 헬퍼를 파일 묶음(school/·app/ 폴더) 컴파일로 바꿈. 예제 대조 8건 통과(컴파일 성공 1·출력 5·컴파일 오류 2), 기대값을 틀리게 바꾸면 빌드가 멈추는 것 확인(std 출력·clash 오류). check 오류 0건(line_unread 1건 허용), pub 장면 넘침을 줄 수 축소로 해결, 자막 공백 0초, 렌더링 2:04.4, 1080×1920·오디오 확인.
