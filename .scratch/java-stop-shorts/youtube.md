# 유튜브 업로드: 자바 입문 25편 스레드 멈추기

## 제목

```
자바 입문 25편: 스레드 멈추기와 끝내기 | volatile · interrupt · 데몬 스레드 #shorts
```

## 설명

```
자바 입문 스물다섯 번째, 스레드 멈추기! 계속 도는 스레드는 어떻게 멈출까요? 스레드는 밖에서 강제로 멈출 수 없어요. 멈춰 달라고 요청하고, 스레드가 스스로 끝내게 해야 해요.

📌 오늘 배우는 것
1. stop()은 오래전에 사용 중단됐고, 지금 자바에서는 예외(UnsupportedOperationException)만 던짐 (자바 20부터)
2. 직접 만든 멈춤 신호: static volatile boolean stop → while (!stop) 반복, main이 stop = true
3. interrupt(): 자고 있는(sleep) 스레드도 깨워 InterruptedException으로 요청을 전달 → 반복 바깥 catch로 빠져나옴
   ⚠️ 함정: catch를 반복 안에 두고 비워 두면 인터럽트 상태가 지워져 반복이 끝나지 않음 → catch 안에서 Thread.currentThread().interrupt()로 되살리기
4. 데몬 스레드: start() 전에 setDaemon(true) → 일반 스레드가 모두 끝나면 함께 끝남. 일반 스레드가 남아 있으면 main이 끝나도 프로그램이 끝나지 않음

📖 용어 정리
· 멈춤 신호: 다른 스레드에게 "이제 그만"을 알리려고 직접 만든 boolean 변수. 작업 스레드가 반복할 때마다 확인해 스스로 끝내요
· volatile: 다른 스레드가 바꾼 값을 보게 해 줘요. 여러 스레드가 함께 보는 멈춤 신호에 붙여요
· 인터럽트: interrupt()로 다른 스레드에게 멈춰 달라고 요청하는 것. 강제로 멈추는 게 아니에요
· 인터럽트 상태: 스레드가 인터럽트를 받았는지 나타내는 표시. isInterrupted()로 확인하고, InterruptedException이 나면 지워져요
· 데몬 스레드: 일반 스레드가 모두 끝나면 함께 끝나는 스레드

💡 main에서 Thread.sleep(1000)을 쓰기 때문에 main에 throws InterruptedException을 붙였어요

✅ 영상 속 예제는 모두 실제로 컴파일·실행해서 확인한 결과예요 (OpenJDK 25). "끝나지 않는다"고 한 예제도 3초 동안 실행해 끝나지 않는 것을 확인했어요

#자바 #java #자바입문 #스레드 #인터럽트 #volatile #데몬스레드 #멀티스레드 #shorts
```

## 썸네일

`output/java-stop-shorts-thumb.png` (1080×1920). 다시 만들기: [issues/05-thumbnail.md](issues/05-thumbnail.md)의 렌더링 명령.

## README 영상 목록 행 (업로드 후 URL을 넣어 추가)

```
| 2026-11-27 | 자바 입문: 스레드 멈추기와 끝내기 (stop 금지 · 멈춤 신호 · volatile · interrupt · InterruptedException · 인터럽트 상태 · 데몬 스레드) | 2:16 | [java-stop-shorts](java-stop-shorts) | [YouTube](https://www.youtube.com/watch?v=VGYqlPkCnmg) |
```
