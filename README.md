# IT·기술 영상 만들기

## 유튜브 채널

- 채널 URL: https://www.youtube.com/@wiwi-dev-yb

## 제출 영상

- 주제: MySQL SQL 개요와 종류 — 가성비 학습 순위 TOP 5 (DQL · DML · DDL · TCL · DCL)
- 영상 URL: https://www.youtube.com/watch?v=TL1x_Wq0S4c

## 영상 목록

| 날짜 | 주제 | 길이 | 폴더 | 영상 |
| --- | --- | --- | --- | --- |
| 2026-10-28 | MySQL SQL 개요와 종류 — 가성비 학습 순위 TOP 5 | 2:32 | [mysql-shorts](mysql-shorts) | [YouTube](https://www.youtube.com/watch?v=TL1x_Wq0S4c) |
| 2026-10-28 | DQL SELECT 기본 문법 · JOIN · GROUP BY | 2:36 | [select-join-groupby-shorts](select-join-groupby-shorts) | [YouTube](https://www.youtube.com/watch?v=fm1n7fj-ulI) |

## 제작 방식

- **영상**: [HyperFrames](https://hyperframes.heygen.com) — HTML/CSS + GSAP 애니메이션을 MP4로 렌더링
- **나레이션**: [Edge TTS](https://github.com/rany2/edge-tts) `ko-KR-SunHiNeural` 음성 (+12% 속도)
- **자막**: Edge TTS의 단어 경계(WordBoundary) 타이밍에 맞춰 자동 생성
- **폰트**: [Pretendard](https://github.com/orioncactus/pretendard) (SIL OFL 1.1)

## 폴더 구조

```
.
├── README.md
├── requirements.txt          # Python 의존성 (edge-tts)
├── output/                   # 렌더링된 영상 (git 제외)
├── select-join-groupby-shorts/   # (영상별 폴더, 구조는 아래와 동일)
└── mysql-shorts/             # HyperFrames 프로젝트 (영상 1개 = 폴더 1개)
    ├── script.json           # 장면별 나레이션 대본
    ├── gen_vo.py             # 대본 → 장면별 TTS 음성 + 타이밍(vo.json)
    ├── build.py              # vo.json → narration.mp3 + index.html(화면·자막)
    ├── index.html            # 생성된 HyperFrames 컴포지션
    └── assets/fonts/         # Pretendard 폰트 + 라이선스(OFL.txt)
```

> 렌더링된 영상과 나레이션 음성(`*.mp3`)은 저장소에 포함하지 않습니다. 음성은 아래 1~2단계로 다시 만들 수 있습니다.

## 다시 만들기

필요한 것: Node.js 22 이상, Python 3, FFmpeg

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd mysql-shorts                 # 만들 영상 폴더로 이동
../.venv/bin/python gen_vo.py   # 1. 나레이션 생성
python3 build.py                # 2. 화면·자막 생성
npx hyperframes check           # 3. 검사
npx hyperframes render -o ../output/<영상이름>.mp4   # 4. 렌더링
```

대본을 고치려면 `script.json`을, 화면 문구와 코드 예시를 고치려면 `build.py`의 `scenes`를 수정한 뒤 1~4단계를 다시 실행하세요.
