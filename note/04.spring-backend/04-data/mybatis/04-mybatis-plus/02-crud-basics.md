<!--
module:
  parent: 04.spring-backend
  slug: 04.spring-backend\04-data\mybatis\04-mybatis-plus\02-crud-basics
  type: article
  category: MyBatis-Plus 实战
  summary: MyBatis-Plus CRUD 与条件构造器基础——BaseMapper 17 个方法 + Wrapper 常用 API 完整清单。
  depth: ⭐⭐⭐
-->

# 02 CRUD 与条件构造器基础

> 继承 `BaseMapper<T>` 后,**17 个 CRUD 方法开箱即用**,无需编写任何 XML 或实现类。本章列出每个方法签名、参数含义、返回类型,以及条件构造器(`QueryWrapper` / `UpdateWrapper`)的常用 API。

## 🎯 一句话定位

**`BaseMapper<T>` = 通用 CRUD 17 方法 + `Wrapper` = 动态 SQL 构造器**,两者结合覆盖单表 95% 增删改查场景,无需写一行 XML。

---

## 一、BaseMapper 完整方法清单

继承 `BaseMapper<T>` 后,Mapper 接口自动拥有 17 个方法。按操作分 4 类:

### 1.1 插入(1 个)

```java
public interface BaseMapper<T> {
    // 插入一条记录,自动回填主键到 entity
    int insert(T entity);
}
```

```java
// 示例:插入 User
User user = new User();
user.setName("Tom");
user.setAge(25);
int rows = userMapper.insert(user);  // rows = 1
// 主键回填:user.getId() 自动赋值(ASSIGN_ID 策略)
```

### 1.2 删除(4 个)

```java
// 根据 ID 删除(逻辑删除场景会转为 UPDATE)
int deleteById(Serializable id);

// 根据 columnMap 条件删除(等值匹配)
int deleteByMap(@Param(Constants.COLUMN_MAP) Map<String, Object> columnMap);

// 根据 Wrapper 条件删除
int delete(@Param(Constants.WRAPPER) Wrapper<T> wrapper);

// 批量删除 ID(3.5.4+ 支持)
int deleteBatchIds(@Param(Constants.COLLECTION) Collection<? extends Serializable> idList);
```

```java
// 示例 1:按 ID 删
userMapper.deleteById(1L);

// 示例 2:批量删
userMapper.deleteBatchIds(Arrays.asList(1L, 2L, 3L));

// 示例 3:条件删
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("status", 0).lt("create_time", LocalDateTime.now().minusYears(1));
userMapper.delete(wrapper);  // 删除 1 年前 status=0 的用户
```

### 1.3 更新(2 个)

```java
// 根据 ID 更新(entity 中非 null 字段)
int updateById(@Param(Constants.ENTITY) T entity);

// 根据 whereWrapper 更新(entity 可为 null,SET 内容通过 UpdateWrapper 指定)
int update(@Param(Constants.ENTITY) T entity,
           @Param(Constants.WRAPPER) Wrapper<T> updateWrapper);
```

```java
// 示例 1:按 ID 更新非空字段
User user = new User();
user.setId(1L);
user.setName("Jerry");
userMapper.updateById(user);  // UPDATE user SET name='Jerry' WHERE id=1

// 示例 2:批量条件更新
User user = new User();
user.setStatus(0);  // 全员禁用
userMapper.update(user, new QueryWrapper<User>().lt("age", 18));
// UPDATE user SET status=0 WHERE age < 18
```

### 1.4 查询(8 个)

```java
// 根据 ID 查
T selectById(Serializable id);

// 根据 ID 批量查
List<T> selectBatchIds(@Param(Constants.COLLECTION) Collection<? extends Serializable> idList);

// 根据 columnMap 等值查询
List<T> selectByMap(@Param(Constants.COLUMN_MAP) Map<String, Object> columnMap);

// 根据 Wrapper 查 1 条(多条会抛 TooManyResultsException)
T selectOne(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

// 查询记录数
Long selectCount(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

// 查询列表(可能返回大量数据,慎用)
List<T> selectList(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

// 查询列表(返回 Map 列表,字段名为 key)
List<Map<String, Object>> selectMaps(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

// 查询某列(配合 select() 指定单列)
List<Object> selectObjs(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);
```

