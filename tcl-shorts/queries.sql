-- TCL: START TRANSACTION · COMMIT · ROLLBACK · SAVEPOINT · 영상에 나오는 예제 쿼리 (build.py가 생성 · 직접 고치지 말 것)
-- MySQL에서 위에서부터 차례로 실행. '계정:' 표시가 있는 블록은 그 계정으로 접속해서 실행
-- 검증 환경: MySQL 26.10.0 · 기본 엔진 InnoDB · 격리 수준 REPEATABLE-READ · autocommit=1 (../tools/mysql-sandbox.sh)

-- [왜 필요할까] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE accounts (id INT PRIMARY KEY, name VARCHAR(20), balance INT) ENGINE=InnoDB;
INSERT INTO accounts VALUES (1, 'kim', 50000), (2, 'lee', 10000);

-- [왜 필요할까] → kim, 40000 / lee, 10000
UPDATE accounts
  SET balance = balance - 10000
  WHERE name = 'kim';
-- 여기서 멈추면?
SELECT name, balance FROM accounts ORDER BY id;

-- [1-1. COMMIT] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE accounts (id INT PRIMARY KEY, name VARCHAR(20), balance INT) ENGINE=InnoDB;
INSERT INTO accounts VALUES (1, 'kim', 50000), (2, 'lee', 10000);

-- [1-1. COMMIT] → kim, 40000 / lee, 20000
START TRANSACTION;
UPDATE accounts
  SET balance = balance - 10000
  WHERE name = 'kim';
UPDATE accounts
  SET balance = balance + 10000
  WHERE name = 'lee';
COMMIT;
SELECT name, balance FROM accounts ORDER BY id;

-- [2. ROLLBACK] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE accounts (id INT PRIMARY KEY, name VARCHAR(20), balance INT) ENGINE=InnoDB;
INSERT INTO accounts VALUES (1, 'kim', 50000), (2, 'lee', 10000);

-- [2. ROLLBACK] → kim, 50000 / lee, 10000
START TRANSACTION;
UPDATE accounts
  SET balance = balance - 10000
  WHERE name = 'kim';
-- 문제 발생!
ROLLBACK;
SELECT name, balance FROM accounts ORDER BY id;

-- [3. 커밋 전 변경] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE accounts (id INT PRIMARY KEY, name VARCHAR(20), balance INT) ENGINE=InnoDB;
INSERT INTO accounts VALUES (1, 'kim', 50000), (2, 'lee', 10000);

-- [3. 커밋 전 변경] (세션 A · 창 1) → 40000
START TRANSACTION;
UPDATE accounts
  SET balance = balance - 10000
  WHERE name = 'kim';
SELECT balance FROM accounts WHERE name = 'kim';

-- [3. 커밋 전 변경] (세션 B · 창 2, A를 커밋하기 전에) → 50000
SELECT balance FROM accounts
  WHERE name = 'kim';

-- [3. 커밋 전 변경] (세션 A · 창 1)
ROLLBACK;

-- [3. 커밋 전 변경] → REPEATABLE-READ
SELECT @@transaction_isolation;

-- [4. 오토 커밋] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE accounts (id INT PRIMARY KEY, name VARCHAR(20), balance INT) ENGINE=InnoDB;
INSERT INTO accounts VALUES (1, 'kim', 50000), (2, 'lee', 10000);

-- [4. 오토 커밋] → 1
SELECT @@autocommit;

-- [4. 오토 커밋] → kim, 40000 / lee, 10000
UPDATE accounts
  SET balance = balance - 10000
  WHERE name = 'kim';
ROLLBACK;
SELECT name, balance FROM accounts ORDER BY id;

-- [5. SAVEPOINT] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE accounts (id INT PRIMARY KEY, name VARCHAR(20), balance INT) ENGINE=InnoDB;
INSERT INTO accounts VALUES (1, 'kim', 50000), (2, 'lee', 10000);

-- [5. SAVEPOINT] → kim, 40000 / lee, 10000
START TRANSACTION;
UPDATE accounts
  SET balance = balance - 10000
  WHERE name = 'kim';
SAVEPOINT sent;
UPDATE accounts
  SET balance = balance + 100000
  WHERE name = 'lee';
ROLLBACK TO sent;
SELECT name, balance FROM accounts ORDER BY id;

-- [5-1. 마무리] (앞 블록에 이어서 같은 세션) → kim, 40000 / lee, 20000
UPDATE accounts
  SET balance = balance + 10000
  WHERE name = 'lee';
COMMIT;
SELECT name, balance FROM accounts ORDER BY id;

-- [5-2. 주의점] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE accounts (id INT PRIMARY KEY, name VARCHAR(20), balance INT) ENGINE=InnoDB;
INSERT INTO accounts VALUES (1, 'kim', 50000), (2, 'lee', 10000);

-- [5-2. 주의점] → kim, 40000 / lee, 10000
START TRANSACTION;
UPDATE accounts
  SET balance = balance - 10000
  WHERE name = 'kim';
ALTER TABLE accounts
  ADD COLUMN memo VARCHAR(20);
ROLLBACK;
SELECT name, balance FROM accounts ORDER BY id;
