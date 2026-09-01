<!--
module:
  parent: spring
  slug: spring/transaction/distributed
  type: article
  category: 主模块子文章
  summary: Spring 分布式事务：理论 + Seata 落地
  depth: ⭐⭐⭐
-->

# Spring 分布式事务

> ⬅️ [返回 03 数据层/事务](../README.md) | [返回 Spring 主页](../../README.md)

> **一句话定位**：单库事务用 `@Transactional`，**跨库跨服务事务**用 **Seata + Saga/TCC/2PC** 三件套。本节聚焦 Spring 集成层，理论深度见 [`12.interview/04.system-design/02-distributed/distributed-transaction`](../../../../06.distributed-systems/02-distributed/distributed-transaction/README.md)。

---

## 🎯 学习目标

完成本节后，你能够：

- **理论**：说清 2PC / 3PC / TCC / Saga / 本地消息表 5 大方案的核心差异与选型
- **落地**：用 Seata AT/TCC/Saga 三种模式集成 Spring Boot 微服务
- **避坑**：识别分布式事务的 6 大反模式（同步阻塞 / 空回滚 / 幂等悬挂 / 脑裂 / 锁膨胀 / 长事务）
- **监控**：配置 Seata TC + RM + TM 三大组件的可观测性

---

## 📚 文章清单（2 篇）

| 主题 | 核心内容 | 阅读时长 |
|------|---------|---------|
| [分布式事务理论与模式](theory-and-patterns.md) | 2PC / 3PC / TCC / Saga / 本地消息表 5 大方案 + 6 大反模式 | 35 min |
| [Seata 分布式事务框架](seata.md) | TC/TM/RM 核心组件 + AT/TCC/Saga/XA 4 种模式 + Spring Boot 集成 | 40 min |

---

## 🔗 兄弟章节

- **理论深度**：[`12.interview/04.system-design/02-distributed/distributed-transaction`](../../../../06.distributed-systems/02-distributed/distributed-transaction/README.md) — 共识算法 / CAP / BASE 理论
- **工作流视角**：[`07.workflow`](../../../../07.devops-and-tools/02-workflow/README.md) — Saga/TCC 也是分布式协作模式
- **咬文嚼字**：[`13.split-hairs/03.database`](../../../../12.interview/03.database/README.md) — 数据库事务隔离级别
- **面试深挖**：[`13.split-hairs/06.spring`](../../../../12.interview/06.spring/README.md) — Spring 事务高频题

---

## ⚠️ 反模式速查

| # | 反模式 | 后果 | 修复 |
|---|--------|------|------|
| 1 | **同步阻塞** | TC 单点 → 全链路雪崩 | TC 集群化 + 异步化 |
| 2 | **空回滚** | TCC Try 未执行 → Cancel 报空 | 记录 Try 状态 + 幂等 |
| 3 | **幂等悬挂** | 重复 Try → Cancel 状态错乱 | 主键去重 + 状态机 |
| 4 | **脑裂** | 网络分区导致双 TC 决策 | 多数派 + 租约机制 |
| 5 | **锁膨胀** | 长事务占用数据库锁 | 异步化 + 补偿 + 最终一致 |
| 6 | **大事务** | 一锁 N 张表 → 性能塌方 | 拆小 + Saga + 异步消息 |

<details><summary>🔧 @GlobalTransactional 最小可运行示例</summary>

```java
@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements OrderService {

    private final InventoryFeignClient inventoryClient;
    private final AccountFeignClient accountClient;
    private final OrderDao orderDao;

    @GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
    public Order createOrder(Long userId, Long productId, int count) {
        // 1. 创建订单（本地事务）
        Order order = Order.builder().userId(userId).productId(productId).count(count).build();
        orderDao.insert(order);
        // 2. 扣减库存（远程调用，RM 自动注册分支事务）
        inventoryClient.deduct(productId, count);
        // 3. 扣减余额（远程调用）
        accountClient.debit(userId, order.getTotalPrice());
        // 任一步骤抛异常 → Seata TC 协调三个 RM 全部回滚
        return order;
    }
}
```

**TC 集群配置片段**（Nacos 注册 + DB 存储，生产推荐）：

```yaml
# seata-server/resources/application.yml
seata:
  server:
    service-port: 8091
  store:
    mode: db
    db:
      datasource: druid
      db-type: mysql
      url: jdbc:mysql://127.0.0.1:3306/seata?rewriteBatchedStatements=true
      user: root
      password: root
      min-conn: 5
      max-conn: 100
  registry:
    type: nacos
    nacos:
      server-addr: 127.0.0.1:8848
      namespace: seata-server
      group: SEATA_GROUP
```

</details>

---

## 🔍 模式选型速查（精简版）

| 场景 | 推荐模式 | 关键约束 |
|------|---------|---------|
| 跨 2-3 个微服务的常规写操作 | **AT** | 数据库需支持本地事务（MySQL/Oracle） |
| 高并发 + 强一致（支付/资金） | **TCC** | 业务需实现 Try/Confirm/Cancel 三接口 |
| 长事务 + 第三方系统参与 | **Saga** | 接受最终一致 + 需补偿逻辑 |
| 遗留 XA 数据库 / 强合规要求 | **XA** | 性能差，仅用于无法改造的遗留系统 |
| 跨系统弱一致 + 异步化 | **本地消息表** | 不依赖 Seata，业务侵入小 |

← [返回: Spring 事务](../README.md)