# 增删改查SQL语句

## 1. SELECT语句（查询）
```sql
SELECT column1, column2, ...
FROM table_name
[WHERE condition]
[GROUP BY column_name]
[HAVING condition]
[ORDER BY column_name [ASC|DESC]]
[LIMIT number];
```

组成部分：
- **SELECT子句**：指定要检索的列
- **FROM子句**：指定数据来源的表
- **WHERE子句**（可选）：过滤条件
- **GROUP BY子句**（可选）：分组依据
- **HAVING子句**（可选）：对分组结果过滤
- **ORDER BY子句**（可选）：排序依据
- **LIMIT子句**（可选）：限制返回行数

## 2. INSERT语句（新增）
```sql
INSERT INTO table_name (column1, column2, ...)
VALUES (value1, value2, ...);
```
或
```sql
INSERT INTO table_name
SELECT ... FROM ... WHERE ...;
```

组成部分：
- **INSERT INTO子句**：指定目标表
- **列名列表**（可选）：指定要插入的列
- **VALUES子句**：提供要插入的值

## 3. UPDATE语句（修改）
```sql
UPDATE table_name
SET column1 = value1, column2 = value2, ...
[WHERE condition];
```

组成部分：
- **UPDATE子句**：指定要更新的表
- **SET子句**：指定要更新的列及其新值
- **WHERE子句**（可选）：限定要更新的行

## 4. DELETE语句（删除）
```sql
DELETE FROM table_name
[WHERE condition];
```

组成部分：
- **DELETE FROM子句**：指定要删除数据的表
- **WHERE子句**（可选）：限定要删除的行

## 共同特点
所有SQL语句通常可以包含：
- **注释**：`-- 单行注释` 或 `/* 多行注释 */`
- **事务控制**：如 `BEGIN TRANSACTION`, `COMMIT`, `ROLLBACK`
- **权限控制**：如 `GRANT`, `REVOKE`

这些组成部分可以根据具体需求组合使用，构成完整的SQL语句。