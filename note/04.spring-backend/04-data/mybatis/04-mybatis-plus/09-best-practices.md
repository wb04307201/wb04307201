<!--
module:
  parent: 04.spring-backend
  slug: 04.spring-backend\04-data\mybatis\04-mybatis-plus\09-best-practices
  type: article
  category: 主模块子文章
  summary: 09 最佳实践与踩坑
  depth: ⭐⭐⭐
-->

# 09 最佳实践与踩坑

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L317-419（§五 常见问题 + §六 最佳实践 + §七 总结）

MyBatis-Plus 把 MyBatis 的样板代码压到极致，但也带来"误用风险"——Lambda 表达式、`Wrapper` 滥用、`Page` 性能、`@TableLogic` 隐形条件、`MetaObjectHandler` 顺序等坑遍布生产。本章按 **8 条主原则** + 每条 **❌/✅ 反例对比** 整理踩坑实录，所有反例都来自真实项目翻车现场。

---

## 一、主键策略：避免 auto-increment 与分布式 ID 混用

### ❌ 反例

```java
// 老库迁移：原表 AUTO_INCREMENT，新服务分库分表
@TableId(type = IdType.AUTO)
private Long id;  // 单库没问题；分表后 ID 冲突 + 无法全局排序
```

### ✅ 正例

```java
// 分布式场景：雪花算法（默认 ASSIGN_ID）
@TableId(type = IdType.ASSIGN_ID)   // 19 位 Long，趋势递增，全局唯一
private Long id;
```

```yaml
# application.yml：可调 workerId / datacenterId（雪花算法）
mybatis-plus:
  global-config:
    id-type: ASSIGN_ID
```

**ID 类型选择决策树**：
- 单库小项目 → `AUTO`
- 分布式 / 分库分表 → `ASSIGN_ID`（Long）
- 对外暴露（订单号要可读） → `ASSIGN_UUID` 或自定义生成器

---

## 二、字段命名：DB ↔ 实体 ↔ JSON 三端一致

### ❌ 反例

```sql
-- DB 字段：user_name（snake_case）
CREATE TABLE user (user_name VARCHAR(50), user_age INT);
```

```java
// 实体类：驼峰
private String userName;
```

```java
// Controller 返回：Pascal
public UserVO getUser(...) { return new UserVO(); }
// 序列化后 JSON: {"UserName": "tom"}  ← 大小写不一致，前端哭晕
```

### ✅ 正例

统一三端：

```java
// 方案 A：application.yml 全局开启驼峰转换（推荐）
mybatis-plus:
  configuration:
    map-underscore-to-camel-case: true

// DB: user_name
// 实体: userName → 自动映射 user_name
// JSON: 实体序列化后 {"userName": "tom"}
```

```java
// 方案 B：使用 @JsonNaming 控制 JSON 字段名
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class UserVO {
    private String userName;  // JSON: {"user_name": "tom"}
}
```

**黄金法则**：DB snake_case + 实体 camelCase + JSON camelCase，三端一致最省心。

---

## 三、Wrapper 使用边界：能用 Lambda 别用字符串

### ❌ 反例

```java
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("user_name", "tom")
       .eq("is_deletd", 0);  // 拼错字段名 → SQL 不报错但查不到数据
wrapper.like("user_naem", "to");  // 同样拼错 → 静默 bug
```

### ✅ 正例

```java
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
wrapper.eq(User::getUserName, "tom")
       .eq(User::getDeleted, 0);   // 编译期检查，字段重命名 IDE 自动追踪
wrapper.like(User::getUserName, "to");
```

**何时退回 Wrapper（非 Lambda）**：
- 动态字段名（运行时根据配置决定查哪列）
- SQL 注入式拼接（业务必须用字符串字段名）
- 跨实体聚合查询

