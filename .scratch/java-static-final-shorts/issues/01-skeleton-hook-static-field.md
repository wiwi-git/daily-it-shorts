# 01: 프로젝트 골격 + 도입·STEP 1 static 필드

**What to build:** 상속 편과 같은 방식·템포(1.2배)로 static과 final 영상 프로젝트를 만든다. 상단 바 브랜드는 "자바 입문 static·final 정리"로 하고, "static·final"을 주황으로 강조한다.

도입("자바 입문 열한 번째, static과 final")과 STEP 1을 대본 → 음성 → 화면까지 만든다. STEP 1은 두 장면이다.
- sfield: `Student`의 인스턴스 필드 `score`와 static 필드 `count`를 비교 카드로 대비하고, 생성자에서 `count++` 한다.
- sfrun: 민수·85, 지영·92를 만든 뒤 `Student.count`를 출력하면 2가 나온다.

이 장면들만으로 볼 수 있는 빌드가 나와야 한다.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 새 영상 프로젝트가 상속 편의 음성 생성·빌드 스크립트를 기반으로 만들어지고, 디자인 토큰·글꼴·모션은 그대로다(`SPEED = 1.2`, TTS `+34%`)
- [ ] `Student`는 부모 클래스 없는 단독 클래스이고 색 k2를 쓴다
- [ ] sfrun 예제가 빌드 중 실제로 실행되고, 출력 `2`와 대조되어 통과한다
- [ ] static 필드는 항상 `Student.count`처럼 클래스 이름으로 쓴다
- [ ] "인스턴스 필드"에는 처음 한 번 "(객체마다 따로)"를 덧붙인다. 대본은 GLOSSARY 표기를 쓰고, 영어 키워드는 한글 발음으로 쓴다
- [ ] 코드 한 줄이 33자 이하이고, 하단 약 300px에 본문이 없다
- [ ] `hyperframes check` 오류 0건이고, snapshot으로 세 장면을 확인한다
