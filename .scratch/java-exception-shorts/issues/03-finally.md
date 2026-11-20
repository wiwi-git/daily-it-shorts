# 03: STEP 3 finally

**What to build:** 예외가 나든 안 나든 `finally`가 실행된다는 것을 두 실행 결과로 비교하는 장면.
- finally: `try`에서 문자열을 `Integer.parseInt`로 바꾸고, `catch (NumberFormatException e)`, `finally`에서 "끝" 출력. `"85"`(예외 없음)와 `"abc"`(예외 남)를 각각 실행해 두 출력 상자를 나란히 보여 준다. 둘 다 "끝"이 있다

진행 표시는 3번째 칸. `System.exit` 같은 예외 상황은 다루지 않는다.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] 두 실행의 출력이 각각 빌드에서 대조되고, 둘 다 "끝"으로 끝난다
- [ ] 화면의 두 출력 상자는 실제 출력으로 그린다
- [ ] 390px 폭에서도 두 상자가 읽힌다
- [ ] 나레이션이 화면 결과와 같은지 직접 확인했다
