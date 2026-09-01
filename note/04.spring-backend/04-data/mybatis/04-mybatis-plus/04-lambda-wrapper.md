<!--
module:
  parent: 04.spring-backend
  slug: 04.spring-backend\04-data\mybatis\04-mybatis-plus\04-lambda-wrapper
  type: article
  category: MyBatis-Plus 实战
  summary: MyBatis-Plus Lambda 条件构造器——User::getName 类型安全替代硬编码字段名。
  depth: ⭐⭐⭐
-->

# 04 Lambda 条件构造器

> `LambdaQueryWrapper` / `LambdaUpdateWrapper` 通过方法引用(`User::getName`)替代字符串字段名,**编译期类型安全 + IDE 重构友好**,是新项目的**默认选择**。

## 🎯 一句话定位

**Lambda 构造器 = `SFunction<T, ?>` 替换 `String column`,让字段名从"运行时拼接"变成"编译期类型检查"**;核心价值:**避免字段拼写错误 + 重命名自动追踪 + 零 SQL 注入**。

---

## 一、核心优势对比

| 维度 | `QueryWrapper`(字符串) | `LambdaQueryWrapper`(方法引用) |
|------|----------------------|------------------------------|
| 编译期检查 | ❌ 字段拼错不报错 | ✅ getter 不存在 → 编译失败 |
| IDE 重构 | ❌ 改名后全文搜 | ✅ 改名自动追踪所有引用 |
| SQL 注入 | ⚠️ `last()` 拼接有风险 | ✅ 框架解析字段名,无注入 |
| 性能 | 略快(直接拼字符串) | 略慢(反射 `SerializedLambda`) |
| 多表字段冲突 | 易踩坑(`name` 在多表都有) | 通过类限定解决 |
| 适用场景 | 跨表动态查询 / 复杂字段 | **99% 单表场景** |

---

## 二、查询实战

### 2.1 基础查询

```java
// 基础:name = 'Tom' AND age > 20
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<User>()
    .eq(User::getName, "Tom")
    .gt(User::getAge, 20);
List<User> users = userMapper.selectList(wrapper);
// SQL: SELECT * FROM user WHERE name='Tom' AND age>20
```

### 2.2 复杂条件:OR + LIKE + 排序

```java
// 场景:姓"张" OR (status=1 且 score>80),按 create_time 倒序,前 10 条
LambdaQueryWrapper<User> complex = new LambdaQueryWrapper<User>()
    .like(User::getName, "张")                              // name LIKE '%张%'
    .or(w -> w.eq(User::getStatus, 1).gt(User::getScore, 80)) // AND (status=1 AND score>80)
    .orderByDesc(User::getCreateTime)
    .select(User::getId, User::getName, User::getScore)    // 只查 3 列
    .last("LIMIT 10");
List<User> topUsers = userMapper.selectList(complex);
// SQL: SELECT id,name,score FROM user
//      WHERE name LIKE '%张%' AND (status=1 AND score>80)
//      ORDER BY create_time DESC LIMIT 10
```

### 2.3 动态查询:condition 判空拼接

```java
// 场景:根据前端传入参数动态拼接(任一参数可能为 null)
String name = request.getName();          // 可能为 null 或空字符串
Integer minAge = request.getMinAge();     // 可能为 null
String email = request.getEmail();        // 可能为 null

LambdaQueryWrapper<User> dynamic = new LambdaQueryWrapper<User>()
    .eq(StringUtils.isNotBlank(name), User::getName, name)        // name 空 → 跳过
    .ge(minAge != null, User::getAge, minAge)                    // minAge null → 跳过
    .likeRight(StringUtils.isNotBlank(email), User::getEmail, email) // email 空 → 跳过
    .orderByDesc(User::getCreateTime);
List<User> users = userMapper.selectList(dynamic);
```

### 2.4 子查询(IN)

