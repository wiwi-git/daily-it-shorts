# 03: STEP 4 스레드 안전 리스트

**What to build:** 컬렉션도 경쟁 조건에 걸린다는 것을 보여 주고 고치는 장면을 대본 → 음성 → 화면까지 만든다.

- `static List<Integer> list = new ArrayList<>();`(33자 넘으면 나눔)에 두 스레드가 각각 10000번 `add`, 둘 다 `join` 뒤 `list.size()` 출력
  - `jmulti`: `each` = 크기가 20000 이하, `all_` = 한 번 이상 20000 미만
  - 화면은 고정 예시 `14302`, 라벨 "실행 결과 예시 · 매번 다름"
  - 일부 실행에서 작업 스레드가 `ArrayIndexOutOfBoundsException`으로 끝나지만 종료 코드는 0이라 `jmulti`는 출력(크기)만 검사한다. 헬퍼는 고치지 않는다
  - 화면에 예외 상자는 그리지 않고, `.warn` 한 줄과 나레이션으로 "값이 빠지거나 예외가 나기도 해요"를 알린다. 결과 숫자는 말하지 않는다("이만보다 적게, 실행할 때마다 달라요")
- `Collections.synchronizedList(` / `new ArrayList<>());`로 바꾸면 `jmulti`로 매 실행 `20000`. "스레드 안전"의 뜻을 말한다. "이제 어떤 사용이든 안전하다"처럼 넓게 말하지 않는다
- 실행 코드에는 `java.util` import를 넣는다(화면 표시 여부는 높이를 보고 결정)

자세한 결정은 [../spec.md](../spec.md).

**Blocked by:** 01

**Status:** resolved

- [x] ArrayList 예제가 `jmulti`로 20회 검증되고(20000 이하 + 한 번 이상 미만), 화면 예시 `14302`가 `each` 검사를 통과한다
- [x] synchronizedList 예제가 `jmulti`로 20회 모두 `20000`이고, 기대값을 일부러 틀리게 바꾸면 빌드가 멈춘다
- [x] 예외 가능성이 `.warn`으로 화면에 보인다
- [x] 코드 한 줄 33자 이하
- [x] 나레이션이 화면 결과와 같은지 직접 확인했다
- [x] `tools/verify-video.sh java-sync-shorts --no-render` 통과, list 장면을 390px 폭 시트에서 확인

## Comments

- ArrayList 버전: 빌드의 20회 실행이 검사(매번 20000 이하 + 한 번 이상 미만)를 통과. 화면 예시 `14302`는 기획 중 실제 실행에서 나온 값(기획 때 50회 관찰: 대부분 13000~15250, 예외로 스레드 하나가 끝난 실행은 약 10000).
- 검사를 `int(o) <= 100`으로 바꾸면 `list: a run printed '14317\n', which the script's check rejects`로 멈춤.
- synchronizedList 버전은 실행만 검증(`list-sync`)하고 화면에는 바뀐 선언 3줄만 `code()`로 그림.
- 장면이 빽빽해 `#sc-list`의 간격·결과 숫자·메모 크기를 줄임. 390px 폭 시트에서 자막과 겹치지 않음 확인.

### 독립 검토 반영 (2026-11-24)

- 화면대로 따라 치면 컴파일되도록 atomic 장면처럼 코드 위 라벨로 `import java.util.*;`를 보여 줌. 라벨을 넣어도 자막과 겹치지 않음(snapshot 확인).
