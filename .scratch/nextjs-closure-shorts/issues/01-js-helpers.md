# 01: 자바스크립트 실행·보여주기 헬퍼와 키워드 하이라이트

**What to build:** 공용 모듈 `tools/javashorts.py`가 자바스크립트 예제를 다룰 수 있게 한다. 영상 프로젝트와 무관하게 먼저 끝낸다.

- **실행·대조 헬퍼**: 화면의 자바스크립트 코드를 `node`로 실행하고, 출력이 `expect`와 정확히 같아야 한다. 다르거나 실행 중 예외가 나면 실제 출력과 함께 빌드를 멈춘다. 결과 상자는 실제 출력으로 그린다. 인자 모양은 `jcode`와 맞춘다(`sid, lines, expect, mark=, sm=`). 이름은 구현하면서 정한다(예: `jscode`)
- **보여 주기 전용 헬퍼**: React·Next.js 코드처럼 실행할 수 없는 코드를 실행 없이 코드 블록으로만 그린다. 33자 제한·하이라이트·`mark`는 똑같이 적용한다(예: `xshow`)
- 두 헬퍼 모두 예제 기록 파일(`examples.txt`)에 남긴다. 자바스크립트 예제는 언어를 구분해 표시하고, 보여 주기 전용은 "실행하지 않음(React·Next.js 코드)" 주석을 단다
- **하이라이터**: `let`, `const`, `var`, `function`, `return`, `async`, `await`, `export`, `default`, `throw`, `for`, `of` 등 자바스크립트 키워드와 `=>`를 키워드 색으로 칠한다. 기존 자바 키워드 목록은 추가만 하고 빼지 않는다. `"use server"`는 문자열 색 그대로
- `docs/java-helpers.md` 헬퍼 표에 두 헬퍼를 추가한다

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] 자바스크립트 예제가 `node`로 실행·대조되고, `expect`를 일부러 틀리게 주면 실제 출력과 함께 빌드가 멈춘다
- [x] 실행 중 예외가 나는 자바스크립트 예제도 빌드를 멈춘다
- [x] 보여 주기 전용 헬퍼가 33자 넘는 줄에서 빌드를 멈춘다
- [x] `let`·`const`·`=>` 등이 키워드 색으로 칠해진다
- [x] 기존 자바 영상 두 편 이상(예: `java-thread-shorts`, `java-lambda-shorts`)을 다시 빌드해 `index.html`·`examples.txt`에 `git diff`가 없다. 차이가 생기면(예: 자바 코드의 `var`, `default`가 새로 칠해짐) 원인과 처리를 Comments에 남긴다
- [x] `docs/java-helpers.md`에 문서화했다

## Comments

- 구현: `jscode`(node 실행·대조), `xshow`(실행 없이 그리기), `code(js=True)`/`hl(js=True)`.
- 범위 조정: 티켓은 자바 키워드 목록에 자바스크립트 키워드를 추가하자고 했지만, `of`(`List.of`)·`var`·`default` 등이 기존 자바 코드 색을 바꿀 수 있어 **별도 목록 `JSKW`**를 두고 `js=True` 블록에만 적용했다. `=>`도 자바스크립트 블록에서만 칠한다.
- `examples.txt`: 자바스크립트는 `main.js`, 보여 주기 전용은 "실행하지 않음 (React·Next.js 코드)"로 남는다(`build()`의 결과 문구 분기에 "실행하지" 추가).
- 검증: 기대값 틀림·실행 중 예외(`TypeError`)·33자 초과에서 모두 빌드 중단 확인. 22편·19편·21편 재빌드 `git diff` 없음.
