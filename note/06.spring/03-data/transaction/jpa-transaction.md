# JPA 事务管理

> 最后更新: 2026-06-14
> ⬅️ [返回事务总览](README.md) | [编程式事务](programmatic-transaction.md)

JPA（Java Persistence API）通过 `JpaTransactionManager` 集成 Spring 事务，支持声明式 `@Transactional`、`@Lock` 悲观锁、`@Version` 乐观锁。本文详解 JPA 与 Spring 事务的协作机制。

---

## 🎯 一句话定位

**JPA 事务 = `JpaTransactionManager` + `@Transactional` + Repository 自动事务**——Repository 方法默认自带事务；业务层加 `@Transactional` 即可管理 EntityManager 生命周期；`@Lock` / `@Version` 解决并发写问题。

---

## 一、JPA 与 Spring 事务的关系

### 1. `JpaTransactionManager`

```java
@Configuration
@EnableTransactionManagement
public class JpaConfig {

    @Bean
    public PlatformTransactionManager transactionManager(EntityManagerFactory emf) {
        return new JpaTransactionManager(emf);
    }
}
```

| 特性 | 说明 |
|------|------|
| **管理 EntityManager** | 每个事务绑定独立的 `EntityManager`（线程安全） |
| **支持传播行为** | 完整支持 7 种 `Propagation` |
| **支持隔离级别** | 完整支持 4 种 `Isolation` |
| **事务边界** | EntityManager 在 `@Transactional` 方法结束后自动 close |

### 2. Repository 自带事务

> Spring Data JPA 的 `SimpleJpaRepository` 默认所有方法都加了 `@Transactional`。

```java
public class SimpleJpaRepository<T, ID> implements JpaRepository<T, ID> {

    @Transactional  // 写操作：readOnly = false
    public <S extends T> S save(S entity) { ... }

    @Transactional(readOnly = true)  // 读操作：优化性能
    public Optional<T> findById(ID id) { ... }
}
```

---

## 二、`@Transactional` 与 Repository 协作

### 1. 默认 REQUIRED 传播

```java
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;  // SimpleJpaRepository 自带事务

    @Transactional  // 开启事务
    public void createUser(User user) {
        userRepository.save(user);  // 加入外层事务（不新建）
    }
}
```

**行为**：
- 外层 `@Transactional` 创建事务
- Repository 方法默认 `REQUIRED`，**加入外层事务**
- 整个方法在一个事务中执行

### 2. readOnly 优化

```java
@Transactional(readOnly = true)  // 整个方法只读
public List<User> findAll() {
    return userRepository.findAll();  // 底层走 JDBC 只读连接
}
```

> 📌 JPA 层 `readOnly = true` 会让 Hibernate 跳过脏检查（flush），性能更好。

### 3. EntityManager 注入

```java
@Service
public class UserService {

    @PersistenceContext
    private EntityManager em;  // 线程绑定，事务结束后自动关闭

    @Transactional
    public void customUpdate(Long id) {
        User user = em.find(User.class, id);
        user.setName("new name");
        em.merge(user);
        // 事务提交时自动 flush 到 DB
    }
}
```

---

## 三、悲观锁 `@Lock`

### 1. 场景

> 读取数据时**立即加锁**（SELECT ... FOR UPDATE），防止其他事务并发修改。**强一致性但并发性能低**。

### 2. 用法

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // 1. PESSIMISTIC_READ：共享锁（其他事务可读，不可写）
    @Lock(LockModeType.PESSIMISTIC_READ)
    Optional<User> findById(Long id);

    // 2. PESSIMISTIC_WRITE：排他锁（其他事务不可读写）
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select u from User u where u.id = :id")
    Optional<User> lockById(@Param("id") Long id);

    // 3. PESSIMISTIC_FORCE_INCREMENT：强制版本号递增（Oracle 专属）
    @Lock(LockModeType.PESSIMISTIC_FORCE_INCREMENT)
    Optional<User> forceLock(Long id);
}
```

### 3. SQL 实际效果

```sql
-- PESSIMISTIC_WRITE 翻译为 SQL
SELECT * FROM users WHERE id = ? FOR UPDATE;
-- 行被锁住，其他事务等待（直到 commit/rollback）
```

### 4. 典型场景

```java
@Service
public class AccountService {

