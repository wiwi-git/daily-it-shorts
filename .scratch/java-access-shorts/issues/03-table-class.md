# 03: 4-1 네 단계 표 · 4-2 클래스에는 둘만

**What to build:** 진행 표시 4번째 칸에 속하는 두 장면을 대본 → 음성 → 화면까지 만든다.

- table: 4×4 표(행: public·protected·기본·private / 열: 같은 클래스·같은 패키지·다른 패키지의 자식·다른 패키지 전체). 16칸을 **실제 컴파일로 확인한 결과로 그린다**(직접 적지 않는다). 각 접근 제어자의 필드를 네 위치(`Person` 안, `school`의 자식이 아닌 다른 클래스, `app.Tutor` 안, `app.Main`)에서 접근해 성공·실패를 얻는다. "같은 패키지" 열은 자식이 아닌 클래스로 확인한다. 기존 `table()` 헬퍼와 빨간 표시를 재사용하고 새 디자인 토큰은 추가하지 않는다
- cls: 파일에 바로 쓰는 클래스(최상위 클래스)에는 `public`과 기본 접근만. `private class Club` → `modifier private not allowed here`. 중첩 클래스는 다루지 않으므로 "최상위/파일에 바로 쓰는" 클래스로 한정해 말한다

**Blocked by:** 02

**Status:** resolved

- [x] 표 16칸이 실제 컴파일 결과로 그려지고, 기대 표와 다르면 빌드가 멈춘다
- [x] 표의 각 행이 02까지의 단계 칩과 같은 ✅/❌다
- [x] cls 오류 `modifier private not allowed here`가 빌드에서 대조된다
- [x] 표를 390px 폭으로 줄여도 읽힌다
- [x] `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-17: 표 16칸을 매 빌드마다 실제 컴파일(Person 안 · school.Desk · app.Tutor 안 · app.Main)로 계산하고, 단계 장면의 범위 칩도 같은 결과로 그림. 결과는 examples.txt에 O/X로 기록.
