# 04 多数据源路由

> ⬅️ [返回 MyBatis 整合总览](README.md) | [⬅️ 03 @Transactional 与 MyBatis 事务边界](03-transaction-with-mybatis.md)

多数据源场景在 Spring + MyBatis 项目中非常常见（读写分离、业务分库、多租户）。MyBatis 比 JPA 简单的地方在于：每个数据源有自己的 `SqlSessionFactory` + `SqlSessionTemplate`，Mapper 通过包名区分数据源归属。

---

## 🎯 一句话定位

**MyBatis 多数据源 = 多个 `SqlSessionFactory` + 多个 `SqlSessionTemplate` + 包级 Mapper 隔离 + 动态场景用 `AbstractRoutingDataSource` 路由**——关键挑战在于事务管理：跨数据源需引入分布式事务方案。

---

## 一、场景与方案选型

### 1. 常见多数据源场景

| 场景 | 数据源特点 | 推荐方案 |
|------|-----------|---------|
| **读写分离** | 1 主 N 从 | `AbstractRoutingDataSource` + AOP |
| **业务分库** | 订单库 + 用户库 + 库存库 | 多个 `SqlSessionFactory` + 包隔离 |
| **多租户 SaaS** | 每租户独立数据库 | 动态 `SqlSessionFactory` + ThreadLocal |
| **数据迁移期** | 旧库 + 新库并存 | `AbstractRoutingDataSource` |
| **分库分表** | ShardingSphere / MyCat 接管 | 不在本章范围 |

### 2. 方案对比

| 方案 | 一致性 | 复杂度 | 性能 | 适用 |
|------|:------:|:------:|:----:|------|
| **包级 Mapper 隔离** | 单数据源内一致 | 低 | 高 | 业务分库 |
| **`AbstractRoutingDataSource` + AOP** | 单数据源内一致 | 中 | 高 | 读写分离、多租户 |
| **JTA + Atomikos（XA）** | **跨数据源强一致** | 高 | 低 | 金融核心 |
| **Seata AT/TCC** | 最终一致 | 中 | 高 | 微服务跨库 |
| **本地消息表** | 最终一致 | 中 | 高 | 异步解耦 |

---

## 二、方案一：包级 Mapper 隔离（最简单）

> 每个数据源对应独立的 Mapper 包 + 独立的 SqlSessionFactory。

### 1. 项目结构

```
src/main/java/com/example/
├── mapper/
│   ├── order/         # 订单库 Mapper
│   │   ├── OrderMapper.java
│   │   └── OrderItemMapper.java
│   └── user/          # 用户库 Mapper
│       ├── UserMapper.java
│       └── UserProfileMapper.java
├── config/
│   ├── OrderDataSourceConfig.java
│   └── UserDataSourceConfig.java
```

### 2. 订单数据源配置

```java
@Configuration
@MapperScan(
    basePackages = "com.example.mapper.order",  // 扫描订单 Mapper
    sqlSessionTemplateRef = "orderSqlSessionTemplate"
)
public class OrderDataSourceConfig {

    @Bean
    @ConfigurationProperties("spring.datasource.order")
    public DataSource orderDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    public SqlSessionFactory orderSqlSessionFactory(
            @Qualifier("orderDataSource") DataSource dataSource) throws Exception {
        SqlSessionFactoryBean factory = new SqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        factory.setMapperLocations(
            new PathMatchingResourcePatternResolver()
                .getResources("classpath:mapper/order/**/*.xml"));
        return factory.getObject();
    }

    @Bean
    public SqlSessionTemplate orderSqlSessionTemplate(
            @Qualifier("orderSqlSessionFactory") SqlSessionFactory sqlSessionFactory) {
        return new SqlSessionTemplate(sqlSessionFactory);
    }

    @Bean
    public PlatformTransactionManager orderTransactionManager(
            @Qualifier("orderDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

### 3. 用户数据源配置

```java
@Configuration
@MapperScan(
    basePackages = "com.example.mapper.user",
    sqlSessionTemplateRef = "userSqlSessionTemplate"
)
public class UserDataSourceConfig {

