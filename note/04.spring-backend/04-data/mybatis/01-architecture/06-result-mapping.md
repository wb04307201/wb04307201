<!--
module:
  parent: spring/mybatis/01-architecture
  slug: spring/mybatis/01-architecture/06-result-mapping
  type: topic
  category: MyBatis 内部原理
  summary: 一对一 association / 一对多 collection 关联映射的配置与用法
  depth: ⭐⭐⭐
-->

# 06 Result Mapping 结果映射

> 来源:整合自原 08.mybatis/README.md § 四.4.2
>
> 🎯 一句话定位：resultMap 解决数据库列名与 Java 属性名不匹配，以及一对一 association / 一对多 collection 的关联映射。

### 4.2 关联映射
#### 4.2.1 一对一关联
```xml
<!-- 用户与详细信息 -->
<resultMap id="userWithDetail" type="User">
    <id property="id" column="user_id"/>
    <association property="detail" javaType="UserDetail">
        <id property="id" column="detail_id"/>
        <result property="address" column="address"/>
    </association>
</resultMap>
```

#### 4.2.2 一对多关联
```xml
<!-- 用户与订单 -->
<resultMap id="userWithOrders" type="User">
    <id property="id" column="user_id"/>
    <collection property="orders" ofType="Order">
        <id property="id" column="order_id"/>
        <result property="amount" column="amount"/>
    </collection>
</resultMap>
```

## 1. 基础字段映射

### 1.1 `<id>` 与 `<result>` 的区别

`<id>` 和 `<result>` 结构相同（都是 `property / column` 映射），区别仅在**语义和缓存策略**：

| 子元素 | 用途 | 缓存 key |
|--------|------|---------|
| `<id>` | 主键字段（必须出现一次,作为对象的唯一标识） | 参与缓存 key 计算 |
| `<result>` | 普通字段 | 不参与缓存 key |

```xml
<resultMap id="userMap" type="User">
    <id property="id" column="user_id"/>            <!-- 主键 -->
    <result property="userName" column="user_name"/><!-- 普通字段 -->
    <result property="createTime" column="gmt_create"/>
</resultMap>
```

**为什么 `<id>` 必须出现**：MyBatis 二级缓存以 `[MappedStatement namespace + id + offset + limit + SQL + 参数值 + rowBounds]` 作为 CacheKey,但**对象去重**依赖 `<id>` 标识同一对象。如果不写 `<id>`,同一行记录在不同 rowBounds 下可能产生重复对象。

### 1.2 `autoMapping` 驼峰自动映射

```xml
<!-- 显式开启自动映射（默认 true） -->
<resultMap id="userMap" type="User" autoMapping="true">
    <id property="id" column="id"/>
    <!-- 其余字段（user_name → userName / gmt_create → gmtCreate）无需手动声明 -->
</resultMap>
```

开启 `autoMapping=true` 后,MyBatis 按以下规则匹配：
- `user_name` → `userName`（下划线转驼峰,需 `mapUnderscoreToCamelCase=true`）
- 严格大小写不敏感
- 类型转换（`ResultSet.getObject(col)` → setter）

### 1.3 `mapUnderscoreToCamelCase` 全局开关

```xml
<settings>
    <!-- 全局开启下划线转驼峰,无需每个 resultMap 都写 -->
    <setting name="mapUnderscoreToCamelCase" value="true"/>
</settings>
```

> ⚠️ 字段名含连续大写时（如 `userID` → 数据库 `user_id`）,驼峰规则默认转成 `userId`,Java 字段也必须命名为 `userId`,不能叫 `userID`。

## 2. 一对一 `<association>`

`<association>` 表示"属于"语义（Has-A），有**两种加载策略**：

### 2.1 嵌套 select（分步查询,多 SQL）

```xml
<resultMap id="userWithDetailStep" type="User">
    <id property="id" column="id"/>
    <result property="userName" column="user_name"/>
    <!-- 嵌套 select:另一个 statement 的 id -->
    <association property="detail"
                 select="com.example.mapper.UserDetailMapper.findByUserId"
                 column="id"/>
</resultMap>

<!-- UserDetailMapper.xml -->
<select id="findByUserId" resultType="UserDetail">
    SELECT * FROM user_detail WHERE user_id = #{id}
</select>
```

