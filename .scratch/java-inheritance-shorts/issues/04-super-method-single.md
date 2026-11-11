# 04: STEP 5 super.hello() + 5-1 단일 상속

**What to build:** STEP 5에서는 Student가 오버라이딩한 `hello()` 안에서 `super.hello()`를 먼저 부르고 점수를 출력한다. 결과로 "민수 안녕", "점수 85" 두 줄이 나오는 것을 보여 주고, `super()`와 `super.메소드()`의 차이를 구분한다. 5-1에서는 `extends Person, Teacher`가 컴파일 오류를 내는 것을 보여 주고 "부모 클래스는 하나만"으로 마무리한다.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] STEP 5 예제의 실제 출력이 "민수 안녕", "점수 85"와 대조되어 통과한다
- [ ] 5-1 예제가 실제 컴파일 오류를 내는지 빌드가 대조한다
- [ ] 여러 단계 상속·인터페이스는 언급하지 않는다
- [ ] 진행 표시가 5번 칸이다(5-1 포함)
- [ ] `hyperframes check` 오류 0건, snapshot 확인
