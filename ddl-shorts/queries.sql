-- DDL: CREATE · ALTER · INDEX · DROP · 영상에 나오는 예제 쿼리 (build.py가 생성 · 직접 고치지 말 것)
-- MySQL에서 위에서부터 차례로 실행. '계정:' 표시가 있는 블록은 그 계정으로 접속해서 실행
-- 검증 환경: MySQL 26.10.0 · 기본 엔진 InnoDB · 격리 수준 REPEATABLE-READ · autocommit=1 (../tools/mysql-sandbox.sh)

-- [1. CREATE TABLE] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;

-- [1. CREATE TABLE] → products
CREATE TABLE products (
  id INT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  category VARCHAR(20),
  price INT DEFAULT 0
);
SHOW TABLES;

-- [1-1. 제약 조건] → id, int, NO, PRI, NULL,  / name, varchar(50), NO, , NULL,  / category, varchar(20), YES, , NULL,  / price, int, YES, , 0, 
DESC products;

-- [1-1. 제약 조건] → 1
INSERT INTO products (id, name) VALUES (7, '');
SELECT COUNT(*) FROM products WHERE name = '';

-- [1-1. 제약 조건] → ERROR 1048: Column 'name' cannot be null
INSERT INTO products (id, name) VALUES (8, NULL);

-- [2. ALTER · ADD] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE products (
  id INT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  category VARCHAR(20),
  price INT DEFAULT 0
);
INSERT INTO products VALUES (1, 'SQL 입문서', 'book', 18000), (2, '볼펜', 'pen', 1500), (3, 'SQL 문제집', 'book', 9000), (4, '노트', 'note', 3000), (5, '만년필', 'pen', 45000), (6, '형광펜', 'pen', 2000);

-- [2. ALTER · ADD] → SQL 입문서, 0 / 볼펜, 0 / SQL 문제집, 0 / 노트, 0 / 만년필, 0 / 형광펜, 0
ALTER TABLE products
  ADD COLUMN stock INT DEFAULT 0;
SELECT name, stock FROM products;

-- [2-1. MODIFY 주의점] → YES
ALTER TABLE products
  MODIFY name VARCHAR(100);
SELECT is_nullable FROM information_schema.columns
WHERE table_schema = 'shop' AND table_name = 'products' AND column_name = 'name';

-- [2-1. MODIFY 주의점] → NO
ALTER TABLE products
  MODIFY name VARCHAR(100)
    NOT NULL;
SELECT is_nullable FROM information_schema.columns
WHERE table_schema = 'shop' AND table_name = 'products' AND column_name = 'name';

-- [3. CREATE INDEX] → PRIMARY, id / idx_category, category
CREATE INDEX idx_category
  ON products (category);
SELECT index_name, column_name FROM information_schema.statistics
WHERE table_schema = 'shop' AND table_name = 'products'
ORDER BY index_name <> 'PRIMARY', index_name;

-- [2-1. MODIFY 주의점] → qty
ALTER TABLE products
  RENAME COLUMN stock TO qty;
SELECT column_name FROM information_schema.columns
WHERE table_schema = 'shop' AND table_name = 'products' AND column_name IN ('stock', 'qty');

-- [2-1. MODIFY 주의점] → 결과 없음
ALTER TABLE products
  DROP COLUMN qty;
SELECT column_name FROM information_schema.columns
WHERE table_schema = 'shop' AND table_name = 'products' AND column_name IN ('stock', 'qty');

-- [4. DROP · TRUNCATE] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE products (
  id INT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  category VARCHAR(20),
  price INT DEFAULT 0
);
INSERT INTO products VALUES (1, 'SQL 입문서', 'book', 18000), (2, '볼펜', 'pen', 1500), (3, 'SQL 문제집', 'book', 9000), (4, '노트', 'note', 3000), (5, '만년필', 'pen', 45000), (6, '형광펜', 'pen', 2000);

-- [4. DROP · TRUNCATE] → 3
DELETE FROM products
  WHERE category = 'pen';
SELECT COUNT(*) FROM products;

-- [4. DROP · TRUNCATE] → products / 0
TRUNCATE TABLE products;
SHOW TABLES;
SELECT COUNT(*) FROM products;

-- [4. DROP · TRUNCATE] → 결과 없음
DROP TABLE products;
SHOW TABLES;

-- [5. 자동 커밋] 준비
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;
CREATE TABLE products (
  id INT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  category VARCHAR(20),
  price INT DEFAULT 0
);
INSERT INTO products VALUES (1, 'SQL 입문서', 'book', 18000), (2, '볼펜', 'pen', 1500), (3, 'SQL 문제집', 'book', 9000), (4, '노트', 'note', 3000), (5, '만년필', 'pen', 45000), (6, '형광펜', 'pen', 2000);

-- [5. 자동 커밋] → 6
START TRANSACTION;
DELETE FROM products;
ROLLBACK;
SELECT COUNT(*) FROM products;

-- [5. 자동 커밋] → 결과 없음
START TRANSACTION;
DROP TABLE products;
ROLLBACK;
SHOW TABLES;
