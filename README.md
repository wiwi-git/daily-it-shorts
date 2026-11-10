# IT·기술 영상 만들기

## 유튜브 채널

- 채널 URL: https://www.youtube.com/@wiwi-dev-yb

## 제출 영상

- 주제: MySQL SQL 개요와 종류 — 가성비 학습 순위 TOP 5 (DQL · DML · DDL · TCL · DCL)
- 영상 URL: https://www.youtube.com/watch?v=TL1x_Wq0S4c

- 주제: DQL SELECT 기본 문법 · JOIN · GROUP BY (WHERE · ORDER BY · LIMIT · HAVING · 논리적 처리 순서)
- 영상 URL: https://www.youtube.com/watch?v=fm1n7fj-ulI

## 영상 목록

| 날짜 | 주제 | 길이 | 폴더 | 영상 |
| --- | --- | --- | --- | --- |
| 2026-10-28 | MySQL SQL 개요와 종류 — 가성비 학습 순위 TOP 5 | 2:32 | [mysql-shorts](mysql-shorts) | [YouTube](https://www.youtube.com/watch?v=TL1x_Wq0S4c) |
| 2026-10-28 | DQL SELECT 기본 문법 · JOIN · GROUP BY | 2:36 | [select-join-groupby-shorts](select-join-groupby-shorts) | [YouTube](https://www.youtube.com/watch?v=fm1n7fj-ulI) |
| 2026-10-29 | WHERE 조건: 비교 · AND·OR · IN · LIKE | 2:39 | [where-conditions-shorts](where-conditions-shorts) | [YouTube](https://www.youtube.com/watch?v=FKns3gfo_78) |
| 2026-10-30 | DDL: CREATE · ALTER · INDEX · DROP | 2:22 | [ddl-shorts](ddl-shorts) | [YouTube](https://www.youtube.com/watch?v=4df8EiijSPs) |
| 2026-10-30 | TCL: 트랜잭션 · COMMIT · ROLLBACK · SAVEPOINT | 2:25 | [tcl-shorts](tcl-shorts) | [YouTube](https://www.youtube.com/watch?v=rYCTlI8fT2Q) |
| 2026-10-30 | DCL: CREATE USER · GRANT · REVOKE | 1:53 | [dcl-shorts](dcl-shorts) | [YouTube](https://www.youtube.com/watch?v=DXtrvu4V6QA) |
| 2026-11-02 | 자바 입문: Hello World 출력하기 (class · main · println · \n · print) | 2:33 | [java-hello-shorts](java-hello-shorts) | [YouTube](https://www.youtube.com/watch?v=vmLd9hf1s18) |
| 2026-11-03 | 자바 입문: 변수 (선언 · 대입 · int · double · char · String) | 2:50 | [java-variables-shorts](java-variables-shorts) | [YouTube](https://www.youtube.com/watch?v=fnfHwBrKP1A) |
| 2026-11-04 | 자바 입문: 배열 (new · 인덱스 · 값 교환 · 인덱스 에러 · 다차원 배열) | 2:44 | [java-arrays-shorts](java-arrays-shorts) | [YouTube](https://www.youtube.com/watch?v=PvgAXvu44S8) |
| 2026-11-05 | 자바 입문: 산술연산자 (+ - * / % · 몫과 나머지 · 0으로 나누기 · 계산 순서 · 복합 대입 · ++) | 2:45 | [java-arithmetic-shorts](java-arithmetic-shorts) | [YouTube](https://www.youtube.com/watch?v=qsWIQJt4wvI) |
| 2026-11-06 | 자바 입문: 비교·논리 연산자 (== != · equals() · && \|\| ! · 단락 평가 · 범위 검사 · 우선순위) | 2:44 | [java-compare-logic-shorts](java-compare-logic-shorts) | [YouTube](https://www.youtube.com/watch?v=2ytYJfWjn60) |
| 2026-11-06 | 자바 입문: 조건문 (if · else if · 삼항 연산자 · switch · break · 화살표 switch) | 2:24 | [java-if-switch-shorts](java-if-switch-shorts) | [YouTube](https://www.youtube.com/watch?v=3LjHCPxlE5o) |
| 2026-11-06 | 자바 입문: 반복문 (for · 합계 · 배열 순회 · while · do-while · break · continue) | 2:19 | [java-loops-shorts](java-loops-shorts) | [YouTube](https://www.youtube.com/watch?v=FillAoh7FIY) |
| 2026-11-09 | 자바 입문: 클래스와 객체 (class · new · 필드 · 기본값 · 참조) | 2:18 | [java-class-shorts](java-class-shorts) | [YouTube](https://www.youtube.com/watch?v=W85T7Ndfn3Q) |
| 2026-11-10 | 자바 입문: 메소드와 생성자 (메소드 정의·호출 · 매개변수 · return · 생성자 · this · 기본 생성자 · 오버로딩) | 2:29 | [java-method-constructor-shorts](java-method-constructor-shorts) | [YouTube](https://www.youtube.com/watch?v=Uhyl_6oat3Y) |

## 제작 방식

- **영상**: [HyperFrames](https://hyperframes.heygen.com) — HTML/CSS + GSAP 애니메이션을 MP4로 렌더링
- **나레이션**: [Edge TTS](https://github.com/rany2/edge-tts) `ko-KR-SunHiNeural` 음성 (+34% 속도, `java-method-constructor-shorts`부터 · 이전 영상은 +12%)
- **자막**: Edge TTS의 단어 경계(WordBoundary) 타이밍에 맞춰 자동 생성
- **예제 검증**: 빌드할 때 화면의 예제 쿼리를 실제로 실행해 대본의 결과와 대조하고, `queries.sql`로 저장
  (SELECT는 SQLite, DDL·TCL·DCL은 Docker로 띄운 임시 MySQL 26.10.0(이미지 고정) — `tools/mysql-sandbox.sh start`)
  (Java 영상은 화면의 예제를 `javac`·`java`로 컴파일·실행해 출력 또는 컴파일 오류를 대조하고, `examples.txt`로 저장)
- **폰트**: [Pretendard](https://github.com/orioncactus/pretendard) (SIL OFL 1.1)

## 폴더 구조

```
.
├── README.md
├── requirements.txt          # Python 의존성 (edge-tts)
├── output/                   # 렌더링된 영상 (git 제외)
├── tools/mysql-sandbox.sh    # 예제 검증용 임시 MySQL 컨테이너 (start / stop)
├── select-join-groupby-shorts/   # (영상별 폴더, 구조는 아래와 동일)
└── mysql-shorts/             # HyperFrames 프로젝트 (영상 1개 = 폴더 1개)
    ├── script.json           # 장면별 나레이션 대본
    ├── gen_vo.py             # 대본 → 장면별 TTS 음성 + 타이밍(vo.json)
    ├── build.py              # vo.json → narration.mp3 + index.html(화면·자막)
    ├── index.html            # 생성된 HyperFrames 컴포지션
    ├── queries.sql           # 영상의 예제 쿼리 (where-conditions-shorts부터, 직접 실행 가능)
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
