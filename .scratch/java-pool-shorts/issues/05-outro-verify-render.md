# 05: 정리 장면 + 전체 검증·렌더링 + 업로드 문구

**What to build:** 정리 장면을 완성하고 영상 전체를 검증·렌더링한 뒤, 업로드용 제목·설명을 준비한다.

- outro: 목록 6줄을 먼저 모두 보여 주고, 나레이션이 항목을 말하는 순간 그 줄을 강조한다(`word_time()`). 마지막은 예고 없이 "👍 구독 · 좋아요"
  - 스레드 풀 = 미리 만든 스레드를 돌려 쓰기
  - `newFixedThreadPool(2)` + `submit(작업)`
  - 값을 돌려주는 작업 → `Future`로 받기
  - `get()`은 끝날 때까지 기다렸다 꺼낸다
  - try-with-resources로 닫기(안 닫으면 안 끝남)
  - 가상 스레드: `newVirtualThreadPerTaskExecutor()`
- 전체 검증·렌더링: `tools/verify-video.sh java-pool-shorts` → `output/java-pool-shorts.mp4`
- 업로드 문구: `docs/youtube-upload.md` 형식으로 `../youtube.md`. 제목 "자바 입문 24편: 스레드 풀 | ExecutorService · submit · Future · get #shorts". 꺾쇠 금지(`Future<Integer>`를 제목·설명에 쓰지 않음)
- 업로드 후(사용자가 URL을 알려 주면): README 영상 목록에 행 추가, `.scratch/java-thread-shorts/not-covered.md`의 제작 현황 표와 **[24편 예정]** 표시를 **[24편 완료]**로 바꾼다. 커밋은 사용자가 요청할 때만

자세한 결정은 [../spec.md](../spec.md).

**Blocked by:** 02, 03

**Status:** resolved

- [x] 정리 목록 6줄이 나레이션에 맞춰 강조된다(단어를 못 찾으면 빌드가 멈춤)
- [x] `npx hyperframes check` 오류 0건, 레이아웃 겹침·넘침 없음(`line_unread` 경고만 허용)
- [x] 자막: 대사 중 자막 없는 시간 0초
- [x] 모든 장면 snapshot 시트와 가장 빽빽한 장면의 390px 시트를 직접 열어 확인했다
- [x] 렌더링 결과가 ffprobe로 1080×1920, 오디오 트랙 있음, 길이 2분 30초 이하
- [x] 영상 전체 나레이션을 화면 결과·"사실 표현 주의"와 대조했다
- [x] 업로드용 제목·설명 초안을 만들었다(꺾쇠 없음)

## Comments

- 정리 목록(EXEC): 스레드 풀 = 스레드 돌려 쓰기 / newFixedThreadPool(2) + submit(작업) / 값을 돌려주면 → Future / get()은 끝날 때까지 기다림 / try-with-resources로 닫기 / 가상 스레드 + newVirtualThreadPerTaskExecutor(). 6번 줄은 넘쳐서 `#ex6 b`만 38px. 강조 단어: 미리·픽스드·퓨처로·겟은·트라이·가상.
- `tools/verify-video.sh java-pool-shorts`: check 오류 0건, 자막 공백 0초, 장면·휴대폰 폭 시트 확인, `output/java-pool-shorts.mp4` 1080×1920 · 오디오 있음 · 2:06.
- 나레이션 대조: "이번 실행에서는 민수가 먼저"(고정 예시), "합계는 항상 백칠십칠"(20회), "결과는 똑같이 백칠십칠"(가상 스레드 버전 실행). "실무"·성능 수치·"가상 스레드 풀"·예외 이름 없음.
- 업로드 문구: [../youtube.md](../youtube.md)(꺾쇠 없음 확인). 업로드 후 README 행 추가와 not-covered.md [24편 완료] 갱신은 남음.

### 독립 검토 반영 (2026-11-25)

별도 에이전트 검토 결과 중 1~4번을 반영. 2·3번 주장은 직접 실행으로 다시 확인함(풀 생성 직후 `getPoolSize()` 0 → 작업 1개 뒤 1, 닫지 않은 가상 스레드 익스큐터는 바로 종료, `--release 17`에서는 `close()` 없음).
- "미리 만들어 두고" → 고정 풀은 작업이 들어올 때 정해 둔 개수까지 만든다. hook "정해 둔 개수만 만들어 돌려 쓰는", why "정해 둔 개수까지만 스레드를 만들고, 그 스레드들에", outro "만든 스레드를 다시 돌려 써요"(EXEC_SAID "미리"→"만든"), hook 부제·카드·썸네일 부제·업로드 설명도 같이 고침.
- "안 닫으면 안 끝남"은 고정 풀에만 해당(가상 스레드는 데몬) → 나레이션·`.warn`을 "고정 풀은 …"으로.
- try-with-resources로 풀 닫기는 자바 19부터 → 나레이션은 그대로 두고 close 메모 small에 "· 자바 19부터", 업로드 설명 4번에 "(자바 19부터)". 스펙의 "버전을 말하지 않는다"는 나레이션에만 적용한 것으로 해석.
- 자막 "풀에 이를" → 대본을 "풀에 2를"로(TTS는 그대로 "이를"로 읽고, 자막은 "2를").
- 반영하지 않음: close 장면 상자들을 나레이션 시점에 강조(nit, 공용 build에 장면 중 강조 기능이 없음).
- 다시 검증·렌더링: check 오류 0건, 자막 공백 0초, `output/java-pool-shorts.mp4` 1080×1920 · 오디오 있음 · 2:07. 썸네일 다시 렌더링.

### 업로드 (2026-11-26)

- https://www.youtube.com/watch?v=36VyonJ-Ks8 (2:10). README 영상 목록에 행 추가, not-covered.md 제작 현황 24편 행을 업로드 완료로, **[24편 예정]** → **[24편 완료]**.
