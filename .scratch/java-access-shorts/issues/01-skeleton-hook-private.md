# 01: 프로젝트 골격 + 오류 다음 줄 대조 + 도입·STEP 1 private

**What to build:** 패키지 편(15편)과 같은 방식·템포(1.2배)로 접근 제어자 영상 프로젝트를 만든다. 상단 바 브랜드는 "자바 입문 접근 제어자 정리"로 하고, "접근 제어자"를 주황으로 강조한다. 진행 표시는 5칸이다.

15편의 파일 묶음 컴파일 헬퍼를 그대로 쓰되, 컴파일 오류 대조가 javac 오류의 **다음 줄**(예: `attempting to assign weaker access privileges; was public`)까지 대조할 수 있게 넓힌다. 기본 묶음은 다음 다섯 파일이고, 장면마다 바뀐 파일만 넘긴다.
- `school.Person`(k1): `public abstract class`, 필드 `public String name` · `protected int age` · `String phone` · `private String pw`, `public` 생성자, `pw`를 쓰는 `public boolean check(String)`, `public abstract void hello()`
- `school.Student`(k2): 민수·나이 17·점수 85, `public` 생성자, `public void hello()`
- `school.Teacher`(k3): 서준, `public void hello()`
- `app.Tutor`: `public class Tutor extends Person`, 지우·나이 20, `age`를 쓰는 `hello()` → `튜터 지우 20살`
- `app.Main`: 다른 패키지에서 접근하는 문장은 모두 이 클래스의 `main` 안에서 실행된다

이 티켓에서 **영상 전체 대본**을 먼저 쓰고 길이(3분 이하)를 확인한다. 그 다음 도입과 STEP 1을 대본 → 음성 → 화면까지 만든다.
- hook: "자바 입문 열여섯 번째, 접근 제어자", `public`·`protected`·기본·`private` 네 칩
- priv: `private String pw;`(`mark`). `Person` 안의 `check()`로 `s.check("1234")` → `true`. 같은 패키지의 자식 `Student`에서 `pw`를 쓰면 `pw has private access in Person`(`.warn`). 범위 칩: 같은 클래스만 ✅

이 장면들만으로 볼 수 있는 빌드가 나와야 한다.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] 새 영상 프로젝트가 15편의 음성 생성·빌드 스크립트를 기반으로 만들어지고, 디자인 토큰·글꼴·모션은 그대로다
- [x] 오류 대조가 첫 오류 줄과 다음 줄을 모두 대조할 수 있고, 기대값을 일부러 틀리게 바꾸면 빌드가 멈춘다
- [x] 기본 묶음 전체가 컴파일 성공으로 확인되고, 예제 목록 파일에 파일별로 기록된다
- [x] priv의 출력 `true`와 오류 `pw has private access in Person`이 빌드에서 대조된다
- [x] 대본 전체가 GLOSSARY 표기(접근 제어자·기본 접근·캡슐화·getter / setter)를 쓰고, "접근 제한자·접근 지정자·default 접근·디폴트"를 쓰지 않는다. 기본 접근을 처음 말할 때 "아무것도 안 붙이면"을 함께 말한다. 영어 키워드는 한글 발음으로 쓴다
- [x] 대본 전체 길이가 3분 이하임을 음성 생성 전에 확인한다
- [x] 코드 한 줄이 33자 이하이고, 하단 약 300px에 본문이 없다
- [x] `hyperframes check` 오류 0건이고, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-17: 메인 세션에서 01~05를 한 번에 구현(15편과 같은 방식, 워크트리·서브에이전트 없음). 오류 대조가 javac 오류 블록 전체(캐럿 아래 설명 줄 포함)를 보도록 넓힘(`detail=`). 필드 이름은 읽기 쉽게 `pw` → `password`로 바꿈. 기대값을 일부러 틀리게 바꾸면 빌드가 멈추는 것 확인(표 1칸·ovr 설명 줄·enc 출력). 대본 전체 TTS 154.6초.
