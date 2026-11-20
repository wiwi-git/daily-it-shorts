# 02: STEP 2 스트림 3단계 + map

**What to build:** 스트림 코드를 읽는 순서와, 값을 바꾸는 `map`을 보여 주는 두 장면을 대본 → 음성 → 화면까지 만든다.
- flow: `scores.stream()` / `.filter(s -> s >= 80)` / `.toList()` 세 줄을 만들기 · 중간 연산 · 최종 연산 이름표와 함께 나레이션에 맞춰 한 줄씩 강조한다. 결과 `[85, 92]`. `.note`: 옛 코드에서는 `.collect(Collectors.toList())`
- map: `names.stream().map(n -> n + "님").toList()` → `[민수님, 서준님, 지우님]`. `map`은 값을 다른 값으로 바꾼다(`filter`는 거르기). 개수는 그대로. 진행 표시는 2번째 칸

색: 민수 k1·서준 k2·지우 k3, 점수 85=k1·92=k2·78=k3.

**Blocked by:** 01

**Status:** resolved

- [x] flow·map의 출력이 빌드에서 대조되고, 결과는 실제 결과로 그린다
- [x] flow의 단계 이름표와 강조가 나레이션 순서와 맞는다
- [x] `collect(Collectors.toList())`는 메모 한 줄로만 나오고, `toList()` 결과가 수정 불가라는 점은 다루지 않는다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-20: 메인 세션에서 01~06을 한 번에 구현(18편과 같은 방식, 모든 티켓이 같은 build.py·script.json을 고침. 저장소 규칙상 커밋하지 않아 통합 브랜치는 만들지 않음). 18편 build.py를 복사해 import에 Collectors·Stream 추가, `jrt(before=)`로 오류 전 출력도 대조, flow 단계 행을 나레이션 단어 시점에 강조. 예제 대조 출력 11건(why 2·flow 2·map·chain·sorted 2·count 2·once 해결)·실행 중 오류 1건(앞선 출력 3 포함)·실행 확인 1건 통과, 기대값을 일부러 틀리게 바꾼 5가지 경우 모두 빌드가 멈춤. 대본 TTS 115.1초(영상 119.4초). check 오류 0건(line_unread 경고 4건), 자막 공백 0.001초(반올림), why·once 장면 390px 폭 확인. 렌더링 1:59(1080×1920, 오디오 있음). 스펙과 다른 점: why 장면의 결과·원본 칩 두 줄은 하단 300px을 침범해 빼고, 코드의 `// scores → [85, 92, 78]` 줄을 강조로 대신함. count 장면에 `long` 타입이 화면에 나옴(나레이션은 언급 안 함).
