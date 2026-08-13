# Seata 集成（Spring Cloud Alibaba 视角）

> ⬅️ [返回 05 Spring Cloud](README.md) | [Config 中心](config-center.md) | [熔断降级](circuit-breaker.md)

本文档聚焦 **Spring Cloud Alibaba 集成 Seata 的工程实践**——`@GlobalTransactional` 在微服务调用链中的落地、与 OpenFeign / Nacos 的协同。Seata 框架原理（TC/TM/RM 三角色、AT 模式回滚日志）请见 [03-data/transaction/distributed/seata.md](../03-data/transaction/distributed/seata.md)。

---

## 一、Spring Cloud 中 Seata 三角色

| 角色 | 在 Spring Cloud 中的部署 | 职责 |
|------|--------------------------|------|
| **TC** (Transaction Coordinator) | 独立 Server 进程（`seata-server`） | 全局事务协调、维护全局/分支事务状态、驱动提交/回滚 |
| **TM** (Transaction Manager) | `@GlobalTransactional` 注解所在 Bean | 事务边界定义（begin / commit / rollback） |
| **RM** (Resource Manager) | 数据源代理（DataSourceProxy） | 分支事务注册、本地事务执行、上报状态 |

微服务调用链中的发起方为 TM（带 `@GlobalTransactional`），参与方为 RM。TC 是中心化服务。

---

## 二、依赖与配置

### Maven 依赖

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-seata</artifactId>
</dependency>
```

版本由 [Spring Cloud Alibaba BOM](README.md#spring-cloud-与-spring-cloud-alibaba-关系) 仲裁。

### application.yml

```yaml
spring:
  cloud:
    alibaba:
      seata:
        tx-service-group: my_tx_group     # 事务组名（对应 TC cluster）
        registry:
          type: nacos                     # TC 注册中心（Nacos / Eureka / File）
          nacos:
            server-addr: localhost:8848
            namespace: public
            group: SEATA_GROUP
        config:
          type: nacos
          nacos:
            server-addr: localhost:8848
            group: SEATA_GROUP
```

TC 的 `registry.conf` 和客户端的 `seata.conf` **事务组名必须一致**，否则找不到 TC 集群。

---

## 三、`@GlobalTransactional` 使用

```java
@Service
public class OrderService {

    @Autowired
    private StorageFeign storageFeign;

    @Autowired
    private AccountFeign accountFeign;

    @GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
    public Order createOrder(OrderDTO dto) {
        // 1. 本地：创建订单
        orderMapper.insert(dto);

        // 2. 远程：扣减库存（Feign 调用，自动注册分支事务）
        storageFeign.deduct(dto.getSkuId(), dto.getQty());

        // 3. 远程：扣减余额
        accountFeign.debit(dto.getUserId(), dto.getAmount());

        return dto;
    }
}
```

**关键点**：
- `@GlobalTransactional` 仅在**事务发起方**使用
- Feign 调用走的是 `RM` 分支事务，由 SDK 自动注册到 TC
- 任意参与者抛异常，TC 通知所有 RM 回滚

---

## 四、四种模式选型

| 模式 | 一致性 | 性能 | 侵入性 | 适用场景 |
|------|--------|------|--------|---------|
| **AT** | 最终一致 | ⭐⭐⭐⭐⭐ | 零侵入（自动代理） | **默认首选**，80% 业务场景 |
| **TCC** | 强一致 | ⭐⭐⭐ | 高（Try/Confirm/Cancel 三方法） | 高一致性金融、库存 |
| **Saga** | 最终一致 | ⭐⭐ | 中（状态机定义） | 长事务、跨服务多步骤 |
| **XA** | 强一致 | ⭐⭐ | 低（依赖数据库 XA 驱动） | 强一致 + 数据库支持 XA |

**经验法则**：
- 新项目 → 直接 **AT**，日单量百万级以下足够
- 资金交易、库存扣减 → **TCC**（业务可承担额外编码）
- 跨 ERP / 第三方系统的长流程 → **Saga**
- 已有 Oracle / MySQL 5.7+ XA 配置 + 强一致要求 → **XA**

---

## 五、与 OpenFeign 协同

Seata 通过 **`SeataFeignClient`** 拦截器传递 **XID**（全局事务 ID）：

```java
@Bean
public Feign.Builder feignBuilder() {
    return Feign.builder()
        .requestInterceptor(new SeataFeignInterceptor());
}
```

或在 Spring Cloud 2021+ 之后无需手动配置，AutoConfiguration 已默认注册拦截器，**XID 通过 Header `TX_XID` 透传**。

---

## 六、常见问题

### 1. 全局事务不生效

- 检查 `@GlobalTransactional` 是否在**发起方**（非参与方）
- 确认 TC 服务可达（`registry.conf` 配置正确）
- 数据库驱动版本是否在 Seata 兼容矩阵内

### 2. AT 模式脏写

- 同一行记录被**非 Seata 事务**直接修改后，Seata 回滚会失败
- 解决：业务入口统一走 Seata 事务，或使用 **SELECT FOR UPDATE** 锁

### 3. 性能调优

```yaml
# 客户端：减少 RPC 调用次数
seata.client.rm.report-retry-count: 5
seata.client.tm.commit-retry-count: 5

# TC Server：调整存储模式
store.mode: db    # file / db / redis
```

---

## 七、与本书其他章节的关系

- **原理篇**：[Seata 框架原理](../03-data/transaction/distributed/seata.md) — AT 模式回滚日志、TC 集群选举
- **理论篇**：[分布式事务理论与模式](../03-data/transaction/distributed/theory-and-patterns.md) — CAP / BASE / 2PC / 3PC
- **熔断篇**：[熔断降级](circuit-breaker.md) — Seata 与 Sentinel 的协同（异常触发降级 vs 回滚）

---

## 相关章节

- ⬅️ [返回 05 Spring Cloud](README.md)
- [Config 中心](config-center.md) — Seata 配置接入 Nacos
- [熔断降级](circuit-breaker.md) — 微服务容错组合拳
- ➡️ [Seata 框架原理](../03-data/transaction/distributed/seata.md)