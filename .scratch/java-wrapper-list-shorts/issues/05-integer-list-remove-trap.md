# 05: STEP 5 List<Integer>로 점수 모으기 + remove(1) 함정

**What to build:** 래퍼 클래스와 List를 합쳐 점수 리스트를 만들고, 숫자 리스트에서만 생기는 `remove` 함정을 보여 주는 두 장면을 만든다.
- nums: `ArrayList<int>` → 컴파일 오류 `unexpected type` / 설명 줄 `required: reference`(`.warn`, 화면에는 "꺾쇠 안에 기본 타입은 안 됨 → `Integer`"로 풀고 원문은 작게). `List<Integer> scores = new ArrayList<>();`(긴 줄은 `=` 뒤에서 줄바꿈), `add(85)`·`add(92)`·`add(78)`, 향상된 for(7편)로 합계 → `255`(꺼낼 때 자동 언박싱). `.note`: 변수 타입은 기본적으로 `List`로 받는다 — `List`는 인터페이스, `ArrayList`는 구현 클래스, 14편 업캐스팅
- rm: `[85, 92, 78]`에서 `scores.remove(1)` → `[85, 78]`(값 1이 아니라 1번 칸, `.warn`). 값으로 지우려면 `scores.remove(Integer.valueOf(85))` → `[92, 78]`(각각 새 리스트에서 시작). 진행 표시는 5번째 칸

**Blocked by:** 01

**Status:** resolved

- [x] nums의 컴파일 오류(첫 줄 + 설명 줄)와 출력 `255`가 빌드에서 대조된다
- [x] rm의 두 출력이 빌드에서 대조된다
- [x] `remove(1)`을 "인덱스를 받는 remove가 먼저 선택된다"로 말하고, 오버로딩 선택 규칙 세부는 다루지 않는다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-18: 메인 세션에서 01~06을 한 번에 구현(12~16편과 같은 방식, 워크트리·서브에이전트 없음 — 모든 티켓이 같은 build.py·script.json을 고쳐 병렬 이득이 없음). 빌드 기반은 스펙의 16편 대신 단일 파일·실행 오류 헬퍼(jrt)가 이미 있는 14편(다형성)을 복사. `-g` 컴파일 추가, 결과 주석을 그 자리에서 출력해 대조하는 `jshow()`와 jce의 설명 줄 대조(`detail=`) 추가. 예제 대조 10건(출력 7·컴파일 오류 1·실행 중 오류 2) 통과, 기대값을 일부러 틀리게 바꾼 5가지 경우 모두 빌드가 멈춤. check 오류 0건(line_unread 경고 3건), 자막 공백 0초(반올림 0.001초), 대본 TTS 152.9초.
