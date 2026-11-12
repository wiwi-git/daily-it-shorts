# 02: STEP 2 static 메소드 + 2-1 static 주의

**What to build:** STEP 2는 두 장면이다.
- smethod: `static int getCount()`를 만든다. 객체를 하나도 만들기 전에 `Student.getCount()`를 부르면 0이 나오고, 민수·지영을 만든 뒤에는 2가 나온다. 이 결과로 static 메소드는 객체 없이 호출할 수 있다는 것을 보여 준다.
- sme(주의할 점!): static 메소드 안에서 `score`를 쓰면 컴파일 오류가 나는 것을 보여 준다. 이유는 "객체 없이 실행되니 누구의 `score`인지 알 수 없다"로 설명한다. 지금까지 써 온 `main`도 static이라, 객체를 만들어 점으로 필드를 썼다는 메모를 넣는다.

진행 표시는 두 장면 모두 2번째 칸이다.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] smethod 예제가 빌드 중 실행되고, 출력 `0`, `2` 두 줄과 대조되어 통과한다
- [ ] sme 예제가 빌드 중 컴파일되고, 오류에 `non-static variable score cannot be referenced from a static context`가 포함되어야 통과한다
- [ ] 나레이션에서 말한 "main도 static" 내용이 화면 메모로 보인다
- [ ] 나레이션 문장의 결과("처음엔 영, 두 명을 만든 뒤엔 이")가 화면 결과와 같은지 직접 확인한다
- [ ] `hyperframes check` 오류 0건이고, snapshot으로 새 장면을 확인한다
