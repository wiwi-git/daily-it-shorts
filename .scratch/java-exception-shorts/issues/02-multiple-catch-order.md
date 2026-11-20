# 02: STEP 2 여러 catch + catch 순서 함정

**What to build:** 예외 종류마다 `catch`를 따로 쓰는 법과, 순서를 잘못 쓰면 컴파일 오류가 나는 함정을 보여 주는 두 장면.
- kinds: `Integer.parseInt("abc")` → `NumberFormatException`, `int[] scores = {85, 92, 78}`의 `scores[3]` → `ArrayIndexOutOfBoundsException`. 각각 `catch`로 잡아 `e.getMessage()`를 출력(`For input string: "abc"`, `Index 3 out of bounds for length 3`)
- order: `catch (Exception e)`를 위에 먼저 쓰면 아래 `catch (ArithmeticException e)`가 컴파일 오류(`exception ArithmeticException has already been caught`). 이유는 `Exception`이 예외 클래스들의 부모 클래스라 먼저 다 잡기 때문. "구체적인 예외부터 위에"

진행 표시는 둘 다 2번째 칸.

**Blocked by:** 01

**Status:** resolved

- [x] kinds의 출력 2건이 빌드에서 대조되고 화면 상자는 실제 출력으로 그린다
- [x] order의 컴파일 오류 문구가 빌드에서 대조되고 화면 상자는 실제 문구로 그린다
- [x] "모든 예외의 부모"라고 단정하지 않고 "예외 클래스들의 부모"처럼 말한다
- [x] 코드 한 줄은 33자 이하다
- [x] 나레이션이 화면 결과와 같은지 직접 확인했다
