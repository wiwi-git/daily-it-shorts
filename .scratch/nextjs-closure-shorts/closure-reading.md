# 클로저 읽기 자료 — 자바스크립트 · 자바 · Next.js

> 영상 기획 전에 읽는 배경 자료. 각 절 끝에 공식 문서 링크를 달았다.
> 아래 예제의 출력은 Node.js와 OpenJDK 25로 직접 실행해 확인했다(2026-11-24).

---

## 1. 클로저란 무엇인가 (공식 정의)

MDN의 정의를 옮기면:

> 클로저는 **함수**와, 그 함수를 둘러싼 상태(**렉시컬 환경**)에 대한 **참조**를 묶은 조합이다.
> 즉 클로저는 함수가 자신의 바깥 스코프에 접근할 수 있게 해 준다.
> 자바스크립트에서는 함수가 만들어질 때마다, 만들어지는 시점에 클로저도 함께 만들어진다.

핵심 단어는 세 개다.

| 단어 | 뜻 |
|---|---|
| 렉시컬(lexical) 스코프 | 변수를 찾는 범위가 **코드를 적은 위치**로 정해진다(호출한 위치가 아님) |
| 캡처(capture) | 안쪽 함수가 바깥 변수를 붙잡아 두는 것 |
| 바깥 함수가 끝난 뒤 | 바깥 함수의 실행이 끝나도, 안쪽 함수가 살아 있는 한 붙잡은 변수도 살아 있다 |

출처: [MDN — Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)

---

## 2. 자바스크립트 클로저

### 2-1. 대표 예제: 카운터

```js
function makeCounter() {
  let count = 0;
  return () => ++count;   // count를 캡처
}
const c1 = makeCounter();
const c2 = makeCounter();
console.log(c1(), c1(), c2());   // 1 2 1
```

- `makeCounter()`는 이미 끝났지만 `c1`은 자기 `count`를 계속 들고 있다.
- `c1`과 `c2`는 **각자 다른** `count`를 가진다 — 호출할 때마다 새 렉시컬 환경이 생기기 때문.
- 바깥에서 `count`에 직접 접근할 방법이 없다 → MDN은 이를 "클로저로 private 흉내 내기"로 소개한다.

### 2-2. 값이 아니라 "변수"를 붙잡는다

```js
let x = 1;
const f = () => x;
x = 2;
console.log(f());   // 2
```

자바스크립트 클로저는 만들어진 순간의 **값을 복사하지 않고 변수 자체(참조)** 를 붙잡는다.
그래서 나중에 바뀐 값이 보인다. → **자바와 가장 크게 다른 점**(3절).

### 2-3. 고전적인 함정: 반복문 + `var`

```js
const a = [], b = [];
for (var i = 0; i < 3; i++) a.push(() => i);
for (let j = 0; j < 3; j++) b.push(() => j);
console.log(a.map(g => g()));   // [3, 3, 3]
console.log(b.map(g => g()));   // [0, 1, 2]
```

- `var i`는 함수 전체에 **하나뿐**이라 세 함수가 같은 `i`를 붙잡는다 → 반복이 끝난 뒤의 3.
- `let j`는 블록 스코프라 **반복마다 새 변수**가 생긴다 → 0, 1, 2.
- MDN은 해결책으로 `let`/`const`, `for...of`, `forEach`를 제시한다.

위 설명이 잘 와닿지 않으면 아래 순서대로 천천히 따라가 보자. 출력은 모두 Node.js로 실행해 확인했다.

#### ① 핵심 한 줄

> 함수는 변수의 **값**이 아니라 **변수 상자**를 기억한다. 그리고 **실행하는 순간** 상자 안을 들여다본다.

#### ② 반복문 없이 먼저

```js
var i = 0;
const f = () => i;   // f는 "상자 i"를 기억 (0이라는 값을 복사하지 않음)
i = 5;               // 상자 안의 값을 바꿈
console.log(f());    // 5  ← 실행하는 순간 상자를 보니 5
```

2-2절과 같은 이야기다. 함수를 **만든 때**의 값(0)이 아니라 **실행한 때**의 값(5)이 나온다.

#### ③ `var` 반복문을 풀어 쓰면

```js
const a = [];
for (var k = 0; k < 3; k++) {
  a.push(() => k);
}
```

이 반복문은 사실상 이렇게 돌아간다.

```js
var k = 0;           // 상자 k는 딱 하나
a.push(() => k);     // 함수1: 상자 k를 기억 (지금 k는 0)
k++;                 // 같은 상자 k → 1
a.push(() => k);     // 함수2: 같은 상자 k를 기억
k++;                 // → 2
a.push(() => k);     // 함수3: 또 같은 상자 k를 기억
k++;                 // → 3, 이제 3 < 3이 거짓이라 반복 끝

console.log(a.map(f => f()));  // [3, 3, 3]
console.log(k);                // 3  ← var라서 반복문 밖에서도 상자가 보인다
```

