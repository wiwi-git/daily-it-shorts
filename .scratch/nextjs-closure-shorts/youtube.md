# 유튜브 업로드: Next.js 클로저

## 제목

```
Next.js: 클로저 | 자바스크립트 vs 자바 · 사실상 final · React 스냅샷 · 서버 액션 #shorts
```

## 설명

```
Next.js 클로저! 같은 코드인데 자바스크립트는 2를 출력하고, 자바는 컴파일 오류가 나요. 자바와 비교하면서 클로저를 정리해요. (자바 입문 시리즈를 본 분들을 위한 새 Next.js 시리즈예요)

📌 오늘 배우는 것
1. 클로저 = 함수 + 그 함수가 만들어진 곳의 바깥 변수 · makeCounter()가 끝나도 count는 살아 있음 (1 2 1)
2. 자바스크립트는 변수 자체를 붙잡아서 바뀐 값(2)이 보임 · 자바는 클로저 대신 '람다식의 캡처'라고 부르고, 사실상 final만 캡처할 수 있어 컴파일 오류
3. 자바가 막은 이유: 계속 바뀌는 지역 변수를 붙잡으면 동시성 문제 (자바 언어 명세) · int 배열로 우회, 실무는 AtomicInteger
4. 반복문 함정: var는 모두 3, let은 0 1 2 · 자바는 일반 for 변수를 람다식에서 못 쓰고, 향상된 for는 가능
5. React 상태는 스냅샷: 3초 뒤 알림은 0 · 한 핸들러에서 여러 번 바꿀 땐 업데이터 함수 (+1 세 번 → 1, 업데이터면 3)
   ⚠️ 서버 액션이 붙잡은 변수는 브라우저를 오가요. 자동 암호화되지만 암호화만 믿고 비밀값을 넣지 마세요

✅ 자바스크립트·자바 예제는 모두 실제로 실행해서 확인한 결과예요 (Node.js 24, OpenJDK 25). React·Next.js 코드는 공식 문서(react.dev, nextjs.org) 내용을 따랐어요

#nextjs #자바스크립트 #javascript #클로저 #closure #자바 #java #react #shorts
```

## README 영상 목록 행 (업로드 후 URL 채우기)

```
| 2026-11-24 | Next.js: 클로저 (자바스크립트 vs 자바 · 변수 붙잡기 · 사실상 final · var/let 반복문 · React 스냅샷 · 서버 액션) | 2:51 | [nextjs-closure-shorts](nextjs-closure-shorts) | [YouTube](https://www.youtube.com/watch?v=<id>) |
```