**何时退回 XML/注解 SQL**：
- 多表 JOIN（≥3 张）
- 子查询 / 复杂聚合（`GROUP BY` + `HAVING`）
- 数据库方言特性（`CONNECT BY`、`FOR UPDATE SKIP LOCKED`）

---

## 四、N+1 查询：用 JOIN 或 IN 一次性取

### ❌ 反例

```java
List<Order> orders = orderMapper.selectList(null);   // 100 单
for (Order o : orders) {
    User user = userMapper.selectById(o.getUserId());  // 100 次单查
    o.setUserName(user.getName());
}
// → 1 + 100 次 SQL，慢
```

### ✅ 正例

```java
// 方案 A：单 SQL JOIN（推荐）
@Select("SELECT o.*, u.name AS user_name " +
       "FROM orders o LEFT JOIN users u ON o.user_id = u.id " +
       "WHERE o.status = 1")
List<OrderVO> selectActiveOrders();

// 方案 B：IN 批量
List<Long> userIds = orders.stream().map(Order::getUserId).toList();
List<User> users = userMapper.selectBatchIds(userIds);
Map<Long, User> userMap = users.stream().collect(Collectors.toMap(User::getId, u -> u));
for (Order o : orders) {
    o.setUserName(userMap.get(o.getUserId()).getName());
}
```

---

## 五、分页：大表深翻页用游标，别用 OFFSET

### ❌ 反例

```java
// 100 万数据翻到第 1000 页：LIMIT 99990, 10
Page<Order> page = new Page<>(1000, 10);
orderMapper.selectPage(page, null);
// → MySQL 仍要扫前 999990 行，30 秒+
```

### ✅ 正例

```java
// 方案 A：游标分页（推荐，适合无限滚动）
LambdaQueryWrapper<Order> wrapper = new LambdaQueryWrapper<>();
wrapper.gt(Order::getId, lastId)  // 上一页最后一条的 ID
       .orderByAsc(Order::getId)
       .last("LIMIT 10");
List<Order> page = orderMapper.selectList(wrapper);

// 方案 B：子查询优化（适合仍需 OFFSET 的场景）
// SELECT * FROM orders WHERE id IN (
//   SELECT id FROM orders WHERE status = 1 ORDER BY id LIMIT 99990, 10
// )
```

**深翻页阈值**：offset > 1000 就考虑游标分页。

---

## 六、@TableLogic：自定义 SQL 记得手动加 deleted = 0

### ❌ 反例

```java
// 自定义 XML 查询 → @TableLogic 不生效
List<User> selectByEmail(@Param("email") String email);

// XML
<select id="selectByEmail">
    SELECT * FROM user WHERE email = #{email}    -- 没加 deleted = 0
</select>
// → 把已删除的用户也查出来
```

### ✅ 正例

```xml
<!-- 手动加 deleted = 0 -->
<select id="selectByEmail">
    SELECT * FROM user WHERE email = #{email} AND deleted = 0
</select>
```

**或用 AOP 统一拦截**：自定义拦截器扫描 Mapper 方法名，自动追加逻辑删除条件（项目级抽象）。

---

## 七、批量操作：用 saveBatch + rewriteBatchedStatements

### ❌ 反例

```java
for (User u : users) {
    userMapper.insert(u);   // 1000 条 = 1000 次 INSERT，每次网络往返
}
```

### ✅ 正例

```java
// MP saveBatch 底层用 ExecutorType.BATCH
userService.saveBatch(users, 500);   // 每批 500 条
```

```yaml
# MySQL JDBC URL 关键参数：开启批量重写
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/test?rewriteBatchedStatements=true
```

**性能对比**（1000 条 INSERT）：
- ❌ 循环 insert：约 12 秒
- ✅ `saveBatch` + `rewriteBatchedStatements=true`：约 200ms

**注意**：
- 事务中调用才生效（`saveBatch` 非自动事务）
- 主键策略 `AUTO` 在某些驱动下 batch 会失效 → 用 `ASSIGN_ID`

---

