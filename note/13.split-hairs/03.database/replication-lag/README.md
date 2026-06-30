<!--
question:
  id: 03.database-replication-lag
  topic: 03.database
  difficulty: 未标
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [03.database, MySQL, replication]
-->

# MySQL 主从复制延迟原因与解决方案

## 引子：刚注册完，为什么查不到用户？

```java
// 写入主库
userMapper.insert(user);  // 主库写入成功

// 立刻查从库
User u = userMapper.selectById(user.getId());  // null ？？？
```

数据写到主库了，但从库查不到？

这就是**主从复制延迟**。MySQL 主从复制是**异步**的——主库写 binlog，从库拉取 binlog 再回放。这个过程中有延迟，可能几毫秒，也可能几秒。

怎么解决？看业务能容忍多大延迟。

---

> 📚 **前置知识**：[MySQL](../../../03.database/05-mysql/README.md)

## 一、核心原理

MySQL 主从复制（Replication）基于 binlog 实现，整个流程分为三个关键步骤：

### 1. 主库 Dump Thread
当从库发起复制请求时，主库会为该从库创建一个 **Binlog Dump Thread**，负责读取主库的 binlog 事件并发送给从库的 IO 线程。

### 2. 从库 IO Thread
从库的 **IO Thread** 连接到主库，接收 binlog 事件并写入本地的 **Relay Log**（中继日志）。

### 3. 从库 SQL Thread
从库的 **SQL Thread** 读取 Relay Log 中的事件，并在从库上重放执行。

```
Master                         Slave
+-----------+                  +------------+
| Binlog    | --Dump Thread--> | IO Thread  | --> Relay Log
+-----------+                  +------------+
                                    |
                                    v
                               +------------+
                               | SQL Thread | --> 重放执行
                               +------------+
```

### 异步复制 vs 半同步复制

- **异步复制（Asynchronous）**：默认模式。主库提交事务后，不等待从库确认即可返回客户端。
- **半同步复制（Semi-Sync）**：主库提交事务后，至少等待一个从库写入 Relay Log 并返回 ACK，才向客户端返回成功。

---

## 二、延迟原因分析

生产环境中，`Seconds_Behind_Master` 持续增大，通常由以下五大原因导致：

### 1. 大事务回放慢

这是最常见的延迟原因。一个大事务（如批量删除 100 万行、ALTER TABLE 加索引）在从库上由 SQL Thread **单线程串行回放**，会阻塞后续所有小事务，造成「队头阻塞」效应。

### 2. SQL Thread 单线程瓶颈

MySQL 5.6 之前从库只有一个 SQL Thread，无法利用多核 CPU。5.6 引入基于库（DATABASE）的并行复制，5.7 引入基于组提交（LOGICAL_CLOCK）的并行复制，8.0 优化了 WRITESET 模式。

### 3. 网络延迟与带宽瓶颈

主从跨机房、跨地域部署时，网络 RTT 可能达到几十甚至上百毫秒。binlog 传输受网络带宽限制。

### 4. 从库 IO 瓶颈

从库需要同时做两件事：IO Thread 写 Relay Log、SQL Thread 读 Relay Log 并重放。如果从库磁盘是 HDD 而非 SSD，磁盘 IO 会成为瓶颈。

### 5. 慢查询堆积

从库上如果有分析型查询（OLAP）、备份任务等耗时操作，会占用 CPU、内存、IO 资源，导致 SQL Thread 调度优先级降低。

---

## 三、监控与排查

### SHOW SLAVE STATUS

最基础的排查命令：

```sql
SHOW SLAVE STATUS\G
```

关键字段解读：

| 字段 | 含义 | 正常值 | 异常信号 |
|------|------|--------|----------|
| `Slave_IO_Running` | IO 线程状态 | Yes | No/Connecting 表示网络或权限问题 |
| `Slave_SQL_Running` | SQL 线程状态 | Yes | No 表示回放出错 |
| `Seconds_Behind_Master` | 延迟秒数 | 0~几秒 | 持续增大表示有延迟 |
| `Last_IO_Error` | IO 线程错误信息 | 空 | 非空表示具体错误原因 |
| `Last_SQL_Error` | SQL 线程错误信息 | 空 | 非空表示回放失败的具体 SQL |

> **注意**：`Seconds_Behind_Master` 的计算方式是「主库当前时间戳 - 从库 SQL Thread 当前处理事件的时间戳」。如果主库长时间没有写入，该值可能显示为 NULL 或 0。

### pt-heartbeat

Percona Toolkit 的 `pt-heartbeat` 工具通过在主库定期插入带时间戳的心跳记录，从库读取并与本地时间对比，得到真实的端到端延迟。精度可达毫秒级。

```bash
pt-heartbeat --daemonize --update --database percona --host=master_host
pt-heartbeat --check --database percona --host=slave_host
```

---

## 四、解决方案

### 1. 并行复制（Parallel Replication）

MySQL 5.7 引入基于 LOGICAL_CLOCK 的并行复制，允许从库使用多个 worker 线程并行回放事务。

```ini
# my.cnf 配置
[mysqld]
slave_parallel_type = LOGICAL_CLOCK    # 基于组提交的并行（5.7+推荐）
slave_parallel_workers = 16            # worker 线程数，建议设为 CPU 核数的 2-4 倍
master_info_repository = TABLE
relay_log_info_repository = TABLE
relay_log_recovery = ON
```

- `DATABASE` 模式（5.6）：不同数据库的事务可以并行
- `LOGICAL_CLOCK` 模式（5.7）：基于主库组提交的 timestamp，同一组提交的事务可以并行
- `WRITESET` 模式（8.0）：基于行的依赖关系检测，无依赖的事务即使不在同一组也能并行

