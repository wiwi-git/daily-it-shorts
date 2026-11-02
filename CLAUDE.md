# daily-it-shorts

IT·기술 정보성 유튜브 쇼츠를 매일 하나씩 만드는 저장소. 영상 1개 = 폴더 1개(HyperFrames 프로젝트).
새 영상은 **기존 영상과 같은 디자인·제작 방식**으로 만든다. 기준 구현은 가장 최근 폴더인
`where-conditions-shorts/`(`gen_vo.py`, `build.py`)이며, 새 폴더는 이를 복사해 `script.json`과
`build.py`의 `scenes`만 바꾸는 것에서 시작한다.

## 영상 규격

- 세로 9:16, 1080×1920, 길이 3분 이하(지금까지 2분 30초 안팎)
- 한국어 나레이션: Edge TTS `ko-KR-SunHiNeural`, rate `+12%`
- 한국어 자막 필수, 나레이션과 단어 단위로 동기화
- 렌더링 결과는 `output/<영상이름>.mp4` (git 제외)

## 제작 순서

1. **내용 구성**: 장면 목록(도입 → STEP 1… → 정리)과 각 장면에서 보여줄 코드·표를 먼저 정한다
2. **대본**: `script.json`에 `{id, section, text}`로 장면별 나레이션 작성
3. **음성**: `../.venv/bin/python gen_vo.py` → `assets/vo/*.mp3`, `vo.json`(단어 타이밍 포함)
4. **화면**: `build.py`의 `scenes`, `PROG` 수정 → `python3 build.py` → `index.html`, `assets/narration.mp3`, `queries.sql`
   (빌드가 예제 쿼리를 실제로 실행해 대본의 기대 결과와 다르면 멈춘다)
5. **검증**: `npx hyperframes check` 통과 → `npx hyperframes snapshot`으로 모든 장면 확인 → 렌더링
6. **기록**: README의 "영상 목록"에 행 추가(URL은 업로드 후 `watch?v=` 형식으로)

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

**구성 요소** (`build.py` 헬퍼)

- `head(step, title, desc)`: STEP 라벨 + 제목 + 설명(`<b>`는 주황 강조)
- `code(lines, mark=())`: 42px 코드 블록, `mark`로 그 장면의 핵심 줄에 주황 배경
- `qcode(sid, lines, *expect, mark=())`: 실행되는 예제 쿼리용 `code()`. 각 문장을 예시 데이터 `P`에 실행해
  `expect`(나레이션이 말하는 결과 id 목록)와 다르면 빌드 중단, `queries.sql`에 기록. `WHERE`만 보여줘도 됨.
  결과 표·칩은 id를 직접 쓰지 말고 `got()`(직전 쿼리의 실제 결과)로 그린다
- `qsql(sid, lines, expect, check=, user=)` / `setup(sid, sql)`: SELECT 결과로 확인할 수 없는 주제(DDL·TCL·DCL)용.
  `../tools/mysql-sandbox.sh start`로 띄운 임시 MySQL에서 코드를 `user` 계정으로 실행하고, 이어서 보이지 않는
  `check` 쿼리의 결과 행(또는 코드가 낸 `ERROR nnnn`)을 `expect`와 대조. 기준 구현은 `ddl-shorts`·`tcl-shorts`·`dcl-shorts`.
  앞 블록에서 이어지는 트랜잭션은 `pre=`로 같은 세션에서 실행하고, 두 세션 예제는 `two_sessions()`처럼
  A가 자기 값을 읽은 뒤에 B를 조회하게 동기화한다(고정 sleep 금지). 트랜잭션 예제는 COMMIT/ROLLBACK으로 닫는다
- `res(ids, bad=())`: 결과를 한 줄 칩으로(공간이 좁은 두 쿼리 비교 장면용), `bad`는 빨간 ⚠ 표시
- `table(cols, rows, label)`: 40px 결과 표. 행 클래스 `k1`/`k2`/`k3`은 대상별 색, `out`은 제외(취소선), 값 `None`은 빨간 NULL
- `.warn`(빨간 경고) · `.note`(파란 메모) · `.chips`(키워드 칩) · `.vs`(두 개념 비교 카드) · `.list/.row`(번호 목록)
- 도입 장면: `.hook` + 150px `.big` 제목(핵심 단어 `<em>` 주황)
- 정리 장면: 목록 전체를 먼저 보여주고, 나레이션이 항목을 말하는 순간 `word_time()`으로 그 줄을 강조. 마지막에 "👍 구독 · 좋아요"

**모션**: 각 장면의 `.in` 요소는 아래에서 50px 올라오며 순서대로 등장(0.5s, power3.out), 코드는 한 줄씩 등장.
장면 전환은 다음 장면 시작 0.15초 전. 장면 사이 간격 0.45초.

## 내용·대본 원칙

- 대본 작성 후 제작 전에 사실 검토: 결과가 있는 예제 쿼리는 모두 `qcode()`로 넣어 빌드가 실행·대조하게 한다.
  자동 대조는 쿼리 결과까지만이므로, 나레이션 문장("네 개가 남아요")이 `expect`와 같은지는 직접 확인한다

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
