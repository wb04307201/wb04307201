# 04 Lambda 条件构造器

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L153-162(§三.3 Lambda 构造器)

## 1. 核心优势

使用 Lambda 表达式可以避免字段名硬编码，**编译期类型安全**，重构时 IDE 自动追踪。

| 构造器类型 | 用途 | 对应操作 |
|-----------|------|---------|
| `LambdaQueryWrapper` | 查询条件 | SELECT / WHERE |
| `LambdaUpdateWrapper` | 更新条件 | UPDATE / SET / WHERE |
| `LambdaChainWrapper` | 链式调用 | 无需注入 Mapper |

## 2. 查询示例

```java
// 基础查询：name = 'Tom' AND age > 20
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<User>()
    .eq(User::getName, "Tom")
    .gt(User::getAge, 20);
List<User> users = userMapper.selectList(wrapper);

// 条件构造：OR + LIKE + 排序
LambdaQueryWrapper<User> complex = new LambdaQueryWrapper<User>()
    .like(User::getName, "张")
    .or(w -> w.eq(User::getStatus, 1).gt(User::getScore, 80))
    .orderByDesc(User::getCreateTime)
    .last("LIMIT 10");  // 注意：last() 有 SQL 注入风险

// 条件判空拼接（动态查询）
String name = ...;  // 可能为 null
LambdaQueryWrapper<User> dynamic = new LambdaQueryWrapper<User>()
    .eq(StringUtils.isNotBlank(name), User::getName, name)
    .ge(User::getAge, 18);
```

## 3. 更新示例

```java
// LambdaUpdateWrapper：SET name = 'NewName' WHERE id = 1
LambdaUpdateWrapper<User> updateWrapper = new LambdaUpdateWrapper<User>()
    .set(User::getName, "NewName")
    .set(User::getUpdateTime, LocalDateTime.now())
    .eq(User::getId, 1);
userMapper.update(null, updateWrapper);

// 使用 entity 的字段作为 SET 值
User user = new User();
user.setName("Updated");
userMapper.update(user, new LambdaUpdateWrapper<User>()
    .eq(User::getId, 1));
```

## 4. 常用条件方法速查

| 方法 | SQL | 示例 |
|------|-----|------|
| `eq` | `= value` | `.eq(User::getStatus, 1)` |
| `ne` | `<> value` | `.ne(User::getStatus, 0)` |
| `gt / ge / lt / le` | `> / >= / < / <=` | `.ge(User::getAge, 18)` |
| `between` | `BETWEEN ? AND ?` | `.between(User::getAge, 18, 60)` |
| `like / likeLeft / likeRight` | `LIKE '%?%' / '?%' / '%?'` | `.like(User::getName, "张")` |
| `in` | `IN (...)` | `.in(User::getStatus, Arrays.asList(1, 2))` |
| `orderByDesc` | `ORDER BY ... DESC` | `.orderByDesc(User::getCreateTime)` |
| `select` | 指定列 | `.select(User::getId, User::getName)` |

## 5. 注意事项

- **Lambda 引用的是 getter 方法**，不是字段名；确保 Lombok `@Data` 已生成 getter
- **`last()` 方法有 SQL 注入风险**，仅用于固定 LIMIT 等场景，不要拼接用户输入
- **嵌套条件**用 `and(w -> w...)` 或 `or(w -> w...)` 实现括号包裹

> 进一步深入 LambdaQueryWrapper 背后的 SFunction 序列化原理,见 [05 LambdaQueryWrapper 中的 SFunction 序列化原理](./05-lambda-sfunction-deep-dive.md)。

---

## 相关章节

- 前置：[`MyBatis-Plus 概览`](README.md)
- 深入：[`05 SFunction 序列化原理`](05-lambda-sfunction-deep-dive.md)
- 对比：[`MyBatis 动态 SQL`](../01-architecture/05-dynamic-sql.md)
