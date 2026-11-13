# 03: STEP 3 부모 타입의 한계 + STEP 4 다운캐스팅·잘못된 캐스트

**What to build:** 세 장면을 대본 → 음성 → 화면까지 만든다.
- limit(STEP 3): `Person p`로 `p.score`를 쓰면 컴파일 오류가 난다. Person에는 score가 없다. 오류 아래에 "컴파일러는 변수 타입만 본다" 메모를 두어, STEP 1의 "실행은 실제 객체 기준"과 대비한다.
- down(STEP 4): `if (p instanceof Student)`로 먼저 확인하고 `Student s = (Student) p;`로 바꾼 뒤 `s.score`를 출력하면 `85`가 나온다. 다운캐스팅이며, 화면에 처음 한 번 "(부모 → 자식 타입)"을 덧붙인다. 메모 한 줄: `p instanceof Student s`로 줄여 쓸 수 있다(Java 16+).
- cce(4-1): Teacher가 담긴 `p`를 `(Student) p`로 바꾸면 컴파일은 되지만 실행 중 `ClassCastException`이 난다. `.warn`으로 "컴파일은 OK, 실행 중 오류"를 강조한다. 화면에는 `ClassCastException`과 앞부분만 보여 주고 모듈·로더 설명은 생략한다.

빌드에 실행 중 오류를 기대값과 대조하는 헬퍼가 없으면, 출력·컴파일 오류 대조 헬퍼와 같은 모양으로 이 티켓에서 추가하고 예제 목록 파일에도 기록한다.

**Blocked by:** 02

**Status:** resolved

- [x] limit 오류가 javac의 `cannot find symbol`과 대조되어 통과한다
- [x] down 예제(기본 형태와 패턴 매칭 형태)가 빌드 중 실행되고, 출력 `85`와 대조되어 통과한다
- [x] cce 예제가 컴파일되고, 실행 중 오류 `java.lang.ClassCastException: class Teacher cannot be cast to class Student`와 대조되어 통과한다
- [x] 실행 중 오류 대조가 빌드를 멈출 수 있다(기대와 다르면 빌드 실패)
- [x] 나레이션에서 말한 `instanceof`·캐스트·패턴 매칭 메모가 모두 화면에 보인다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 세 장면을 확인한다(down은 390px 폭으로도 확인)

## Comments

- 2026-11-13: Opus가 메인 세션에서 직접 구현(워크트리·서브에이전트 없음). 첫 빌드에서 예제 대조 9건 통과(출력 6·컴파일 성공 1·컴파일 오류 1·실행 중 오류 1). 실행 중 오류 헬퍼(jrt)는 이미 있어 cls 인자만 추가, 기대값을 틀리게 바꾸면 빌드가 멈추는 것 확인. check 오류 0건, 자막 공백 0초(반올림 0.001초), 렌더링 1:50.0.
