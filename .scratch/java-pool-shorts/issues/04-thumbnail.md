# 04: 썸네일

**What to build:** 이 영상 하나의 썸네일을 23편과 같은 방식으로 만든다. 빌드가 `J.build()` 뒤에 index.html의 `<style>`을 가져와 영상 폴더에 `thumbnail.html`을 만들고, 1080×1920 PNG `output/java-pool-shorts-thumb.png`(git 제외)로 렌더링한다.

- 구성(위에서 아래): 23편처럼 도입과 같은 알약 라벨 "JAVA 입문 · 24편" → 큰 글씨 "스레드 <em>풀</em>"(주황 강조) → 작은 줄 `submit · Future · get`
- 하단 300px에는 아무것도 두지 않는다
- 렌더링 명령(저장소 루트에서, 23편과 같음):
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=1080,1920 --virtual-time-budget=3000 --screenshot="$PWD/output/java-pool-shorts-thumb.png" "file://$PWD/java-pool-shorts/thumbnail.html"`

자세한 결정은 [../spec.md](../spec.md).

**Blocked by:** 01

**Status:** resolved

- [x] `thumbnail.html`이 빌드로 만들어지고 영상과 같은 `:root` 토큰·`@font-face`를 쓴다
- [x] PNG가 1080×1920이다(ffprobe 또는 이미지 정보로 확인)
- [x] PNG를 직접 열어 글자가 하단 300px 밖에 있는지 확인했다
- [x] 390px 폭으로 줄여도 큰 제목이 읽힌다
- [x] PNG는 `output/`에만 있고 git에 잡히지 않는다
- [x] 영상 `index.html`은 이 티켓으로 바뀌지 않는다(`git diff`로 확인)

## Comments

- 23편과 같은 방식: build.py가 `J.build()` 뒤에 index.html의 `<style>`로 `thumbnail.html`을 만든다. 구성: 알약 "JAVA 입문 · 24편" → "스레드 / 풀"(220px, 두 줄) → 부제 "미리 만든 스레드를 돌려 쓰기" → 칩 submit · Future · get.
- 렌더링: 위 명령 그대로. 결과 1080×1920(ffprobe), 내용은 y≈360~1260, 하단 300px 비어 있음. `git check-ignore`로 output/ 제외 확인.
- 썸네일 코드를 붙인 뒤 다시 빌드해도 index.html이 그대로인지 `cmp`로 확인.
