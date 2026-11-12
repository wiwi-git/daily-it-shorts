# 03: STEP 3 final 변수·필드 + 3-1 final 주의

**What to build:** STEP 3은 세 장면이다.
- fvar: `final int x = 10;` 뒤에 `x = 20;`이면 컴파일 오류가 난다.
- ffield: `Student`의 `name`을 `final String name`으로 바꾼다. 생성자에서 한 번 대입하는 것은 되고, 나중에 `s1.name = ...`이면 컴파일 오류가 난다. 이름은 한 번 정하면 바뀌지 않고 점수는 계속 바뀌는 값이라 `name`만 final로 했다는 이유를 말한다.
- fref(주의할 점!): `final Student s`라도 `s.score = 100`은 되고 출력은 100이다. `s = new Student(...)`만 컴파일 오류다. 클래스 편의 "참조 주의"와 연결한다.

진행 표시는 세 장면 모두 3번째 칸이다.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] fvar·ffield의 오류 예제와 fref의 둘째 블록이 빌드 중 컴파일되고, 오류에 `cannot assign a value to final variable`이 포함되어야 통과한다
- [ ] fref의 첫 블록이 빌드 중 실행되고, 출력 `100`과 대조되어 통과한다
- [ ] 이 티켓 이후 `Student`의 `name`은 final이고, 생성자로만 값을 넣는다(앞 장면 예제도 계속 통과한다)
- [ ] 대본은 final 변수를 "상수"라고 부르지 않는다
- [ ] `hyperframes check` 오류 0건이고, snapshot으로 새 장면을 확인한다
