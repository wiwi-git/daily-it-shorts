# Next.js 1편 클로저 — 기획 결정 (grill 결과, 2026-11-24)

배경 자료: [closure-reading.md](closure-reading.md)

- **중심**: 자바스크립트 클로저 + 자바 비교가 본론. Next.js/React는 STEP 5에서 "실무에서는 이렇게"로
- **시리즈**: 새 Next.js 시리즈 1편(자바 입문 번호 없음). 폴더 `nextjs-closure-shorts`, 브랜드 `<b>Next.js <em>클로저</em> 정리</b>`, README 영상 목록은 기존 표에 한 줄
- **대상**: 자바 시리즈 시청자(람다식·사실상 final은 앎, 자바스크립트 문법은 처음). JS 문법은 화면 메모로 자바와 대응시켜 설명(`() => x` = `() -> x`)
- **두 언어 구분**: 위아래로 쌓은 비교 카드(2열 `.vs`는 33자 코드가 안 들어감, 코드 `sm`), 라벨 "JavaScript"/"Java", 라벨 색 JS=`--blue`·Java=`--green`(영상 전용 CSS — 기존 k1은 주황이라 쓰지 않음), 하이라이터는 기존 것 + 자바스크립트 키워드 추가
- **검증**: `tools/javashorts.py`에 node 실행·대조 헬퍼 추가. React/Next.js 코드는 실행 없이 보여주기만, 나레이션은 공식 문서 범위 안에서만
- **예시 데이터**: 카운터(`count`)로 통일(STEP 1·3·5-1). STEP 2의 `x`, STEP 4 반복 변수만 별도 짧은 예제
- **용어**: GLOSSARY.md의 클로저·붙잡다·스냅샷

## 장면

| 장면 | 내용 |
|---|---|
| 도입 | "같은 코드인데 자바스크립트는 2, 자바는 컴파일 오류?" (`.hook` + `.big`) |
| STEP 1 클로저란 | JS `makeCounter` → `1 2 1`, 함수가 끝나도 `count`가 살아 있음 |
| STEP 2 변수를 붙잡는다 | JS `x = 2` 후 `f()` → `2` / 자바 같은 코드 컴파일 오류 (`.vs`) |
| STEP 3 자바는 왜? | JLS 이유: 동시성 문제. 우회 `int[] count = {0}` → `1 2 1`. `.note`: 실무는 `AtomicInteger` — 22편 스레드 참고(나레이션에서도 한 번 언급) |
| STEP 4 반복문 함정 | `var` → `3,3,3`, `let` → `0,1,2` / 자바 일반 `for` 오류, 향상된 `for` 가능 (`.vs`) |
| STEP 5-1 React 스냅샷 | `+5` 클릭 3초 뒤 알림 `0`, 해결은 업데이터 `c => c + 1` (실행 없음) |
| STEP 5-2 서버 액션 | 공식 예제를 33자 이하로 축약(`version`, `getVersion()`). 붙잡은 변수가 브라우저를 오감 → 자동 암호화 → 암호화만 믿지 말 것 (`.warn`) |
| 정리 | 다섯 줄 요약 한 줄씩 강조 + 👍 구독 · 좋아요 |

범위 밖: `this`, 지역·익명 클래스, `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`. 목표 길이 2:30 안팎.

## 대본 발음

넥스트 제이에스(Next.js) · 바/렛/콘스트(`var`/`let`/`const`) · 유즈 서버(`"use server"`) · 유즈 스테이트(`useState`) · 아토믹 인티저(`AtomicInteger`) · 인트 배열(`int[]`). TTS로 들어 보고 어색한 것만 수정.
