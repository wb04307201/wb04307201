# 乐观锁 / Version

> 乐观锁（Optimistic Locking）通过**版本号**控制并发更新：每次更新检查版本号是否匹配，不匹配则重试或失败。无需数据库行锁，性能高。

## 目录

- [原理](#原理)
- [适用场景](#适用场景)
- [代码实现](#代码实现)
- [注意事项](#注意事项)
- [选型建议](#选型建议)
- [相关章节](#相关章节)
- [参考资料](#参考资料)

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

乐观锁 / Version 本应该很简单，乐观锁（Optimistic Locking）通过**版本号**控制并发更新：每次更新检查版本号是否匹配，不匹配则重试或失败。无需数据库行锁，性能高

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 原理

```
时间线：
                                         
T1          T2          DB(inventory)
 │           │                │
 │  读       │                │
 │  quantity=10               │
 │  version=5                 │
 │  ────────────────────────▶│
 │           │                │
 │           │  读            │
 │           │  quantity=10   │
 │           │  version=5     │
 │           │  ────────────▶│
 │           │                │
 │ UPDATE   │                │
 │ SET q=9, v=6              │
 │ WHERE id=1001              │
 │ AND version=5              │
 │ ────────────────────────▶│
 │           │                │  ← 影响 1 行，OK
 │           │                │
 │           │  UPDATE        │
 │           │  SET q=9, v=6  │
 │           │  WHERE id=1001 │
 │           │  AND version=5 │
 │           │  ────────────▶│
 │           │                │  ← 影响 0 行，被 T1 抢先
 │           │                │
```

T2 拿到结果 `affectedRows = 0`，知道发生冲突，可以：

- **自动重试**：重新读取最新数据 + 重试
- **报错给用户**：提示"操作过于频繁，请重试"

---

## 适用场景

- **库存扣减**（防超卖）
- **余额更新**（账户余额、积分）
- **文档 / 文章编辑**（多人协作时防覆盖）
- **任何读多写少**的并发更新场景

**不适用**：

- 高竞争场景（重试成本高）—— 改用悲观锁
- 跨多行更新（版本号维护成本高）
- 业务需要"先到先得"语义

---

## 代码实现

### 1. SQL 层（基于 version 列）

```sql
CREATE TABLE inventory (
    id          BIGINT PRIMARY KEY,
    product_id  BIGINT NOT NULL,
    quantity    INT NOT NULL,
    version     INT NOT NULL DEFAULT 0,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_product (product_id)
);

-- 扣减库存
UPDATE inventory
SET quantity = quantity - 1,
    version  = version + 1
WHERE product_id = 1001
  AND quantity  >= 1
  AND version    = #{currentVersion};
```

**关键点**：

- `WHERE version = #{oldVersion}` 确保别人没改过
- 同时 `quantity >= 1` 防止超卖
- 返回影响行数：1 = 成功，0 = 冲突

### 2. MyBatis 实现

```xml
<update id="decreaseStock" parameterType="map">
    UPDATE inventory
    SET quantity = quantity - #{delta},
        version  = version + 1
    WHERE product_id = #{productId}
      AND quantity  >= #{delta}
      AND version    = #{version}
</update>
```

```java
public boolean decreaseStock(Long productId, int delta) {
    int maxRetries = 3;
    for (int i = 0; i < maxRetries; i++) {
        Inventory inv = inventoryMapper.findByProductId(productId);
        if (inv == null) {
            throw new NotFoundException("商品不存在");
        }
        if (inv.getQuantity() < delta) {
            throw new InsufficientStockException("库存不足");
        }
        int affected = inventoryMapper.decreaseStock(
            productId, delta, inv.getVersion());
        if (affected == 1) {
            return true;     // 成功
        }
        // affected == 0: 版本冲突，重试
        log.warn("库存扣减冲突, productId={}, retry={}", productId, i + 1);
    }
    throw new OptimisticLockException("库存扣减冲突，请重试");
}
```

### 3. JPA / Hibernate 实现（@Version）

```java
@Entity
public class Inventory {
    @Id
    private Long id;

    @Column(nullable = false)
    private Long productId;

    @Column(nullable = false)
    private Integer quantity;

    @Version    // 关键注解
    private Integer version;
}
```

```java
@Service
@Transactional
public class InventoryService {

    @Autowired
    private InventoryRepository repo;

    public void decreaseStock(Long productId, int delta) {
        int maxRetries = 3;
        for (int i = 0; i < maxRetries; i++) {
            try {
                Inventory inv = repo.findByProductId(productId)
                        .orElseThrow();
                if (inv.getQuantity() < delta) {
                    throw new InsufficientStockException();
                }
                inv.setQuantity(inv.getQuantity() - delta);
                repo.save(inv);    // 自动按 @Version 校验
                return;
            } catch (OptimisticLockingFailureException e) {
                if (i == maxRetries - 1) throw e;
            }
        }
    }
}
```

### 4. 雪花 ID / 时间戳作为版本

无需新增列，复用业务字段：

```sql
-- 用 updated_at 作为版本（必须支持毫秒精度）
UPDATE inventory
SET quantity = quantity - 1,
    updated_at = NOW(3)
WHERE product_id = 1001
  AND quantity  >= 1
  AND updated_at = '2025-06-09 10:00:00.123';
```

> 注意：时间戳在并发场景下分辨率可能不够（同一毫秒内的并发），推荐使用单调递增的 `version` 列。

---

## 注意事项

### 1. ABA 问题

```
T1 读 v=5
T2 修改后 v=6 → T2 又改回 v=5
T1 仍然能更新成功（v=5 匹配）
```

**应对**：

- 配合业务字段校验（如 quantity 数值）
- 使用单调递增 ID 作版本

### 2. 饥饿 / 活锁

高并发下大量重试，可能导致部分请求一直拿不到锁。

**应对**：

- 设置最大重试次数（3~5 次）
- 退避策略（指数退避 + 抖动）
- 极端场景改用悲观锁或排队

### 3. 长事务

事务内不要做重试（Hibernate 的 @Version 自动重试会反复开启事务）。重试应在事务外层。

### 4. 跨表更新

一次更新涉及多张表的 version，维护成本高：

```sql
-- 不推荐
UPDATE order SET version=v+1 WHERE id=?
UPDATE order_item SET order_version=? WHERE order_id=?
```

**应对**：尽量把"是否冲突"的判断收敛到一张表的 version。

### 5. 与悲观锁的对比

| 维度 | 乐观锁 | 悲观锁（SELECT FOR UPDATE） |
|------|--------|----------------------------|
| 锁粒度 | 无 DB 锁 | 行级 / 表级 |
| 读性能 | 高（不加锁） | 中（共享读锁） |
| 写性能 | 高（CAS） | 中（等待 / 死锁风险） |
| 适用竞争 | 低~中 | 高竞争 |
| 死锁 | 无 | 有 |
| 实现复杂度 | 重试逻辑 | 简单（自动阻塞） |

---

## 选型建议

| 场景 | 推荐 |
|------|------|
| 库存扣减（一般竞争） | ✅ 乐观锁 + 3 次重试 |
| 库存扣减（秒杀 / 超高竞争） | ⚠ 乐观锁 + 限流 + 排队；或悲观锁 |
| 账户余额（中等并发） | ✅ 乐观锁 |
| 文档 / 文章协作 | ✅ 乐观锁 |
| 资金清结算（强一致） | ⚠ 悲观锁 或 分布式事务 |
| 跨多行复杂更新 | ❌ 改用悲观锁或分布式锁 |

---

## 相关章节

- [Idempotency-Key 唯一标识](../idempotency-key/README.md) — 接口层幂等
- [状态机](../state-machine/README.md) — 状态流转场景
- [去重表](../deduplication-table/README.md) — MQ 消费场景
- [与分布式事务的关系](../vs-distributed-transaction/README.md) — 何时升级到 TCC
- [02 分布式 / 分布式锁](../../02-distributed/distributed-lock/README.md) — 悲观锁与分布式锁

## 参考资料

- [Martin Fowler - Patterns of Enterprise Application Architecture - Optimistic Offline Lock](https://martinfowler.com/eaaCatalog/optimisticOfflineLock.html)
- [MySQL - InnoDB 行锁与版本控制](https://dev.mysql.com/doc/refman/8.0/en/innodb-locking.html)
- [JPA @Version 文档](https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html#locking-optimistic)
