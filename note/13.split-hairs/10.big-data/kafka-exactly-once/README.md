<!--
question:
  id: 10.big-data-kafka-exactly-once
  topic: 10.big-data
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [10.big-data, Kafka, Exactly-Once, 幂等, 事务, Producer ID, Consumer Offset]
-->

# Kafka 如何实现端到端 Exactly-Once？

> 一句话定位：Kafka 从 0.11 版本开始，通过幂等 Producer + 事务 API + Consumer Offset 原子提交，首次实现了消息队列的 Exactly-Once 语义——但"端到端"远比想象中复杂。

> **系列定位**：经典大数据面试题（消息队列可靠性高频）。考察的不是"Kafka 支持 Exactly-Once"，而是 **三个层面的语义保障** + **Producer ID 与 Sequence Number 机制** + **事务协调器原理** + **端到端 Exactly-Once 的真正边界**。

---

## 引子：一笔订单被扣了两次款

```text
电商支付系统：
1. 用户下单 → 订单服务发送 "order_paid" 消息到 Kafka
2. 扣款服务消费消息 → 调用银行接口扣款 → 提交 offset
3. 网络抖动：扣款成功但 offset 提交失败
4. 消费者重启 → 重新消费同一条消息 → 又扣了一次款

结果：用户被扣了两次款，客服电话被打爆。
```

这就是 **At-Least-Once** 语义的代价——消息至少被处理一次，但可能重复。要解决这个问题，需要**端到端 Exactly-Once**——从 Producer 发送到 Consumer 处理再到结果输出，整条链路上每条消息只被"有效处理"一次。

Kafka 从 0.11 开始提供了解决方案的三个拼图：**幂等 Producer** + **事务 API** + **Consumer Offset 原子提交**。

---

## 一、核心原理

### 1.1 TL;DR：三种语义对比

| 语义 | 含义 | Kafka 实现方式 | 风险 |
|------|------|--------------|------|
| **At-Most-Once** | 最多一次（可能丢失） | Producer 发完即忘，Consumer 先提交 offset 再处理 | 消息丢失 |
| **At-Least-Once** | 至少一次（可能重复） | Producer 重试 + acks=all，Consumer 先处理再提交 offset | 消息重复 |
| **Exactly-Once** | 精确一次（不丢不重） | 幂等 Producer + 事务 + Offset 原子提交 | 性能降低 10-20% |

### 1.2 幂等 Producer（单 Partition Exactly-Once）

```text
核心机制：Producer ID + Sequence Number

1. Producer 初始化时，Broker 分配一个唯一的 Producer ID（PID）
2. Producer 发送到每个 Partition 的每条消息携带递增的 Sequence Number
3. Broker 端维护每个 PID + Partition 的 lastSequenceNumber
4. 收到消息时检查：
   - 新序号 = 上次序号 + 1 → 正常写入
   - 新序号 ≤ 上次序号 → 重复消息，丢弃（幂等）
   - 新序号 > 上次序号 + 1 → 乱序/丢失，抛 OutOfOrderSequenceException

保障范围：单个 Partition 内的去重
不能保障：跨 Partition 的原子写入
```

### 1.3 事务 API（跨 Partition Exactly-Once）

```text
核心机制：Transaction Coordinator + Transaction Log

1. Producer 调用 initTransactions() 注册事务
2. 调用 beginTransaction() 开始事务
3. 发送消息到多个 Topic/Partition（消息暂存在 Broker 端，标记为"未提交"）
4. 发送 offset 到 __consumer_offsets（也在同一事务中）
5. 调用 commitTransaction() → Coordinator 原子写入所有 Partition
6. 或调用 abortTransaction() → Coordinator 标记所有消息为"已中止"

Consumer 端配置：
- isolation.level = read_committed → 只读已提交的消息
- isolation.level = read_uncommitted → 读所有消息（默认，含未提交）
```

### 1.4 Transaction Coordinator 流程