```java
// 场景:查在指定部门 ID 列表中的用户
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<User>()
    .in(User::getDeptId, Arrays.asList(1L, 2L, 3L, 4L))
    .eq(User::getStatus, 1);
// SQL: SELECT * FROM user WHERE dept_id IN (1,2,3,4) AND status=1
```

### 2.5 exists 子查询(自定义 SQL)

```java
// 场景:查存在订单的用户(user 表 + order 表关联)
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<User>()
    .eq(User::getStatus, 1)
    .apply("id IN (SELECT user_id FROM t_order WHERE amount > 1000)");
// apply 慎用,这里 amount > 1000 是硬编码,无注入风险
```

---

## 三、更新实战

### 3.1 基础更新:SET name='NewName' WHERE id=1

```java
LambdaUpdateWrapper<User> updateWrapper = new LambdaUpdateWrapper<User>()
    .set(User::getName, "NewName")
    .set(User::getUpdateTime, LocalDateTime.now())  // 自动填充兜底
    .eq(User::getId, 1);
userMapper.update(null, updateWrapper);
// SQL: UPDATE user SET name='NewName', update_time=NOW() WHERE id=1
```

### 3.2 entity + Wrapper 组合(entity 非空字段自动 SET)

```java
User user = new User();
user.setName("Updated");
user.setAge(30);
// Wrapper 只指定 WHERE,SET 字段从 user 非空字段读
userMapper.update(user, new LambdaUpdateWrapper<User>()
    .eq(User::getId, 1));
// SQL: UPDATE user SET name='Updated', age=30, ... WHERE id=1
```

### 3.3 链式更新(无需 Mapper,Service 层)

```java
// IService.lambdaUpdate() 链式调用,无需写 Mapper
boolean ok = userService.lambdaUpdate()
    .set(User::getStatus, 0)
    .set(User::getUpdateTime, LocalDateTime.now())
    .eq(User::getDeptId, 5L)
    .gt(User::getLastLoginTime, LocalDateTime.now().minusYears(1))
    .update();
// 等价 SQL: UPDATE user SET status=0, update_time=NOW()
//          WHERE dept_id=5 AND last_login_time > DATE_SUB(NOW(), INTERVAL 1 YEAR)
```

### 3.4 链式查询

```java
// 查询:status=1 且 name='Tom' 的唯一一条
User user = userService.lambdaQuery()
    .eq(User::getStatus, 1)
    .eq(User::getName, "Tom")
    .one();  // 返回单条,多条会抛 TooManyResultsException

// 查询列表:age 在 [18, 60] 且按 create_time 倒序的前 20 条
List<User> users = userService.lambdaQuery()
    .between(User::getAge, 18, 60)
    .orderByDesc(User::getCreateTime)
    .last("LIMIT 20")
    .list();

// 查询总数
Long count = userService.lambdaQuery()
    .eq(User::getStatus, 1)
    .count();
```

---

## 四、常用条件方法速查

| 方法 | SQL | 示例 |
|------|-----|------|
| `eq` | `= value` | `.eq(User::getStatus, 1)` |
| `ne` | `<> value` | `.ne(User::getStatus, 0)` |
| `gt / ge / lt / le` | `> / >= / < / <=` | `.ge(User::getAge, 18)` |
| `between` | `BETWEEN ? AND ?` | `.between(User::getAge, 18, 60)` |
| `notBetween` | `NOT BETWEEN` | `.notBetween(User::getAge, 0, 18)` |
| `like / notLike` | `LIKE / NOT LIKE '%?%'` | `.like(User::getName, "张")` |
| `likeLeft / likeRight` | `LIKE '%?' / '?%'` | `.likeRight(User::getPhone, "138")` |
| `in / notIn` | `IN (...) / NOT IN` | `.in(User::getStatus, 1, 2, 3)` |
| `isNull / isNotNull` | `IS NULL / IS NOT NULL` | `.isNull(User::getPhone)` |
| `orderByAsc / orderByDesc` | `ORDER BY` | `.orderByDesc(User::getCreateTime)` |
| `groupBy / having` | `GROUP BY / HAVING` | `.groupBy(User::getDeptId).having("COUNT(*) > 5")` |
| `select` | 指定查询列 | `.select(User::getId, User::getName)` |
| `last` | SQL 末尾拼接 | `.last("LIMIT 10")` ⚠️ 注入风险 |

