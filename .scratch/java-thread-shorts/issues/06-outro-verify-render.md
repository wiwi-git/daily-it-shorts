# 06: 정리 장면 + 전체 검증 + 렌더링

**What to build:** 정리 장면과 영상 전체 검증·렌더링.

- outro: 목록 전체를 먼저 보여 주고, 나레이션이 항목을 말하는 순간 그 줄을 강조한다(`outro=(EXEC, EXEC_SAID, EXEC_END)`)
  - `new Thread(람다) · start()`
  - `run()`은 그냥 메소드 호출
  - 출력 순서는 보장 안 됨
  - `join()` 끝날 때까지 기다리기
  - 같은 변수 → 경쟁 조건
  - `synchronized` 한 번에 하나
  - 예고 없이 "구독과 좋아요"로 끝, "👍 구독 · 좋아요"
- 전체 빌드 후 `tools/verify-video.sh java-thread-shorts`로 검증하고, 렌더링해 `output/java-thread-shorts.mp4`를 만든다
- `docs/youtube-upload.md` 형식으로 업로드용 제목·설명을 준비한다(꺾쇠 금지, 제목 끝 `#shorts`)

진행 표시는 5번째 칸.

**Blocked by:** 03, 04, 05

**Status:** resolved

- [x] 정리 장면의 줄 강조가 나레이션 단어에 맞고, 단어를 못 찾으면 빌드가 멈춘다
- [x] HyperFrames check 오류 0건, 레이아웃 겹침·넘침 없음(`line_unread` 경고만 허용)
- [x] 대사 중 자막 없는 시간 0초
- [x] snapshot 시트를 직접 열어 모든 장면을 확인하고, 가장 빽빽한 장면을 390px 폭으로 확인했다
- [x] 렌더링 결과가 ffprobe로 1080×1920, 오디오 트랙 있음, 3분 이하
- [x] 업로드용 제목·설명이 준비됐다

## Comments

- 정리 장면: 6줄 목록, 나레이션 단어(`뉴`, `런을`, `출력`, `조인은`, `같은`, `싱크로나이즈드로`)에 맞춰 줄 강조, 끝에 "👍 구독 · 좋아요". 자리표시 헬퍼 `todo()` 제거.
- `tools/verify-video.sh java-thread-shorts`: check 오류 0건, 자막 공백 0초, 렌더링 `output/java-thread-shorts.mp4` 1080×1920 · 오디오 있음 · 2:08.
- 휴대폰 폭 시트에서 정리 장면 강조 순서 확인. 다른 장면은 03~05에서 확인한 뒤 바뀌지 않음.
- 업로드용 제목·설명·README 행: `.scratch/java-thread-shorts/youtube.md`.
- 독립 검토(별도 세션) 반영 — 사용자 승인 묶음:
  - 대본: start "실행해 보면 메인 끝이 중간에 끼어 있어요" → "이번 실행에서는 메인 끝이 중간에 끼었어요"(검토 세션 40회 실행에서 순서 다섯 가지 관찰), race "이만보다 적게" → "대부분 이만보다 적게". 음성 재생성
  - join "t.join() 있음" 상자의 `민수 85`가 `.term.ok div` 초록에 덮여 서준 색으로 보이던 문제: 큰 숫자 스타일을 `#sc-race`·`#sc-sync`로 한정
  - 정리 장면의 진행 표시 5번째 칸 제거(`PROG`에서 outro 삭제, 다른 자바 영상과 같게)
  - race·sync 코드: 메소드 선언과 main 본문 사이 빈 줄
  - 공용 `jce()`도 결과 상자 라벨을 초기화(`jmulti` 다음 `jce`의 경계 사례). 20·21·19편 재빌드 diff 없음
  - 그대로 둔 것: synchronized 범위(루프 메소드 전체, 한 단어 차이 비교 유지), join 상자 라벨, 화면 코드의 main throws, 사소한 항목
- 재검증: check 0건, 자막 공백 0초, 렌더링 1080×1920 · 오디오 · 2:09.
