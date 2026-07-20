<!--
question:
  id: 03.database-isolation
  topic: 03.database
  difficulty: ⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [03.database, MySQL, isolation]
-->

# MySQL事务隔离级别深度解析

## 引子：三个经典的并发问题

```sql
-- 事务 A
BEGIN;
SELECT * FROM accounts WHERE id = 1;  -- 余额 100

-- 与此同时，事务 B
BEGIN;
UPDATE accounts SET balance = 200 WHERE id = 1;  -- 改成了 200
COMMIT;

-- 事务 A 再读一次
SELECT * FROM accounts WHERE id = 1;  -- 读到 200？还是 100？
```

这涉及三个经典的并发问题：
1. **脏读**：读到了别的事务还没提交的数据（万一人家回滚了呢？）
2. **不可重复读**：同一条数据，两次读结果不一样
3. **幻读**：两次查询，行数不一样（多了或少了）

MySQL 用 **4 种隔离级别** 解决这些问题。

---

> 📚 **前置知识**：[事务](../../../03.database/03-transaction/README.md)

## 一、核心原理

MySQL通过MVCC和锁机制实现四种隔离级别，保障并发数据一致性。

**四大隔离级别：**

| **隔离级别** | **脏读** | **不可重复读** | **幻读** | **实现机制** | **性能** | **典型场景** |
|------------|---------|--------------|---------|------------|---------|------------|
| **READ UNCOMMITTED** | ❌可能 | ❌可能 | ❌可能 | 几乎无锁 | 最高 | 极少使用 |
| **READ COMMITTED** | ✅避免 | ❌可能 | ❌可能 | MVCC快照读 | 高 | OLTP系统 |
| **REPEATABLE READ** | ✅避免 | ✅避免 | ✅避免(InnoDB) | MVCC+间隙锁 | 中 | 默认级别 |
| **SERIALIZABLE** | ✅避免 | ✅避免 | ✅避免 | 强制串行 | 最低 | 金融核销 |

**三种并发异常：**
1. **脏读**：读取未提交的修改。B改100→200（未提交），A读到200；B回滚后A数据无效
2. **不可重复读**：同一事务内多次读同一行结果不一致。A读100，B改为200并提交，A再读变200
3. **幻读**：范围查询行数不一致。A查`WHERE amount>100`得10条，B插入一条，A再查得11条

**MVCC核心机制：**
```text
InnoDB每行隐藏列：DB_TRX_ID(最后修改事务ID)、DB_ROLL_PTR(回滚指针)、DB_ROW_ID(隐式主键)
Undo Log版本链：当前(v3,TRX=105) → Undo v2(TRX=102) → Undo v1(TRX=100) → 初始值

快照读：普通SELECT，读历史版本，不加锁
当前读：SELECT...FOR UPDATE，读最新版本，加锁
```

**ReadView可见性判断：**
```text
row.trx_id < min_trx_id → 可见（已提交老版本）
row.trx_id >= max_trx_id → 不可见（未来事务）
row.trx_id in m_ids → 不可见（活跃事务未提交）
否则 → 可见

RC每次SELECT生成新ReadView；RR只在第一次SELECT生成
```

## 二、代码示例

**设置隔离级别：**
```sql
SELECT @@session.transaction_isolation;
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET GLOBAL TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- my.cnf永久设置：[mysqld] transaction-isolation = READ-COMMITTED
```

**演示脏读：**
```sql
-- A: SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED; START TRANSACTION;
-- B: START TRANSACTION; UPDATE accounts SET balance=200 WHERE id=1;  -- 未提交
-- A: SELECT balance FROM accounts WHERE id=1;  -- 脏读：200！
-- B: ROLLBACK;
-- A: SELECT balance FROM accounts WHERE id=1;  -- 变回100
```

**演示不可重复读：**
```sql
-- A: SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED; START TRANSACTION;
--    SELECT balance FROM accounts WHERE id=1;  -- 100
-- B: UPDATE accounts SET balance=200 WHERE id=1; COMMIT;
-- A: SELECT balance FROM accounts WHERE id=1;  -- 200（不可重复读）
```

**演示间隙锁防幻读：**
```sql
CREATE TABLE orders (id INT PRIMARY KEY AUTO_INCREMENT, user_id INT, amount DECIMAL(10,2), INDEX idx_user(user_id));
INSERT INTO orders (user_id, amount) VALUES (1,50), (2,120), (3,200);

-- A: SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ; START TRANSACTION;
--    SELECT * FROM orders WHERE user_id=2 FOR UPDATE;  -- 加间隙锁
-- B: INSERT INTO orders (user_id, amount) VALUES (2,150);  -- 阻塞！
-- A: COMMIT;  -- B现在才能成功
```