执行流程：
```
1. 主查询:SELECT * FROM user  → 拿到 N 个 User
2. 对每个 User,执行 1 次 SELECT * FROM user_detail WHERE user_id = #{id}
3. 共 N+1 次 SQL（这就是著名的 N+1 问题）
```

### 2.2 嵌套 resultMap（join 查询,单 SQL）

```xml
<resultMap id="userWithDetailJoin" type="User">
    <id property="id" column="user_id"/>
    <result property="userName" column="user_name"/>
    <association property="detail" javaType="UserDetail">
        <id property="id" column="detail_id"/>
        <result property="address" column="detail_address"/>
        <result property="phone" column="detail_phone"/>
    </association>
</resultMap>

<select id="findUserJoin" resultMap="userWithDetailJoin">
    SELECT
        u.id AS user_id, u.user_name,
        d.id AS detail_id, d.address AS detail_address, d.phone AS detail_phone
    FROM user u
    LEFT JOIN user_detail d ON u.id = d.user_id
    WHERE u.id = #{id}
</select>
```

执行流程：
```
1. 单次 JOIN 查询,数据库返回扁平行集
2. MyBatis 按 <id> 分组去重,把同一 user 的 detail 列映射到 detail 属性
3. 共 1 次 SQL
```

### 2.3 嵌套查询的 N+1 问题

```java
// Service 层伪代码：看似"取出所有用户"
List<User> users = userMapper.selectAll(); // 1 次 SQL
// users.get(0).getDetail() 触发第 2 次 SQL
// users.get(1).getDetail() 触发第 3 次 SQL
// ...
// users.get(N-1).getDetail() 触发第 N+1 次 SQL
```

**症状**：列表页展示 N 条用户,每条访问关联对象,SQL 数 1+N,数据库连接池爆满。

**优化方案**：
1. 改用嵌套 resultMap JOIN 查询（见 §2.2）
2. 开启批量懒加载（`lazyLoadingEnabled=true` + 手动控制访问时机）
3. 在 Service 层用 `@Batch` 或 IN 查询一次性取回所有 detail,然后手动装配

## 3. 一对多 `<collection>`

`<collection>` 表示"包含"语义（Has-Many）。

### 3.1 `ofType` 指定集合元素类型

```xml
<resultMap id="userWithOrders" type="User">
    <id property="id" column="user_id"/>
    <collection property="orders" ofType="Order">  <!-- ofType 必须是元素类型,不是 List -->
        <id property="id" column="order_id"/>
        <result property="amount" column="order_amount"/>
    </collection>
</resultMap>

<select id="findUserOrders" resultMap="userWithOrders">
    SELECT
        u.id AS user_id,
        o.id AS order_id, o.amount AS order_amount
    FROM user u
    LEFT JOIN `order` o ON u.id = o.user_id
    WHERE u.id = #{id}
</select>
```

| 元素 | 含义 | 类型 |
|------|------|------|
| `property` | Java 类的集合属性名 | `List<Order>` |
| `ofType` | 集合元素类型 | `Order.class` |
| `javaType`（可选） | 集合类型,默认 `ArrayList` | `List.class` |

### 3.2 分步查询 vs JOIN 查询对比

```xml
<!-- 分步:association 用 select 属性 -->
<collection property="orders"
            select="com.example.mapper.OrderMapper.findByUserId"
            column="id"/>
<!-- 单查 user → 触发 N 次 order 查询（N+1） -->

<!-- JOIN:association 用嵌套 resultMap -->
<collection property="orders" ofType="Order">
    <id property="id" column="order_id"/>
    ...
</collection>
<!-- 单次 LEFT JOIN,扁平行集由 MyBatis 自动按 <id> 分组 -->
```

| 方式 | SQL 数 | 数据量 | 适用场景 |
|------|--------|--------|---------|
| 嵌套 resultMap JOIN | 1 | 笛卡尔膨胀（user × orders） | 关联表小、列表短 |
| 嵌套 select | 1+N | 主表全量 + 按需查关联 | 关联表大、订单数多 |
| 延迟加载 | 1+按需 | 触发访问时才查 | 字段大或需要按页签加载 |

> 💡 **JOIN 的性能陷阱**：当用户表 1000 行,每个用户平均 50 个订单,JOIN 后返回 50000 行,网络传输和 ResultSet 解析都是负担。**这时反而是嵌套 select + 延迟加载更快**。