```text
Producer                    Coordinator                  Broker (Partitions)
   |                            |                              |
   |-- initTransactions() ----->|                              |
   |<---- PID + epoch ----------|                              |
   |                            |                              |
   |-- beginTransaction() ----->|                              |
   |                            |                              |
   |-- send(msg, topic-A) ------------------------------>-----|
   |                            |                              |
   |-- send(msg, topic-B) ------------------------------>-----|
   |                            |                              |
   |-- sendOffsets(offsets) --->|                              |
   |                            |--- write txn log ----------->|
   |                            |                              |
   |-- commitTransaction() ---->|                              |
   |                            |--- write COMMIT marker ----->|  (所有 Partition)
   |                            |                              |
   |<---- success --------------|                              |
```

---

## 二、代码示例

### 2.1 幂等 Producer

```java
Properties props = new Properties();
props.put("bootstrap.servers", "kafka:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

// 开启幂等（自动设置 acks=all + retries > 0）
props.put("enable.idempotence", true);
props.put("acks", "all");
props.put("retries", 3);
props.put("max.in.flight.requests.per.connection", 5);  // 幂等模式下 <= 5 保证有序

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("orders", "key1", "order_paid"));
```

### 2.2 事务 Producer

```java
Properties props = new Properties();
props.put("bootstrap.servers", "kafka:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("enable.idempotence", true);
props.put("transactional.id", "payment-txn-001");  // 全局唯一，重启不变

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.initTransactions();

try {
    producer.beginTransaction();

    // 1. 处理消息并发送结果到下游 Topic
    producer.send(new ProducerRecord<>("payment_result", "order_123", "SUCCESS"));

    // 2. 原子提交 Consumer Offset（与消息发送在同一事务中）
    Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
    offsets.put(new TopicPartition("orders", 0), new OffsetAndMetadata(100L));
    producer.sendOffsetsToTransaction(offsets, consumer.groupMetadata());

    producer.commitTransaction();
} catch (Exception e) {
    producer.abortTransaction();
    // 重试或告警
}
```

### 2.3 Consumer 端配置

```java
Properties consumerProps = new Properties();
consumerProps.put("bootstrap.servers", "kafka:9092");
consumerProps.put("group.id", "payment-service");
consumerProps.put("enable.auto.commit", false);  // 禁用自动提交！

// 只读已提交的消息（过滤掉未提交和中止的消息）
consumerProps.put("isolation.level", "read_committed");

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(consumerProps);
consumer.subscribe(Arrays.asList("orders"));

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        processPayment(record);  // 业务处理
    }
    // offset 在 Producer 事务中提交，不在 Consumer 端提交
}
```

### 2.4 Kafka Streams 的 Exactly-Once

```java
Properties streamsProps = new Properties();
streamsProps.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
streamsProps.put(StreamsConfig.APPLICATION_ID_CONFIG, "payment-streams");

// Exactly-Once v2（Kafka 2.6+，性能更好）
streamsProps.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);

StreamsBuilder builder = new StreamsBuilder();
builder.<String, String>stream("orders")
    .filter((key, value) -> value.contains("PAID"))
    .mapValues(value -> processOrder(value))
    .to("payment_result");

KafkaStreams streams = new KafkaStreams(builder.build(), streamsProps);
streams.start();
```

---

## 三、常见陷阱

### 陷阱 1：Exactly-Once 只保障 Kafka 内部
- **真相**：Kafka 的 Exactly-Once 保障的是"消息写入 Kafka + Offset 提交"的原子性。如果 Consumer 处理后调用了**外部系统**（数据库、API），Kafka 无法保障外部系统的幂等性。真正的端到端 Exactly-Once 需要外部系统也支持幂等或事务（如数据库的 INSERT ON CONFLICT）。

