# IT·기술 영상 만들기

## 유튜브 채널

- 채널 URL: https://www.youtube.com/@wiwi-dev-yb

## 제출 영상

- 주제: MySQL SQL 개요와 종류 — 가성비 학습 순위 TOP 5 (DQL · DML · DDL · TCL · DCL)
- 영상 URL: https://www.youtube.com/shorts/TL1x_Wq0S4c

## 영상 소개

SQL을 처음 배울 때 무엇부터 공부하면 좋은지, 실무에서 쓰는 빈도를 기준으로 정리한 유튜브 쇼츠(2분 32초, 1080×1920)입니다.

| 순위 | 분류 | 대표 명령어 | 핵심 포인트 |
| --- | --- | --- | --- |
| 1 | DQL | `SELECT` (+ `JOIN`, `GROUP BY`) | 실무 쿼리의 대부분은 조회 |
| 2 | DML | `INSERT` · `UPDATE` · `DELETE` | `WHERE`를 빠뜨리면 테이블 전체가 바뀜 |
| 3 | DDL | `CREATE` · `ALTER` · `DROP` | 잘못 쓰면 되돌리기 어려움 |
| 4 | TCL | `COMMIT` · `ROLLBACK` | MySQL 기본값은 `autocommit = 1` |
| 5 | DCL | `GRANT` · `REVOKE` | 주로 DBA·인프라 담당 업무 |

## 제작 방식

- **영상**: [HyperFrames](https://hyperframes.heygen.com) — HTML/CSS + GSAP 애니메이션을 MP4로 렌더링
- **나레이션**: [Edge TTS](https://github.com/rany2/edge-tts) `ko-KR-SunHiNeural` 음성 (+12% 속도)
- **자막**: Edge TTS의 문장 경계 타이밍을 이용해 자동 생성
- **폰트**: [Pretendard](https://github.com/orioncactus/pretendard) (SIL OFL 1.1)

## 폴더 구조

```
.
├── README.md
├── requirements.txt          # Python 의존성 (edge-tts)
├── output/                   # 렌더링된 영상 (git 제외)
└── mysql-shorts/             # HyperFrames 프로젝트
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
cd mysql-shorts
../.venv/bin/python gen_vo.py   # 1. 나레이션 생성
python3 build.py                # 2. 화면·자막 생성
npx hyperframes check           # 3. 검사
npx hyperframes render -o ../output/mysql-sql-shorts.mp4   # 4. 렌더링
```

대본을 고치려면 `script.json`을, 화면 문구와 코드 예시를 고치려면 `build.py`의 `scenes`를 수정한 뒤 1~4단계를 다시 실행하세요.
