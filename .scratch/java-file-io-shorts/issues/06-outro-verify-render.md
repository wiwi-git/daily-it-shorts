# 06: 정리 + 검증 + 렌더링

**What to build:** 정리 장면을 만들고 영상 전체를 검증·렌더링한다.
- outro: 목록 전체를 먼저 보여 주고, 나레이션이 항목을 말하는 순간 그 줄을 강조(`word_time()`). 항목: BufferedWriter로 쓰고 newLine으로 줄바꿈 / try-with-resources로 자동으로 닫기 / `true`면 이어쓰기, 기본은 덮어쓰기 / readLine은 null이면 끝 / 읽은 값은 split · parseInt / IOException은 체크 예외 / Files로 짧게. `.note`로 한글은 UTF-8 확인. 마지막에 "👍 구독 · 좋아요"

그다음 전체 검증과 렌더링, README 기록 준비.

**Blocked by:** 02, 03, 04, 05

**Status:** ready-for-agent

- [ ] outro 줄 강조가 나레이션 단어 시점과 맞는다
- [ ] 빌드가 모든 출력·파일 내용 대조를 통과하고, 빌드 뒤 저장소에 `scores.txt`가 없다
- [ ] `npx hyperframes check` 오류 0건, 레이아웃 겹침·넘침 없음(`line_unread` 경고만 허용)
- [ ] snapshot으로 모든 장면을 확인하고, 가장 빽빽한 장면을 390px 폭으로 확인했다
- [ ] 대사 중 자막 없는 시간이 0초다
- [ ] `output/`에 렌더링했고 ffprobe로 1080×1920, 오디오 트랙 존재를 확인했다
- [ ] 영상 길이가 3분 이하다
- [ ] README 영상 목록에 넣을 행(URL은 업로드 후)과 유튜브 제목 "자바 입문 21편: 텍스트 파일 읽기·쓰기 | BufferedWriter · BufferedReader · try-with-resources · Files"를 준비했다
