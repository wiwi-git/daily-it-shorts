# 유튜브 업로드: 자바 입문 24편 스레드 풀

## 제목

```
자바 입문 24편: 스레드 풀 | ExecutorService · submit · Future · get #shorts
```

## 설명

```
자바 입문 스물네 번째, 스레드 풀! 22편에서는 작업마다 new Thread로 스레드를 직접 만들었죠. 이번엔 스레드를 정해 둔 개수만 만들어 돌려 쓰는 방법과, 작업의 결과를 돌려받는 방법을 알아봐요.

📌 오늘 배우는 것
1. 작업마다 스레드를 새로 만들면 작업 수만큼 스레드가 생김 → 스레드 풀은 정해 둔 개수까지만 만들어 돌려 씀
2. Executors.newFixedThreadPool(2) + submit(람다식) → start() 없이 풀의 스레드가 실행
3. 값을 돌려주는 작업(Callable)은 Future로 받고, get()은 작업이 끝날 때까지 기다렸다 꺼냄 → 85 + 92 = 177
4. try-with-resources로 풀 닫기 → 작업이 다 끝날 때까지 기다렸다 닫힘 (join 대신, 자바 19부터) · 고정 풀은 안 닫으면 프로그램이 끝나지 않음
5. 자바 21부터: newVirtualThreadPerTaskExecutor()로 바꾸면 작업마다 가벼운 가상 스레드를 만듦 (풀이 아님)

📖 용어 정리
· 스레드 풀: 스레드를 작업마다 새로 만들지 않고, 정해 둔 개수의 스레드를 돌려 쓰는 묶음. 스레드가 모두 바쁘면 새 작업은 대기 줄에서 기다렸다가, 먼저 끝난 스레드가 꺼내 가요
· ExecutorService: 스레드 풀을 다루는 타입. 작업을 맡기고(submit) 닫는(close) 기능이 있어요
· Executors.newFixedThreadPool(2): 스레드를 최대 2개까지 만들어 돌려 쓰는 풀을 만들어요
· 작업: 풀에 맡기는 코드 한 덩어리(람다식). 값을 돌려주지 않으면 Runnable, 값을 돌려주면 Callable
· submit: 풀에 작업을 맡기는 메소드. start()를 부르지 않아도 풀의 스레드가 실행해요
· Future(퓨처): submit이 바로 돌려주는, 작업 결과를 나중에 꺼내는 상자
· get(): 작업이 끝날 때까지 기다렸다가 결과를 꺼내요. 기다리는 동안 메인 스레드는 멈춰 있어요
· try-with-resources: try 괄호 안에서 연 것을 블록이 끝나면 자동으로 닫는 문법. 풀은 작업이 다 끝날 때까지 기다렸다 닫혀요
· 가상 스레드: 자바 21부터 생긴 아주 가벼운 스레드. 수천 개를 만들어도 부담이 적어요

💡 get()은 예외를 던질 수 있어서 main에 throws Exception을 붙였어요

✅ 영상 속 예제는 모두 실제로 컴파일·실행해서 확인한 결과예요 (OpenJDK 25). 실행할 때마다 순서가 달라지는 예제는 여러 번 반복 실행해 확인했어요

#자바 #java #자바입문 #스레드 #스레드풀 #ExecutorService #Future #멀티스레드 #shorts
```

## 썸네일

`output/java-pool-shorts-thumb.png` (1080×1920). 다시 만들기: [issues/04-thumbnail.md](issues/04-thumbnail.md)의 렌더링 명령.

## README 영상 목록 행 (README에 추가함)

```
| 2026-11-25 | 자바 입문: 스레드 풀 (ExecutorService · newFixedThreadPool · submit · Callable · Future · get · try-with-resources · 가상 스레드) | 2:10 | [java-pool-shorts](java-pool-shorts) | [YouTube](https://www.youtube.com/watch?v=36VyonJ-Ks8) |
```
