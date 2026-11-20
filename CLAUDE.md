# daily-it-shorts

IT·기술 정보성 유튜브 쇼츠를 매일 하나씩 만드는 저장소. 영상 1개 = 폴더 1개(HyperFrames 프로젝트).
새 영상은 **기존 영상과 같은 디자인·제작 방식**으로 만든다.

작업 흐름은 [AGENTS.md](AGENTS.md)를 따른다.

@AGENTS.md

## 응답 언어

- 사용자에게 하는 답변은 항상 한국어로 쓴다(코드·명령어·파일 이름은 원문 그대로)

## 영상 규격

- 세로 9:16, 1080×1920, 길이 3분 이하(지금까지 2분 30초 안팎)
- 한국어 나레이션: Edge TTS `ko-KR-SunHiNeural`, rate `+34%`
- 템포: `java-method-constructor-shorts`부터 1.2배(이전 rate `+12%` × 1.2). 새 자바 영상은 가장 최근 자바 영상의
  `gen_vo.py`·`build.py`(`J.load(speed=1.2)`)를 복사해 장면만 바꾼다 — 장면 간격·전환·등장 모션이 `SPEED`로 함께 줄어든다
- 한국어 자막 필수, 나레이션과 단어 단위로 동기화
- 렌더링 결과는 `output/<영상이름>.mp4` (git 제외)

## 제작 순서

1. **내용 구성**: 장면 목록(도입 → STEP 1… → 정리)과 각 장면에서 보여줄 코드·표를 먼저 정한다
2. **대본**: `script.json`에 `{id, section, text}`로 장면별 나레이션 작성
3. **음성**: `../.venv/bin/python gen_vo.py` → `assets/vo/*.mp3`, `vo.json`(단어 타이밍 포함)
4. **화면**: `build.py`의 `scenes`, `PROG` 수정 → `python3 build.py` → `index.html`, `assets/narration.mp3`, 예제 기록
   (빌드가 화면의 예제를 실제로 실행해 대본의 기대 결과와 다르면 멈춘다)
5. **검증**: `tools/verify-video.sh <영상폴더>` — 아래 검증 기준을 순서대로 실행하고 어기면 멈춘다. 출력된 snapshot 시트는 직접 열어 본다
6. **기록**: 업로드용 제목·설명은 [docs/youtube-upload.md](docs/youtube-upload.md). 업로드 후 README "영상 목록"에 행 추가

## 디자인 컨셉 (바꾸지 말 것)

**색상** (`:root` 토큰)

| 토큰 | 값 | 용도 |
|---|---|---|
| `--ground` | `#0b1220` | 배경 (우상단 파랑·좌하단 주황 radial-gradient) |
| `--panel` | `#131c2e` | 카드·칩·표 배경 |
| `--ink` / `--mute` | `#f4f6fb` / `#9aa6bd` | 본문 / 보조 텍스트 |
| `--blue` | `#3fa7d6` | SQL 키워드, 표 헤더, 브랜드 |
| `--orange` | `#f29111` | 강조, 숫자, 진행 표시, 핵심 코드 줄 배경 |
| `--red` / `--green` / `--violet` | `#ff5d5d` / `#7ee08a` / `#c3a6ff` | 경고·NULL / 문자열·두 번째 대상 / 세 번째 대상 |

**글꼴**: 본문 Pretendard(`assets/fonts/PretendardVariable.woff2`, `@font-face` 필수 — 없으면 lint 오류),
코드는 Menlo. 합자는 `#root`에서 전체적으로 끈다(`font-variant-ligatures: none`) — 켜두면 `>=`가 `≥`로 보인다(인라인 `<code>` 포함).

**화면 구성** (위에서 아래로)

- 상단 고정 바: 왼쪽 브랜드(`<b>주제 <em>키워드</em> 정리</b>`), 오른쪽 5칸 진행 표시(현재 STEP 칸만 주황)
- 장면 본문: 여백 `210px 70px`, 순서는 `pill`(STEP 라벨) → `title`(80px) → `desc`(46px) → 코드/표/메모
- 자막: 하단에서 260px 위, 검은 반투명 박스, 48px 굵게, `word-break: keep-all`
- 맨 아래: 주황 진행 막대(영상 전체 길이)
- 하단 약 300px은 쇼츠 UI에 가려지므로 본문을 두지 않는다

