# 02: 프로젝트 골격 + 대본 전체 + 도입·STEP 1 멈춤 신호

**What to build:** 24편(`java-pool-shorts`)과 같은 방식·템포(1.2배)로 `java-stop-shorts` 영상 프로젝트를 만든다. 음성 생성·빌드 스크립트를 복사해 장면만 바꾼다. 상단 바 브랜드는 `자바 <em>스레드 멈추기</em> 정리`이다. 진행 표시는 flag→1, interrupt→2, swallow→3, daemon→4이고, outro는 시리즈 관례대로 PROG에 넣지 않는다.

이 티켓에서 **영상 전체 대본**(hook, flag, interrupt, swallow, daemon, outro)을 먼저 쓰고, 음성으로 길이를 확인한다(목표 2분 10초 안팎, 2분 30초 이하). 그다음 도입과 STEP 1을 대본 → 음성 → 화면까지 만든다. 나머지 장면은 제목만 있는 자리표시 화면으로 둔다.

- 공통 설정: `J.MAIN_THROWS = "InterruptedException"`
- hook: "자바 입문 스물다섯 번째, 스레드 멈추기와 끝내기". 22편을 짧게 되짚는다. 150px 큰 제목 "스레드 <em>멈추기</em>". `.warn` "`stop()`은 이제 예외만 던져요"는 기존 실행 오류 헬퍼(`jrt`)로 `UnsupportedOperationException`이 나는지 검증만 하고, 코드 블록은 그리지 않는다. 핵심 메시지: "멈춰 달라고 요청하고, 스레드가 스스로 끝내요"
- flag: `static volatile boolean stop;` 선언 줄 + 작업 스레드(반복 바깥 `try`, `catch (` 줄바꿈은 22편 관례) + `t.start();` / `Thread.sleep(1000);` / `stop = true;`. `jmulti` 20회, 매 실행 `작업 중` 1줄 이상 + 마지막 줄 `작업 끝`. 화면 예시는 `작업 중`×5 + `작업 끝`. `.note` "`volatile`이 없으면 바뀐 값을 못 보고 계속 돌 수도 있어요". 자는 동안(0.2초)에는 신호를 확인하지 못한다는 말로 STEP 2를 예고한다

코드 뼈대와 사실 표현은 [../spec.md](../spec.md)의 "33자 제한에 맞춘 코드 모양", "인터럽트 설명의 정확성"을 따른다.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] 새 영상 프로젝트가 24편의 음성 생성·빌드 스크립트를 기반으로 만들어지고, 디자인 토큰·글꼴·모션은 그대로다
- [x] 대본 전체가 GLOSSARY 표기(멈춤 신호, 인터럽트, 인터럽트 상태, 데몬 스레드, 볼라타일)를 쓰고, "플래그(나레이션)·강제 종료·백그라운드 스레드·인터럽트 플래그"를 쓰지 않는다. 영어 키워드는 한글 발음으로 쓴다
- [x] 대본이 스펙의 "인터럽트 설명의 정확성"을 지킨다("요청"이지 "멈춘다"가 아님, `volatile`은 "못 볼 수도", `stop()` 버전 숫자 없음)
- [x] 대본 전체 길이를 음성으로 확인했고 2분 30초 이하다
- [x] `stop()` 검증이 `UnsupportedOperationException`으로 통과한다
- [x] flag 예제가 `jmulti` 20회를 통과하고, 모든 코드 줄이 33자 이하다
- [x] 나레이션이 화면과 같은지 직접 확인했다
- [x] `tools/verify-video.sh java-stop-shorts --no-render` 통과(check 오류 0건, 자막 공백 0초, 시트 확인)

## Comments

- 대본 6장면 음성 합계 130.9초 → 영상 134.1초(2:14). 사용자 요청으로 02~06을 한 번에 구현해서, 자리표시 단계 없이 모든 장면을 같은 빌드에서 만들었다.
- hook: `jrt`로 `t.stop()` → `UnsupportedOperationException` 확인(그리지 않음). 경고 상자 + "① 요청 / ② 스스로" 카드.
- flag: 화면 높이 때문에 메모(`volatile` 설명)를 desc 두 줄로 올리고, main의 마지막 세 줄은 출력 상자 옆에 "이어서 main"으로 나눠 그렸다(한 프로그램으로 `jmulti` 검증). 영상 전용 CSS로 `.code.sm` 줄 간격 1.4.
- 출력 확인(`each`)은 "작업 중 1줄 이상 + 마지막 줄 작업 끝"으로 했다. 1초와 0.2초 간격이 겹쳐서 `작업 중`이 5~6줄이 될 수 있어, 줄 수는 고정하지 않았다.
