# 02: STEP 2 동기화 블록 + STEP 3 AtomicInteger

**What to build:** 22편의 `count` 예제를 두 가지 방법으로 고치는 장면 두 개를 대본 → 음성 → 화면까지 만든다.

- block: 잠금 객체 `static final Object lock =` / `new Object();`(두 줄)를 만들고, 반복 안의 `count++` 한 줄만 `synchronized (lock) { }`(세 줄)로 감싼다. `jmulti`로 매 실행 `20000`. 나레이션·화면에서 "필요한 줄만 잠근다"는 원칙과 "두 스레드가 **같은** 잠금 객체를 써야 한다"를 말하고 보여 준다. "더 빠르다"고 말하지 않는다
- atomic: `static AtomicInteger count =` / `new AtomicInteger();`, 반복 안은 `count.incrementAndGet();`, 출력은 `count.get()`. `jmulti`로 매 실행 `20000`. 22편의 읽기·더하기·쓰기를 한 번에 하는 원자적 연산이라고 설명하고, 화면에는 처음 한 번 "(쪼개지지 않는)"을 덧붙인다. 실행 코드에는 `java.util.concurrent.atomic` import를 넣는다(화면 표시 여부는 높이를 보고 결정)

자세한 결정은 [../spec.md](../spec.md).

**Blocked by:** 01

**Status:** resolved

- [x] block·atomic 예제가 각각 `jmulti`로 20회 검증되고, 기대값을 일부러 틀리게 바꾸면 빌드가 멈춘다
- [x] 잠금 객체가 두 스레드에 공통인 static 필드라는 점이 화면에 보인다
- [x] "원자적 연산(쪼개지지 않는)"이 화면에 처음 한 번 나온다
- [x] 코드 한 줄 33자 이하
- [x] 나레이션이 화면 결과와 같은지 직접 확인했다("항상 이만")
- [x] `tools/verify-video.sh java-sync-shorts --no-render` 통과, block 장면을 390px 폭 시트에서 확인

## Comments

- block은 main의 스레드 코드를 화면에서 숨기고(hidden) 멤버만 보여 줌. atomic은 `get()`을 보여야 해서 `// a·b start·join 뒤` 주석 + 출력 줄을 보이고 스레드 줄은 `pre=`로 숨김.
- import는 `J.IMPORTS = ["import java.util.concurrent.atomic.*;", ""]`로 실행 코드에 넣고, 화면에는 코드 위 라벨로 같은 줄을 보여 줌.
- 기대값 변경 시 빌드가 멈추는 것은 공용 `ALWAYS` 검사로 확인(01과 같은 검사). block·atomic 각 20회 모두 20000.

### 독립 검토 반영 (2026-11-24)

- atomic 출력 줄 위 주석을 `// main에서: a·b start·join 뒤`로 바꿔 클래스 안에 바로 문장이 있는 것처럼 보이지 않게 함.
- 강조 줄 `mark=(0, 1, 4, 7)`: 두 줄로 나눈 `AtomicInteger` 선언의 둘째 줄도 강조(block 장면과 같은 방식).
