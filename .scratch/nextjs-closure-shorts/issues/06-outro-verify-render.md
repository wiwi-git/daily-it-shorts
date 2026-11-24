# 06: 정리 장면 + 전체 검증 + 렌더링 + 업로드 문서

**What to build:** 정리 장면과 영상 전체 검증·렌더링.

- outro: 목록 전체를 먼저 보여 주고, 나레이션이 항목을 말하는 순간 그 줄을 강조한다(`outro=(EXEC, EXEC_SAID, EXEC_END)`). 진행 표시 칸 없음(22편과 같게)
  - 클로저 = 함수 + 바깥 변수
  - 자바스크립트는 변수 자체를 붙잡는다
  - 자바는 사실상 final만 (동시성 문제)
  - 반복문은 `let`
  - React 상태는 스냅샷 · 서버 액션 값은 브라우저를 오간다
  - 예고 없이 "구독과 좋아요"로 끝, "👍 구독 · 좋아요"
- 전체 빌드 후 `tools/verify-video.sh nextjs-closure-shorts`로 검증하고, 렌더링해 `output/nextjs-closure-shorts.mp4`를 만든다
- `docs/youtube-upload.md` 형식으로 업로드용 제목·설명을 `.scratch/nextjs-closure-shorts/youtube.md`에 준비한다(꺾쇠 금지, 제목 끝 `#shorts`). 새 시리즈 1편이므로 설명에 시리즈 소개 한 줄. README 영상 목록 행은 업로드 후 추가

**Blocked by:** 03, 04, 05

**Status:** resolved

- [x] 정리 장면의 줄 강조가 나레이션 단어에 맞고, 단어를 못 찾으면 빌드가 멈춘다
- [x] HyperFrames check 오류 0건, 레이아웃 겹침·넘침 없음(`line_unread` 경고만 허용)
- [x] 대사 중 자막 없는 시간 0초
- [x] snapshot 시트를 직접 열어 모든 장면을 확인하고, 가장 빽빽한 장면(capture 또는 loop)을 390px 폭으로 확인했다
- [x] 렌더링 결과가 ffprobe로 1080×1920, 오디오 트랙 있음, 3분 이하
- [x] 업로드용 제목·설명이 준비됐다

## Comments

- 정리 장면: 5줄 목록, 나레이션 단어(`클로저는`, `자바스크립트는`, `자바는`, `반복문에서는`, `리액트`)에 맞춰 줄 강조, 끝에 "👍 구독 · 좋아요". 목록은 고정폭 글꼴이면 한글 간격이 벌어져 본문 글꼴로 바꿨다.
- `tools/verify-video.sh nextjs-closure-shorts`: check 오류 0건, 자막 공백 0초, 렌더링 `output/nextjs-closure-shorts.mp4` 1080×1920 · 오디오 있음 · 2:33.
- 장면마다 끝 직전 프레임을 따로 찍어 확인(겹침·넘침 없음). 휴대폰 폭 시트로 STEP 1, STEP 3, 가장 빽빽한 STEP 4(loop)를 확인 — 읽힘. loop의 자막 한 조각("…영, 일,")이 두 줄로 꺾이며 "일,"이 홀로 남는 것은 그대로 둠.
- 업로드용 제목·설명·README 행: `.scratch/nextjs-closure-shorts/youtube.md`.
