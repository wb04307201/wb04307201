<!--
question:
  id: 04.system-design-still-need-rocketmq
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [04.system-design, still, need]
-->

# 有了 Kafka 为什么还要 RocketMQ？

## 引子：两个消息队列，该怎么选？

```
Kafka：百万 TPS，日志采集利器
RocketMQ：金融级可靠性，事务消息

你的场景：电商订单系统
→ 需要事务消息（下单 → 扣库存 → 支付，要么全成功要么全失败）
→ 需要延时消息（30 分钟未支付自动取消）
→ 需要精确投递（消息不能丢）

选 Kafka？还是 RocketMQ？
```

Kafka 和 RocketMQ 的设计哲学完全不同：
- **Kafka**：追求极致吞吐量，牺牲部分功能
- **RocketMQ**：追求金融级可靠性，功能丰富

没有谁更好，只有谁更适合。

---

## 一、核心原理

Kafka 和 RocketMQ 都是分布式消息队列领域的优秀代表，但它们的设计哲学和目标场景存在本质差异：

### 1. 设计目标的根本分歧
- **Kafka**：以**高吞吐量**为核心目标，源于 LinkedIn 的大数据日志采集场景。采用顺序写磁盘、零拷贝（Zero-Copy）、批量发送等极致优化，单机可支撑百万级 TPS。牺牲部分功能特性（如延时消息、事务消息）换取性能。
- **RocketMQ**：以**金融级可靠性**为核心目标，源于阿里巴巴的交易链路场景。强调消息不丢失、事务一致性、精确投递，在保持较高吞吐量的同时提供丰富的企业级功能。

### 2. 架构对比
| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 吞吐量 | ⭐⭐⭐⭐⭐（千万级 TPS） | ⭐⭐⭐⭐（百万级 TPS） |
| 延迟 | ⭐⭐⭐（毫秒级） | ⭐⭐⭐⭐（亚毫秒级） |
| 消息可靠性 | 可能丢失（异步刷盘） | 零丢失（同步刷盘） |
| 事务消息 | 不支持 | 原生支持 |
| 延时消息 | 需自行实现 | 原生支持（18 个级别） |
| 消息回溯 | 基于时间偏移量 | 基于时间戳任意回溯 |
| 消费模式 | Pull 为主 | Push + Pull |
| 典型场景 | 日志采集、实时计算 | 订单交易、支付通知 |

### 3. 为什么不能"一招鲜"？
- **大数据场景不需要事务**：Hadoop/Spark 消费 Kafka 数据做离线分析，允许少量数据重复或丢失（通过幂等性兜底），但要求极高的写入吞吐。
- **交易场景不能接受丢失**：订单创建、支付回调等核心链路，消息丢失意味着资损，必须保证 Exactly-Once 语义。
- **功能与性能的权衡**：RocketMQ 的事务消息、延时消息等功能引入了额外的协调开销，吞吐量约为 Kafka 的 1/5~1/10，但在交易场景中这是可接受的代价。

---

## 二、代码示例

以下展示 RocketMQ 相比 Kafka 独有的核心功能：

