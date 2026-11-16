# 03: STEP 4 표준 라이브러리·java.lang + STEP 5 같은 이름 클래스

**What to build:** 세 장면을 대본 → 음성 → 화면까지 만든다.
- std(STEP 4): `import java.util.Arrays;` → `int[] scores = {85, 90, 70};` → `Arrays.sort(scores);` → `Arrays.toString(scores)` 출력 → `[70, 85, 90]`. 자바가 미리 만들어 둔 기능도 패키지로 묶여 있고, import해서 가져다 쓴다고 설명한다. `.note` 한 줄: `import java.util.*;`는 그 패키지의 클래스를 모두 쓰게 해 준다.
- lang(4-1): `String`·`System`은 `java.lang` 패키지라서 import 없이 쓴다. `java.lang.String name = "민수";`처럼 전체 이름으로 써도 같다는 것을 보여 주고, 출력 `민수`를 보여 준다.
- clash(STEP 5): `import java.util.Date;`와 `import java.sql.Date;`를 둘 다 쓰면 컴파일 오류가 난다. 해결 코드에서는 `java.util.Date`를 import하고, `java.sql.Date`는 전체 이름으로 쓴다. `java.sql.Date.valueOf("2026-11-16")`를 출력하면 `2026-11-16`이 나온다. `java.util.Date`는 선언만 하고 출력하지 않는다(실행 시각에 따라 결과가 달라지므로). `=` 뒤에서 줄을 바꿔 한 줄 33자 이하를 지킨다. 화면이 좁으면 오류 예제는 import 두 줄과 오류 문구만 보여 준다.

진행 표시는 std·lang이 4번째 칸, clash가 5번째 칸이다.

**Blocked by:** 02

**Status:** resolved

- [x] std 예제가 빌드 중 실행되고, 출력 `[70, 85, 90]`과 대조되어 통과한다
- [x] lang 예제가 빌드 중 실행되고, 출력 `민수`와 대조되어 통과한다
- [x] clash의 두 import가 javac의 `a type with the same simple name is already defined by the single-type-import of Date`와 대조되어 통과한다
- [x] clash 해결 예제가 빌드 중 실행되고, 출력 `2026-11-16`과 대조되어 통과한다
- [x] 나레이션 문장이 화면의 기대 결과와 같은지 직접 확인한다(예: 70, 85, 90 순서)
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 세 장면을 확인한다(clash는 390px 폭으로도 확인)

## Comments

- 2026-11-16: Opus가 메인 세션에서 01~04를 한 번에 구현(워크트리·서브에이전트 없음). Java 헬퍼를 파일 묶음(school/·app/ 폴더) 컴파일로 바꿈. 예제 대조 8건 통과(컴파일 성공 1·출력 5·컴파일 오류 2), 기대값을 틀리게 바꾸면 빌드가 멈추는 것 확인(std 출력·clash 오류). check 오류 0건(line_unread 1건 허용), pub 장면 넘침을 줄 수 축소로 해결, 자막 공백 0초, 렌더링 2:04.4, 1080×1920·오디오 확인.