- 함수를 **만드는 시점**(k가 0, 1, 2일 때)과 **실행하는 시점**(반복이 다 끝난 뒤)이 다르다.
- 실행할 때 세 함수가 모두 같은 상자를 들여다보는데, 그 안에는 3이 들어 있다.
- 왜 하필 3일까? 마지막 `k++`로 3이 된 뒤 `3 < 3`을 검사하고 멈췄기 때문이다.

#### ④ `let`은 반복마다 새 상자

```js
const b = [];
for (let j = 0; j < 3; j++) {
  b.push(() => j);
}
```

`let`이면 반복 한 번마다 상자가 새로 생긴다. 풀어 쓰면 대략 이런 모양이다.

```js
{ let j = 0; b.push(() => j); }   // 함수1: 상자 j① (0)
{ let j = 1; b.push(() => j); }   // 함수2: 상자 j② (1)
{ let j = 2; b.push(() => j); }   // 함수3: 상자 j③ (2)

console.log(b.map(f => f()));  // [0, 1, 2]
console.log(typeof j);         // "undefined"  ← 반복문 밖에는 j가 없다
```

각 함수가 **자기만의 상자**를 기억하고, 그 상자의 값은 나중에 바뀌지 않는다. 그래서 0, 1, 2가 나온다.

#### ⑤ 그림으로 보면

```
var:   함수1 ─┐
       함수2 ─┼─→ [ k ] = 3       (상자 하나를 셋이 같이 씀)
       함수3 ─┘

let:   함수1 ───→ [ j① ] = 0
       함수2 ───→ [ j② ] = 1      (각자 자기 상자)
       함수3 ───→ [ j③ ] = 2
```

#### ⑥ 해결 방법 세 가지

핵심은 **반복마다 새 상자를 만드는 것**이다.

```js
// 1) var 대신 let  (④번)
for (let j = 0; j < 3; j++) b.push(() => j);           // [0, 1, 2]

// 2) var 반복은 그대로 두고, 안에서 const로 새 상자를 만든다
const c = [];
for (var m = 0; m < 3; m++) {
  const v = m;           // 반복마다 새 상자 v
  c.push(() => v);
}
console.log(c.map(f => f()));  // [0, 1, 2]

// 3) for...of  (반복마다 x가 새로 생김)
const d = [];
for (const x of [0, 1, 2]) d.push(() => x);
console.log(d.map(f => f()));  // [0, 1, 2]
```

#### ⑦ 실무에서는 어디서 만나나

함수를 **나중에 실행하는** 곳이면 어디서든 나온다. 대표적인 것이 타이머다.

```js
for (var p = 0; p < 3; p++) {
  setTimeout(() => console.log(p), 100);   // 0.1초 뒤: 3, 3, 3
}
for (let q = 0; q < 3; q++) {
  setTimeout(() => console.log(q), 100);   // 0.1초 뒤: 0, 1, 2
}
```

`onClick` 같은 이벤트 핸들러도 같다. 핸들러는 반복문 안에서 **만들고**, 사용자가 클릭할 때 **실행**되므로 그때는 반복이 이미 끝나 있다. MDN의 클로저 문서가 이 함정을 `onfocus` 핸들러 예제로 설명하는 것도 이 때문이다.

#### ⑧ 자바와 연결하면

- 자바에서 일반 `for`의 `i`를 람다식 안에서 쓰면 **컴파일 오류**가 난다(3-4절). `i`는 계속 바뀌는 변수라 사실상 final이 아니기 때문이다. 자바스크립트의 `var` 함정을 컴파일러가 미리 막아 주는 셈이다.
- 향상된 `for`(`for (int x : list)`)의 `x`는 **반복마다 새 변수**라서 람다식에서 쓸 수 있다. 자바스크립트의 `let`이나 `for...of`와 같은 구조다.

### 2-4. 클로저 = "메소드 하나짜리 객체"

MDN: 클로저는 데이터(렉시컬 환경)와 그 데이터를 다루는 함수를 묶는다.
객체가 속성과 메소드를 묶는 것과 닮았으므로, **메소드가 하나뿐인 객체를 쓸 자리에 클로저를 쓸 수 있다.**
→ 자바의 "함수형 인터페이스를 구현한 객체 = 람다식"과 바로 이어지는 관점.

출처: [MDN — Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)
(절: *Lexical scoping*, *Practical closures*, *Emulating private methods with closures*, *Creating closures in loops*)

---

## 3. 자바에서의 클로저: 람다식 · 지역 클래스 · 익명 클래스

