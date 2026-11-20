# 04: STEP 4 파일 예외

**What to build:** 없는 파일을 읽을 때의 예외와, 파일 코드에 처리가 필수인 이유를 보여 주는 장면.
- except: 이름을 잘못 쓴 `score.txt`(s 빠짐)를 읽으면 `FileNotFoundException`. `catch (IOException e)`로 잡아 안내 문구와 `e.getMessage()` 출력. `FileNotFoundException`은 `IOException`의 자식 클래스라 함께 잡힌다. `IOException`은 체크 예외(20편)라 `try-catch`나 `throws`가 필수

진행 표시는 4번째 칸. 예외 문구는 운영체제마다 다를 수 있으므로 화면에는 빌드가 얻은 실제 문구를 그린다(로컬 macOS 기준 `score.txt (No such file or directory)`).

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] except의 출력이 빌드에서 대조되고, 화면 상자는 실제 출력으로 그린다
- [ ] 체크 예외를 20편의 표기 그대로 쓴다
- [ ] 자식 클래스 관계를 정확히 말한다
- [ ] 나레이션이 화면 결과와 같은지 직접 확인했다