## 4. 鉴别器 `<discriminator>`

`<discriminator>` 根据某列的值切换 resultType,适用于**多态查询**（同表存不同类型）。

```xml
<!-- 车辆表:同一张表存汽车、摩托车、自行车,字段不同 -->
<resultMap id="vehicleMap" type="Vehicle">
    <id property="id" column="id"/>
    <result property="type" column="type"/>
    <!-- 根据 type 列值切换 resultMap -->
    <discriminator javaType="string" column="type">
        <case value="CAR" resultMap="carMap"/>
        <case value="MOTORCYCLE" resultMap="motorcycleMap"/>
        <case value="BICYCLE" resultMap="bicycleMap"/>
    </discriminator>
</resultMap>

<resultMap id="carMap" type="Car" extends="vehicleMap">
    <result property="doorCount" column="door_count"/>
    <result property="engineSize" column="engine_size"/>
</resultMap>

<resultMap id="motorcycleMap" type="Motorcycle" extends="vehicleMap">
    <result property="hasSidecar" column="has_sidecar"/>
</resultMap>

<resultMap id="bicycleMap" type="Bicycle" extends="vehicleMap">
    <result property="gears" column="gears"/>
</resultMap>
```

**工作原理**：MyBatis 在构造结果对象时,根据 `type` 列的值选择对应 resultMap,后续字段按该 resultMap 映射。

> ⚠️ 实际开发中,多态查询建议**按类型拆表**或**用单表继承 + JSON 字段**,discriminator 适合传统遗留系统改造。

## 5. 延迟加载

### 5.1 全局开关

```xml
<settings>
    <!-- 开启延迟加载（默认 false）-->
    <setting name="lazyLoadingEnabled" value="true"/>
    <!-- 3.x 已移除 aggressiveLazyLoading,4.x 仍存在 -->
    <!-- 任意属性访问即触发加载 -->
    <setting name="aggressiveLazyLoading" value="false"/>
</settings>
```

| 配置 | 行为 |
|------|------|
| `lazyLoadingEnabled=false`（默认） | 关联对象在主查询时立即加载 |
| `lazyLoadingEnabled=true` + `aggressiveLazyLoading=false` | 调用任意 getter 时按需触发加载 |
| `lazyLoadingEnabled=true` + `aggressiveLazyLoading=true`（MyBatis 3） | 任意属性访问即递归加载所有懒加载属性 |

### 5.2 `fetchType` 单个关联覆盖

```xml
<!-- 全局懒加载,但这一个 association 强制立即加载 -->
<resultMap id="userMap" type="User">
    <id property="id" column="id"/>
    <!-- 强制立即加载,不受 lazyLoadingEnabled 影响 -->
    <association property="detail"
                 fetchType="eager"
                 select="..."/>
    <!-- 这个仍走全局懒加载 -->
    <collection property="orders"
                fetchType="lazy"
                select="..."/>
</resultMap>
```

`fetchType` 取值：`eager`（立即）/ `lazy`（延迟）。**优先级高于全局配置**,用于"关键关联用即时、非关键关联延迟"的混合策略。

### 5.3 触发代理调用的常见 pattern

MyBatis 延迟加载依赖 **Javassist / CGLIB 代理**,代理对象在 getter 被调用时才触发 SQL：

```java
// 真实场景：return null 时也触发
public UserDetail getDetail() {
    if (this.detail == null) {
        // 代理拦截:触发 SQL 查询,赋值给 this.detail
        return this.detail; // 第二次进入时不再触发（已被填充）
    }
    return this.detail;
}
```

```java
// Service 层使用延迟加载的注意点
User user = userMapper.findById(1L);              // SQL 1
System.out.println(user.getUserName());           // 不触发 SQL
UserDetail detail = userMapper.getDetail(user);   // SQL 2 (懒加载触发)
```

**避坑**：
- 必须在**同一个 SqlSession** 内触发懒加载,否则 `SqlSession closed` 报错
- 用 `try-with-resources` 管理 SqlSession 时,关闭后访问延迟属性会爆 `LazyInitializationException`
- 解决方案：① Service 层 @Transactional 内完成所有 getter 调用 ② 用 `openSession(ExecutorType.SIMPLE, false)` 延长会话 ③ 改用 JOIN 一次性加载

## 6. 实战对比

