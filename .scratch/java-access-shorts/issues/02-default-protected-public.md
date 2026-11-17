# 02: STEP 2 기본 접근 · STEP 3 protected · STEP 4 public

**What to build:** 단계 장면 세 개를 priv와 같은 모양(필드 선언 `mark` → 되는 코드와 결과 → 안 되는 코드와 오류 `.warn` → 네 위치 범위 칩)으로 대본 → 음성 → 화면까지 만든다.

- dflt(진행 2): `String phone;`(아무것도 안 붙임). 화면에 처음 한 번 "(아무것도 안 붙임 = 같은 패키지 전용)". `school.Student` 안에서 `phone` → `010-1234`. `app.Main`에서 `s.phone` → `phone is not public in Person; cannot be accessed from outside package`. `.note`: `default`라고 적는 게 아님 — 빌드는 `default int x;`가 `modifier default not allowed here`인지 확인한다(화면에 문구는 선택)
- prot(진행 3): `protected int age;`. `app.Tutor`(다른 패키지의 자식) 안에서 → `튜터 지우 20살`. `app.Main`에서 `s.age` → `age has protected access in Person`. "같은 패키지, 그리고 다른 패키지의 자식"으로 말하고 "자식만"이라고 말하지 않는다
- pub(진행 4): `public String name;`. `app.Main`에서 `s.name` → `민수`. 15편에서 클래스·생성자·메소드에 붙였던 그 `public`임을 연결한다

**Blocked by:** 01

**Status:** resolved

- [x] 출력 3건(`010-1234`, `튜터 지우 20살`, `민수`)과 오류 4건(dflt·`default` 메모·prot의 문구)이 빌드에서 대조된다
- [x] 범위 칩의 ✅/❌가 GLOSSARY·스펙의 정의와 같다(protected는 같은 패키지 ✅)
- [x] 세 장면이 priv와 같은 배치이고, 대상별 색(Person k1 · 민수 k2)을 유지한다
- [x] 나레이션 문장이 화면의 결과·오류와 같음을 직접 확인한다
- [x] `hyperframes check` 오류 0건, snapshot으로 세 장면을 확인한다

## Comments

- 2026-11-17: dflt 장면이 자막과 겹쳐 `default`라고 적지 않는다는 메모를 Person 코드 블록의 둘째 줄(`default String phone; // 오류`)로 합침. 빌드는 이 줄을 실제 Person에 넣어 `modifier default not allowed here`를 대조. Student 코드는 `System.out.println(phone);` 한 줄로 줄임. Tutor 출력 색은 Teacher(k3)와 구분해 파랑(k4).