자바에는 "클로저"라는 문법 이름은 없지만, 람다식과 지역·익명 클래스가 바깥 지역 변수를 **캡처**한다.
오라클 튜토리얼: *"람다식도 지역 클래스·익명 클래스처럼 변수를 캡처할 수 있다."*

### 3-1. 규칙: final 또는 사실상 final만 캡처할 수 있다

JLS §15.27.2:

> 람다식 안에서 쓰지만 람다식 안에서 선언하지 않은 지역 변수·매개변수·예외 매개변수는
> `final`이거나 **사실상 final(effectively final)** 이어야 한다.

사실상 final = 초기화한 뒤 **한 번도 값을 바꾸지 않은** 변수(오라클 튜토리얼, Java SE 8부터).

```java
int x = 1;
Supplier<Integer> f = () -> x;
x = 2;   // ← 컴파일 오류
```

```
error: local variables referenced from a lambda expression
       must be final or effectively final
```

자바스크립트 2-2와 같은 코드인데, 자바스크립트는 `2`를 출력하고 자바는 **컴파일조차 안 된다.**

### 3-2. 왜 이런 제한이 있나 (공식 이유)

JLS §15.27.2:

> 사실상 final 제한은 **계속 바뀌는 지역 변수**에 접근하는 것을 막는다.
> 그런 변수를 캡처하면 **동시성 문제**를 일으킬 가능성이 크다.
> `final`만 허용하던 때보다는 프로그래머의 수고를 줄여 준다.

정리하면 자바는 지역 변수의 **값을 복사해** 캡처한다(스택의 지역 변수는 메소드가 끝나면 사라지므로).
값이 바뀔 수 있다면 "복사본"과 "원본"이 달라져 헷갈리므로, 아예 바뀌지 않는 변수만 허용한다.
※ "값을 복사한다"는 표현은 JLS 원문이 아니라 동작을 설명하는 말이다. 영상에서는 "바뀌지 않는 변수만 붙잡을 수 있다"까지만 단정한다.

### 3-3. 카운터를 자바로 옮기면

```java
static IntSupplier makeCounter() {
    int count = 0;
    return () -> ++count;   // ← 컴파일 오류: count가 사실상 final이 아님
}
```

우회 방법(변수 자체가 아니라 **가리키는 객체의 내용**을 바꾼다):

```java
static IntSupplier makeCounter() {
    int[] count = {0};             // 배열 참조는 바뀌지 않음 → 사실상 final
    return () -> ++count[0];
}
// c1 → 1, 2 / c2 → 1   (자바스크립트와 같은 결과)
```

실무에서는 배열 대신 `AtomicInteger`나 필드를 가진 클래스를 쓴다(스레드 안전성 때문 — 22편 스레드·동기화 영상과 연결 가능).

### 3-4. 반복문 비교 (JLS 예제 m9·m10)

- 일반 `for (int i = 0; ...; i++)`의 `i`는 바뀌므로 람다에서 쓸 수 없다 → 컴파일 오류.
- 향상된 `for (String s : arr)`의 `s`는 **반복마다 새 변수**라 사실상 final → 쓸 수 있다.
- 자바스크립트의 `var`(같은 변수 공유) vs `let`(반복마다 새 변수)과 같은 구도. 자바는 틀릴 수 있는 쪽을 **컴파일러가 막는다.**

### 3-5. `this`의 의미

JLS §15.27.2: 람다 몸체 안의 `this`·이름의 의미는 **바깥 문맥과 같다**(익명 클래스는 자기 자신을 가리킴).
→ 자바스크립트의 화살표 함수가 바깥 `this`를 그대로 쓰는 것과 닮았다(영상 범위 밖으로 둘 후보).