> **调优建议**：`slave_parallel_workers` 不是越大越好，建议从 4-8 开始逐步调整。

### 2. 半同步复制（Semi-Synchronous Replication）

启用半同步复制，确保主库提交前至少有一个从库确认收到 binlog。

```ini
# 主库配置
[mysqld]
rpl_semi_sync_master_enabled = ON
rpl_semi_sync_master_timeout = 1000      # 超时 1 秒后降级为异步复制
rpl_semi_sync_master_wait_point = AFTER_SYNC  # 5.7+ 推荐

# 从库配置
[mysqld]
rpl_semi_sync_slave_enabled = ON
```

**AFTER_COMMIT vs AFTER_SYNC**：
- `AFTER_COMMIT`（5.6 及以前）：主库引擎层 commit 后等待从库 ACK，**主从切换时有丢数据风险**。
- `AFTER_SYNC`（5.7+ 推荐）：主库刷盘后等待从库 ACK，然后引擎层 commit。即使主库宕机，新主库一定拥有完整 binlog。

> **注意**：半同步复制会增加写延迟（约 1 个 RTT），适合对数据一致性要求高、网络质量好的场景。

### 3. 强制读主库

对于强一致性要求的读请求（如支付成功后查订单状态），直接路由到主库。

```java
// 伪代码：通过注解标记需要读主库的方法
@TargetDataSource("master")
public Order getOrderDetail(Long orderId) {
    return orderMapper.selectById(orderId);
}
```

实现方式：Session 级路由（用户登录后所有请求路由到主库）；方法级注解（通过 AOP 拦截，推荐）。

### 4. Group Replication（MGR）

MySQL 5.7 引入的组复制插件，基于 Paxos 协议实现多主一致性和自动故障转移。

```ini
[mysqld]
plugin_load_add = group_replication.so
group_replication_group_name = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
group_replication_local_address = "node1:33061"
group_replication_group_seeds = "node1:33061,node2:33061,node3:33061"
loose-group_replication_single_primary_mode = ON  # 单主模式（推荐）
```

MGR 的优势：强一致性、自动故障转移、无 binlog 位置管理。劣势：性能开销、网络要求高、运维复杂度高。

> **适用场景**：金融、电商等对数据一致性要求极高的核心业务。

---

## 五、业务层方案

### 1. 写后读一致性（Session 级路由）

用户在短时间内（如 30 秒）的写请求和后续读请求，都路由到主库。

```java
@Component
public class DataSourceRouter extends AbstractRoutingDataSource {
    private static final ThreadLocal<String> contextHolder = new ThreadLocal<>();
    public static void useMaster() { contextHolder.set("master"); }
    public static void useSlave() { contextHolder.set("slave"); }
    @Override
    protected Object determineCurrentLookupKey() { return contextHolder.get(); }
}

// AOP 拦截器：写操作后标记当前 Session 需读主库
@Aspect
@Component
public class WriteReadConsistencyAspect {
    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @AfterReturning("@annotation(writeOperation)")
    public void afterWrite(JoinPoint joinPoint, WriteOperation writeOperation) {
        String userId = getCurrentUserId();
        redisTemplate.opsForValue().set("force_master:" + userId, "1", 30, TimeUnit.SECONDS);
    }
}
```

### 2. 缓存标记法

对于热点数据，写入后在缓存中标记该 Key 需要在短时间内读主库。

```java
// 写入后标记 10 秒内读主库
redisTemplate.opsForValue().set("force_master_product:" + productId, "1", 10, TimeUnit.SECONDS);

// 读操作判断
String forceMaster = redisTemplate.opsForValue().get("force_master_product:" + productId);
if ("1".equals(forceMaster)) {
    product = productMapper.selectFromMaster(productId);
} else {
    product = productMapper.selectFromSlave(productId);
}
```

### 3. 重试与补偿

对于从库延迟导致的读取失败，可以在应用层做短暂休眠后重试，重试耗尽则降级读主库。

```java
public Product getProductWithRetry(Long productId, int maxRetries) {
    for (int i = 0; i < maxRetries; i++) {
        Product product = productMapper.selectFromSlave(productId);
        if (product != null) return product;
        try { Thread.sleep(100); } catch (InterruptedException e) { break; }
    }
    return productMapper.selectFromMaster(productId);
}
```

> **关键点**：标记时间不宜过长（5-30 秒足够）。

---

## 六、面试话术（30 秒版）

> 「MySQL 主从延迟的核心原因是 binlog 传输慢或 SQL 回放慢。常见场景包括大事务单线程回放、从库 IO 瓶颈、网络延迟等。解决思路分三层：**第一层是 MySQL 层面**，开启并行复制（slave_parallel_type=LOGICAL_CLOCK + 多个 worker 线程），必要时用半同步复制（AFTER_SYNC 模式）保证至少一份从库数据完整；**第二层是架构层面**，强一致性读请求强制路由到主库，或者上 MGR 组复制实现 Paxos 强一致；**第三层是业务层面**，写后短时间内通过 Session 或缓存标记，让该用户的读请求走主库，实现短时强一致性。实际项目中我们用的是『异步复制 + 并行复制 + 业务层写后读主库』的组合方案。」

---

## 七、交叉引用

- 主模块：[`03.database`](../../../03.database/) — 数据库知识体系
- 相关主题：[MySQL 核心知识](../../../03.database/05-mysql/README.md)、[MVCC 原理](../mvcc/README.md)、[索引优化](../../../03.database/04-index/README.md)

## 相关章节

- 深度阅读：[`03.database`](../../03.database/README.md) — 主模块详细内容
