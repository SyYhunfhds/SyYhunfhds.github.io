---
title: PostgreSQL 16 SQL语句操作指南
日期: 2026-04-17
footer: Trae编辑
---

# PostgreSQL 16 SQL语句操作指南

本指南从易到难介绍PostgreSQL 16的SQL语句操作，包括基础语句、表结构操作、查询进阶、高级特性以及PostgreSQL 16的新特性。

## 1. 基础SQL语句

### 1.1 SELECT语句

**基本语法**：
```sql
SELECT column1, column2, ...
FROM table_name
WHERE condition
ORDER BY column1, column2, ...;
```

**示例**：
```sql
-- 选择所有列
SELECT * FROM users;

-- 选择特定列
SELECT id, name, email FROM users;

-- 带条件的查询
SELECT * FROM users WHERE age > 18;

-- 排序
SELECT * FROM users ORDER BY age DESC;

-- 限制结果数量
SELECT * FROM users LIMIT 10;
```

### 1.2 INSERT语句

**基本语法**：
```sql
INSERT INTO table_name (column1, column2, ...) 
VALUES (value1, value2, ...);
```

**示例**：
```sql
-- 插入单行
INSERT INTO users (name, email, age) 
VALUES ('John Doe', 'john@example.com', 30);

-- 插入多行
INSERT INTO users (name, email, age) 
VALUES 
  ('Jane Smith', 'jane@example.com', 25),
  ('Bob Johnson', 'bob@example.com', 35);

-- 使用默认值
INSERT INTO users (name, email) 
VALUES ('Alice Brown', 'alice@example.com');
```

### 1.3 UPDATE语句

**基本语法**：
```sql
UPDATE table_name 
SET column1 = value1, column2 = value2, ...
WHERE condition;
```

**示例**：
```sql
-- 更新单个字段
UPDATE users 
SET age = 31 
WHERE id = 1;

-- 更新多个字段
UPDATE users 
SET name = 'Johnathan Doe', email = 'johnathan@example.com' 
WHERE id = 1;

-- 基于其他字段更新
UPDATE users 
SET age = age + 1 
WHERE id = 1;
```

### 1.4 DELETE语句

**基本语法**：
```sql
DELETE FROM table_name 
WHERE condition;
```

**示例**：
```sql
-- 删除特定行
DELETE FROM users 
WHERE id = 1;

-- 删除满足条件的多行
DELETE FROM users 
WHERE age < 18;

-- 删除所有行（保留表结构）
DELETE FROM users;
```

## 2. 表结构操作

### 2.1 CREATE TABLE语句

**基本语法**：
```sql
CREATE TABLE [IF NOT EXISTS] table_name (
    column1 datatype [constraint],
    column2 datatype [constraint],
    ...
    [table_constraint]
);
```

**示例**：
```sql
-- 创建基本表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建带外键的表
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    total DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 ALTER TABLE语句

**基本语法**：
```sql
ALTER TABLE table_name
ADD COLUMN column_name datatype [constraint],
ALTER COLUMN column_name [SET DATA TYPE datatype],
DROP COLUMN column_name,
RENAME COLUMN old_name TO new_name,
RENAME TO new_table_name;
```

**示例**：
```sql
-- 添加新列
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- 修改列数据类型
ALTER TABLE users ALTER COLUMN age SET DATA TYPE SMALLINT;

-- 删除列
ALTER TABLE users DROP COLUMN phone;

-- 重命名列
ALTER TABLE users RENAME COLUMN email TO email_address;

-- 重命名表
ALTER TABLE users RENAME TO customers;
```

::: tip PostgreSQL 16新特性
PostgreSQL 16 开始，添加 `NOT NULL DEFAULT` 字段不再重写表，而是通过系统表记录默认值，读取时动态填充，写入时存储真实值。
:::

### 2.3 DROP TABLE语句

**基本语法**：
```sql
DROP TABLE [IF EXISTS] table_name [CASCADE | RESTRICT];
```

**示例**：
```sql
-- 删除表（如果存在）
DROP TABLE IF EXISTS orders;