### 陷阱 2：transactional.id 重启后必须不变
- **真相**：`transactional.id` 是事务协调器识别 Producer 的唯一标识。重启后换了 ID，旧事务会被认为超时中止，新事务的 PID 不同无法去重。通常按 **应用实例 + 分片号** 命名，如 `payment-txn-{instanceId}`。

### 陷阱 3：事务模式下的性能开销
- **真相**：事务 API 引入了 Transaction Coordinator 的额外 RPC + 事务日志写入 + COMMIT marker 写入。实测吞吐量比 At-Least-Once 降低 **10-20%**，延迟增加 **5-20ms**。非关键场景（日志、指标）不需要开启。

### 陷阱 4：Consumer 的 isolation.level 默认是 read_uncommitted
- **真相**：如果 Consumer 没有配置 `isolation.level = read_committed`，即使 Producer 使用了事务，Consumer 也会读到未提交和中止的消息。这是最常见的"明明开了事务还是读到重复数据"的原因。

### 陷阱 5：Producer 的 zombie fencing
- **真相**：当同一个 `transactional.id` 的新 Producer 启动时，Coordinator 会中止旧 Producer 的未完成事务（通过 epoch 机制）。这防止了"僵尸 Producer"的脏数据，但也意味着旧 Producer 的后续写入会被拒绝。

---

## 四、最佳实践

```text
Kafka Exactly-Once 使用决策树：
├── 消息丢失可接受？（日志/指标/埋点）
│   └── → At-Least-Once（无需幂等/事务，性能最优）
├── 单 Partition 去重就够？
│   └── → 幂等 Producer（enable.idempotence = true）
├── 需要跨 Partition 原子写入 + Offset 提交？
│   └── → 事务 API（transactional.id + sendOffsetsToTransaction）
├── Consumer 处理结果写入外部系统？
│   ├── → 外部系统支持幂等（UPSERT / INSERT ON CONFLICT）→ Kafka 事务 + 幂等写入
│   └── → 外部系统不支持幂等 → 两阶段提交 / Saga 模式
└── 使用 Kafka Streams？
    └── → PROCESSING_GUARANTEE = EXACTLY_ONCE_V2（内置全流程保障）
```

---

## 五、面试话术（90 秒版本）

> "Kafka 的 Exactly-Once 语义由三个机制组合实现：**幂等 Producer** 通过 Producer ID + Sequence Number 实现单 Partition 内去重；**事务 API** 通过 Transaction Coordinator + 事务日志实现跨 Partition 原子写入，将消息发送和 Offset 提交放在同一个事务中；**Consumer 端**配置 `isolation.level = read_committed` 只读已提交的消息。"
>
> "但要注意 Kafka 的 Exactly-Once 只保障 **Kafka 内部**的精确一次。真正的端到端 Exactly-Once 需要下游系统也支持幂等——比如数据库用 UPSERT，API 调用用幂等键。如果下游不支持，Kafka 事务也救不了你。"
>
> "生产中我通常在关键环节开启事务（订单、支付），日志和指标场景用 At-Least-Once 就够了。事务模式的性能开销大约 10-20%，transactional.id 必须在重启后保持不变，否则旧事务会被中止。"

---

## 六、交叉引用

- **同栏目**：[`Flink Checkpoint vs Savepoint`](../flink-checkpoint-vs-savepoint/README.md) — Flink + Kafka 的端到端 Exactly-Once 联动
- **同栏目**：[`Iceberg ACID`](../iceberg-acid/README.md) — 数据湖层面的事务保障对比
- **同栏目**：[`Doris vs ClickHouse`](../doris-vs-clickhouse/README.md) — Doris Routine Load 的 Exactly-Once 导入
- **主模块**：[`04.system-design`](../../../04.system-design/README.md) — 分布式事务与一致性模式

---

> 📅 2026-07-16 · 咬文嚼字 · 大数据 · 消息可靠性 · ⭐⭐⭐⭐⭐

← [返回: 咬文嚼字 · 大数据](../README.md)