```java
// 示例:查 status=1 的所有用户名
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.select("name").eq("status", 1);
List<Object> names = userMapper.selectObjs(wrapper);  // ["Tom", "Jerry", ...]
```

### 1.5 分页(1 个,需配合插件)

```java
// 分页查询(必须注册 PaginationInnerInterceptor)
<P extends IPage<T>> P selectPage(P page, @Param(Constants.WRAPPER) Wrapper<T> queryWrapper);
```

```java
Page<User> page = new Page<>(1, 10);  // 第 1 页,每页 10 条
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.ge("age", 18);
Page<User> result = userMapper.selectPage(page, wrapper);
result.getRecords();  // 当前页数据
result.getTotal();    // 总记录数:23
result.getPages();    // 总页数:3
```

### 1.6 IService 补充(可选)

```java
// 继承 IService<T> 额外获得批量操作 + 链式查询
public interface UserService extends IService<User> {
    // 批量插入(foreach 拼接,性能优于循环 insert)
    boolean saveBatch(Collection<User> entityList);

    // 链式查询(无需写 Mapper)
    User oneLambda = userService.lambdaQuery()
            .eq(User::getName, "Tom")
            .one();
}
```

> IService 详情见 [02-crud-basics 进阶](#) 与 [10-code-generator](./10-code-generator.md)。

---

## 二、Wrapper 常用 API(完整清单)

`QueryWrapper` / `UpdateWrapper` 继承自 `AbstractWrapper`,常用方法分 6 类:

### 2.1 比较运算(eq / ne / gt / ge / lt / le)

```java
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("name", "Tom")      // name = 'Tom'
      .ne("status", 0)         // AND status <> 0
      .gt("age", 18)           // AND age > 18
      .ge("create_time", startDate)  // AND create_time >= ?
      .lt("score", 100)        // AND score < 100
      .le("update_time", endDate);   // AND update_time <= ?
```

### 2.2 范围查询(between / notBetween)

```java
wrapper.between("age", 18, 60)        // age BETWEEN 18 AND 60
      .notBetween("score", 0, 60);    // score NOT BETWEEN 0 AND 60
```

### 2.3 模糊匹配(like / notLike / likeLeft / likeRight)

```java
wrapper.like("name", "张")          // name LIKE '%张%'
      .notLike("email", "spam")    // email NOT LIKE '%spam%'
      .likeLeft("name", "三")       // name LIKE '%三'
      .likeRight("name", "张");     // name LIKE '张%'
```

### 2.4 集合查询(in / notIn)

```java
wrapper.in("status", 1, 2, 3)              // status IN (1, 2, 3)
      .in("id", Arrays.asList(1L, 2L, 3L))  // 同上
      .notIn("type", "A", "B");             // type NOT IN ('A', 'B')
```

### 2.5 空值判断(isNull / isNotNull)

```java
wrapper.isNull("phone")      // phone IS NULL
      .isNotNull("email");   // email IS NOT NULL
```

### 2.6 排序 + 分组(orderBy / groupBy / having)

```java
// 排序
wrapper.orderByAsc("age")              // ORDER BY age ASC
      .orderByDesc("create_time")      // ORDER BY create_time DESC
      .orderBy(true, true, "age", "create_time");  // 多字段,第一个 true=生效

// 分组 + having
wrapper.select("dept_id, COUNT(*) cnt")
      .groupBy("dept_id")
      .having("COUNT(*) > {0}", 10);
```

### 2.7 条件拼接(condition,真则拼接)

```java
// 动态查询:condition=false 时,整个 eq 条件被跳过
String name = request.getName();  // 可能为 null
Integer minAge = request.getMinAge();

QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq(StringUtils.isNotBlank(name), "name", name)  // name 为空字符串时跳过
      .ge(minAge != null, "age", minAge)               // minAge 为 null 时跳过
      .orderByDesc("create_time");
```

### 2.8 SQL 片段拼接(last / apply / func)

```java
// 1. last:在 SQL 末尾拼接(注意 SQL 注入风险)
wrapper.last("LIMIT 1");

// 2. func:多分支拼接
wrapper.func(i -> {
    if (useCustomCondition) {
        i.eq("custom_col", 1);
    } else {
        i.eq("default_col", 0);
    }
});

// 3. 复杂 OR:用 and(w -> ...) / or(w -> ...) 实现括号包裹
wrapper.and(w -> w.eq("a", 1).or().eq("b", 2));  // AND (a = 1 OR b = 2)
```

---

## 三、5 个反例对比

### ❌/✅ 1:Wrapper 字段名拼错,运行时才发现

```java
// ❌ 字段名拼成"userName",运行时抛 SQL 异常
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("userName", "Tom");  // 字段不存在
```

```java
// ✅ 改用 LambdaQueryWrapper,编译期报错
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
wrapper.eq(User::getName, "Tom");  // getName 拼错会编译失败
```

### ❌/✅ 2:updateById 把 null 字段也更新了

```java
// ❌ 想更新 name,结果 age 被设为 null(因为 user.getAge() == null)
User user = new User();
user.setId(1L);
user.setName("NewName");
userMapper.updateById(user);
// 实际 SQL: UPDATE user SET name='NewName', age=null, ... WHERE id=1
```

```java
// ✅ 解决 1:用 UpdateWrapper 精确指定要更新的字段
LambdaUpdateWrapper<User> wrapper = new LambdaUpdateWrapper<>();
wrapper.set(User::getName, "NewName").eq(User::getId, 1L);
userMapper.update(null, wrapper);

// ✅ 解决 2:在实体类上加 @TableField(updateStrategy = FieldStrategy.NOT_NULL)
// age 字段为 null 时,MP 不会拼接到 UPDATE SET 中
```

### ❌/✅ 3:selectList(null) 误用导致 OOM

```java
// ❌ 传 null = 无条件查询,大表全表扫描 → OOM
List<User> allUsers = userMapper.selectList(null);
```

```java
// ✅ 必须有 WHERE 条件;或用分页 / 游标分页
Page<User> page = new Page<>(1, 100);
userMapper.selectPage(page, null);  // 限制单次最多 100 条
```

### ❌/✅ 4:逻辑删除字段没配 @TableLogic,DELETE 真删了

```java
// ❌ deleted 字段没加 @TableLogic,userMapper.deleteById() 执行真 DELETE
@Data
public class User {
    private Integer deleted;  // 业务字段,不会被识别为逻辑删除字段
}
userMapper.deleteById(1L);  // 真删,数据没了!
```

```java
// ✅ 加 @TableLogic,DELETE 自动转为 UPDATE ... SET deleted=1
@Data
public class User {
    @TableLogic
    private Integer deleted;  // 0-未删除 1-已删除
}
// 配置见 [07-auto-fill-and-logic-delete](./07-auto-fill-and-logic-delete.md)
```

### ❌/✅ 5:批量插入用循环 insert

```java
// ❌ 1000 条数据 = 1000 次 INSERT,每次都要走连接池获取连接
for (User user : userList) {
    userMapper.insert(user);
}
```

```java
// ✅ 用 IService.saveBatch(底层 foreach 拼接成 1 条 INSERT,默认 1000 条/批)
boolean ok = userService.saveBatch(userList);
// 或自定义批次大小
boolean ok = userService.saveBatch(userList, 500);
```

---

## 四、3 大常见陷阱

### 陷阱 1:`selectOne` 返回多条会抛异常

```java
// ❌ 查询条件命中多条 → 抛 TooManyResultsException
User user = userMapper.selectOne(
    new QueryWrapper<User>().eq("status", 1)
);

// ✅ 确定只有一条时用 selectOne;不确定用 selectList 然后取第一条
List<User> users = userMapper.selectList(
    new QueryWrapper<User>().eq("status", 1).last("LIMIT 1")
);
User user = users.isEmpty() ? null : users.get(0);
```

### 陷阱 2:`UpdateWrapper.set` 不会触发自动填充

```java
// ❌ 用 UpdateWrapper.set("update_time", now) 手动设置
UpdateWrapper<User> wrapper = new UpdateWrapper<>();
wrapper.set("update_time", LocalDateTime.now()).eq("id", 1L);

// ✅ 用 entity + Wrapper 方式,自动填充才会生效
User user = new User();
user.setUpdateTime(LocalDateTime.now());  // 自动填充兜底
UpdateWrapper<User> wrapper = new UpdateWrapper<User>().eq("id", 1L);
userMapper.update(user, wrapper);
```

### 陷阱 3:`columnMap` 的 key 必须是数据库字段名,不是实体类名

```java
// ❌ entity 字段名是 userName,columnMap 写 "userName" → 找不到列
Map<String, Object> map = new HashMap<>();
map.put("userName", "Tom");  // 实际数据库列是 user_name
userMapper.selectByMap(map);  // SQL: WHERE userName = 'Tom' → 报错

// ✅ columnMap 用数据库列名
map.put("user_name", "Tom");  // OK
```

---

## 五、5 大反模式

1. **反模式 1:把 Wrapper 当万能 SQL 构造器** — 多表 JOIN / 子查询 / 复杂统计仍写 XML;Wrapper 只适合**单表 + 中等条件**的场景,过度使用会导致代码可读性骤降。
2. **反模式 2:`selectList(null)` 无脑查全表** — 生产环境大表全表扫描必 OOM;任何列表查询**必须**带 WHERE 条件 + LIMIT/分页。
3. **反模式 3:`updateById(entity)` 默认更新所有非 null 字段** — entity 中某个字段恰好为 null 时会被 UPDATE 成 NULL;**必须**给字段加 `updateStrategy = FieldStrategy.NOT_NULL`,或用 UpdateWrapper 显式指定。
4. **反模式 4:`selectOne` 当 `selectList` 用** — 数据有重复时 `selectOne` 抛 `TooManyResultsException`;不确定唯一性时**永远用 selectList + isEmpty 判断**。
5. **反模式 5:批量插入用循环 `mapper.insert()`** — 1000 条数据 = 1000 次 SQL 往返;**必须**用 `IService.saveBatch()`,底层用 `<foreach>` 拼接成单条 SQL。

---

## 六、30 秒话术

> **面试高频问法**:`BaseMapper` 提供哪些方法?`IService` 和 `BaseMapper` 的区别?
>
> **回答模板**:`BaseMapper<T>` 提供 17 个 CRUD 方法(1 insert / 4 delete / 2 update / 8 select / 1 selectPage / 1 selectMaps 变体),**单表操作零 XML**。`IService<T>` 是 Service 层增强,提供 `saveBatch` / `lambdaQuery` / `lambdaUpdate` 等链式 API,适合**单表批处理 + 简单业务**。**复杂业务仍写 Service + Mapper + XML 三件套**;Wrapper 只负责动态 SQL 构造,不代表业务逻辑。

---

## 相关章节

- 上一步:[01-quickstart](./01-quickstart.md)
- 同主题:[03-wrapper-system](./03-wrapper-system.md) — Wrapper 体系全貌
- 同主题:[04-lambda-wrapper](./04-lambda-wrapper.md) — Lambda 构造器类型安全
- 实战:[09-best-practices](./09-best-practices.md) — 主键 / 乐观锁 / 多租户

← [返回: MyBatis-Plus 总览](./README.md)
