# 02: STEP 2 작업 맡기기 + STEP 3 값 돌려받기

**What to build:** 풀에 작업을 맡기고, 작업이 돌려준 값을 받는 장면 두 개를 대본 → 음성 → 화면까지 만든다. 두 장면 모두 화면 코드는 try-with-resources 블록까지 포함한 완전한 모양이다(따라 치면 실행되고 끝남).

- 공통 머리(33자 이하, 스펙에서 확정): `try (ExecutorService pool =` / `  Executors.newFixedThreadPool(2)` / `) {` … `}`
- submit: 블록 안에 `pool.submit(() ->` / `  System.out.println("민수 85"));`, 서준 92도 같게
  - `jmulti` + `same_lines("민수 85", "서준 92")`. 화면 고정 예시 `민수 85 / 서준 92`, 나레이션 "이번 실행에서는"
  - 22편 `new Thread(() -> …)` + `start()`와 비교해 람다식은 그대로이고 맡기는 방법만 바뀐다는 것이 보여야 한다(`.vs` 카드나 두 코드 블록 중 화면 높이를 보고 결정)
- future: `Future<Integer> f1 =` / `  pool.submit(() -> 85);`, f2(92)도 같게, `int sum = f1.get() + f2.get();`, `System.out.println(sum);`
  - `jmulti`로 매 실행 `177`
  - 퓨처는 화면에 처음 한 번 "(나중에 결과를 꺼내는 상자)"를 덧붙인다
  - 값을 돌려주는 작업을 `Callable`이라고 부른다는 것을 화면·나레이션에 한 번 보여 준다
  - `get()`은 작업이 끝날 때까지 기다렸다 꺼낸다. `main`의 `throws Exception`은 "겟도 예외를 던질 수 있어서"로만 설명(예외 이름은 말하지 않음). `throws Exception`이 붙은 `main` 줄을 화면에 보여 줄지는 높이를 보고 정하되, 따라 칠 때 필요하다는 것은 어딘가에 보여야 한다
- `import java.util.concurrent.*;`는 23편처럼 코드 위 라벨로 보여 준다

자세한 결정은 [../spec.md](../spec.md).

**Blocked by:** 01

**Status:** resolved

- [x] submit 예제가 `jmulti`로 20회 검증되고, 화면 고정 예시가 `each` 검사를 통과한다
- [x] future 예제가 `jmulti`로 20회 모두 `177`이고, 기대값을 일부러 틀리게 바꾸면 빌드가 멈춘다
- [x] 22편 방식과 submit 방식의 비교가 한 화면에 보인다
- [x] "퓨처(나중에 결과를 꺼내는 상자)"와 `Callable`이 화면에 나온다
- [x] 화면 코드를 그대로 따라 치면 컴파일·실행된다(import, `throws Exception`, try-with-resources 포함)
- [x] 코드 한 줄 33자 이하
- [x] 나레이션이 화면 결과와 같은지 직접 확인했다("백칠십칠", "이번 실행에서는")
- [x] `tools/verify-video.sh java-pool-shorts --no-render` 통과, future 장면을 390px 폭 시트에서 확인

## Comments

- 화면 코드는 `pool(body, make)` 헬퍼(build.py 지역)로 만든다: `try (ExecutorService pool =` / `  Executors.<make>` / `) {` … `}`. 모든 줄 33자 이하.
- submit: `jmulti` + `same_lines("민수 85", "서준 92")` 20회 통과. 결과 상자는 22편 `kterm`(민수 k1 주황, 서준 k2 초록). 22편 비교는 결과 상자 옆 `.note.cmp`(22편 `new Thread(…)` `.start()` / 오늘 `pool.submit(…)`), 아래 메모 "람다식은 그대로 · start() 없이 실행".
- future: `jmulti` 20회 모두 `177`. 기대값을 176으로 바꾸면 `future: a run printed '177\n', which the script's check rejects`로 멈춤. `main(…) throws Exception`은 코드 위 라벨("get()도 예외를 던질 수 있어서"), 퓨처 설명은 결과 옆 메모, `Callable`은 설명 줄에.
- import는 submit 장면 코드 위 라벨로만 보여 줌(future 장면은 높이 때문에 `throws Exception` 라벨로 대신).
- 390px 시트에서 future 장면(가장 빽빽함) 겹침 없음. sm 코드는 23편과 같은 크기.