---

## 五、5 个反例对比

### ❌/✅ 1:实体类没用 Lombok,Lambda 引用不到 getter

```java
// ❌ 手写 getter,但拼错了 getNmae
public class User {
    private String name;
    public String getNmae() { return name; }  // 拼错
}
wrapper.eq(User::getName, "Tom");  // 编译失败
```

```java
// ✅ 用 Lombok @Data 自动生成 getter
@Data
public class User {
    private String name;  // 自动生成 getName()
}
wrapper.eq(User::getName, "Tom");  // 编译通过
```

### ❌/✅ 2:`last()` 拼接用户输入,SQL 注入

```java
// ❌ 把 pageSize 直接拼到 last(),攻击者构造恶意输入
String pageSize = request.getPageSize();  // 用户可控
wrapper.last("LIMIT " + pageSize);
// 攻击输入:pageSize=1; DROP TABLE user; --
// 最终 SQL: SELECT * FROM user LIMIT 1; DROP TABLE user; --
```

```java
// ✅ 用 Page<T> 自带分页,不要拼 LIMIT
Page<User> page = new Page<>(1, 10);  // 第 1 页,每页 10
userMapper.selectPage(page, wrapper);
// 或对 pageSize 做强类型转换 + 范围校验
int safePageSize = Math.min(Math.max(parseInt(pageSize), 1), 100);
wrapper.last("LIMIT " + safePageSize);
```

### ❌/✅ 3:嵌套条件用 `.or()` 而非 `.or(w -> w...)`,括号丢失

```java
// ❌ 期望 (status=1 AND score>80),实际 OR 括号丢了
wrapper.like(User::getName, "张")
       .or()
       .eq(User::getStatus, 1)
       .gt(User::getScore, 80);
// SQL: WHERE name LIKE '%张%' OR status=1 AND score>80  ← AND 优先级高于 OR
```

```java
// ✅ 用 .or(w -> w...) 显式包裹
wrapper.like(User::getName, "张")
       .or(w -> w.eq(User::getStatus, 1).gt(User::getScore, 80));
// SQL: WHERE name LIKE '%张%' OR (status=1 AND score>80)
```

### ❌/✅ 4:Lambda 引用了非持久化字段

```java
// ❌ getFullName 是计算属性,MP 不知道,拼到 SQL 报错
@Data
public class User {
    private String firstName;
    private String lastName;
    public String getFullName() { return firstName + lastName; }
}
wrapper.eq(User::getFullName, "Tom");  // WHERE full_name='Tom' → 列不存在
```

```java
// ✅ 用 @TableField(exist = false) 标记非持久化字段
@Data
public class User {
    private String firstName;
    private String lastName;

    @TableField(exist = false)
    public String getFullName() { return firstName + lastName; }
}
// MP 遇到 exist=false 的字段会跳过,不会拼到 SQL
```

### ❌/✅ 5:动态查询没传 condition,条件永远生效

```java
// ❌ name 为 null 时,SQL 拼 WHERE name=null,导致无结果
String name = request.getName();  // null
wrapper.eq(name != null, User::getName, name);
// 实际仍拼接,只是值为 null → WHERE name = NULL(永远 false)
```

```java
// ✅ 用 StringUtils.isNotBlank 避免空字符串
wrapper.eq(StringUtils.isNotBlank(name), User::getName, name);
// name=null 或 name="" → 整个 eq 条件被跳过
```

---

## 六、3 大常见陷阱

### 陷阱 1:Lambda 引用要的是 getter,不是字段

