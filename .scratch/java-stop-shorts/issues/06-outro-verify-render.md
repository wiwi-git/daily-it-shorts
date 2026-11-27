# 06: 정리 장면 + 전체 검증 + 렌더링

**What to build:** 시청자가 정리 장면에서 다섯 가지 핵심을 한 화면에 보고, 나레이션이 각 항목을 말하는 순간 그 줄이 강조되는 것을 따라간다. 마지막은 "👍 구독 · 좋아요"(예고 없음). 그다음 영상 전체를 검증 기준대로 확인하고 렌더링한다.

- 정리 목록(`EXEC`, 안)
  1. `stop()`은 쓰지 않는다 — 멈춰 달라고 요청한다
  2. 멈춤 신호에는 `volatile`
  3. `interrupt()`는 자고 있는 스레드도 깨운다
  4. 예외를 삼키지 말고 `interrupt()`로 상태를 되살린다
  5. 데몬 스레드는 일반 스레드와 함께 끝난다(독립 검토 반영)
- 줄 강조는 `word_time()`으로 나레이션 단어 시각에 맞춘다
- 전체 검증: `tools/verify-video.sh java-stop-shorts`(렌더링 포함)
- 업로드용 제목·설명 초안을 `docs/youtube-upload.md` 형식(꺾쇠 금지, 끝에 `#shorts`)으로 `.scratch/java-stop-shorts/youtube.md`에 남긴다

자세한 결정은 [../spec.md](../spec.md)의 Testing Decisions·Further Notes.

**Blocked by:** 03, 04, 05

**Status:** resolved

- [x] 정리 목록 5줄이 처음부터 모두 보이고, 나레이션이 항목을 말하는 순간 해당 줄이 강조된다
- [x] HyperFrames check 오류 0건, 레이아웃 겹침·넘침 없음(`line_unread` 경고만 허용)
- [x] 자막: 대사 중 자막 없는 시간 0초
- [x] 모든 장면 snapshot을 직접 확인했고, 가장 빽빽한 장면을 390px 폭으로 줄여도 읽힌다
- [x] 렌더링 결과 `output/java-stop-shorts.mp4`가 ffprobe로 1080×1920, 오디오 트랙 있음, 길이 2분 30초 이하
- [x] 영상 전체 나레이션을 화면 결과와 다시 대조했다(작업 중 줄 수, "이번 실행에서는", 스펙의 사실 표현)
- [x] 유튜브 제목·설명 초안이 저장소 형식을 따른다

## Comments

- `tools/verify-video.sh java-stop-shorts` 전체 통과: check 오류 0건, 자막 공백 0초, 렌더링 `output/java-stop-shorts.mp4` 1080×1920 · 오디오 있음 · 2:14(검토 반영 후 재렌더링 2:16).
- 장면·휴대폰 폭 시트를 직접 확인: 정리 5줄이 나레이션에 맞춰 강조됨. 유튜브 초안은 [../youtube.md](../youtube.md).
