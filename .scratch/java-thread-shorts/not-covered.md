# 22편 "스레드"에서 다루지 않은 내용

자바 입문 22편 `java-thread-shorts`(2:09, 업로드 완료)에서 범위 밖으로 뺀 주제와, 영상에서 단순화했거나 검토 후 그대로 둔 점을 정리한다. 후속편을 기획할 때 출발점으로 쓴다.

근거 자료: [spec.md](spec.md)의 Out of Scope·Further Notes, [issues/](issues/)의 Comments, `java-thread-shorts/script.json`·`build.py`, `GLOSSARY.md`(스레드·메인 스레드·경쟁 조건·동기화).

## 제작 현황 (후속편 기획 때마다 갱신)

이 파일은 스레드 후속편 기획의 출발점으로 계속 쓴다. 후속편을 기획하면 아래 표에 한 줄 추가하고, 다룬 항목의 주제 칸 앞에 표시를 붙인다.
표시: **[23편 예정]** 기획 확정·제작 전 / **[23편 완료]** 업로드 완료 / **[23편 제외]** 그 편에서 검토했지만 뺌(다음 후보로 남김). 업로드하면 "예정"을 "완료"로 바꾼다.

| 편 | 폴더 | 주제 | 상태 | 다룬 항목 |
|---|---|---|---|---|
| 23 | `java-sync-shorts` | 동기화 더 깊이 (후보 1) | 업로드 완료(2:05, [YouTube](https://www.youtube.com/watch?v=xaI4QK6Pfes)) | 22편 `synchronized` 범위 짚기(그림으로만, 시간 측정 없음) · 동기화 블록 + 잠금 객체 · `AtomicInteger.incrementAndGet()` · `ArrayList` 동시 `add` → `Collections.synchronizedList`. 썸네일 1장 |

23편에서 뺀 것: `volatile`(별도 "멈춤 신호" 예제가 필요), `ConcurrentHashMap`, 데드락 → 다음 후보로 남김. 남은 추천: 후보 2(스레드 풀) → 후보 3.

## 22편에서 실제로 다룬 것 (기준점)

| 장면 id | 진행 | 내용 |
|---|---|---|
| `hook` | — | 스레드 = 코드를 실행하는 흐름. 지금까지는 메인 스레드 하나. "동시에 실행되는 것처럼 번갈아" |
| `start` | 1 | `new Thread(() -> ...)` 두 개 + `start()`, 결과 예시 `민수 85 / main 끝 / 서준 92`. 메인은 기다리지 않음, 출력 순서 보장 안 됨. 메모 한 줄: `extends Thread` |
| `run-trap` | 1 | `Thread.currentThread().getName()` → `start()`는 `Thread-0`, `run()`은 `main` |
| `join` | 2 | 람다 안 `try { Thread.sleep(1000); } catch (InterruptedException e) {}`, `t.join()` 유무 비교. 메모: sleep → 스레드 안 try-catch, join → main에 throws |
| `race` | 3 | `static int count` + `static void inc()`(만 번 `count++`), `new Thread(Main::inc)` 두 개 → 결과 예시 `13426`. 읽기→더하기→쓰기. 경쟁 조건(레이스 컨디션) |
| `sync` | 4 | `static synchronized void inc()` → 20회 모두 `20000` |
| `outro` | — | 6줄 정리, 구독·좋아요 |

예시 데이터: STEP 1·2는 민수 85(k1)·서준 92(k2), STEP 3·4는 공유 변수 `count`.

## 1. 범위 밖으로 뺀 주제

중요도는 **자바 입문자**에게 얼마나 먼저 필요한지 기준이다(높음: 바로 다음에 배워야 함 / 중간: 알아 두면 좋음 / 낮음: 입문 단계에선 미뤄도 됨).

### 스레드를 만들고 관리하는 다른 방법

| 주제 | 설명 | 중요도 | 이어지는 장면 |
|---|---|---|---|
| `ExecutorService`·스레드 풀 | 스레드를 직접 `new`하지 않고, 미리 만든 스레드 몇 개(풀)에 작업을 `submit`해 맡긴다. 실무 코드는 대부분 이 방식이고, 다 쓰면 `shutdown()`(자바 19부터 try-with-resources로 닫기 가능 → 21편과 연결) | 높음 | `start`(스레드 직접 생성의 대안), `join`(끝날 때까지 기다리기의 대안) |
| `Callable`·`Future` | `Runnable`은 값을 돌려줄 수 없다. `Callable`로 결과를 돌려받고 `Future.get()`으로 기다렸다가 꺼낸다. `ExecutorService`와 짝 | 높음 | `start`·`join`(결과를 "출력"만 했지 돌려받지는 못함) |
| 가상 스레드 | 자바 21에서 정식 기능. `Thread.ofVirtual().start(...)`, `Executors.newVirtualThreadPerTaskExecutor()`. 아주 가벼워서 수천~수만 개를 만들어도 된다 | 중간 | `start`(같은 람다를 넘기는 방식이라 연결이 쉬움) |
| `CompletableFuture` | 비동기 작업을 이어 붙이는(`thenApply` 등) 방식. 콜백·체이닝 개념이 필요해 입문 범위를 넘는다 | 낮음 | 직접 연결되는 장면 없음(스트림 편의 메소드 체이닝과 모양만 비슷) |
| `extends Thread` 코드 | `Thread`를 상속하고 `run()`을 오버라이딩하는 방식. 영상에는 메모 한 줄("Thread 클래스를 물려받기")만 나옴. 상속(10편)·오버라이딩과 연결되지만, 단일 상속을 써 버리므로 보통 `Runnable`/람다를 권한다 | 중간 | `start` 하단 `.note`, `run-trap`(`run()`을 오버라이딩한다는 점과 함정이 이어짐) |
| `Runnable` 이름 | 람다가 실제로는 함수형 인터페이스 `Runnable`의 `run()`을 구현한다는 점. 영상은 "람다식으로 할 일을 넘겨요"까지만 말함 | 중간 | `start`, `run-trap`(`run()`이 어디서 왔는지), 19편 람다·함수형 인터페이스 |

### 동기화를 더 깊이

| 주제 | 설명 | 중요도 | 이어지는 장면 |
|---|---|---|---|
| **[23편 완료]** `synchronized` 블록 | `synchronized (lock) { count++; }`처럼 메소드 전체가 아니라 필요한 부분만 잠근다. 어떤 객체를 잠금으로 쓰는지(`this`, 클래스, 별도 객체) 개념이 함께 나온다 | 높음 | `sync`(메소드 전체를 잠가 사실상 순차 실행이 된 점 — 아래 2절) |
| **[23편 완료]** `AtomicInteger` | `count.incrementAndGet()` 한 번이 쪼개지지 않는(원자적) 연산이라 `synchronized` 없이 카운터를 안전하게 올린다. 같은 `count` 예제로 바로 비교 가능 | 높음 | `race`(읽기→더하기→쓰기가 쪼개지는 문제의 직접 해법), `sync`(다른 해법) |
| **[23편 완료]** 스레드 안전 컬렉션 (`Collections.synchronizedList`만. `ConcurrentHashMap`은 **[23편 제외]**) | `ArrayList`·`HashMap`도 여러 스레드가 함께 바꾸면 깨진다. `ConcurrentHashMap`, `Collections.synchronizedList` 등. 스펙 Out of Scope엔 없지만 18편 List와 바로 이어짐 | 중간 | `race`(변수 대신 리스트로 같은 문제), 18편 래퍼·List |
| **[23편 제외]** `volatile` | 한 스레드가 바꾼 값을 다른 스레드가 **보게** 해 주는 가시성 보장. `count++` 같은 경쟁 조건은 막지 못한다는 점이 흔한 오해 | 중간 | `race`(경쟁 조건과 구별), "멈춤 신호" 플래그 예제로 따로 보여야 함 |
| `Lock`(`ReentrantLock`) | `lock()`/`unlock()`을 직접 부르는 잠금. `finally`에서 꼭 풀어야 한다(20편 finally와 연결). `tryLock`·공정성 등 기능이 더 많다 | 낮음 | `sync`(같은 일을 하는 다른 도구) |
| `wait`/`notify` | 조건이 될 때까지 잠금을 놓고 기다리고 깨우는 저수준 도구. 지금은 `BlockingQueue` 같은 고수준 도구를 먼저 쓰는 편 | 낮음 | `join`(기다리기의 다른 형태) |
| **[23편 제외]** 데드락 | 두 스레드가 서로 상대가 가진 잠금을 기다리며 영원히 멈추는 문제. 잠금을 두 개 이상 쓸 때 생긴다 | 중간 | `sync`(잠금을 쓰기 시작하면 생기는 새 문제) |

### 스레드의 생명주기와 제어

| 주제 | 설명 | 중요도 | 이어지는 장면 |
|---|---|---|---|
| `interrupt()` | 다른 스레드에 "멈춰 달라"고 요청하는 협력적 종료 방법. 자고 있던(`sleep`·`join`) 스레드는 `InterruptedException`을 받는다. 영상은 이 예외를 `throws`·빈 `catch`로 넘기는 데까지만 | 중간 | `join`(빈 `catch {}` — 아래 2절), 20편 체크 예외 |
| 스레드 상태 | `NEW` → `RUNNABLE` → (`BLOCKED`·`WAITING`·`TIMED_WAITING`) → `TERMINATED`. `getState()`로 확인. `start()`를 두 번 부르면 `IllegalThreadStateException` | 낮음 | `start`(만들기만 하면 `NEW`), `join`(`sleep` 중 `TIMED_WAITING`), `sync`(잠금 대기 중 `BLOCKED`) |
| 데몬 스레드 | `setDaemon(true)`인 스레드는 다른 일반 스레드가 다 끝나면 같이 끝난다. 반대로 일반 스레드가 남아 있으면 `main`이 끝나도 프로그램이 안 끝난다 — `start` 장면에서 `main 끝` 뒤에 `서준 92`가 나온 이유 | 중간 | `start`(main이 먼저 끝나도 프로그램이 계속된 이유) |
| 우선순위 | `setPriority(1~10)`. 운영체제가 힌트로만 쓰므로 실행 순서를 보장하지 않는다 | 낮음 | `start`(순서 보장 안 됨의 연장 — "우선순위로도 순서를 못 정한다") |
| 스레드 이름 | `new Thread(runnable, "민수")`, `setName`. `Thread-0`이라는 기본 이름이 붙는 규칙 | 낮음 | `run-trap`(`getName()` 결과 `Thread-0`) |
| 스레드 안의 예외 | 스레드에서 잡지 않은 예외는 그 스레드만 끝내고 `main`은 계속 돈다. `main`의 `try-catch`로 잡을 수 없다 | 중간 | `join`(람다 안에서 따로 `try-catch`해야 했던 이유와 같은 뿌리), 20편 예외 |

## 2. 영상에서 단순화했거나 검토 후 그대로 둔 점

후속편에서 바로잡거나 이어서 설명할 지점이다.

| 항목 | 영상에서 한 것 | 실제로는 | 중요도 | 이어지는 장면 |
|---|---|---|---|---|
| **[23편 완료]** `synchronized` 범위 | `count++` 한 줄이 아니라 만 번 도는 `inc()` 메소드 전체에 붙였다. 경쟁 조건 코드와 **단어 하나만** 다르게 보이려는 선택(05 티켓, 독립 검토에서도 유지) | 한 스레드가 반복 전체를 끝낼 때까지 다른 스레드가 못 들어가서 사실상 순차 실행이 된다. 스레드를 쓴 의미가 없어지는 예. 잠금 범위는 필요한 만큼만 좁히는 게 원칙 | 높음 | `sync` → 후속편에서 `synchronized` 블록·`AtomicInteger`로 비교 |
| 빈 `catch {}` | 람다 안 `catch (InterruptedException e) {}`로 예외를 삼켰다(`Runnable.run()`은 체크 예외를 던질 수 없어서, 33자 제한 안에서 가장 짧은 형태) | 인터럽트 요청을 조용히 버리는 습관은 좋지 않다. 보통 `Thread.currentThread().interrupt();`로 인터럽트 상태를 되살리거나 작업을 끝낸다. 20편에서 "예외를 삼키지 말라"는 메시지가 없었는지도 함께 점검할 것 | 중간 | `join`, 후속편의 `interrupt()` |
| "동시에 실행되는 것처럼 번갈아" | 나레이션을 이렇게 완화했다(스펙의 용어 결정) | 코어가 여러 개면 정말로 동시에(병렬로) 돈다. GLOSSARY "스레드" 정의에는 괄호로 적혀 있지만 영상에선 말하지 않았다. 동시성(concurrency)과 병렬성(parallelism)의 구분 | 중간 | `hook`, `race`(동시에 돌기 때문에 값이 사라짐) |
| `main`의 `throws` | 화면 코드에 `main` 선언이 보이지 않는다. `throws InterruptedException`은 메모(`join → main에 throws`)로만 보여 줬다(04 티켓에서 자막 영역 침범 때문에 줄임). 빌드는 `J.MAIN_THROWS`로 실제 붙여 컴파일 | 화면 코드를 그대로 따라 치면 `main`에 `throws`를 직접 붙여야 컴파일된다. `race`·`sync`도 `join` 때문에 같은 처리가 필요 | 낮음 | `join`, `race`, `sync` |
| 출력 순서 예시 | `민수 85 / main 끝 / 서준 92` 한 가지만 그리고, 순서가 섞이는 모습은 화면으로 보여 주지 않음. 나레이션은 "이번 실행에서는" | 독립 검토 40회 실행에서 다섯 가지 순서가 관찰됨(06 티켓) | 낮음 | `start` |
| `join`이 주는 가시성 | `race`에서 `join` 뒤 `count`를 읽는 것을 당연하게 처리 | `join`은 "끝날 때까지 기다림"뿐 아니라 그 스레드가 쓴 값을 메인이 볼 수 있게 보장한다(happens-before). `volatile` 설명의 좋은 출발점 | 낮음 | `race`, `sync` |

## 다음 편 후보

### 후보 1 **[23편 완료]**: "동기화 더 깊이: synchronized 블록 · AtomicInteger · 스레드 안전 컬렉션"

- **다룰 주제**: 22편 `sync`의 범위 문제 짚기(메소드 전체 = 순차 실행) → `synchronized (lock) { count++; }` 블록 → `AtomicInteger.incrementAndGet()` → `ArrayList`에 두 스레드가 `add`하면 생기는 문제와 `ConcurrentHashMap`/`Collections.synchronizedList`. 여유가 되면 `volatile`은 "경쟁 조건은 못 막는다" 경고 한 줄
- **이유**: 22편의 `count` 예제를 그대로 이어 쓸 수 있어 시청자 부담이 적고, 22편에서 그대로 둔 가장 큰 단순화(`synchronized` 범위)를 바로잡는다. `race`의 "읽기→더하기→쓰기" 설명이 `AtomicInteger`의 동기가 된다. 빌드 쪽도 `jmulti`를 그대로 쓴다(race·sync와 같은 검증 방식)

### 후보 2 (다음 추천): "스레드 풀과 ExecutorService: submit · Callable · Future · 가상 스레드"

- **다룰 주제**: `Executors.newFixedThreadPool(2)` + `submit` → `Callable`로 점수 돌려받기 + `Future.get()` → try-with-resources로 닫기(21편 연결) → 마지막에 `newVirtualThreadPerTaskExecutor()` 한 줄 비교
- **이유**: 실무에서 스레드를 쓰는 표준 방법이고, 22편의 `new Thread` + `start` + `join` 세 단계를 한 번에 대체한다. 민수 85·서준 92 데이터를 "출력"이 아니라 "돌려받는" 예제로 바꾸면 22편 `start`·`join`과 자연스럽게 대비된다

### 후보 3: "스레드 멈추기와 끝내기: interrupt · 데몬 스레드 · 데드락"

- **다룰 주제**: `interrupt()`와 `InterruptedException`(22편의 빈 `catch {}` 바로잡기, `Thread.currentThread().interrupt()`) → 데몬 스레드(`main`이 끝나도 프로그램이 계속된 이유) → 잠금 두 개로 만드는 데드락과 잠금 순서 맞추기
- **이유**: 22편에서 넘어간 "멈춤·종료" 쪽 질문을 모은다. 다만 데드락은 일부러 멈추는 예제라 빌드 검증(`jmulti`가 실행을 끝내야 함)에 시간 제한·탐지 방식을 새로 만들어야 할 수 있어 제작 부담이 가장 크다. 후보 1·2 뒤에 두는 것을 권한다

권장 순서: 후보 1 → 후보 2 → (필요하면) 후보 3. 시리즈를 입문 범위에서 마무리한다면 후보 1·2만으로도 충분하다.
