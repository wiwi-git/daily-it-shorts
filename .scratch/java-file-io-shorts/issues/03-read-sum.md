# 03: STEP 2 읽기 + STEP 3 계산

**What to build:** 세 줄 파일을 한 줄씩 읽고, 읽은 값으로 합계를 구하는 두 장면. 둘 다 write와 append 코드를 사전 코드로 먼저 실행해 세 줄 파일을 만든다.
- read: try-with-resources로 `BufferedReader`(`new FileReader("scores.txt")`)를 열고 `while ((line = r.readLine()) != null)`로 세 줄 출력. 더 읽을 줄이 없으면 `readLine()`이 `null`
- sum: 읽은 줄을 `split(",")`으로 나누고 `Integer.parseInt`로 점수를 바꿔 더하면 `255`. 19편 스트림 합계와 같다는 연결

진행 표시는 read가 2번째, sum이 3번째 칸.

**Blocked by:** 02

**Status:** resolved

- [x] read의 출력(세 줄), sum의 출력(`255`)이 빌드에서 대조된다
- [x] 읽는 파일의 내용 상자도 함께 보여 준다
- [x] 33자 제한을 넘는 줄은 의미 단위로 나눈다
- [x] 가장 빽빽한 장면(read 또는 sum)을 390px 폭으로 확인했다
- [x] 나레이션이 화면 결과와 같은지 직접 확인했다
