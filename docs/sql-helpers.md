# SQL 영상 빌드 헬퍼

SQL 영상(`mysql-shorts`, `where-conditions-shorts`, `select-join-groupby-shorts`, `ddl-shorts`, `tcl-shorts`, `dcl-shorts`)의 `build.py`에 들어 있는 예제 실행 헬퍼. 자바 영상과 달리 공용 모듈이 없으므로, 새 SQL 영상은 가장 가까운 주제의 영상 폴더를 복사한다. 빌드는 예제 쿼리를 `queries.sql`에 기록한다.

- `qcode(sid, lines, *expect, mark=())`: 실행되는 예제 쿼리용 `code()`. 각 문장을 예시 데이터 `P`에 실행해
  `expect`(나레이션이 말하는 결과 id 목록)와 다르면 빌드 중단, `queries.sql`에 기록. `WHERE`만 보여줘도 됨.
  결과 표·칩은 id를 직접 쓰지 말고 `got()`(직전 쿼리의 실제 결과)로 그린다
- `qsql(sid, lines, expect, check=, user=)` / `setup(sid, sql)`: SELECT 결과로 확인할 수 없는 주제(DDL·TCL·DCL)용.
  `../tools/mysql-sandbox.sh start`로 띄운 임시 MySQL에서 코드를 `user` 계정으로 실행하고, 이어서 보이지 않는
  `check` 쿼리의 결과 행(또는 코드가 낸 `ERROR nnnn`)을 `expect`와 대조. 기준 구현은 `ddl-shorts`·`tcl-shorts`·`dcl-shorts`.
  앞 블록에서 이어지는 트랜잭션은 `pre=`로 같은 세션에서 실행하고, 두 세션 예제는 `two_sessions()`처럼
  A가 자기 값을 읽은 뒤에 B를 조회하게 동기화한다(고정 sleep 금지). 트랜잭션 예제는 COMMIT/ROLLBACK으로 닫는다
- `res(ids, bad=())`: 결과를 한 줄 칩으로(공간이 좁은 두 쿼리 비교 장면용), `bad`는 빨간 ⚠ 표시
- `table(cols, rows, label)`: 40px 결과 표. 행 클래스 `k1`/`k2`/`k3`은 대상별 색, `out`은 제외(취소선), 값 `None`은 빨간 NULL
- 결과가 있는 예제 쿼리는 모두 `qcode()`로 넣어 빌드가 실행·대조하게 한다. 자동 대조는 쿼리 결과까지만이므로,
  나레이션 문장("네 개가 남아요")이 `expect`와 같은지는 직접 확인한다
