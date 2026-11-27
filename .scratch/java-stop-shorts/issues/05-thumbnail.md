# 05: 썸네일

**What to build:** 피드·채널 화면에서 주제가 바로 보이는 25편 썸네일을 24편과 같은 방식으로 만든다. 빌드 스크립트가 영상과 같은 CSS(디자인 토큰·Pretendard)로 영상 폴더에 `thumbnail.html`을 만들고, 24편과 같은 렌더링 명령으로 `output/java-stop-shorts-thumb.png`(git 제외)를 만든다.

- 구성: 작은 글씨 "자바 입문 25" → 큰 글씨 "스레드 <em>멈추기</em>"(주황 강조) → 작은 줄 `volatile · interrupt · 데몬`
- 하단 300px에는 아무것도 두지 않는다

자세한 결정은 [../spec.md](../spec.md)의 "썸네일".

**Blocked by:** 02 (프로젝트 골격·빌드 스크립트)

**Status:** resolved

- [x] 빌드 시 영상 폴더에 `thumbnail.html`이 생기고, 영상과 같은 토큰·글꼴을 쓴다
- [x] PNG가 1080×1920이고 `output/`에만 있다(커밋 대상 아님)
- [x] 글자가 하단 300px 밖에 있다
- [x] 390px 폭으로 줄여도 큰 제목이 읽힌다(직접 열어 확인)

## Comments

- 렌더링 명령(저장소 루트에서): `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=1080,1920 --virtual-time-budget=3000 --screenshot="$PWD/output/java-stop-shorts-thumb.png" "file://$PWD/java-stop-shorts/thumbnail.html"`
- PNG 1080×1920, 하단 300px 비어 있음을 직접 확인. 작은 줄 "멈춰 달라고 요청하기" 추가.
