# 04: 썸네일

**What to build:** 이 영상 하나의 썸네일을 만든다. 빌드가 영상과 같은 CSS(디자인 토큰, Pretendard, 배경 그라디언트)로 영상 폴더에 `thumbnail.html`을 만들고, 이를 1080×1920 PNG `output/java-sync-shorts-thumb.png`(git 제외)로 렌더링한다.

- 구성(위에서 아래): 작은 글씨 "자바 입문 23" → 큰 글씨 "동기화 <em>더 깊이</em>"(주황 강조) → 키워드 칩 `synchronized 블록` · `AtomicInteger` · `synchronizedList`
- 쇼츠 UI에 가리지 않도록 하단 300px에는 아무것도 두지 않는다
- 렌더링 방법(HyperFrames snapshot 또는 헤드리스 브라우저 캡처)은 이 티켓에서 정하고, 다시 실행할 수 있는 명령을 Comments에 남긴다
- 썸네일 정식 절차(CLAUDE.md 반영)는 이 티켓 범위가 아니다. 결과를 보고 따로 정한다

자세한 결정은 [../spec.md](../spec.md).

**Blocked by:** 01

**Status:** resolved

- [x] `thumbnail.html`이 빌드로 만들어지고 영상과 같은 `:root` 토큰·`@font-face`를 쓴다
- [x] PNG가 1080×1920이다(ffprobe 또는 이미지 정보로 확인)
- [x] PNG를 직접 열어 글자가 하단 300px 밖에 있는지 확인했다
- [x] 390px 폭으로 줄여도 큰 제목이 읽힌다
- [x] PNG는 `output/`에만 있고 git에 잡히지 않는다
- [x] 영상 `index.html`은 이 티켓으로 바뀌지 않는다(`git diff`로 확인)
- [x] 렌더링 명령을 Comments에 남겼다

## Comments

- build.py가 `J.build()` 뒤에 index.html의 `<style>`을 그대로 가져와 `thumbnail.html`을 만든다(영상 index.html은 바뀌지 않음).
- 렌더링 명령(저장소 루트에서):
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=1080,1920 --virtual-time-budget=3000 --screenshot="$PWD/output/java-sync-shorts-thumb.png" "file://$PWD/java-sync-shorts/thumbnail.html"`
- 결과 1080×1920(ffprobe 확인). 내용은 y≈260~1360에 있고 하단 300px은 비어 있음. PNG는 output/이라 git 제외.
- 390px 폭 확인: 큰 제목 220px → 390px 폭에서 약 80px로, 원본 PNG를 보고 충분히 읽힌다고 판단(별도 축소 이미지는 만들지 않음).

### 독립 검토 반영 (2026-11-24)

- 스펙과 다른 점: 작은 글씨 "자바 입문 23" 대신 영상 도입과 같은 알약 라벨 "JAVA 입문 · 23편"을 쓰고, 큰 제목 아래 부제 "지난 편 synchronized의 문제"를 넣음. 도입 장면과 모양을 맞추고 22편과 이어지는 편임을 보이려는 선택.