```java
// ==================== 功能1：事务消息（Transactional Message）====================
// 场景：订单创建与库存扣减的最终一致性
public class TransactionalMessageExample {

    @Autowired
    private TransactionMQProducer transactionProducer;

    public void createOrderWithStockDeduction(Order order) {
        // 1. 发送半消息（Prepare 状态，消费者不可见）
        Message msg = new Message("OrderTopic", "create", JSON.toJSONString(order).getBytes());
        SendResult sendResult = transactionProducer.sendMessageInTransaction(msg, order);

        if (sendResult.getSendStatus() == SendStatus.SEND_OK) {
            System.out.println("半消息发送成功");
        }
    }

    // 2. 本地事务执行器
    @Bean
    public TransactionListener transactionListener() {
        return new TransactionListener() {
            @Override
            public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
                Order order = (Order) arg;
                try {
                    // 执行本地事务：创建订单 + 扣减库存
                    orderService.createOrder(order);
                    stockService.deductStock(order.getItemId(), order.getQuantity());
                    return LocalTransactionState.COMMIT_MESSAGE; // 提交消息，对消费者可见
                } catch (Exception e) {
                    return LocalTransactionState.ROLLBACK_MESSAGE; // 回滚消息，丢弃
                }
            }

            @Override
            public LocalTransactionState checkLocalTransaction(MessageExt msg) {
                // 3. 事务回查：若 Broker 未收到 Commit/Rollback，会定期回查
                String orderId = msg.getKeys();
                Order order = orderService.findById(orderId);
                if (order != null && order.getStatus() == OrderStatus.CREATED) {
                    return LocalTransactionState.COMMIT_MESSAGE;
                }
                return LocalTransactionState.UNKNOW; // 继续等待下次回查
            }
        };
    }
}

// ==================== 功能2：延时消息（Delayed Message）====================
// 场景：订单 30 分钟未支付自动取消
public class DelayedMessageExample {

    @Autowired
    private DefaultMQProducer producer;

    public void sendOrderTimeoutMessage(Order order) {
        Message msg = new Message("OrderTimeoutTopic", "timeout",
                                  order.getId().toString(),
                                  JSON.toJSONString(order).getBytes());

        // 设置延时级别（RocketMQ 预定义 18 个级别）
        // Level 1: 1s, Level 2: 5s, Level 3: 10s, ..., Level 16: 30m
        msg.setDelayTimeLevel(16); // 30 分钟后投递

        SendResult result = producer.send(msg);
        System.out.println("延时消息发送成功，msgId=" + result.getMsgId());
    }

    // 消费者：30 分钟后才会收到消息
    @RocketMQMessageListener(topic = "OrderTimeoutTopic", consumerGroup = "order-timeout-group")
    public class OrderTimeoutConsumer implements RocketMQListener<MessageExt> {
        @Override
        public void onMessage(MessageExt message) {
            Order order = JSON.parseObject(new String(message.getBody()), Order.class);
            if (order.getStatus() == OrderStatus.UNPAID) {
                orderService.cancelOrder(order.getId()); // 自动取消未支付订单
            }
        }
    }
}

// ==================== 功能3：消息回溯（Message Trace Back）====================
// 场景：重新消费昨天某一时段的消息进行数据修复
public class MessageTraceBackExample {

    public void replayMessages(String topic, long timestamp) {
        DefaultLitePullConsumer consumer = new DefaultLitePullConsumer("replay-group");
        consumer.setNamesrvAddr("127.0.0.1:9876");
        consumer.subscribe(topic, "*");

        // 将消费位点重置到指定时间戳
        long targetTime = timestamp; // 昨天的某个时间点
        consumer.seek(targetTime);

        while (true) {
            List<MessageExt> messages = consumer.poll();
            for (MessageExt msg : messages) {
                // 重新处理消息
                processMessage(msg);
            }
        }
    }
}

// ==================== 功能4：标签过滤（Tag Filter）====================
// 场景：不同业务线订阅同一 Topic 的不同标签
public class TagFilterExample {

    // 生产者：发送带标签的消息
    public void sendWithTags(Order order) {
        String tag = order.getOrderType() == OrderType.NORMAL ? "normal" : "vip";
        Message msg = new Message("OrderTopic", tag,
                                  JSON.toJSONString(order).getBytes());
        producer.send(msg);
    }

    // 消费者 A：只订阅普通订单
    @RocketMQMessageListener(topic = "OrderTopic", selectorExpression = "normal")
    public class NormalOrderConsumer implements RocketMQListener<MessageExt> { ... }

    // 消费者 B：只订阅 VIP 订单
    @RocketMQMessageListener(topic = "OrderTopic", selectorExpression = "vip")
    public class VipOrderConsumer implements RocketMQListener<MessageExt> { ... }
}
```

---

## 三、常见陷阱

### 1. 误认为 RocketMQ 一定比 Kafka 慢
很多人认为"功能多=性能差"，但实际上：
- **异步刷盘模式下**，RocketMQ 的吞吐量与 Kafka 相当（单机数万 TPS）。
- **同步刷盘模式下**，吞吐量确实下降（约 Kafka 的 1/5），但换来的是零数据丢失保障。
- **关键指标是 P99 延迟**：RocketMQ 的 Push 消费模型能实现亚毫秒级推送，而 Kafka 的 Pull 模型在低频消息场景下可能有秒级延迟。

### 2. 事务消息的使用误区
```java
// ❌ 错误做法：在半消息发送前执行本地事务
orderService.createOrder(order);  // 先执行
transactionProducer.send(...);    // 后发消息 → 若发送失败，无法回滚

// ✅ 正确做法：在半消息发送后的 Listener 中执行本地事务
transactionProducer.sendMessageInTransaction(msg, order);
// Listener 内：执行本地事务 → 根据结果返回 COMMIT/ROLLBACK
```

### 3. 延时消息的级别限制
RocketMQ 默认的 18 个延时级别是固定的：
```
Level:  1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18
Time:   1s  5s  10s 30s 1m  2m  3m  4m  5m  6m  7m  8m  9m  10m 20m 30m 1h  2h
```
若需要自定义延时时间（如 45 分钟），需修改 Broker 配置 `messageDelayLevel` 并重启，或使用 RocketMQ 5.x 的定时消息新功能（支持任意时间戳）。

### 4. 消费者幂等性缺失
RocketMQ 保证**至少投递一次**（At-Least-Once），网络抖动时可能重复投递。消费者必须实现幂等性：
```java
// ✅ 推荐：基于唯一键的幂等性
@Autowired
private RedisTemplate<String, String> redisTemplate;

public void onMessage(MessageExt message) {
    String msgId = message.getMsgId();
    Boolean isFirst = redisTemplate.opsForValue()
        .setIfAbsent("msg_processed:" + msgId, "1", 24, TimeUnit.HOURS);

    if (!Boolean.TRUE.equals(isFirst)) {
        return; // 已处理过，直接返回
    }

    // 处理业务逻辑...
}
```