    @Bean
    @ConfigurationProperties("spring.datasource.user")
    public DataSource userDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    public SqlSessionFactory userSqlSessionFactory(
            @Qualifier("userDataSource") DataSource dataSource) throws Exception {
        SqlSessionFactoryBean factory = new SqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        factory.setMapperLocations(
            new PathMatchingResourcePatternResolver()
                .getResources("classpath:mapper/user/**/*.xml"));
        return factory.getObject();
    }

    @Bean
    public SqlSessionTemplate userSqlSessionTemplate(
            @Qualifier("userSqlSessionFactory") SqlSessionFactory sqlSessionFactory) {
        return new SqlSessionTemplate(sqlSessionFactory);
    }

    @Bean
    public PlatformTransactionManager userTransactionManager(
            @Qualifier("userDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

### 4. `application.yml`

```yaml
spring:
  datasource:
    order:
      jdbc-url: jdbc:mysql://localhost:3306/order_db
      username: root
      password: root
      driver-class-name: com.mysql.cj.jdbc.Driver
    user:
      jdbc-url: jdbc:mysql://localhost:3306/user_db
      username: root
      password: root
      driver-class-name: com.mysql.cj.jdbc.Driver
```

### 5. 业务使用

```java
@Service
public class OrderService {

    @Autowired private OrderMapper orderMapper;       // 订单库 Mapper
    @Autowired private UserMapper userMapper;         // 用户库 Mapper

    // 订单库事务
    @Transactional(transactionManager = "orderTransactionManager")
    public void createOrder(Order order) {
        orderMapper.insert(order);  // 走订单库
    }

    // 用户库事务
    @Transactional(transactionManager = "userTransactionManager")
    public void updateUser(User user) {
        userMapper.update(user);    // 走用户库
    }

    // ❌ 跨数据源事务（两库同时更新，普通 @Transactional 无法保证一致性）
    @Transactional  // 默认 orderTransactionManager，无法管理 user 库
    public void createOrderAndUpdateUser(Order order, User user) {
        orderMapper.insert(order);
        userMapper.update(user);  // 订单库事务回滚时，用户库无法回滚
    }
}
```

**问题**：跨数据源事务需引入 JTA 或 Seata（见 [transaction/multi-datasource-and-jta.md](../transaction/multi-datasource-and-jta.md)）。

---

## 三、方案二：AbstractRoutingDataSource 动态路由

> 同一组 Mapper，根据运行时上下文动态决定走哪个数据源（典型场景：读写分离、多租户）。

### 1. 核心架构

```mermaid
graph TB
    App[业务代码] --> Router[DynamicDataSource<br/>extends AbstractRoutingDataSource]
    Router --> Master[masterDataSource<br/>主库]
    Router --> Slave1[slaveDataSource<br/>从库1]
    Router --> Slave2[slaveDataSource<br/>从库2]
    
    Holder[DataSourceContextHolder<br/>ThreadLocal] -.提供key.-> Router
    
    AOP[DataSourceAOP<br/>@DS annotation] -.设置key.-> Holder
    
    style Router fill:#fff3e0,stroke:#f57c00
```

### 2. 路由键 + ThreadLocal

```java
public class DataSourceContextHolder {
    private static final ThreadLocal<String> CONTEXT = new ThreadLocal<>();

    public static void set(String ds) { CONTEXT.set(ds); }
    public static String get() { return CONTEXT.get(); }
    public static void clear() { CONTEXT.remove(); }
}
```

### 3. 自定义路由 DataSource

```java
public class DynamicDataSource extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContextHolder.get();
    }
}
```

### 4. 主数据源配置（默认）

```java
@Configuration
public class DataSourceConfig {

    @Bean
    @ConfigurationProperties("spring.datasource.master")
    public DataSource masterDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.slave")
    public DataSource slaveDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @Primary  // 关键：标记为主数据源，否则 MyBatis 注入会失败
    public DataSource dynamicDataSource(
            @Qualifier("masterDataSource") DataSource master,
            @Qualifier("slaveDataSource") DataSource slave) {
        Map<Object, Object> targetDataSources = new HashMap<>();
        targetDataSources.put("master", master);
        targetDataSources.put("slave", slave);

        DynamicDataSource ds = new DynamicDataSource();
        ds.setTargetDataSources(targetDataSources);
        ds.setDefaultTargetDataSource(master);  // 默认走主库
        return ds;
    }
}
```

### 5. MyBatis 配置（共用一个 SqlSessionFactory）

```java
@Configuration
@MapperScan("com.example.mapper")
public class MyBatisConfig {

    @Bean
    public SqlSessionFactory sqlSessionFactory(
            @Qualifier("dynamicDataSource") DataSource dataSource) throws Exception {
        SqlSessionFactoryBean factory = new SqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        factory.setMapperLocations(
            new PathMatchingResourcePatternResolver()
                .getResources("classpath:mapper/**/*.xml"));
        return factory.getObject();
    }

    @Bean
    public PlatformTransactionManager transactionManager(
            @Qualifier("dynamicDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

### 6. `@DS` 注解 + AOP

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface DS {
    String value() default "master";  // 默认主库
}
```

```java
@Aspect
@Component
@Order(0)  // 优先级高于事务切面（事务切面通常 -1）
public class DataSourceAspect {

    @Before("@annotation(ds)")
    public void before(JoinPoint point, DS ds) {
        DataSourceContextHolder.set(ds.value());
    }

    @After("@annotation(ds)")
    public void after(JoinPoint point, DS ds) {
        DataSourceContextHolder.clear();
    }
}
```

### 7. 业务使用

```java
@Service
public class UserService {

    @Autowired private UserMapper userMapper;

    // 默认走主库
    @Transactional
    public void createUser(User user) {
        userMapper.insert(user);  // master
    }

    // 显式指定从库（读操作）
    @DS("slave")
    public User getUser(Long id) {
        return userMapper.selectById(id);  // slave
    }

    // 同方法内动态切换（需注意 AOP 切面顺序）
    public List<User> complexQuery() {
        User newUser = new User();
        createUser(newUser);  // master

        DataSourceContextHolder.set("slave");
        try {
            return userMapper.selectById(newUser.getId());  // slave
        } finally {
            DataSourceContextHolder.clear();
        }
    }
}
```

---

## 四、读写分离进阶

### 1. 基于 SQL 类型的自动路由

```java
@Aspect
@Component
@Order(0)
public class ReadWriteRoutingAspect {

    @Before("execution(* com.example.mapper.*.*(..))")
    public void before(JoinPoint point) {
        String methodName = point.getSignature().getName();
        // 约定：以 select/get/list/count 开头走从库，其他走主库
        if (methodName.startsWith("select") || methodName.startsWith("get")
                || methodName.startsWith("list") || methodName.startsWith("count")) {
            DataSourceContextHolder.set("slave");
        } else {
            DataSourceContextHolder.set("master");
        }
    }

    @After("execution(* com.example.mapper.*.*(..))")
    public void after(JoinPoint point) {
        DataSourceContextHolder.clear();
    }
}
```

**注意**：这种约定式路由易踩坑（`selectCount` 内部调用了写操作就会路由到从库）。

### 2. MyBatis-Plus 的 `DynamicDataSource` + `@DS`

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>dynamic-datasource-spring-boot-starter</artifactId>
</dependency>
```

```yaml
spring:
  datasource:
    dynamic:
      primary: master
      datasource:
        master:
          url: jdbc:mysql://localhost:3306/master
          username: root
          password: root
        slave_1:
          url: jdbc:mysql://localhost:3306/slave_1
          username: root
          password: root
        slave_2:
          url: jdbc:mysql://localhost:3306/slave_2
          username: root
          password: root
```

```java
@Service
public class OrderService {

    @DS("master")
    public void createOrder(Order order) {
        orderMapper.insert(order);
    }

    @DS("slave_1")
    public List<Order> listOrders() {
        return orderMapper.selectList(null);
    }
}
```

**优点**：开源方案成熟，支持负载均衡、加密、多租户等高级特性。

---

## 五、多数据源事务衔接

### 1. 本地事务（不保证跨库一致性）

```java
// 订单库事务管理器
@Bean("orderTxManager")
public PlatformTransactionManager orderTxManager(
        @Qualifier("orderDataSource") DataSource ds) {
    return new DataSourceTransactionManager(ds);
}

// 用户库事务管理器
@Bean("userTxManager")
public PlatformTransactionManager userTxManager(
        @Qualifier("userDataSource") DataSource ds) {
    return new DataSourceTransactionManager(ds);
}

@Service
public class CrossDBService {

    @Autowired private OrderMapper orderMapper;
    @Autowired private UserMapper userMapper;

    // ❌ 分布式问题：两个事务管理器无法协同
    @Transactional(transactionManager = "orderTxManager")
    public void crossOperation(Order order, User user) {
        orderMapper.insert(order);
        userMapper.update(user);  // 没有事务
    }
}
```

### 2. JTA + Atomikos（强一致）

```java
@Bean
public AtomikosDataSourceBean orderDataSource() {
    // 配置 XA 数据源
}

@Bean
public JtaTransactionManager transactionManager() {
    return new JtaTransactionManager();
}
```

**缺点**：性能差（两阶段提交）、SQL 限制（不支持某些 DDL）、运维复杂。

### 3. Seata（最终一致，推荐）

```xml
<dependency>
    <groupId>io.seata</groupId>
    <artifactId>seata-spring-boot-starter</artifactId>
</dependency>
```

```java
@GlobalTransactional  // Seata 全局事务
public void crossOperation(Order order, User user) {
    orderMapper.insert(order);   // 订单库本地事务（Seata AT 模式自动接管）
    userMapper.update(user);     // 用户库本地事务
}
```

详见 [transaction/distributed/seata.md](../transaction/distributed/seata.md)。

### 4. 本地消息表（最终一致，无中间件）

```java
@Transactional(transactionManager = "orderTxManager")
public void createOrderWithNotify(Order order, User user) {
    orderMapper.insert(order);

    // 在订单库插入消息记录（保证与订单同时提交）
    messageMapper.insert(new LocalMessage(
        "UPDATE_USER", user.getId(), user, LocalDateTime.now()
    ));
}

// 定时任务扫描消息表，发送到 MQ 或调用用户库
```

详见 [transaction/distributed/theory-and-patterns.md](../transaction/distributed/theory-and-patterns.md)。

---

## 六、踩坑与最佳实践

### 1. AOP 切面顺序

```java
// ✅ 数据源切面必须在事务切面之前
@Aspect @Component @Order(0)
public class DataSourceAspect { ... }

@Aspect @Component @Order(1)  // Spring 事务切面默认 Integer.MAX_VALUE
public class TransactionAspect { ... }
```

### 2. 跨方法调用的数据源传递

```java
@Service
public class UserService {

    @DS("slave")
    public User getUser(Long id) {
        return userMapper.selectById(id);
    }

    public List<User> batchGet(List<Long> ids) {
        // ❌ 内部调用不经过 AOP
        return ids.stream().map(this::getUser).collect(toList());
    }
}
```

**解决**：注入自己的代理 `@Autowired private UserService self;`。

### 3. 线程池场景

```java
@DS("slave")
public CompletableFuture<List<User>> asyncBatchGet(List<Long> ids) {
    return CompletableFuture.supplyAsync(() -> {
        // ❌ 异步线程拿不到主线程的 DataSourceContextHolder
        return userMapper.selectBatchIds(ids);
    });
}
```

**解决**：在异步线程内部重新设置数据源，或继承 ThreadLocal（`InheritableThreadLocal` 也不能解决线程池复用问题）。

### 4. `@Transactional` 失效检查清单

| 检查项 | 说明 |
|--------|------|
| 数据源切面先于事务切面？ | AOP 顺序是否正确 |
| `@DS` 注解的方法是否被内部调用？ | 应通过代理调用 |
| `DataSourceContextHolder.clear()` 是否遗漏？ | 可能导致 ThreadLocal 内存泄漏 |
| 多线程是否传递了 ThreadLocal？ | 线程池需手动设置 |

---

## 相关章节

- ⬅️ [返回 MyBatis 整合总览](README.md)
- ⬅️ [03 @Transactional 与 MyBatis 事务边界](03-transaction-with-mybatis.md)
- ➡️ [05 二级缓存与 Redis/Caffeine 整合](05-secondary-cache-integration.md)
- [transaction/multi-datasource-and-jta.md](../transaction/multi-datasource-and-jta.md) — 多数据源事务
- [transaction/distributed/seata.md](../transaction/distributed/seata.md) — Seata 分布式事务
- [08.mybatis/mybatis-plus/README.md](../../08.mybatis/mybatis-plus/README.md) — MyBatis-Plus 动态数据源