-- 级联删除（删除依赖此表的对象）
DROP TABLE IF EXISTS users CASCADE;
```

## 3. 查询进阶

### 3.1 JOIN操作

**基本语法**：
```sql
SELECT columns
FROM table1
[INNER | LEFT | RIGHT | FULL] JOIN table2
ON table1.column = table2.column;
```

**示例**：
```sql
-- 内连接
SELECT u.name, o.total, o.order_date
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- 左连接
SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- 右连接
SELECT u.name, o.total
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- 全连接
SELECT u.name, o.total
FROM users u
FULL JOIN orders o ON u.id = o.user_id;
```

::: tip PostgreSQL 16新特性
PostgreSQL 16 支持并行执行 FULL 和 RIGHT 连接，提高查询性能。
:::

### 3.2 GROUP BY和HAVING

**基本语法**：
```sql
SELECT column1, aggregate_function(column2)
FROM table_name
WHERE condition
GROUP BY column1
HAVING condition;
```

**示例**：
```sql
-- 按用户分组计算订单总额
SELECT u.name, SUM(o.total) as total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.name;

-- 按用户分组，只显示消费超过1000的用户
SELECT u.name, SUM(o.total) as total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.name
HAVING SUM(o.total) > 1000;
```

### 3.3 子查询

**示例**：
```sql
-- 子查询作为条件
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 500);

-- 子查询作为表
SELECT u.name, order_count
FROM users u
JOIN (
    SELECT user_id, COUNT(*) as order_count
    FROM orders
    GROUP BY user_id
) o ON u.id = o.user_id;

-- 相关子查询
SELECT u.name, (
    SELECT SUM(total) FROM orders o WHERE o.user_id = u.id
) as total_spent
FROM users u;
```

::: tip PostgreSQL 16新特性
PostgreSQL 16 允许 FROM 子句中的子查询省略别名。
:::

## 4. 高级特性

### 4.1 窗口函数

**基本语法**：
```sql
SELECT column1, column2, 
       window_function(column3) OVER (PARTITION BY column4 ORDER BY column5)
FROM table_name;
```

**示例**：
```sql
-- 计算每个用户的订单金额排名
SELECT u.name, o.total, 
       ROW_NUMBER() OVER (PARTITION BY o.user_id ORDER BY o.total DESC) as rank
FROM users u
JOIN orders o ON u.id = o.user_id;

