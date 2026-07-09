<!--
module:
  parent: spring
  slug: spring/mybatis-plus/pagination
  type: article
  category: 主模块子文章
  summary: MyBatis-Plus 分页插件——配置、自定义 count 查询与常见陷阱。
-->

# 06 分页插件

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L164-194(§三.4 分页插件)

## 6.1 配置分页插件

```java
@Configuration
public class MybatisPlusConfig {

    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }
}
```

## 6.2 使用分页

```java
// 查询第1页,每页10条
Page<User> page = new Page<>(1, 10);
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("age", 25);
Page<User> userPage = userMapper.selectPage(page, wrapper);

// 获取分页数据
List<User> records = userPage.getRecords();  // 当前页数据
long total = userPage.getTotal();           // 总记录数
long pages = userPage.getPages();           // 总页数
```

---

## 二、核心参数表

`PaginationInnerInterceptor` 提供以下关键配置参数：

| 参数 | 类型 | 默认值 | 推荐值 | 说明 |
|------|------|--------|--------|------|
| `maxLimit` | `Long` | `null`（不限制） | `500L` | 单页最大条数上限。**生产环境必须设置**，否则 `new Page<>(1, 999999)` 可导致全表扫描 OOM |
| `overflow` | `boolean` | `false` | `false` | 页码溢出处理。`false` → 请求超出范围页码返回空列表；`true` → 回绕到第 1 页继续查询 |
| `optimizeCountSql` | `boolean` | `true` | `true` | 自动优化 count SQL：移除 `ORDER BY`，将 `SELECT col1, col2` 替换为 `SELECT COUNT(*)` |
| `optimizeJoinOfCountSql` | `boolean` | `true` | `true`（3.5.3.1+） | 自动去除 count SQL 中不必要的 `JOIN`（当 JOIN 不影响行数时） |
| `dbType` | `DbType` | 自动识别 | 显式指定 | 数据库类型。多数据源场景建议显式传入 `DbType.MYSQL` / `DbType.POSTGRE_SQL` |
| `dialectClass` | `Class` | `null` | 按需 | 自定义方言类，用于非标准数据库的分页 SQL 生成 |

```java
// 推荐：生产环境配置示例
PaginationInnerInterceptor paginationInterceptor = new PaginationInnerInterceptor(DbType.MYSQL);
paginationInterceptor.setMaxLimit(500L);          // 防止恶意大页查询
paginationInterceptor.setOverflow(false);          // 页码溢出返回空
paginationInterceptor.setOptimizeCountSql(true);   // 优化 count SQL
paginationInterceptor.setOptimizeJoinOfCountSql(true); // 优化 count 中的 JOIN
interceptor.addInnerInterceptor(paginationInterceptor);
```

---

## 三、自定义 Count 查询

默认 `SELECT COUNT(*)` 在含 `JOIN`、`GROUP BY`、`DISTINCT` 的复杂 SQL 中可能返回错误结果。此时需手写 count 查询。

### 3.1 问题场景

```java
// ❌ 原始 SQL 含 LEFT JOIN + GROUP BY，默认 count 结果不正确
// SELECT o.*, u.name FROM orders o LEFT JOIN users u ON o.user_id = u.id GROUP BY o.id
// 自动生成的 count: SELECT COUNT(*) FROM orders o LEFT JOIN users u ON o.user_id = u.id GROUP BY o.id
// → 返回的是分组后的行数，而非总组数
```

### 3.2 使用 `@SqlParser` 自定义 count（XML 方式）

```xml
<!-- 主查询 -->
<select id="selectOrderPage" resultType="OrderVO">
    SELECT o.*, u.name
    FROM orders o
    LEFT JOIN users u ON o.user_id = u.id
    GROUP BY o.id
</select>

<!-- 自定义 count 查询：方法名 + _mpCount 后缀 -->
<select id="selectOrderPage_mpCount" resultType="Long">
    SELECT COUNT(*) FROM (
        SELECT o.id FROM orders o GROUP BY o.id
    ) tmp
</select>
```

### 3.3 关闭自动 count 优化

对于特定查询，可在 `Page` 对象上单独关闭优化：

```java
Page<OrderVO> page = new Page<>(1, 10);
page.setSearchCount(true);  // 仍然执行 count
// 但在 Mapper 层手动指定 count SQL（见上方 XML 方式）

// 或者：完全不执行 count（适合已知总数的场景）
Page<OrderVO> page = new Page<>(1, 10, false);  // 第三个参数 searchCount = false
```

