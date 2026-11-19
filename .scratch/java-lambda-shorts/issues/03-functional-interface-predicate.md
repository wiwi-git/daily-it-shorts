# 03: STEP 3 함수형 인터페이스 + Predicate

**What to build:** 람다식을 담을 수 있는 인터페이스의 조건과, 자바가 미리 만들어 둔 함수형 인터페이스를 보여 주는 두 장면을 만든다.
- fi: `Checker`에 추상 메소드를 하나 더 넣고 람다식에 담으면 컴파일 오류(`.warn`) — 첫 줄 `incompatible types: Checker is not a functional interface`, 설명 줄 `multiple non-overriding abstract methods found in interface Checker`. 추상 메소드가 딱 하나인 인터페이스 = 함수형 인터페이스. `@FunctionalInterface`를 붙이면 인터페이스 쪽에서 바로 오류 — `Unexpected @FunctionalInterface annotation` / `Checker is not a functional interface`. 공간이 부족하면 람다식 오류를 크게, 이 오류는 한 줄 메모로
- pred: `import java.util.function.Predicate;`(15편 import 연결), `Predicate<Integer> p = s -> s >= 80;`, `p.test(85)` → `true`. `Checker`를 직접 만들지 않아도 된다. 꺾쇠는 17편의 담을 타입과 같은 문법. 진행 표시는 3번째 칸

**Blocked by:** 01

**Status:** resolved

- [x] fi의 컴파일 오류 2건(첫 줄 + 설명 줄)이 빌드에서 대조되고, 화면의 오류 문구는 실제 결과로 그린다
- [x] pred의 출력 `true`가 빌드에서 대조된다
- [x] 함수형 인터페이스를 "메소드가 하나"가 아니라 "추상 메소드가 딱 하나"로 말한다
- [x] 코드 한 줄이 33자 이하이고(`Predicate<Integer> p = …`는 `=` 뒤에서 줄바꿈), `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-19: 메인 세션에서 01~06을 한 번에 구현(17편과 같은 방식, 모든 티켓이 같은 build.py·script.json을 고침). 17편 build.py를 복사해 `wrap(top=)`(인터페이스를 class Main 위에 둠), 출력 없는 조각의 컴파일만 확인하는 `jok()`, `jce(show_top=)`, `->`·`::` 주황 강조를 추가. 예제 대조 출력 9건(why 2·pred·each·rmif·sort·sort a-b·ref 2)·컴파일 오류 3건·컴파일 확인 8건 통과, 기대값을 일부러 틀리게 바꾼 5가지 경우 모두 빌드가 멈춤. 첫 대본이 TTS 176.7초라 줄여서 146.6초(영상 152.0초). check 오류 0건(line_unread 경고 3건, nested_structure 경고는 17편과 같음), 자막 공백 0.001초(반올림), fi·short 장면 390px 폭 확인. 스펙과 다른 점: 브랜드는 17편처럼 "자바 입문 람다식 정리", 나레이션의 Predicate 발음은 "프레디케이트".