### 5. NameServer 的单点风险
RocketMQ 依赖 NameServer 进行服务发现，若所有 NameServer 节点宕机，生产者将无法发送消息。**解决方案**：
- 部署至少 2 个 NameServer 节点。
- 生产者客户端配置多个地址：`producer.setNamesrvAddr("ns1:9876;ns2:9876")`。
- 使用 DNS 或负载均衡器提供虚拟 IP，隐藏真实 NameServer 地址。

---

## 四、最佳实践

### 1. 技术选型决策树
```
是否需要事务消息 / 延时消息？
├─ 是 → 选择 RocketMQ
└─ 否 ↓
    是否需要超高吞吐量（>10万 TPS）？
    ├─ 是 → 选择 Kafka
    └─ 否 ↓
        是否需要低延迟推送（<1ms）？
        ├─ 是 → 选择 RocketMQ
        └─ 否 → 根据团队技术栈决定
```

### 2. RocketMQ 的性能调优
```properties
# Broker 配置优化
flushDiskType=ASYNC_FLUSH          # 异步刷盘（性能优先）
# flushDiskType=SYNC_FLUSH         # 同步刷盘（可靠性优先）
sendMessageThreadPoolNums=16       # 发送线程池大小
useReentrantLockWhenPutMessage=true # 使用可重入锁提升并发

# Producer 配置优化
producer.setSendMsgTimeout(3000);  # 发送超时 3 秒
producer.setRetryTimesWhenSendFailed(2); # 失败重试 2 次
producer.setCompressMsgBodyOverHowmuch(4096); # 超过 4KB 压缩
```

### 3. 消息可靠性保障体系
- **生产端**：启用事务消息或同步发送 + 重试机制。
- **存储端**：主从同步复制（`brokerRole=SYNC_MASTER`），确保 Master 宕机时 Slave 有完整数据。
- **消费端**：手动 ACK（`ConsumeConcurrentlyStatus.CONSUME_SUCCESS`），业务处理完成后再确认。
- **监控端**：接入 Prometheus + Grafana，监控消息堆积量、投递延迟、消费失败率。

### 4. 消息堆积的应急处理
```bash
# 步骤1：临时扩容消费者
# 增加 Consumer 实例数量（不超过 Queue 数量）

# 步骤2：跳过非关键消息
# 修改消费逻辑，将非核心消息直接丢弃或转存到文件

# 步骤3：使用 Admin 工具重置位点
sh mqadmin resetOffsetByTime \
   -n "nameserver:9876" \
   -g "consumer-group" \
   -t "topic-name" \
   -s "2024-01-01#00:00:00"  # 重置到最近
```

### 5. 混合部署策略
在大型系统中，Kafka 和 RocketMQ 可以共存：
- **Kafka**：承载日志采集、用户行为追踪、实时计算等高吞吐场景。
- **RocketMQ**：承载订单交易、支付通知、会员积分等强一致性场景。
通过统一的消息网关（Message Gateway）屏蔽底层差异，上层业务按需选择通道。

---

## 五、面试话术

**面试官**："既然 Kafka 吞吐量这么高，为什么阿里还要搞 RocketMQ？"

**参考回答**：
> "这本质上是**场景驱动技术选型**的问题。Kafka 和 RocketMQ 解决的是两类不同的问题。
>
> Kafka 的优势在于极致吞吐量，适合日志采集、实时计算这类允许少量数据丢失、但要求高并发写入的场景。它的异步刷盘机制使得单机可以轻松达到百万 TPS，但在 Broker 宕机时可能丢失内存中尚未落盘的消息。
>
> RocketMQ 的核心价值是**金融级可靠性**。它支持同步刷盘（消息落盘后才返回 ACK）、事务消息（本地事务与消息发送的原子性）、延时消息（无需外部定时器），这些功能在交易场景中是刚需。比如淘宝的下单流程，订单创建和库存扣减必须保证最终一致性，用 Kafka 需要自己在应用层实现复杂的补偿逻辑，而 RocketMQ 通过事务消息一条语句就搞定。
>
> 在实际架构中，我们通常会根据业务属性做分层：用户行为日志走 Kafka，订单支付走 RocketMQ。两者不是替代关系，而是互补关系。如果团队只能维护一套 MQ，且业务以交易为主，那 RocketMQ 是更安全的选择；如果是大数据平台，Kafka 的生态整合度（Flink、Spark、Hadoop）更好。"

**加分项**：提及 RocketMQ 在 Apache 基金会的孵化历程，或讨论 Dledger 架构（Raft 共识算法）带来的高可用提升。

---

## 六、交叉引用

- 消息队列选型指南见 [MQ 核心原理](../../../../../04.system-design/04-high-performance/mq/README.md)

## 相关章节

- 深度阅读：[`04.system-design`](../../../../04.system-design/README.md) — 主模块详细内容

## 相关章节

- 排查实战：[`支付消息丢失排查`](../../../payment-message-lost/README.md) — MQ 可靠性在支付场景的实战排查

← [返回: 咬文嚼字 · still-need-rocketmq](README.md)