---

## 四、常见陷阱

### 4.1 ❌ 忘记注册分页拦截器

```java
// ❌ 没有注册 PaginationInnerInterceptor
// selectPage() 不会报错，但返回全部数据（分页不生效）
Page<User> page = new Page<>(1, 10);
userMapper.selectPage(page, null); // 返回全表数据！
```

```java
// ✅ 确保拦截器已注册
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
    return interceptor;
}
```

### 4.2 ❌ 未设置 maxLimit 导致全表扫描

```java
// ❌ 攻击者可构造 pageSize = Integer.MAX_VALUE，导致 OOM
Page<User> page = new Page<>(1, Integer.MAX_VALUE);
userMapper.selectPage(page, null); // SELECT * FROM user（无 LIMIT）
```

```java
// ✅ 设置 maxLimit，超出部分自动截断
paginationInterceptor.setMaxLimit(500L);
// new Page<>(1, 10000) → 实际执行 LIMIT 500
```

### 4.3 ❌ 多数据源场景分页失效

```java
// ❌ 只配了一个数据源的分页拦截器，第二个数据源分页不生效
// 每个 SqlSessionFactory 都需要独立的 MybatisPlusInterceptor
```

```java
// ✅ 每个数据源各自配置拦截器
@Bean
@Qualifier("mysql")
public MybatisPlusInterceptor mysqlInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
    return interceptor;
}

@Bean
@Qualifier("postgres")
public MybatisPlusInterceptor pgInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.POSTGRE_SQL));
    return interceptor;
}
```

### 4.4 ❌ 拦截器顺序错误

```java
// ❌ 分页拦截器必须在动态表名、乐观锁等拦截器之前注册
interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor()); // 先加
interceptor.addInnerInterceptor(new PaginationInnerInterceptor());        // 后加 → 分页可能失效
```

```java
// ✅ 推荐顺序：分页 → 乐观锁 → 动态表名
interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor());
interceptor.addInnerInterceptor(new DynamicTableNameInnerInterceptor());
```

### 4.5 ❌ Page 参数非序列化导致 Redis 缓存失败

```java
// ❌ Page 对象包含大量内部状态，直接序列化到 Redis 会报错或体积过大
redisTemplate.opsForValue().set("user:page:1", userPage);
```

```java
// ✅ 只缓存 records + total，封装为简单 DTO
record PageResult<T>(List<T> records, long total) {}
var result = new PageResult<>(userPage.getRecords(), userPage.getTotal());
redisTemplate.opsForValue().set("user:page:1", result);
```

---

## 五、性能优化

### 5.1 optimizeCountSql — 自动优化 count SQL

开启后（默认 `true`），插件会：
1. 移除 `ORDER BY` 子句（排序不影响计数）
2. 将 `SELECT col1, col2, ...` 替换为 `SELECT COUNT(*)`
3. 移除不必要的 `LIMIT`

```sql
-- 原始 SQL
SELECT id, name, age FROM user WHERE age > 18 ORDER BY create_time DESC

-- 优化后的 count SQL
SELECT COUNT(*) FROM user WHERE age > 18
```

> **注意**：当 SQL 含 `GROUP BY` 时，自动优化可能产生错误结果。此时应关闭优化或使用自定义 count（见第三节）。

### 5.2 optimizeJoinOfCountSql — 去除无用 JOIN

3.5.3.1+ 版本新增。当 `JOIN` 不影响主表行数时，自动去除：

```sql
-- 原始 SQL
SELECT o.id, o.amount, u.name
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE o.status = 1

-- 优化后的 count SQL（LEFT JOIN 不影响 orders 行数，自动去除）
SELECT COUNT(*) FROM orders o WHERE o.status = 1
```

> **限制**：仅对 `LEFT JOIN` 有效；`INNER JOIN` 会过滤行，不能安全去除。

### 5.3 大表分页深翻页优化

当 offset 很大时（如第 10000 页），`LIMIT 100000, 10` 性能急剧下降。可选方案：

```java
// 方案 1：游标分页（基于上一页最后一条的 ID）
wrapper.gt("id", lastId);
wrapper.orderByAsc("id");
wrapper.last("LIMIT 10");

// 方案 2：子查询优化（先查 ID，再关联查详情）
// SELECT * FROM user WHERE id IN (
//     SELECT id FROM user ORDER BY id LIMIT 100000, 10
// )
```

---

← [返回: MyBatis-Plus](../README.md)