**구성 요소** (`build.py` 헬퍼): 자바 영상은 [docs/java-helpers.md](docs/java-helpers.md)(공용 모듈 `tools/javashorts.py`),
SQL 영상은 [docs/sql-helpers.md](docs/sql-helpers.md). 공통 화면 요소:

- `.warn`(빨간 경고) · `.note`(파란 메모) · `.chips`(키워드 칩) · `.vs`(두 개념 비교 카드) · `.list/.row`(번호 목록)
- 도입 장면: `.hook` + 150px `.big` 제목(핵심 단어 `<em>` 주황)
- 정리 장면: 목록 전체를 먼저 보여주고, 나레이션이 항목을 말하는 순간 `word_time()`으로 그 줄을 강조. 마지막에 "👍 구독 · 좋아요"

**모션** (`SPEED = 1.2` 기준, 괄호는 1배속 값): 각 장면의 `.in` 요소는 아래에서 50px 올라오며 순서대로 등장
(약 0.42s ← 0.5s, power3.out), 코드는 한 줄씩 등장. 장면 전환은 다음 장면 시작 0.125초(← 0.15초) 전.
장면 사이 간격 0.375초(← 0.45초).

## 내용·대본 원칙

- 대본 작성 후 제작 전에 사실 검토: 결과가 있는 예제는 모두 빌드가 실행·대조하는 헬퍼로 넣는다.
  자동 대조는 예제 결과까지만이므로, 나레이션 문장("네 개가 남아요")이 기대 결과와 같은지는 직접 확인한다

- 예시 데이터는 영상 전체에서 하나로 통일하고, 같은 대상은 모든 표에서 같은 색(k1/k2/k3)을 쓴다
- 나레이션에서 말한 것은 화면에도 보여준다(말로만 나오는 함수·조건 금지). 예제 결과는 실제 데이터로 계산해 맞춘다
- 입문자 대상: 별칭은 `AS`를 명시, 단정적 규칙은 예외가 있으면 "기본적으로"처럼 완화, 정확한 용어 사용(예: "논리적 처리 순서")
- 영어 키워드는 대본에 한글 발음으로 쓴다(셀렉트, 웨어, 그룹 바이, 널) — TTS가 자연스럽게 읽고 자막과도 맞는다
- 코드 한 줄은 33자 이하(42px 기준 카드 폭). 길면 `ON`, `AND` 앞에서 의미 단위로 줄바꿈

## 검증 기준

- `npx hyperframes check` 오류 0건, 레이아웃 겹침·넘침 없음 (`line_unread` 경고는 나레이션 속도 때문이라 허용)
- 자막: 대사 중 자막 없는 시간 0초. `caption_chunks()`가 TTS 단어 경계(WordBoundary)로 타이밍을 잡는다 —
  글자 수 비율로 나누는 방식으로 되돌리지 말 것
- 가장 빽빽한 장면을 390px 폭으로 줄여 모바일 가독성 확인
- 렌더링 후 `ffprobe`로 1080×1920, 오디오 트랙 존재 확인

## 저장소 규칙

- 영상(`*.mp4`)·음성(`*.mp3`)·`output/`·`.hyperframes/`는 커밋하지 않는다(`.gitignore`)
- 커밋·푸시는 사용자가 요청할 때만. 보통 유튜브 업로드 후 URL을 README에 넣고 함께 커밋한다

## Agent skills

### Issue tracker

스펙·티켓은 `.scratch/<기능>/` 아래 로컬 마크다운 파일로 관리한다. See `docs/agents/issue-tracker.md`.

### Triage labels

기본 다섯 역할(`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`)을 각 이슈 파일의 `Status:` 줄에 그대로 쓴다. See `docs/agents/triage-labels.md`.

### Domain docs

단일 컨텍스트: 루트 `GLOSSARY.md` + `docs/adr/`. See `docs/agents/domain.md`.
