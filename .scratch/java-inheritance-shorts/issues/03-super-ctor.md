# 03: STEP 4 super() + 4-1 주의

**What to build:** STEP 4에서는 생성자를 처음 등장시킨다. `Person(String name)`과, `super(name)` 뒤에 점수를 채우는 `Student(String name, int score)`를 쓴다. 각 생성자에 출력문을 한 줄씩 넣어, 부모 생성자가 먼저 실행된다는 것을 실행 결과로 보여 준다. 4-1에서는 `super(name);`을 빼면 컴파일 오류가 나는 것을 보여 주고, 지난 영상의 "생성자를 직접 만들면 기본 생성자가 생기지 않는다"와 연결해 설명한다. Person과 Student만 사용한다.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] STEP 4 예제의 실제 출력이 부모 생성자의 출력 → 자식 생성자의 출력 순서와 대조되어 통과한다
- [ ] 4-1 예제가 실제 컴파일 오류를 내는지 빌드가 대조한다
- [ ] 화면과 나레이션이 `super()`를 "부모 생성자 호출"로 설명한다
- [ ] 진행 표시가 4번 칸이다(4-1 포함)
- [ ] `hyperframes check` 오류 0건, snapshot 확인
