# 01: 프로젝트 골격 + 도입·STEP 1 extends

**What to build:** 상속 영상 프로젝트를 직전 영상(메소드와 생성자)과 같은 방식·템포(1.2배)로 만든다. 상단 바 브랜드는 "자바 상속 정리"("상속" 주황)로 한다. 도입("자바 입문 열 번째, 클래스의 상속")과 STEP 1을 대본 → 음성 → 화면까지 만든다. STEP 1은 Student·Teacher에 중복된 `name`·`hello()`를 보여 준 뒤, 부모 클래스 Person으로 빼고 `extends Person`을 붙인다. 비유는 한 문장만 넣는다. 이 두 장면만으로 볼 수 있는 빌드가 나와야 한다.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 새 영상 프로젝트가 직전 영상의 음성 생성·빌드 스크립트를 기반으로 만들어지고, 디자인 토큰·글꼴·모션은 그대로다
- [ ] Person=k1, Student=k2, Teacher=k3 색이 코드와 표에 적용된다
- [ ] STEP 1의 예제(중복 버전, extends 버전)가 빌드 중 실제로 컴파일되어 통과한다
- [ ] 대본은 GLOSSARY 표기(부모 클래스·자식 클래스)를 쓰고, 영어 키워드는 한글 발음으로 쓴다
- [ ] 코드 한 줄이 33자 이하이고 하단 약 300px에 본문이 없다
- [ ] `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다
