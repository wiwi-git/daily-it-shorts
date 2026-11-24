# 05: 정리 장면 + 전체 검증·렌더링 + 업로드 문구

**What to build:** 정리 장면을 완성하고 영상 전체를 검증·렌더링한 뒤, 업로드용 제목·설명을 준비한다.

- outro: 목록 6줄을 먼저 모두 보여 주고, 나레이션이 항목을 말하는 순간 그 줄을 강조한다. 마지막은 예고 없이 "👍 구독 · 좋아요"
  - 메소드 전체 잠금 → 사실상 순차 실행
  - `synchronized (잠금 객체)` 필요한 줄만
  - 같은 잠금 객체를 써야
  - `AtomicInteger` 원자적 연산
  - `ArrayList`는 스레드 안전 아님
  - `synchronizedList`로 감싸기
- 전체 검증·렌더링: `tools/verify-video.sh java-sync-shorts` → `output/java-sync-shorts.mp4`
- 업로드 문구: `docs/youtube-upload.md` 형식. 제목 "자바 입문 23편: 동기화 더 깊이 | synchronized 블록 · AtomicInteger · synchronizedList #shorts"(꺾쇠 금지)
- 업로드 후(사용자가 URL을 알려 주면): README 영상 목록에 행 추가, `.scratch/java-thread-shorts/not-covered.md`의 제작 현황 표와 **[23편 예정]** 표시를 **[23편 완료]**로 바꾼다. 커밋은 사용자가 요청할 때만

자세한 결정은 [../spec.md](../spec.md).

**Blocked by:** 02, 03

**Status:** resolved

- [x] 정리 목록 6줄이 나레이션에 맞춰 강조된다(단어를 못 찾으면 빌드가 멈춤)
- [x] `npx hyperframes check` 오류 0건, 레이아웃 겹침·넘침 없음(`line_unread` 경고만 허용)
- [x] 자막: 대사 중 자막 없는 시간 0초
- [x] 모든 장면 snapshot 시트와 가장 빽빽한 장면의 390px 시트를 직접 열어 확인했다
- [x] 렌더링 결과가 ffprobe로 1080×1920, 오디오 트랙 있음, 길이 2분 30초 이하
- [x] 영상 전체 나레이션을 화면 결과·"사실 표현 주의"와 대조했다
- [x] 업로드용 제목·설명 초안을 만들었다

## Comments

- 정리 2번 줄이 넘쳐 `synchronized (lock)\n필요한 줄만` 두 줄로 나눔. 6줄 강조가 나레이션에 맞춰 차례로 켜지는 것 snapshot으로 확인.
- `tools/verify-video.sh java-sync-shorts`: check 오류 0건, 자막 공백 0초, 시트 확인, `output/java-sync-shorts.mp4` 1080×1920 · 오디오 있음 · 2:04.
- 나레이션 대조: "항상 이만"(scope·block·atomic·synchronizedList = 20000), "이만보다 적게 … 예외가 나기도"(14302, 예외 관찰), "더 빠르다" 표현 없음.
- 업로드 문구: [../youtube.md](../youtube.md). 업로드 후 README 행 추가와 not-covered.md [23편 완료] 갱신은 남음.

### 독립 검토 반영 (2026-11-24)

- 정리 4번 줄을 "AtomicInteger 원자적 연산"에서 "incrementAndGet() 원자적 연산"으로, 나레이션을 "아토믹 인티저의 인크리먼트 앤 겟은 원자적 연산이에요"로 바꿈(원자적 연산은 클래스가 아니라 메소드 쪽).
- 다시 검증·렌더링: check 오류 0건, 자막 공백 0초, `output/java-sync-shorts.mp4` 1080×1920 · 오디오 있음 · 2:05. 썸네일도 다시 렌더링.
