<!--
module:
  parent: system-design
  slug: system-design/deduplication-table
  type: article
  category: 主模块子文章
  summary: 在消息队列（Kafka / RabbitMQ / RocketMQ）消费场景中，**单条消息可能被投递多次**（至少一次语义）。去重表是处理"消息幂等消费"最直...
-->

# 去重表（Deduplication Table）

> 在消息队列（Kafka / RabbitMQ / RocketMQ）消费场景中，**单条消息可能被投递多次**（至少一次语义）。去重表是处理"消息幂等消费"最直接有效的方案。

## 目录

- [原理](#原理)
- [适用场景](#适用场景)
- [代码实现](#代码实现)
- [进阶：分布式去重](#进阶分布式去重)
- [与业务表唯一约束的关系](#与业务表唯一约束的关系)
- [注意事项](#注意事项)
- [选型建议](#选型建议)
- [相关章节](#相关章节)
- [参考资料](#参考资料)

---
---

## 原理

```
                 ┌─────────────────┐
                 │   MQ Consumer   │
                 └────────┬────────┘
                          │
                          │ 1. 收到消息 messageId=MSG-001
                          ▼
                 ┌─────────────────┐
                 │ SELECT * FROM    │
                 │ dedup_log       │
                 │ WHERE msg_id=?  │ ──▶ 已存在? → ACK, return
                 └────────┬────────┘
                          │ 不存在
                          ▼
                 ┌─────────────────┐
                 │ 执行业务逻辑     │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ INSERT INTO      │
                 │ dedup_log ...   │ ──▶ 失败? → 不 ACK, 重试
                 └────────┬────────┘
                          │
                          ▼
                       ACK
```

### 关键点

1. **插入与业务事务绑定**：消费业务 + 插入去重记录必须在**同一事务**
2. **唯一约束兜底**：即使两个消费者并发处理，DB UNIQUE 约束保证只有一个成功
3. **定期清理**：去重表会无限增长，需要归档 / 删除过期记录

---

## 适用场景

- **消息队列消费**：Kafka / RocketMQ / RabbitMQ
- **定时任务调度**：同一任务在同一时间窗被多次触发
- **异步任务处理**：分布式任务系统
- **Webhook 接收**：第三方回调

**不适用**：

- 同步 API 调用（用 [Idempotency-Key](../idempotency-key/README.md) 更合适）
- 超高 QPS 写入（去重表 INSERT 会成为瓶颈）

---

## 代码实现

### 1. 表设计

```sql
CREATE TABLE deduplication_log (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    message_id    VARCHAR(64)  NOT NULL,
    topic         VARCHAR(128) NOT NULL,
    consumer      VARCHAR(64)  NOT NULL,        -- 消费方标识
    payload_hash  CHAR(64)     NULL,            -- 消息体 SHA256
    processed_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expire_at     DATETIME     NOT NULL,        -- 过期时间
    UNIQUE KEY uk_topic_msg (topic, message_id),
    INDEX idx_expire (expire_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

> **注意**：`UNIQUE (topic, message_id)` 是核心——同一 topic 下同一 messageId 只能插入一次。

### 2. Java 实现

#### DTO / 实体

```java
@Data
@Entity
@Table(name = "deduplication_log")
public class DeduplicationLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "message_id", nullable = false, length = 64)
    private String messageId;

    @Column(nullable = false, length = 128)
    private String topic;

    @Column(nullable = false, length = 64)
    private String consumer;

    @Column(name = "payload_hash", length = 64)
    private String payloadHash;

    @Column(name = "processed_at", nullable = false)
    private Instant processedAt;

    @Column(name = "expire_at", nullable = false)
    private Instant expireAt;
}
```

#### Repository

```java
public interface DeduplicationRepository
        extends JpaRepository<DeduplicationLog, Long> {

    boolean existsByTopicAndMessageId(String topic, String messageId);
}
```

#### 消费服务

```java
@Service
@Slf4j
public class OrderEventConsumer {

    @Autowired
    private DeduplicationRepository deduplicationRepo;

    @Autowired
    private OrderRepository orderRepo;

    /**
     * Kafka 消费示例
     */
    @KafkaListener(topics = "order-events")
    @Transactional
    public void onMessage(ConsumerRecord<String, String> record,
                          Acknowledgment ack) {
        String messageId = record.key();
        String topic = record.topic();
        String payload = record.value();
        String consumer = "order-event-consumer";

        // 1. 快速预检（减少不必要的业务调用）
        if (deduplicationRepo.existsByTopicAndMessageId(topic, messageId)) {
            log.info("消息已处理, 跳过: msgId={}, topic={}", messageId, topic);
            ack.acknowledge();
            return;
        }

        try {
            // 2. 解析消息
            OrderEvent event = objectMapper.readValue(payload, OrderEvent.class);

            // 3. 执行业务（订单状态更新等）
            processOrderEvent(event);

            // 4. 写入去重表
            DeduplicationLog log = new DeduplicationLog();
            log.setMessageId(messageId);
            log.setTopic(topic);
            log.setConsumer(consumer);
            log.setPayloadHash(sha256(payload));
            log.setProcessedAt(Instant.now());
            log.setExpireAt(Instant.now().plus(Duration.ofDays(7)));
            deduplicationRepo.save(log);   // UNIQUE 约束兜底

            // 5. ACK
            ack.acknowledge();
        } catch (DuplicateKeyException e) {
            // 并发场景：另一个 consumer 已写入
            log.info("消息并发处理, 已存在: msgId={}", messageId);
            ack.acknowledge();
        } catch (Exception e) {
            log.error("消息处理失败: msgId={}", messageId, e);
            // 不 ACK, 触发重试 / 进死信队列
        }
    }

    private void processOrderEvent(OrderEvent event) {
        // 业务逻辑...
    }
}
```

### 3. RocketMQ 消费示例

```java
@RocketMQMessageListener(
    topic = "pay-events",
    consumerGroup = "pay-consumer-group"
)
public class PayEventConsumer implements RocketMQListener<PayEvent> {

    @Override
    @Transactional
    public void onMessage(PayEvent event) {
        String messageId = event.getMessageId();
        if (deduplicationRepo.existsByTopicAndMessageId("pay-events", messageId)) {
            return;
        }

        // 业务
        payService.handle(event);

        // 写入去重
        DeduplicationLog log = new DeduplicationLog();
        log.setMessageId(messageId);
        log.setTopic("pay-events");
        log.setConsumer("pay-consumer-group");
        log.setPayloadHash(sha256(JSON.toJSONString(event)));
        log.setProcessedAt(Instant.now());
        log.setExpireAt(Instant.now().plus(Duration.ofDays(30)));
        deduplicationRepo.save(log);
    }
}
```

---

## 进阶：分布式去重

去重表基于**单库**，多库场景下需要重新设计：

### 方案 1：分片键 = messageId

```java
// messageId 哈希后选库
int dbIndex = Math.abs(messageId.hashCode()) % dbCount;
JdbcTemplate jdbc = dataSourceMap.get(dbIndex);
```

### 方案 2：去重表独立集群

去重表独立部署到专用库集群，不与业务库争抢资源。

### 方案 3：Redis BloomFilter

先用 BloomFilter 快速判断**消息是否绝对不存在**：

```java
// 启动时加载历史 messageId（异步）
// 消费时先查 BloomFilter
if (bloomFilter.mightContain(messageId)) {
    // 可能存在，查 DB 确认
    if (deduplicationRepo.exists(messageId)) return;
    // BloomFilter 误判，DB 没有，正常处理
}
bloomFilter.add(messageId);
```

> 优点：内存占用小（10 亿 messageId 约 1.5GB），O(1) 查询
> 缺点：有误判率（~1%），需要 DB 二次确认

### 方案 4：MQ 自身特性

- **RocketMQ**：每条消息有 `MessageId`，使用 `MessageListenerOrderly` 顺序消费可避免并发
- **Kafka**：使用 `enable.idempotence=true`（生产端去重），消费端仍需业务去重
- **RabbitMQ**：用 `Message ID` + 数据库唯一约束

---

## 与业务表唯一约束的关系

**能用业务表唯一约束的，优先用业务表**：

```sql
-- 案例：消息是"创建订单"
-- 直接在 orders 表加 UNIQUE
CREATE TABLE orders (
    id              BIGINT PRIMARY KEY,
    external_id     VARCHAR(64) NOT NULL,    -- 即 messageId
    UNIQUE KEY uk_external (external_id)
);
```

**需要去重表的场景**：

- 业务表已有，但**不能加唯一约束**（如老系统改造成本高）
- 多种消息共享同一张去重表
- 业务处理不直接落库（发通知、调外部 API）

---

## 注意事项

### 1. 清理过期数据

去重表会无限增长，必须定期清理：

```sql
-- 每天凌晨 3 点清理 7 天前的记录
DELETE FROM deduplication_log
WHERE expire_at < NOW()
LIMIT 10000;
```

或用 [TTL 特性](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl-operations.html)（MySQL 8.0 部分支持）。

### 2. 业务事务边界

```java
@Transactional
public void onMessage(...) {
    processBusiness();      // 业务
    deduplicationRepo.save(log);  // 去重记录
}
```

**必须同一事务**：业务成功 + 记录写入；任一失败 → 全部回滚，消息会重投。

### 3. 失败处理

| 场景 | 处理 |
|------|------|
| 业务失败 | 不 ACK / 不提交事务 → MQ 重投 |
| 重复消息 | 去重表命中 → 直接 ACK |
| 去重表写入失败 | 整事务回滚 → MQ 重投 |
| 数据库不可用 | 暂停消费 / 进死信队列 |

### 4. messageId 来源

| 来源 | 可靠性 |
|------|--------|
| 业务系统生成（UUID） | 高 |
| MQ 自带 MessageId | 中（部分 MQ 重启后会变） |
| 业务主键（如订单号） | 高 |
| 时间戳 | ❌ 不可靠（重复可能） |

### 5. 性能

- 单库去重表 INSERT 极限约 **5000 ~ 10000 QPS**
- 超过此值考虑分片 / 异步写入 / BloomFilter

---

## 选型建议

| 场景 | 推荐 |
|------|------|
| 中小规模 MQ 消费 | ✅ 单库去重表 |
| 高 QPS MQ 消费 | ✅ BloomFilter + 去重表 |
| 已有业务主键 | 优先业务表 UNIQUE 约束 |
| 多业务线共享去重 | ✅ 通用去重表（按 topic 区分） |
| 清理成本敏感 | ✅ 短 TTL（7 天）+ 自动清理 |

---

## 相关章节

- [Idempotency-Key 唯一标识](../idempotency-key/README.md) — HTTP 入口幂等
- [乐观锁 / Version](../optimistic-lock/README.md) — 并发更新场景
- [状态机](../state-machine/README.md) — 状态流转场景
- [与分布式事务的关系](../vs-distributed-transaction/README.md) — 消息 + 事务协调

## 参考资料

- [Kafka Consumer - 幂等消费模式](https://kafka.apache.org/documentation/#consumerapi)
- [RocketMQ - 消息幂等](https://rocketmq.apache.org/docs/4.x/bestpractice/)
- [RabbitMQ - Reliable Delivery](https://www.rabbitmq.com/docs/confirms)
- [Bloom Filter 原理与实现](https://llimllib.github.io/bloomfilter-tutorial/)
- [AWS SQS - Message Deduplication](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-deduplication-id.html)

← [返回: 系统设计 · deduplication-table](README.md)
