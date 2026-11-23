# 유튜브 업로드: 자바 입문 22편 스레드

## 제목

```
자바 입문 22편: 스레드 | Thread · start · join · 경쟁 조건 · synchronized #shorts
```

## 설명

```
자바 입문 스물두 번째, 스레드! 지금까지는 메인 스레드 하나가 main을 위에서 아래로 실행했어요. 스레드를 여러 개 만들면 여러 일을 번갈아 처리할 수 있어요.

📌 오늘 배우는 것
1. new Thread에 람다식으로 할 일을 넘기고 start()로 실행 · 출력 순서는 보장되지 않고, 메인 스레드는 기다리지 않음
   ⚠️ 함정: run()을 직접 부르면 새 스레드 없이 그냥 메소드 호출 (getName() → main)
2. join()으로 끝날 때까지 기다리기 · sleep()·join()은 체크 예외 InterruptedException (스레드 안은 try-catch, main은 throws)
3. 두 스레드가 count++를 만 번씩 → 대부분 20000보다 적게 나오는 경쟁 조건 (레이스 컨디션)
4. synchronized를 붙이면 한 번에 한 스레드만 → 항상 20000

💡 Thread 클래스를 물려받는(extends Thread) 방법도 있어요

✅ 영상 속 예제는 모두 실제로 컴파일·실행해서 확인한 결과예요 (OpenJDK 25). 실행할 때마다 순서·값이 달라지는 예제는 여러 번 반복 실행해 확인했어요

#자바 #java #자바입문 #스레드 #thread #멀티스레드 #synchronized #shorts
```

## README 영상 목록 행 (업로드 후 URL 채우기)

```
| 2026-11-23 | 자바 입문: 스레드 (new Thread · start · run 함정 · sleep · join · 경쟁 조건 · synchronized) | 2:09 | [java-thread-shorts](java-thread-shorts) | [YouTube](https://www.youtube.com/watch?v=<id>) |
```
