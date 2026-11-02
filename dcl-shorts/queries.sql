-- DCL: CREATE USER · GRANT · REVOKE · DROP USER · 영상에 나오는 예제 쿼리 (build.py가 생성 · 직접 고치지 말 것)
-- MySQL에서 위에서부터 차례로 실행. '계정:' 표시가 있는 블록은 그 계정으로 접속해서 실행
-- 검증 환경: MySQL 26.10.0 · 기본 엔진 InnoDB · 격리 수준 REPEATABLE-READ · autocommit=1 (../tools/mysql-sandbox.sh)

-- [1. CREATE USER] 준비
DROP USER IF EXISTS 'app'@'localhost', 'report'@'localhost';
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(50), category VARCHAR(20), price INT);
INSERT INTO products VALUES (1, 'SQL 입문서', 'book', 18000), (2, '볼펜', 'pen', 1500), (3, 'SQL 문제집', 'book', 9000),
  (4, '노트', 'note', 3000), (5, '만년필', 'pen', 45000), (6, '형광펜', 'pen', 2000);

-- [1. CREATE USER] → app, localhost
CREATE USER 'app'@'localhost'
  IDENTIFIED BY 'app_pw';
SELECT user, host FROM mysql.user WHERE user = 'app';

-- [2. GRANT] → GRANT USAGE ON *.* TO `app`@`localhost`
SHOW GRANTS
  FOR 'app'@'localhost';

-- [2. GRANT] → 결과 없음
GRANT SELECT, INSERT ON shop.*
  TO 'app'@'localhost';

-- [2. GRANT] → GRANT USAGE ON *.* TO `app`@`localhost` / GRANT SELECT, INSERT ON `shop`.* TO `app`@`localhost`
SHOW GRANTS
  FOR 'app'@'localhost';

-- [3. 권한 없는 작업] → 결과 없음
CREATE USER 'report'@'localhost'
  IDENTIFIED BY 'report_pw';
GRANT SELECT ON shop.products
  TO 'report'@'localhost';

-- [3. 권한 없는 작업] (계정: report) → ERROR 1142: DELETE command denied to user 'report'@'localhost' for table 'products'
DELETE FROM products
  WHERE id = 2;

-- [4. REVOKE] → 결과 없음
REVOKE INSERT ON shop.*
  FROM 'app'@'localhost';

-- [4. REVOKE] → GRANT USAGE ON *.* TO `app`@`localhost` / GRANT SELECT ON `shop`.* TO `app`@`localhost`
SHOW GRANTS
  FOR 'app'@'localhost';

-- [5. 최소 권한 원칙] → app@localhost
DROP USER 'report'@'localhost';
SELECT CONCAT(user, '@', host) FROM mysql.user
WHERE user IN ('app', 'report');