```java
// MP 内部解析流程:
// 1. 编译期:User::getName 编译成 invokedynamic + LambdaMetafactory
// 2. 运行期:MP 通过反射调用 writeReplace() 得到 SerializedLambda
// 3. SerializedLambda.getImplMethodName() 返回 "getName"
// 4. 截取 "get" 后缀 → "Name"
// 5. 转下划线 → "name"
// 任何一步失败都会报错,所以:字段名必须与 getter 后缀严格对应
```

### 陷阱 2:`IService.lambdaUpdate()` 的 `.update()` 必须显式调用

```java
// ❌ 漏了 .update(),链式调用没有任何效果
userService.lambdaUpdate()
    .set(User::getStatus, 0)
    .eq(User::getId, 1L);  // 没有终止操作,SQL 不执行!
```

```java
// ✅ 链式调用必须以 .update() / .update(entity) / .remove() / .list() 等终止
userService.lambdaUpdate()
    .set(User::getStatus, 0)
    .eq(User::getId, 1L)
    .update();  // 终止操作,执行 UPDATE
```

### 陷阱 3:Lambda 引用了父类的 getter

```java
// ❌ User 继承 BaseEntity,getId() 来自父类
@Data
public class BaseEntity {
    private Long id;  // getter: getId()
}
@Data
@EqualsAndHashCode(callSuper = true)
public class User extends BaseEntity {
    private String name;
}
wrapper.eq(User::getId, 1L);  // MP 解析时优先找 User 自己的 getId → 找不到,报错
```

```java
// ✅ 用 BaseEntity::getId 显式引用父类 getter
wrapper.eq(BaseEntity::getId, 1L);
```

---

## 七、5 大反模式

1. **反模式 1:Lambda 引用计算属性且没加 `@TableField(exist = false)`** — MP 会把不存在的字段拼到 SQL 里;**必须**给计算属性加注解告诉框架。
2. **反模式 2:`last()` 拼接用户输入** — `last()` 直接拼 SQL,**SQL 注入高危**;动态 LIMIT 用 `Page<T>`,固定 LIMIT 才用 `.last("LIMIT 1")`。
3. **反模式 3:`IService.lambdaUpdate()` 漏 `.update()` 终止** — 链式调用是 fluent API,没终止就不执行;**容易在 IDE 重构时漏掉**。
4. **反模式 4:动态查询用 `param != null` 而非 `StringUtils.isNotBlank`** — 空字符串(`""`)也会被拼接 → `WHERE name=''`;**字符串字段必须用 isNotBlank**。
5. **反模式 5:Lambda 引用父类 getter** — MP 解析时按声明类找方法,继承场景找不到;**显式用 `Parent::getXxx`** 或在子类重写 getter。

---

## 八、30 秒话术

> **面试高频问法**:`LambdaQueryWrapper` 的底层原理?为什么 `User::getName` 能被框架解析?
>
> **回答模板**:`LambdaQueryWrapper` 通过方法引用(`User::getName`)替代字符串字段名,编译期类型安全、IDE 重构友好。**底层原理**:编译器把 `User::getName` 编译成 `invokedynamic` + `LambdaMetafactory`,生成一个匿名类;MP 在运行期通过 `writeReplace()` 拿到 `SerializedLambda`,从 `implMethodName` 字段提取 `"getName"`,截取 `"get"` 后缀 → `"Name"`,再按命名策略转下划线 → `"name"`。**整个过程不依赖字符串硬编码**,所以字段改名时编译期就会报错。

---

## 相关章节

- 上一步:[03-wrapper-system](./03-wrapper-system.md) — Wrapper 体系全貌
- 底层:[05-lambda-sfunction-deep-dive](./05-lambda-sfunction-deep-dive.md) — SFunction 序列化原理
- 实战:[09-best-practices](./09-best-practices.md) — Wrapper 使用建议

← [返回: MyBatis-Plus 总览](./README.md)
