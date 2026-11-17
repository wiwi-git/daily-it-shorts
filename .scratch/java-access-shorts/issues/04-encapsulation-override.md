# 04: STEP 5 캡슐화 · 5-1 오버라이딩과 접근 범위

**What to build:** 진행 표시 5번째 칸의 두 장면을 대본 → 음성 → 화면까지 만든다.

- enc: 이 장면의 `Student`는 `private int score;` + `getScore()`·`setScore()`(0~100만 받음, 범위 검사 줄 `mark`). `s.setScore(-5)` 후 `s.getScore()` → `85`. `s.score = -5`는 `score has private access in Student`. 이것을 "캡슐화"라고 부른다(GLOSSARY: 캡슐화, getter / setter)
- ovr: `Teacher`(서준)의 `hello()`에서 `public`을 빼면 `hello() in Teacher cannot override hello() in Person`, 다음 줄 `attempting to assign weaker access privileges; was public`. 화면에는 다음 줄을 보여 준다. "범위를 좁힐 수 없다(넓히는 건 된다)"로 말한다. `.note`: 그래서 13편에서 인터페이스 메소드 구현에 `public`이 필수였다

**Blocked by:** 01

**Status:** resolved

- [x] enc의 출력 `85`와 오류 `score has private access in Student`가 빌드에서 대조된다
- [x] ovr의 오류 첫 줄과 다음 줄이 모두 빌드에서 대조된다
- [x] Teacher는 k3 색, 민수는 k2 색을 유지한다
- [x] 나레이션 문장("점수는 그대로 팔십오예요" 등)이 화면 결과와 같음을 직접 확인한다
- [x] `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-17: 나레이션 "넓히는 건 괜찮아요"를 위해 protected → public 넓히기도 컴파일 성공으로 확인하고 화면에 칩으로 보여 줌.
