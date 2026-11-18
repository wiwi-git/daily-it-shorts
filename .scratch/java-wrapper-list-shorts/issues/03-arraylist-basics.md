# 03: STEP 3 ArrayList 기본 + 범위 밖 오류

**What to build:** 이름 리스트를 만들고 넣고 꺼내는 기본 사용법을 배열과 비교해 보여 주는 두 장면을 만든다.
- list: `import java.util.ArrayList;`(15편 import 연결). `ArrayList<String> names = new ArrayList<>();`, `add("민수")`·`add("서준")`·`add("지우")` → `[민수, 서준, 지우]`, `size()` → `3`, `get(0)` → `민수`. 꺾쇠 안 = 담을 타입, 처음 한 번 "(제네릭)". `.vs` 카드로 배열과 비교(`arr[0]` ↔ `get(0)`, `.length` ↔ `size()`). 이름 색은 민수 k1·서준 k2·지우 k3
- idx: `names.get(3)` → `IndexOutOfBoundsException: Index 3 out of bounds for length 3`(`.warn`). 인덱스가 0부터인 건 배열과 같다. 진행 표시는 3번째 칸

**Blocked by:** 01

**Status:** resolved

- [x] list의 출력 세 가지가 빌드에서 대조되고, 화면 콘솔은 실제 결과로 그린다
- [x] idx의 예외 첫 줄이 빌드에서 대조된다
- [x] 이름 색이 이후 장면과 같은 k1/k2/k3이다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-18: 메인 세션에서 01~06을 한 번에 구현(12~16편과 같은 방식, 워크트리·서브에이전트 없음 — 모든 티켓이 같은 build.py·script.json을 고쳐 병렬 이득이 없음). 빌드 기반은 스펙의 16편 대신 단일 파일·실행 오류 헬퍼(jrt)가 이미 있는 14편(다형성)을 복사. `-g` 컴파일 추가, 결과 주석을 그 자리에서 출력해 대조하는 `jshow()`와 jce의 설명 줄 대조(`detail=`) 추가. 예제 대조 10건(출력 7·컴파일 오류 1·실행 중 오류 2) 통과, 기대값을 일부러 틀리게 바꾼 5가지 경우 모두 빌드가 멈춤. check 오류 0건(line_unread 경고 3건), 자막 공백 0초(반올림 0.001초), 대본 TTS 152.9초.
- 2026-11-18: 제네릭 설명 수정 — "꺾쇠 안에 담을 타입을 적어요. 이걸 제네릭이라고 해요"가 꺾쇠 안의 타입을 제네릭이라 부르는 것처럼 들려, "타입을 정하는 문법 = 제네릭, 문자열만 넣을 수 있다"로 바꿈(나레이션·설명 줄·메모·GLOSSARY·스펙). list 음성 재생성, check 오류 0건, 렌더링 2:45.2.
