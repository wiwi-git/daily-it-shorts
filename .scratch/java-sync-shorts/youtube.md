# 유튜브 업로드: 자바 입문 23편 동기화 더 깊이

## 제목

```
자바 입문 23편: 동기화 더 깊이 | synchronized 블록 · AtomicInteger · synchronizedList #shorts
```

## 설명

```
자바 입문 스물세 번째, 동기화 더 깊이! 지난 편의 synchronized는 항상 20000을 만들었지만, 메소드 전체를 잠가서 문제가 하나 있었어요. 잠그는 범위를 좁히는 법과, synchronized 없이 푸는 법을 알아봐요.

📌 오늘 배우는 것
1. 만 번 도는 메소드 전체에 synchronized → 결과는 맞지만 두 스레드가 사실상 차례로 실행
2. synchronized (잠금 객체) { count++; } → 필요한 줄만 동기화 · 두 스레드가 같은 잠금 객체를 써야 함
3. AtomicInteger의 incrementAndGet() → 읽기·더하기·쓰기를 한 번에 하는 원자적 연산 · 값은 get()
4. ArrayList에 두 스레드가 만 번씩 add → 크기가 20000보다 적거나 예외 · Collections.synchronizedList로 감싸면 항상 20000 (스레드 안전)

💡 잠그는 범위는 필요한 만큼만 좁히는 게 원칙이에요

✅ 영상 속 예제는 모두 실제로 컴파일·실행해서 확인한 결과예요 (OpenJDK 25). 실행할 때마다 값이 달라지는 예제는 여러 번 반복 실행해 확인했어요

#자바 #java #자바입문 #스레드 #동기화 #synchronized #AtomicInteger #멀티스레드 #shorts
```

## 썸네일

`output/java-sync-shorts-thumb.png` (1080×1920). 다시 만들기: [issues/04-thumbnail.md](issues/04-thumbnail.md)의 Comments.

## README 영상 목록 행 (업로드 후 URL 채우기)

```
| 2026-11-24 | 자바 입문: 동기화 더 깊이 (synchronized 블록 · 잠금 객체 · AtomicInteger · incrementAndGet · 스레드 안전 리스트 · synchronizedList) | 2:05 | [java-sync-shorts](java-sync-shorts) | [YouTube](https://www.youtube.com/watch?v=<id>) |
```
