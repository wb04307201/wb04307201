# 事务注解

> 最后更新: 2026-06-14
> ⬅️ [返回注解速查](../README.md) | [JPA 注解](jpa.md)

本节是 `@Transactional` 与 `@EnableTransactionManagement` 的速查手册——只列关键属性与失效场景，**深读请前往 [03-data/transaction](../../03-data/transaction/README.md)**。

---

## 🎯 一句话定位

**事务注解 = "给方法加事务边界"**——`@Transactional` 声明方法/类需要事务，Spring 通过 AOP 代理在方法前后开启/提交/回滚。

---

## 一、@Transactional 关键属性速查

| 属性 | 类型 | 默认值 | 说明 |
|:-----|:-----|:-------|:-----|
| `value` / `transactionManager` | String | 容器中首个 `PlatformTransactionManager` | 指定事务管理器 Bean 名称 |
| `propagation` | `Propagation` | `REQUIRED` | 事务传播行为（7 种） |
| `isolation` | `Isolation` | `DEFAULT`（数据库默认） | 事务隔离级别（4 种） |
| `timeout` | int | `-1`（永不超时） | 超时秒数，超出自动回滚 |
| `readOnly` | boolean | `false` | 只读事务（可优化性能，提示 JDBC 驱动） |
| `rollbackFor` | `Class<? extends Throwable>[]` | `{RuntimeException, Error}` | 触发回滚的异常类型 |
| `noRollbackFor` | `Class<? extends Throwable>[]` | `{}` | 不触发回滚的异常类型 |

```java
@Transactional(
    propagation = Propagation.REQUIRED,
    isolation   = Isolation.READ_COMMITTED,
    timeout     = 30,
    readOnly    = false,
    rollbackFor = { Exception.class },        // 检查型异常也回滚
    noRollbackFor = { BusinessWarnException.class }
)
public void doBiz() { ... }
```

---

## 二、7 种传播行为（propagation）

| 传播行为 | 行为 | 典型场景 |
|:---------|:-----|:---------|
| **REQUIRED**（默认） | 存在则加入；不存在则新建 | 90% 业务方法 |
| **SUPPORTS** | 存在则加入；不存在则非事务 | 查询方法（不强求事务） |
| **MANDATORY** | 必须在已有事务中执行 | 内部子方法，强制外层开事务 |
| **REQUIRES_NEW** | 无论是否存在，都开启新事务 | 内外事务隔离（审计日志） |
| **NOT_SUPPORTED** | 存在则挂起；非事务执行 | 与 JMS / 邮件发送配合 |
| **NEVER** | 存在则抛异常 | 严格要求非事务 |
| **NESTED** | 存在则嵌套（Savepoint）；不存在则新建 | 局部回滚 |

> 📌 最常用：`REQUIRED`（默认）、`REQUIRES_NEW`（独立事务）、`NESTED`（嵌套回滚）。

---

## 三、4 种隔离级别（isolation）

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 说明 |
|:---------|:----:|:----------:|:----:|:-----|
| **DEFAULT** | — | — | — | 沿用数据库默认值 |
| **READ_UNCOMMITTED** | ✅ | ✅ | ✅ | 性能最高、一致性最差 |
| **READ_COMMITTED** | ❌ | ✅ | ✅ | 大多数 DB 默认（Oracle、PostgreSQL） |
| **REPEATABLE_READ** | ❌ | ❌ | ✅ | MySQL InnoDB 默认 |
| **SERIALIZABLE** | ❌ | ❌ | ❌ | 性能最低、完全串行 |

> 📌 实际项目**不建议改默认**：隔离级别由 DBA 评估业务后由数据库设置。

---

## 四、@EnableTransactionManagement

> 启用注解驱动的事务管理（Spring Boot 自动启用，可省略）。

```java
@Configuration
@EnableTransactionManagement(proxyTargetClass = true, order = Ordered.LOWEST_PRECEDENCE)
public class TxConfig { }
```

| 属性 | 默认 | 说明 |
|:-----|:-----|:-----|
| `proxyTargetClass` | `false` | `true` 用 CGLIB 代理（需类而非接口） |
| `order` | `LOWEST_PRECEDENCE` | 事务通知顺序，数字越小越先执行 |
| `mode` | `PROXY` | 代理模式 / `ASPECTJ`（编译期织入） |

