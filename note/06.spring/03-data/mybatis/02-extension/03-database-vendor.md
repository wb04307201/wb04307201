# 03 数据库厂商扩展(DatabaseIdProvider)

> 来源:整合自原 08.mybatis/README.md § 七.7.3

## 1. 核心机制

`DatabaseIdProvider` 允许 MyBatis 根据当前数据库类型执行不同的 SQL 语句，实现**一套代码适配多种数据库**。

工作原理：
1. MyBatis 启动时通过 `DatabaseIdProvider` 检测当前数据库的 `DatabaseProductName`
2. 将产品名映射为简短的 `databaseId`（如 `MySQL` → `mysql`）
3. 加载 Mapper XML 时，优先匹配 `databaseId` 一致的语句；无匹配则加载无 `databaseId` 的通用语句

## 2. 配置方式

### 2.1 mybatis-config.xml 配置

```xml
<databaseIdProvider type="DB_VENDOR">
    <property name="MySQL" value="mysql"/>
    <property name="Oracle" value="oracle"/>
    <property name="PostgreSQL" value="pg"/>
    <property name="SQL Server" value="mssql"/>
</databaseIdProvider>
```

### 2.2 Spring Boot 配置

```yaml
mybatis-plus:
  configuration:
    database-id-provider:
      type: DB_VENDOR
      properties:
        MySQL: mysql
        Oracle: oracle
```

## 3. 使用方式

```xml
<!-- MySQL 专用：使用 LIMIT -->
<select id="selectTopUsers" resultType="User" databaseId="mysql">
    SELECT * FROM user ORDER BY score DESC LIMIT #{limit}
</select>

<!-- Oracle 专用：使用 ROWNUM -->
<select id="selectTopUsers" resultType="User" databaseId="oracle">
    SELECT * FROM (
        SELECT u.*, ROWNUM rn FROM user u ORDER BY score DESC
    ) WHERE rn &lt;= #{limit}
</select>

<!-- 通用：无 databaseId，作为兜底 -->
<select id="selectUserById" resultType="User">
    SELECT * FROM user WHERE id = #{id}
</select>
```

## 4. 匹配优先级

| 优先级 | 条件 | 说明 |
|--------|------|------|
| 1（最高） | `databaseId` 匹配当前数据库 | 专用 SQL |
| 2 | 无 `databaseId` 属性 | 通用 SQL 兜底 |
| 3（不会加载） | `databaseId` 不匹配 | 被忽略 |

## 5. 适用场景与注意事项

| 场景 | 建议 |
|------|------|
| 单数据库项目 | 不需要 `DatabaseIdProvider`，增加复杂度 |
| 多数据库兼容产品 | 必备：为不同数据库的 SQL 方言提供差异化实现 |
| 分页差异 | MySQL `LIMIT` vs Oracle `ROWNUM` vs SQL Server `TOP` |
| 函数差异 | MySQL `IFNULL` vs Oracle `NVL` vs PG `COALESCE` |
| 日期函数 | MySQL `DATE_FORMAT` vs Oracle `TO_CHAR` |

**注意**：`databaseId` 匹配是**精确匹配**，`DB_VENDOR` 使用 `DatabaseProductName.contains(key)` 判断。

---

## 相关章节

- 前置：[`01 框架本质`](../01-architecture/01-framework-essence.md)
- 关联：[`02 初始化流程`](../01-architecture/02-initialization-flow.md) — Configuration 加载过程
- 对比：[`MyBatis 动态 SQL`](../01-architecture/05-dynamic-sql.md) — 另一种 SQL 差异化方案