### 6.1 ❌ Service 层 for 循环查询（N+1 反模式）

```java
// ❌ 反模式:Service 层循环查关联
public List<UserVO> listUsers() {
    List<User> users = userMapper.selectAll();
    List<UserVO> vos = new ArrayList<>();
    for (User u : users) {
        UserVO vo = new UserVO();
        BeanUtils.copyProperties(u, vo);
        // 每个用户都查一次详情 + 一次订单
        vo.setDetail(userDetailMapper.findByUserId(u.getId())); // SQL N
        vo.setOrders(orderMapper.findByUserId(u.getId()));      // SQL N
        vos.add(vo);
    }
    return vos;
}
// 100 个用户 = 201 次 SQL（1 + 100 + 100）
```

### 6.2 ✅ 一次 JOIN 查询或 @Batch 批量查

```java
// ✅ 方案一:JOIN 一次性取出
@Select("""
    SELECT u.id, u.user_name, d.address, o.amount
    FROM user u
    LEFT JOIN user_detail d ON u.id = d.user_id
    LEFT JOIN `order` o ON u.id = o.user_id
    WHERE u.status = 'ACTIVE'
""")
@ResultMap("userVOMap")  // 用 resultMap 做映射
List<UserVO> listUsersVO();

// ✅ 方案二:批量查询 + 内存装配
public List<UserVO> listUsersVOBatch() {
    List<User> users = userMapper.selectAll();
    List<Long> userIds = users.stream().map(User::getId).collect(Collectors.toList());
    
    // 一次 IN 查询拿全部 detail
    Map<Long, UserDetail> detailMap = userDetailMapper.findByUserIds(userIds)
        .stream().collect(Collectors.toMap(UserDetail::getUserId, d -> d));
    
    // 一次 IN 查询拿全部 order,再按 userId 分组
    Map<Long, List<Order>> orderMap = orderMapper.findByUserIds(userIds)
        .stream().collect(Collectors.groupingBy(Order::getUserId));
    
    return users.stream().map(u -> {
        UserVO vo = new UserVO();
        BeanUtils.copyProperties(u, vo);
        vo.setDetail(detailMap.get(u.getId()));
        vo.setOrders(orderMap.getOrDefault(u.getId(), Collections.emptyList()));
        return vo;
    }).collect(Collectors.toList());
}
// 100 个用户 = 3 次 SQL（user + detail + order）
```

## 7. 性能对比表

| 方式 | SQL 数 | 适用场景 | 优点 | 缺点 |
|------|--------|---------|------|------|
| **嵌套 resultMap JOIN** | 1 | 数据量小、关联不深（如字典表）、列表短 | 单 SQL 性能可控、避免 N+1 | 笛卡尔膨胀、大表 JOIN 慢 |
| **嵌套 select** | 1+N | 关联大、需按需加载、Service 层需要分别调用 | 单次主查询快 | 典型 N+1,延迟加载可缓解 |
| **延迟加载** | 1+按需 | 大字段（LONGVARCHAR/LOB）、关联表极大 | 按需触发、节省带宽 | 同 SqlSession 限制、调试困难 |
| **批量 IN 查询 + 内存装配** | 3（固定） | 列表分页 + 多关联表 | SQL 数恒定、不受列表长度影响 | 需手写 Service 装配代码 |
| **`@One`/`@Many`（注解式）** | 同 XML | 简单关联 | 注解简洁 | 复杂嵌套场景不直观 |

### 选型决策树

```
1. 是否单条记录查询?
   ├─ 是 → 嵌套 select（一次主查 + 一次关联,共 2 SQL）
   └─ 否（列表）
      ├─ 关联表 < 100 行?
      │   └─ 是 → 嵌套 resultMap JOIN
      └─ 否 → 批量 IN 查询 + 内存装配（或延迟加载 + 控制访问时机）
```

> 📌 **黄金法则**：能 1 次 SQL 解决的绝不 2 次,能固定 SQL 数的绝不 N+1。能用 JOIN 的不偷懒用延迟加载,延迟加载是最后手段而非首选。

---

## 系列导航

- 上一篇：[`05 动态 SQL`](05-dynamic-sql.md) — BoundSql 生成的上游规则
- 下一篇：[`07 缓存机制`](07-cache-mechanism.md) — 一级 / 二级缓存与结果映射的关系

← [返回: 01-architecture](README.md)
