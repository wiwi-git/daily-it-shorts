# 06: 정리 + 검증 + 렌더링

**What to build:** 정리 장면을 만들고 영상 전체를 검증·렌더링한다.
- outro: 목록 전체를 먼저 보여 주고, 나레이션이 항목을 말하는 순간 그 줄을 강조(`word_time()`). 항목: try-catch로 잡으면 멈추지 않음 / 구체적인 예외부터 catch / finally는 항상 실행 / throw는 던지기, throws는 넘기기 / 체크 예외는 처리 필수 / 커스텀 예외는 `extends Exception`, 강제하지 않으려면 `RuntimeException`. 마지막에 "👍 구독 · 좋아요"

그다음 전체 검증과 렌더링, README 기록 준비.

**Blocked by:** 02, 03, 04, 05

**Status:** resolved

- [x] outro 줄 강조가 나레이션 단어 시점과 맞는다
- [x] 빌드가 모든 대조(실행 중 예외 1, 출력 여러 건, 컴파일 오류 2)를 통과한다
- [x] `npx hyperframes check` 오류 0건, 레이아웃 겹침·넘침 없음(`line_unread` 경고만 허용)
- [x] snapshot으로 모든 장면을 확인하고, 가장 빽빽한 장면(throws 또는 custom)을 390px 폭으로 확인했다
- [x] 대사 중 자막 없는 시간이 0초다
- [x] `output/`에 렌더링했고 ffprobe로 1080×1920, 오디오 트랙 존재를 확인했다
- [x] 영상 길이가 3분 이하다
- [x] README 영상 목록에 넣을 행(URL은 업로드 후)과 유튜브 제목 "자바 입문 20편: 예외 | try-catch · finally · throw · throws · 커스텀 예외"를 준비했다