    @Transactional
    public void deduct(Long accountId, BigDecimal amount) {
        // 1. 加锁查询（其他事务拿不到这行）
        Account account = accountRepository.lockById(accountId)
            .orElseThrow(() -> new RuntimeException("账户不存在"));

        // 2. 修改（仍在锁内）
        if (account.getBalance().compareTo(amount) < 0) {
            throw new InsufficientBalanceException();
        }
        account.setBalance(account.getBalance().subtract(amount));
        accountRepository.save(account);
        // 事务提交后释放锁
    }
}
```

> ⚠️ **注意**：必须在 `@Transactional` 方法内调用，`@Lock` 才会真正加锁（没有事务时锁会被立即释放）。

---

## 四、乐观锁 `@Version`

### 1. 场景

> 数据不加锁，**通过版本号检测冲突**——更新时校验版本号，版本不一致则抛 `OptimisticLockException`。**并发性能高，适合读多写少**。

### 2. 实体配置

```java
@Entity
public class Product {

    @Id
    private Long id;

    private String name;
    private BigDecimal price;

    @Version  // JPA 自动维护版本号
    private Long version;
}
```

### 3. 工作流程

```
1. 事务 A 读取 Product（version = 1）
2. 事务 B 读取 Product（version = 1）
3. 事务 A 修改并提交：UPDATE ... SET ..., version = 2 WHERE id = ? AND version = 1   -- 影响 1 行
4. 事务 B 修改并提交：UPDATE ... SET ..., version = 2 WHERE id = ? AND version = 1   -- 影响 0 行
5. 事务 B 抛 ObjectOptimisticLockingFailureException
```

### 4. 异常处理

```java
@Service
public class ProductService {

    @Transactional
    public void update(Long id, ProductDTO dto) {
        try {
            Product p = productRepository.findById(id).orElseThrow();
            p.setPrice(dto.getPrice());
            productRepository.save(p);
        } catch (OptimisticLockingFailureException e) {
            // 重试或提示用户
            throw new ConcurrentUpdateException("数据已被其他用户修改，请刷新");
        }
    }
}
```

---

## 五、悲观锁 vs 乐观锁

| 维度 | 悲观锁 `@Lock` | 乐观锁 `@Version` |
|------|:---------------:|:------------------:|
| **实现机制** | DB 行锁 | 版本号校验 |
| **并发性能** | ⭐⭐（阻塞等待） | ⭐⭐⭐⭐⭐（无阻塞） |
| **适用场景** | 写多、并发冲突高 | 读多写少、冲突概率低 |
| **死锁风险** | 有 | 无 |
| **数据库要求** | 支持 `SELECT ... FOR UPDATE` | 任意（基于 UPDATE WHERE） |
| **重试机制** | 通常不重试 | 失败需重试 |

> 📌 **经验法则**：电商秒杀用乐观锁（高并发读少量写），金融转账用悲观锁（强一致）。

---

## 六、常见陷阱

### 1. 自调用失效

```java
@Service
public class UserService {

    @Transactional
    public void outer() {
        inner();  // ❌ 自调用，事务失效（绕过了代理）
    }

    @Transactional
    public void inner() {
        userRepository.save(new User());
    }
}
```
> 解决：注入自己的代理 `UserService self`，调 `self.inner()`。

### 2. Repository 方法覆盖 `@Transactional` 行为

```java
public interface UserRepository extends JpaRepository<User, Long> {

    @Override
    @Transactional  // 覆盖父接口的默认 readOnly
    List<User> findAll();
}
```

### 3. `EntityManager` 在事务外使用

```java
@Service
public class UserService {

    @PersistenceContext
    private EntityManager em;  // 每个事务绑定的 EntityManager

    public User findByIdBad(Long id) {  // 没有 @Transactional
        return em.find(User.class, id);  // ❌ 拿到 detached 实体
    }
}
```

---

## 🤔 思考

1. **为什么 `SimpleJpaRepository` 默认 `@Transactional`？** 保证单个 Repository 方法的事务原子性，避免每次调用都要在外层加事务。
2. **悲观锁没生效怎么办？** 检查是否在 `@Transactional` 方法内调用、`@Lock` 注解是否在 Repository 接口。
3. **乐观锁冲突如何重试？** Spring Retry `@Retryable(maxAttempts = 3)` 或手动 while 循环。
4. **`@Transactional` + `@Lock` 顺序？** 必须是事务方法内的 Repository 调用，锁才生效。

---

## 相关章节

- ⬅️ [返回事务总览](README.md)
- [事务失效场景](failure-cases.md) — 自调用、异常吞掉
- [Spring Data JPA 实战](https://spring.io/projects/spring-data-jpa) — JPA 上层封装