-- 영상에 나오는 예제 쿼리 (build.py가 생성 · 직접 고치지 말 것)
-- 실행: sqlite3 :memory: < queries.sql   (MySQL에서도 그대로 실행 가능)

CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(50), category VARCHAR(20), price INT);
INSERT INTO products VALUES
  (1, 'SQL 입문서', 'book', 18000),
  (2, '볼펜', 'pen', 1500),
  (3, 'SQL 문제집', 'book', 9000),
  (4, '노트', 'note', 3000),
  (5, '만년필', 'pen', 45000),
  (6, '형광펜', 'pen', 2000);

-- [1. 비교 연산자] 결과: SQL 입문서, 만년필
SELECT name, price
FROM products
WHERE price >= 10000;

-- [1-1. 문자열 비교] 결과: SQL 입문서, SQL 문제집
SELECT name, category
FROM products
WHERE category = 'book';

-- [1-2. BETWEEN] 결과: SQL 문제집, 노트
SELECT name, price
FROM products
WHERE price
  BETWEEN 3000 AND 10000;

-- [2. AND] 결과: SQL 문제집
SELECT name, category, price
FROM products
WHERE category = 'book'
  AND price < 10000;

-- [2-1. OR] 결과: SQL 입문서, 볼펜, 만년필, 형광펜
SELECT name, category, price
FROM products
WHERE category = 'pen'
   OR price >= 18000;

-- [2-2. AND · OR 우선순위] 결과: SQL 입문서, SQL 문제집, 만년필
SELECT name, category, price
FROM products
WHERE category = 'book'
   OR category = 'pen'
  AND price >= 10000;

-- [2-2. AND · OR 우선순위] 결과: SQL 입문서, 만년필
SELECT name, category, price
FROM products
WHERE (category = 'book'
    OR category = 'pen')
  AND price >= 10000;

-- [3. IN · NOT IN] 결과: SQL 입문서, 볼펜, SQL 문제집, 만년필, 형광펜
SELECT name, category, price
FROM products
WHERE category
  IN ('book', 'pen');

-- [3. IN · NOT IN] 결과: 노트
SELECT name, category, price
FROM products
WHERE category
  NOT IN ('book', 'pen');

-- [4. LIKE] 결과: 볼펜, 형광펜
SELECT name, category, price
FROM products
WHERE name LIKE '%펜';

-- [4. LIKE] 결과: 볼펜
SELECT name, category, price
FROM products
WHERE name LIKE '_펜';

-- [5. IS NULL] 결과: 없음
SELECT name, category, price
FROM products
WHERE category = NULL;

-- [5. IS NULL] 결과: 없음
SELECT name, category, price
FROM products
WHERE category IS NULL;

-- [5. IS NULL] 결과: SQL 입문서, 볼펜, SQL 문제집, 노트, 만년필, 형광펜
SELECT name, category, price
FROM products
WHERE category IS NOT NULL;

-- [5. IS NULL] 결과: 없음
SELECT name, category, price
FROM products
WHERE category
  NOT IN ('book', NULL);