---

## 五、失效场景速查表

> 🚨 90% 的"事务不生效"问题都在这一节。

| 失效场景 | 原因 | 解决方案 |
|:---------|:-----|:---------|
| **同类 self-invocation** | `this.xxx()` 绕过 Spring 代理 | 注入自己（`@Autowired OrderService self`）或拆为两个 Bean |
| **private / final 方法** | 无法生成代理 | 改成 `public` 且非 `final` |
| **异常被 try-catch 吞掉** | 未抛到代理方法外 | 重新抛出，或在 `catch` 中 `TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()` |
| **检查型异常（非 RuntimeException）** | 默认只对 RuntimeException/Error 回滚 | 加 `rollbackFor = Exception.class` |
| **`@Transactional` 加在接口方法上 + 类非 public** | CGLIB 无法代理 | 注解加到 **public 类**的方法上 |
| **异步 / 多线程调用** | 跨线程丢失上下文 | 手动传递 `DataSourceUtils` 或用 `TransactionTemplate` |
| **错误的传播行为** | `NEVER` / `SUPPORTS` / `NOT_SUPPORTED` 等不创建事务 | 根据场景选 `REQUIRED` / `REQUIRES_NEW` |
| **同一个类中无事务方法调用有事务方法** | 同上 self-invocation | 同上 |

```java
// ❌ 失效：同类 self-invocation
@Service
public class OrderService {
    @Transactional
    public void create() { ... }

    public void batchCreate() {
        create();   // 内部调用，事务不生效！
    }
}

// ✅ 正确：注入自己或拆 Bean
@Service
public class OrderService {
    @Autowired
    @Lazy
    private OrderService self;        // 注入自身（通过代理）

    @Transactional
    public void create() { ... }

    public void batchCreate() {
        self.create();                // 走代理，事务生效
    }
}
```

---

## 六、典型使用模板

```java
@Service
public class OrderServiceImpl implements OrderService {

    @Autowired
    private OrderRepository orderRepo;

    // 只读事务：查询优化
    @Transactional(readOnly = true)
    public Order findById(Long id) {
        return orderRepo.findById(id).orElseThrow();
    }

    // 写事务：默认 REQUIRED
    @Transactional(rollbackFor = Exception.class)
    public Order create(OrderDTO dto) {
        Order o = new Order(dto);
        return orderRepo.save(o);
    }

    // 独立事务：日志/审计不受业务回滚影响
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void auditLog(String msg) {
        logRepo.save(new AuditLog(msg));
    }
}
```

---

## 🤔 思考

1. **为什么 @Transactional 默认不回滚检查型异常？** Spring 设计哲学：业务异常（`BusinessException` 继承 `Exception`）应当显式声明，避免"看似成功实则已提交"的误判。
2. **propagation = NESTED vs REQUIRES_NEW？** NESTED 是同一物理事务的 Savepoint，可部分回滚；REQUIRES_NEW 是完全独立的新事务。
3. **@Transactional 加在类上 vs 方法上？** 类级别 = 类内所有方法默认应用；方法级别 = 覆盖类级别。建议**加到方法上**以保持显式。
4. **事务方法中调用 RPC / HTTP？** 建议在 RPC 之前 commit，避免"远端成功 + 本地回滚"的不一致（可考虑 TCC/Saga/本地消息表）。

---

## 深入阅读

- [03-data/transaction/README](../../03-data/transaction/README.md) — 事务完整指南
- [03-data/transaction/failure-cases](../../03-data/transaction/failure-cases.md) — 事务失效场景详解
- [03-data/transaction/propagation-and-isolation](../../03-data/transaction/propagation-and-isolation.md) — 传播与隔离级别深入
- [03-data/transaction/jpa-transaction](../../03-data/transaction/jpa-transaction.md) — JPA 事务特性

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [AOP 注解](aop.md) — @Transactional 基于 AOP 代理实现
- [JPA 注解](jpa.md) — 实体 + Repository 与事务配合