**Spring事务配置：**
```java
@Service
public class OrderService {
    @Transactional  // 默认REPEATABLE READ
    public void createOrder(Order order) { orderRepository.save(order); }
    
    @Transactional(isolation = Isolation.READ_COMMITTED)  // 高并发OLTP
    public List<Order> getUserOrders(Long userId) { return orderRepository.findByUserId(userId); }
    
    @Transactional(isolation = Isolation.SERIALIZABLE)  // 强一致性
    public void transferFunds(Long from, Long to, BigDecimal amount) {
        Account f = accountRepository.findByIdForUpdate(from);  // 悲观锁
        Account t = accountRepository.findByIdForUpdate(to);
        if (f.getBalance().compareTo(amount) < 0) throw new InsufficientFundsException();
        f.setBalance(f.getBalance().subtract(amount));
        t.setBalance(t.getBalance().add(amount));
        accountRepository.save(f); accountRepository.save(t);
    }
}

@Repository
public interface AccountRepository extends JpaRepository<Account,Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT a FROM Account a WHERE a.id=:id")
    Account findByIdForUpdate(@Param("id") Long id);
}
```

## 三、常见陷阱

**陷阱1：误认为RR完全杜绝幻读**
```sql
-- 间隙锁只在当前读(FOR UPDATE)时生效，普通快照读不阻止插入
-- A: START TRANSACTION; SELECT * FROM orders WHERE user_id=2;  -- 快照读，不加锁
-- B: INSERT INTO orders (user_id, amount) VALUES (2,150); COMMIT;  -- 成功！
-- A: SELECT * FROM orders WHERE user_id=2;  -- 仍看到旧结果（MVCC保证可重复读）
-- 但当前读会加间隙锁：SELECT * FROM orders WHERE user_id=2 FOR UPDATE;
```

**陷阱2：长事务导致Undo Log膨胀**
```sql
-- 长时间运行的事务阻止Undo Log清理
SELECT trx_id, trx_started, TIMESTAMPDIFF(SECOND, trx_started, NOW()) as duration_sec
FROM information_schema.INNODB_TRX WHERE TIMESTAMPDIFF(SECOND, trx_started, NOW()) > 60;
SHOW ENGINE INNODB STATUS\G  -- 查看"History list length"

-- 解决方案：拆分大事务、避免事务中HTTP请求/文件IO、设置超时
```

**陷阱3：死锁问题**
```sql
-- 两事务以相反顺序获取锁 → 死锁
-- A: UPDATE accounts SET balance=balance-100 WHERE id=1; UPDATE accounts SET balance=balance+100 WHERE id=2;
-- B: UPDATE accounts SET balance=balance-50 WHERE id=2; UPDATE accounts SET balance=balance+50 WHERE id=1;
-- ERROR 1213 (40001): Deadlock found

-- 解决方案：固定加锁顺序、设置锁等待超时、应用层重试
SET innodb_lock_wait_timeout = 10;
```

**陷阱4：忽略数据库默认差异**
```text
MySQL默认：REPEATABLE READ；PostgreSQL/Oracle默认：READ COMMITTED
迁移数据库时可能出现兼容性问题！
-- 解决方案：应用层明确指定，不依赖默认值
@Transactional(isolation = Isolation.REPEATABLE_READ)
```

## 四、最佳实践

**1. 隔离级别选型**
```text
├── 需要绝对一致性？→ SERIALIZABLE（接受性能损失）
├── 有范围查询防幻读？→ REPEATABLE READ（MySQL默认）
├── 高并发OLTP？→ READ COMMITTED（减少锁竞争）
└── 通用场景 → REPEATABLE READ（安全默认值）
```

**2. 读写分离策略**
```java
@Configuration
public class TxConfig {
    @Bean @Primary public PlatformTransactionManager writeTM(EntityManagerFactory emf) {
        JpaTransactionManager tm = new JpaTransactionManager(emf); tm.setDefaultTimeout(30); return tm;
    }
    @Bean public PlatformTransactionManager readTM(EntityManagerFactory emf) {
        JpaTransactionManager tm = new JpaTransactionManager(emf); tm.setDefaultTimeout(5); return tm;
    }
}
@Service
public class UserService {
    @Transactional(transactionManager="writeTM", isolation=Isolation.REPEATABLE_READ)
    public User createUser(User user) { return userRepository.save(user); }
    @Transactional(transactionManager="readTM", isolation=Isolation.READ_COMMITTED, readOnly=true)
    public User getUser(Long id) { return userRepository.findById(id).orElse(null); }
}
```

