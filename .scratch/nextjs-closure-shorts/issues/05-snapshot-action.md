# 05: STEP 5 React 스냅샷 · 서버 액션

**What to build:** 01의 보여 주기 전용 헬퍼로 Next.js 실무 장면 두 개(진행 둘 다 5). 실행하지 않으므로 나레이션은 [closure-reading.md](../closure-reading.md) 5·6절의 공식 문서 문장 범위 안에서만 쓴다.

- snapshot: `useState`로 만든 `number`, `+5` 버튼의 `onClick` 핸들러 몸체만 — `setNumber(number + 5);` 후 `setTimeout`으로 3초 뒤 `alert(number)`. 화면은 5인데 알림은 `0`(결과는 그림·상자로 표시하되 "실행 결과"가 아니라 설명으로 라벨). 그 렌더링의 스냅샷을 붙잡은 클로저라서. 해결: 업데이터 `setCount(c => c + 1)`
- action: 서버 컴포넌트 `Page` 안에서 `const version = await getVersion();`, 안쪽 `async function publish() { "use server"; ... }`가 `version`을 붙잡는다(공식 예제를 33자 이하로 축약). 말할 것은 세 가지뿐: 붙잡은 변수가 브라우저로 갔다가 서버로 돌아온다 / Next.js가 자동으로 암호화한다 / `.warn` "암호화만 믿고 비밀값을 넣지 말 것"
- 키 생성 방식, `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`, `useEffect` 의존성 배열은 말하지 않는다

**Blocked by:** 02

**Status:** resolved

- [x] 두 장면의 코드가 보여 주기 전용 헬퍼로 그려지고 `examples.txt`에 "실행하지 않음" 주석과 함께 남는다
- [x] 코드 한 줄 33자 이하, 하이라이트 정상(`"use server"`는 문자열 색)
- [x] 나레이션 문장마다 closure-reading.md의 공식 문서 근거를 대조해 확인했다
- [x] 겹침·넘침 없음

## Comments

- snapshot: react.dev "State as a Snapshot" 예제 그대로(`onClick` 몸체). "화면 5 · 알림 0"은 실행 결과가 아니라 "클릭 3초 뒤" 설명 라벨. 해결 메모 `setNumber(n => n + 5)`.
- action: 공식 예제 축약(`version`, `getVersion()`, 비교 줄은 `// version 사용` 주석으로). 서버 → 🔒 브라우저 → 서버 칩 + 경고.
- 나레이션 대조: "붙잡은 변수는 브라우저로 보내졌다가 액션을 부를 때 서버로 돌아와요"(captured variables are sent to the client and back), "자동으로 암호화"(automatically encrypts), "암호화만 믿지 말라"(don't recommend relying on encryption alone). 스냅샷 문장은 react.dev 표현.