-- 计算移动平均值
SELECT order_date, total, 
       AVG(total) OVER (ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg
FROM orders;

-- 计算累计和
SELECT order_date, total, 
       SUM(total) OVER (ORDER BY order_date) as cumulative_sum
FROM orders;
```

::: tip PostgreSQL 16新特性
PostgreSQL 16 优化了窗口函数的执行效率。
:::

### 4.2 公共表表达式（CTE）

**基本语法**：
```sql
WITH cte_name (column1, column2, ...) AS (
    SELECT ...
)
SELECT ... FROM cte_name;
```

**示例**：
```sql
-- 简单CTE
WITH high_value_orders AS (
    SELECT * FROM orders WHERE total > 1000
)
SELECT u.name, hvo.total
FROM users u
JOIN high_value_orders hvo ON u.id = hvo.user_id;

-- 递归CTE
WITH RECURSIVE employee_hierarchy AS (
    SELECT id, name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, eh.level + 1
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy;
```

### 4.3 事务处理

**基本语法**：
```sql
BEGIN;
-- SQL语句
COMMIT;
-- 或
ROLLBACK;
```

**示例**：
```sql
-- 转账事务
BEGIN;
UPDATE accounts SET balance = balance - 1000 WHERE id = 1;
UPDATE accounts SET balance = balance + 1000 WHERE id = 2;
COMMIT;

-- 带保存点的事务
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE id = 1;
SAVEPOINT sp1;
UPDATE accounts SET balance = balance + 500 WHERE id = 2;
-- 出现错误
ROLLBACK TO sp1;
-- 修正错误
UPDATE accounts SET balance = balance + 500 WHERE id = 3;
COMMIT;
```

## 5. PostgreSQL 16新特性

### 5.1 SQL/JSON语法增强

**示例**：
```sql
-- 使用JSON_ARRAY()构造JSON数组
SELECT JSON_ARRAY(1, 2, 3);

-- 使用JSON_ARRAYAGG()聚合JSON数组
SELECT JSON_ARRAYAGG(id) FROM users;

-- 使用IS JSON谓词
SELECT * FROM products WHERE attributes IS JSON;

-- 使用JSON_OBJECT()构造JSON对象
SELECT JSON_OBJECT('name', name, 'price', price) FROM products;
```

::: tip PostgreSQL 16新特性
PostgreSQL 16 添加了更多SQL/JSON标准的语法，包括构造函数和谓词。
:::

### 5.2 数字格式增强

**示例**：
```sql
-- 使用下划线作为千位分隔符
SELECT 1_000_000 as million;

-- 使用非十进制整数常量
SELECT 0x1A as hex, 0o123 as octal, 0b1010 as binary;
```

::: tip PostgreSQL 16新特性
PostgreSQL 16 允许使用下划线作为千位分隔符，并支持非十进制整数常量。
:::

### 5.3 增量排序优化

**示例**：
```sql
-- 增量排序优化的查询
SELECT DISTINCT name FROM users ORDER BY name;

-- 带ORDER BY的聚合函数
SELECT department, MAX(salary) FROM employees GROUP BY department ORDER BY department;
```

::: tip PostgreSQL 16新特性
PostgreSQL 16 支持在更多情况下使用增量排序，包括DISTINCT查询和带ORDER BY的聚合函数。
:::

### 5.4 并行查询增强

**示例**：
```sql
-- 并行执行的FULL JOIN
SELECT * FROM table1 FULL JOIN table2 ON table1.id = table2.id;

-- 并行执行的RIGHT JOIN
SELECT * FROM table1 RIGHT JOIN table2 ON table1.id = table2.id;
```

::: tip PostgreSQL 16新特性
PostgreSQL 16 允许并行执行FULL和RIGHT外连接，提高查询性能。
:::

### 5.5 其他新特性

**示例**：
```sql
-- 使用pg_stat_io视图监控I/O统计
SELECT * FROM pg_stat_io;

-- 查看表的最后扫描时间
SELECT relname, last_vacuum, last_analyze, last_scan FROM pg_stat_all_tables;

-- 使用正则表达式匹配用户和数据库名称（在pg_hba.conf中）
-- host all all 192.168.1.0/24 md5
-- host all "^app_.*" 192.168.1.0/24 md5
```

::: tip PostgreSQL 16新特性
PostgreSQL 16 引入了pg_stat_io视图用于监控I/O统计，在pg_stat_all_tables中添加了last_scan字段，并支持在pg_hba.conf中使用正则表达式匹配用户和数据库名称。
:::

## 6. 性能优化技巧

### 6.1 索引使用

**示例**：
```sql
-- 创建B-tree索引
CREATE INDEX idx_users_email ON users(email);

-- 创建部分索引
CREATE INDEX idx_users_active ON users(id) WHERE active = true;

-- 创建表达式索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- 创建复合索引
CREATE INDEX idx_orders_user_total ON orders(user_id, total);
```

### 6.2 查询优化

**示例**：
```sql
-- 使用EXPLAIN分析查询计划
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'john@example.com';

-- 使用LIMIT限制结果
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;

-- 避免SELECT *
SELECT id, name, email FROM users WHERE age > 18;

-- 使用JOIN替代子查询
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.total > 500;
```

### 6.3 真空操作

**示例**：
```sql
-- 手动执行VACUUM
VACUUM users;

-- 带分析的VACUUM
VACUUM ANALYZE users;

-- 强制清理（需要表锁）
VACUUM FULL users;
```

## 7. 最佳实践

1. **使用参数化查询**：避免SQL注入
2. **合理使用索引**：不要过度索引
3. **定期执行VACUUM**：保持数据库健康
4. **使用事务**：确保数据一致性
5. **优化查询**：使用EXPLAIN分析执行计划
6. **监控性能**：使用`pg_stat_*`视图
7. **备份数据**：定期执行pg_dump
8. **使用连接池**：减少连接开销
9. **设置合理的配置参数**：根据硬件调整
10. **保持PostgreSQL版本更新**：获取最新特性和安全修复

## 8. 总结

本指南介绍了PostgreSQL 16的SQL语句操作，从基础的SELECT、INSERT、UPDATE、DELETE语句，到表结构操作、查询进阶、高级特性，以及PostgreSQL 16的新特性。通过学习这些内容，您可以更高效地使用PostgreSQL 16进行数据库操作和管理。

PostgreSQL 16带来了许多性能改进和新特性，包括并行查询增强、SQL/JSON语法支持、数字格式改进等，这些都可以帮助您更高效地处理数据。

::: tip 提示
建议结合PostgreSQL官方文档和实际项目需求，进一步学习和掌握PostgreSQL的高级特性和最佳实践。
:::

## 参考资料

- [PostgreSQL 16官方文档](https://www.postgresql.org/docs/16/)
- [PostgreSQL 16发布说明](https://www.postgresql.org/docs/16/release-16.html)