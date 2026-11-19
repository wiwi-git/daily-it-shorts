# 05: STEP 5 사실상 final + 메소드 참조 맛보기

**What to build:** 람다식의 대표적인 함정과, 람다식을 더 짧게 쓰는 방법을 보여 주는 두 장면을 만든다.
- final: `int pass = 80; pass = 90;` 뒤에 람다식에서 `pass`를 쓰면 컴파일 오류(`.warn`) — `local variables referenced from a lambda expression must be final or effectively final`. "람다식 안에서 쓰는 바깥 지역 변수는 값을 바꾸면 안 된다", 값을 안 바꾸면 `final`을 안 붙여도 된다 = 사실상 final(처음 한 번 "(값을 안 바꾸는 변수)"로 풀어 쓴다)
- ref: `names.forEach(n -> System.out.println(n));`와 `names.forEach(System.out::println);`를 `.vs` 카드로 나란히 놓고, 결과가 같다(민수·서준·지우). "람다식을 더 짧게 쓰는 방법" 정도로만 소개한다. 진행 표시는 5번째 칸

**Blocked by:** 01

**Status:** resolved

- [x] final의 컴파일 오류가 빌드에서 대조된다
- [x] ref의 두 버전 출력이 각각 빌드에서 대조되고 서로 같다
- [x] "지역 변수"를 빼고 말하지 않는다(필드에는 해당하지 않음)
- [x] 메소드 참조의 종류(정적·인스턴스·생성자)를 다루지 않는다
- [x] 코드 한 줄이 33자 이하이고, `hyperframes check` 오류 0건, snapshot으로 두 장면을 확인한다

## Comments

- 2026-11-19: 메인 세션에서 01~06을 한 번에 구현(17편과 같은 방식, 모든 티켓이 같은 build.py·script.json을 고침). 17편 build.py를 복사해 `wrap(top=)`(인터페이스를 class Main 위에 둠), 출력 없는 조각의 컴파일만 확인하는 `jok()`, `jce(show_top=)`, `->`·`::` 주황 강조를 추가. 예제 대조 출력 9건(why 2·pred·each·rmif·sort·sort a-b·ref 2)·컴파일 오류 3건·컴파일 확인 8건 통과, 기대값을 일부러 틀리게 바꾼 5가지 경우 모두 빌드가 멈춤. 첫 대본이 TTS 176.7초라 줄여서 146.6초(영상 152.0초). check 오류 0건(line_unread 경고 3건, nested_structure 경고는 17편과 같음), 자막 공백 0.001초(반올림), fi·short 장면 390px 폭 확인. 스펙과 다른 점: 브랜드는 17편처럼 "자바 입문 람다식 정리", 나레이션의 Predicate 발음은 "프레디케이트".
- 2026-11-19: final 예제 교체 — `int pass = 80; pass = 90;` 뒤 람다식에서 `pass`를 쓰는 예제는 람다식보다 먼저 대입해서 왜 오류인지 직관적으로 보이지 않았음(사용자 지적). 입문자가 실제로 부딪히는 `int sum = 0; scores.forEach(s -> sum += s);`(같은 컴파일 오류)로 바꾸고, "한 번도 다시 대입 안 하는 변수 = 사실상 final" 메모와 대안인 향상된 for 합계(`255`, 빌드 대조)를 추가. 나레이션 재작성, 음성 재생성, check 오류 0건, 렌더링 2:39.