출처:
- [JLS SE 21 §15.27.2 Lambda Body](https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.27.2)
- [Oracle Java Tutorial — Lambda Expressions: Accessing Local Variables of the Enclosing Scope](https://docs.oracle.com/javase/tutorial/java/javaOO/lambdaexpressions.html#accessing-local-variables)
- [Oracle Java Tutorial — Local Classes: Accessing Members of an Enclosing Class](https://docs.oracle.com/javase/tutorial/java/javaOO/localclasses.html)

---

## 4. 자바스크립트 vs 자바 한눈에

| | 자바스크립트 | 자바 |
|---|---|---|
| 무엇이 클로저인가 | 모든 함수(만들어질 때마다) | 람다식, 지역·익명 클래스 |
| 무엇을 붙잡나 | 변수 자체(참조) | 사실상 final인 지역 변수의 값 |
| 붙잡은 뒤 바깥에서 값 변경 | 가능, 클로저에서도 바뀐 값이 보임 | 컴파일 오류 |
| 클로저 안에서 값 변경(`++count`) | 가능 | 컴파일 오류 → 배열·`AtomicInteger`·필드로 우회 |
| 반복문 함정 | `var`면 모두 마지막 값, `let`이면 해결 | 일반 `for` 변수는 아예 못 씀, 향상된 `for`는 가능 |
| 설계 이유 | 렉시컬 환경을 그대로 유지 | 동시성 문제 예방(JLS) |

---

## 5. React에서의 클로저: 상태는 "스냅샷"

Next.js 화면은 React 컴포넌트라 클로저 문제가 대부분 여기서 나온다.

### 5-1. 렌더링마다 새 클로저

react.dev *State as a Snapshot* 예제:

```jsx
const [number, setNumber] = useState(0);
<button onClick={() => {
  setNumber(number + 5);
  setTimeout(() => alert(number), 3000);
}}>+5</button>
```

3초 뒤 화면은 5인데 알림은 **0**. 이벤트 핸들러는 **그 렌더링 때의 `number`(0)** 를 붙잡은 클로저이기 때문이다.
공식 문서 표현: 상태 변수는 일반 변수처럼 보이지만 **스냅샷**처럼 동작한다.

### 5-2. 오래된 클로저(stale closure)와 해결

react.dev *useEffect* 예제: `setInterval` 안에서 `setCount(count + 1)`을 쓰면 `count`를 의존성에 넣어야 하고,
그러면 값이 바뀔 때마다 타이머가 다시 설정된다. 해결은 **업데이터 함수**:

```jsx
useEffect(() => {
  const id = setInterval(() => {
    setCount(c => c + 1);   // 붙잡은 count 대신 "이전 값"을 받아서 계산
  }, 1000);
  return () => clearInterval(id);
}, []);
```

출처:
- [React — State as a Snapshot](https://react.dev/learn/state-as-a-snapshot)
- [React — useEffect: Updating state based on previous state from an Effect](https://react.dev/reference/react/useEffect#updating-state-based-on-previous-state-from-an-effect)

---

## 6. Next.js만의 클로저: 서버 액션과 암호화

Next.js 공식 문서 *Data Security → Closures and encryption* 절:

```tsx
// app/page.tsx  (서버 컴포넌트)
export default async function Page() {
  const publishVersion = await getLatestVersion();

  async function publish() {
    "use server";
    if (publishVersion !== await getLatestVersion()) {
      throw new Error('The version has changed since pressing publish');
    }
    ...
  }

  return (
    <form>
      <button formAction={publish}>Publish</button>
    </form>
  );
}
```

문서 내용 요약:

1. 컴포넌트 안에서 서버 액션을 정의하면 **클로저**가 되어 바깥 변수(`publishVersion`)에 접근할 수 있다.
2. 쓰임새: **렌더링 시점의 데이터 스냅샷**을 붙잡아 두었다가, 나중에 액션이 호출될 때 쓰는 것.
3. 그런데 이렇게 하려면 붙잡은 변수가 **클라이언트(브라우저)로 보내졌다가 액션 호출 때 서버로 돌아온다.**
4. 민감한 값이 노출되지 않도록 Next.js가 붙잡은 변수를 **자동으로 암호화**한다. 빌드할 때마다 액션별 새 개인 키를 만들므로, 액션은 그 빌드에서만 호출할 수 있다.
5. **"암호화에만 의존해 민감한 값을 숨기는 것은 권장하지 않는다."** (공식 Good to know)
6. 여러 서버로 자체 호스팅할 때는 `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`로 키를 통일한다(고급).

왜 흥미로운가: 자바스크립트 클로저는 원래 **같은 메모리 안에서** 변수를 붙잡는데, 서버 액션은 서버 → 브라우저 → 서버로
**네트워크를 건너야** 하므로 붙잡은 값을 직렬화해 들고 다녀야 한다. 같은 "클로저"라는 개념이 프레임워크 경계를 넘을 때 생기는 일.

출처:
- [Next.js — How to think about data security: Closures and encryption](https://nextjs.org/docs/app/guides/data-security#closures-and-encryption)
- [Next.js — Self-Hosting: Server Functions encryption key](https://nextjs.org/docs/app/guides/self-hosting#server-functions-encryption-key)

---

## 7. 이 저장소의 기존 영상과 겹치는 부분

- **19편 람다식**(`java-lambda-shorts`)이 이미 "사실상 final"을 다뤘다 → 이번 영상은 반복 설명보다 **"자바스크립트는 되는데 자바는 왜 안 되나"** 비교로 쓰는 편이 새롭다.
- **22편 스레드·동기화** → JLS가 든 이유(동시성 문제)와 `AtomicInteger` 우회를 연결할 수 있다.
- 지금까지 시리즈는 자바·SQL뿐이라 자바스크립트/Next.js는 **첫 영상**이다. 브랜드·진행 표시·코드 색 규칙(자바스크립트 키워드 색 등)을 새로 정해야 한다.
