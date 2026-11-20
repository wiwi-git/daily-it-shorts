# 05: STEP 5 짧게 쓰기 (Files)

**What to build:** 같은 쓰기·읽기를 `Files`로 짧게 하는 장면.
- files: `main`에 `throws IOException`을 붙이고(20편 throws 연결), `Files.writeString(Path.of("scores.txt"), ...)`로 세 줄을 한 번에 쓰고, `Files.readAllLines(Path.of("scores.txt"))`로 읽어 리스트 출력 → `[민수,85, 서준,92, 지우,78]`. `readAllLines`는 모든 줄을 리스트로 돌려줌(17편 리스트 연결)

진행 표시는 5번째 칸.

**Blocked by:** 01

**Status:** resolved

- [x] 쓰기 뒤 파일 내용(세 줄)과 읽기 출력이 빌드에서 대조된다
- [x] `main`의 `throws IOException` 선언을 화면에 보여 준다
- [x] 코드 한 줄은 33자 이하다
- [x] 나레이션이 화면 결과와 같은지 직접 확인했다