**3. 索引优化减少锁范围**
```sql
-- 无索引UPDATE锁全表！
UPDATE users SET status='active' WHERE email='test@example.com';  -- email无索引→锁全表
CREATE INDEX idx_email ON users(email);  -- 现在只锁匹配的行

-- 范围查询利用间隙锁
CREATE INDEX idx_amount ON orders(amount);
SELECT * FROM orders WHERE amount BETWEEN 100 AND 200 FOR UPDATE;  -- 锁定[100,200]范围
```

**4. 乐观锁替代悲观锁**
```java
// 乐观锁：适合读多写少
@Entity
public class Product {
    @Id private Long id; private Integer stock;
    @Version private Integer version;  // 版本号
}
@Transactional
public void decreaseStock(Long productId, int qty) {
    Product p = productRepository.findById(productId).orElseThrow();
    if (p.getStock() < qty) throw new InsufficientStockException();
    p.setStock(p.getStock() - qty);  // version自动递增，并发修改抛异常
    productRepository.save(p);
}

// 悲观锁：适合写多或强一致
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT p FROM Product p WHERE p.id=:id")
Product findByIdForUpdate(@Param("id") Long id);
```

**5. 监控**
```sql
-- 实时监控事务
SELECT trx_id, trx_state, TIMESTAMPDIFF(SECOND, trx_started, NOW()) as duration
FROM information_schema.INNODB_TRX ORDER BY trx_started;

-- 检测锁等待
SELECT r.trx_query waiting_query, b.trx_query blocking_query
FROM information_schema.INNODB_LOCK_WAITS w
JOIN information_schema.INNODB_TRX r ON w.requesting_trx_id=r.trx_id
JOIN information_schema.INNODB_TRX b ON w.blocking_trx_id=b.trx_id;

-- 死锁日志
SHOW ENGINE INNODB STATUS\G  -- 查看"LATEST DETECTED DEADLOCK"
```

## 五、面试话术

**面试官：解释MySQL四种隔离级别。**

回答要点：
1. **READ UNCOMMITTED**：最低级别，可能脏读/不可重复读/幻读
2. **READ COMMITTED**：解决脏读，MVCC快照读，Oracle/PG默认
3. **REPEATABLE READ**：解决脏读+不可重复读，InnoDB通过MVCC+间隙锁也基本解决幻读，MySQL默认
4. **SERIALIZABLE**：最高级别，强制串行，解决所有问题但性能最低

**面试官：MVCC如何实现？**

回答要点：
- **隐藏列**：DB_TRX_ID（最后修改事务ID）、DB_ROLL_PTR（回滚指针）
- **Undo Log**：保存历史版本形成版本链
- **ReadView**：事务启动时生成读视图
- **可见性**：根据事务ID和ReadView判断哪个版本可见
- **RC vs RR**：RC每次SELECT生成新ReadView；RR只在第一次生成

**面试官：什么是间隙锁？**

回答要点：
- **间隙锁**：锁定索引记录之间的"间隙"，阻止其他事务在该范围内插入
- **Next-Key Lock**：InnoDB使用记录锁+间隙锁组合
- **作用范围**：只在RR及以上的当前读（FOR UPDATE）生效

**面试官：长事务有什么危害？**

回答要点：
- **危害**：阻止Undo Log清理导致膨胀、延长锁持有时间增加死锁风险
- **发现**：查询`information_schema.INNODB_TRX`按trx_started排序
- **处理**：拆分大事务、避免事务中耗时操作、设置超时、定期kill

## 六、交叉引用

- **相关主题**：[MySQL COUNT优化](../mysql-count/README.md) - MVCC对COUNT的影响
- **性能调优**：[MySQL慢查询](../mysql-tuning/README.md)
- **Java关联**：[Spring Data](../../../06.spring/03-data/README.md)
- **分布式系统**：[分布式事务](../../../04.system-design/02-distributed/distributed-transaction/README.md)

## 相关章节

- 深度阅读：[`03.database`](../../../03.database/README.md) — 主模块详细内容

← [返回数据库咬文嚼字](../README.md)