## 八、Wrapper last()：避免 SQL 注入

### ❌ 反例

```java
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.last("LIMIT " + userInput);  // 用户输入 "1; DROP TABLE user;" → 注入！
```

### ✅ 正例

```java
// 方案 A：用分页参数（推荐）
Page<User> page = new Page<>(1, 10);
userMapper.selectPage(page, wrapper);   // MP 自动追加 LIMIT 10 OFFSET 0

// 方案 B：last() 只用于固定常量（项目内审过的值）
wrapper.last("LIMIT 10");

// 方案 C：自定义 SqlInterceptor 拦截 last() 中的危险字符
```

**last() 使用守则**：
- 仅用于固定字符串（`LIMIT 10`、`ORDER BY ... FOR UPDATE`）
- 严禁拼接用户输入
- 分页场景统一用 `Page<T>`，别用 `last("LIMIT ?")`

---

## 九、补充陷阱速查表

| # | 陷阱 | 后果 | 解决 |
|---|------|------|------|
| 1 | `@TableId(type = IdType.AUTO)` + 分库分表 | ID 重复 | 改 `ASSIGN_ID` |
| 2 | 实体 `userName` + DB `user_name` + 默认关闭 map-underscore-to-camel-case | 字段映射为 null | 开启驼峰转换 |
| 3 | Wrapper 用 `"is_deletd"` 拼错字段名 | 静默查询结果错 | 用 `LambdaQueryWrapper` |
| 4 | 100 单循环 selectById | N+1 慢查询 | JOIN 或 IN 批量 |
| 5 | 深翻页 `LIMIT 100000, 10` | 慢 SQL | 游标分页 / 子查询 |
| 6 | XML 漏加 `AND deleted = 0` | 查出已删除 | 自定义 SQL 必加 |
| 7 | `saveBatch` 未开 `rewriteBatchedStatements` | 批量仍是逐条 | JDBC URL 加参数 |
| 8 | `last("LIMIT " + userInput)` | SQL 注入 | 用 Page 参数 |
| 9 | `@Version` 字段未在 updateById 时传递 | 乐观锁失效 | entity 必须有 version |
| 10 | `@TableLogic` + 唯一索引 `UNIQUE(username, deleted)` | 删除后无法重建 | deleted 不进唯一索引 |
| 11 | 多数据源只配一个 `MybatisPlusInterceptor` | 第二个数据源拦截器失效 | 每数据源独立配置 |
| 12 | `Page<T>` 直接 Redis 序列化 | 体积过大 / 报错 | 转 `PageResult<T>(records, total)` |

---

## 十、推荐学习路径

```text
Day 1: 01-quickstart + 02-crud-basics  → 上手 80% 场景
Day 2: 03-wrapper-system + 04-lambda-wrapper  → 链式写条件
Day 3: 05-sfunction-deep-dive  → 理解 Lambda 原理
Day 4: 06-pagination  → 分页必备
Day 5: 07-auto-fill-and-logic-delete  → 通用字段 / 假删除
Day 6: 08-advanced-interceptors  → 多租户 / 动态表名 / 防全表
Day 7: 09 (本文) + 10-code-generator  → 工程化与团队规范
```

## 推荐学习资源

- [MyBatis-Plus 官方文档](https://baomidou.com/)
- [MyBatis-Plus GitHub](https://github.com/baomidou/mybatis-plus)
- [MyBatis-Plus 示例项目](https://github.com/baomidou/mybatis-plus-samples)

---

## 反向链

- [`06-pagination`](06-pagination.md) — 分页深翻页原理
- [`07-auto-fill-and-logic-delete`](07-auto-fill-and-logic-delete.md) — `MetaObjectHandler` / `@TableLogic` 陷阱
- [`08-advanced-interceptors`](08-advanced-interceptors.md) — 多租户 / 数据权限拦截器

← [返回: MyBatis-Plus 全家桶](./README.md)