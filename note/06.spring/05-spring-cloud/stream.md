# Spring Cloud Stream 消息驱动微服务

> 最后更新: 2026-06-14
> ⬅️ [返回 05 Spring Cloud](README.md) | [Config 中心](config-center.md) | [Bus](bus.md)

**Spring Cloud Stream** 把消息中间件（Kafka / RabbitMQ / RocketMQ）的差异**封装在 Binder 后面**，让业务代码只面向 `Supplier` / `Consumer` / `Function` 编程。换底层 MQ **不改业务代码**。

---

## 一、核心抽象

```text
┌─────────────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐
│  Supplier   │ -> │  Binder  │ -> │   MQ     │ -> │ Consumer│
│ (生产)      │    │ (绑定器) │    │ Kafka等  │    │  (消费) │
└─────────────┘    └──────────┘    └──────────┘    └─────────┘
```

| 抽象 | 角色 | 典型场景 |
|------|------|---------|
| **`Supplier`** | 消息生产者 | 定时任务投递、状态变更广播 |
| **`Consumer`** | 消息消费者 | 订单创建后通知库存 |
| **`Function<T,R>`** | 一进一出处理 | 消息转换、过滤、路由 |

---

## 二、Binder：屏蔽 MQ 差异

| Binder 依赖 | 支持的消息中间件 |
|------------|---------------|
| `spring-cloud-stream-binder-kafka` | Apache Kafka |
| `spring-cloud-stream-binder-rabbit` | RabbitMQ |
| `spring-cloud-stream-binder-rocketmq` | Apache RocketMQ（阿里） |

依赖切换即可换 MQ，业务代码不变。

---

## 三、3.x 之前：`@EnableBinding`（已废弃）

```java
@EnableBinding(Source.class)
public class OrderProducer {

    @Autowired
    private Source source;

    public void send(OrderEvent event) {
        source.output().send(MessageBuilder.withPayload(event).build());
    }
}
```

`Source` / `Sink` / `Processor` 是预定义接口，绑定 channel 名。

---

## 四、3.x 之后：函数式编程模型（推荐）

### 生产者 `Supplier`

```java
@Bean
public Supplier<OrderEvent> orderSupplier() {
    return () -> {
        // 定时或事件触发投递
        return new OrderEvent("ORDER_" + System.currentTimeMillis());
    };
}
```

### 消费者 `Consumer`

```java
@Bean
public Consumer<OrderEvent> orderConsumer(InventoryService inventory) {
    return event -> {
        log.info("收到订单事件: {}", event);
        inventory.reduceStock(event.getSkuId(), event.getQty());
    };
}
```

### 处理器 `Function`

```java
@Bean
public Function<OrderEvent, ShipmentEvent> orderToShipment(
        ShippingService shipping) {
    return order -> {
        String trackingNo = shipping.bookCarrier(order);
        return new ShipmentEvent(order.getOrderId(), trackingNo);
    };
}
```

---

## 五、配置文件

```yaml
spring:
  cloud:
    stream:
      bindings:
        orderSupplier-out-0:
          destination: orders          # topic / exchange 名
          content-type: application/json
        orderConsumer-in-0:
          destination: orders
          group: inventory-svc         # 消费组（MQ 概念）
        orderToShipment-in-0:
          destination: orders
        orderToShipment-out-0:
          destination: shipments
```

---

## 六、消息分区 / 消费组 / 错误处理

### 1. 消费组

```yaml
spring.cloud.stream.bindings.orderConsumer-in-0.group: inventory-svc
```

同组多个实例**竞争消费**（MQ 队列语义）；不同组**全量广播**。

### 2. 分区（Partition）

```yaml
spring.cloud.stream.bindings.orderConsumer-in-0.consumer.partitioned: true
spring.cloud.stream.bindings.orderConsumer-in-0.consumer.instance-count: 3
spring.cloud.stream.bindings.orderConsumer-in-0.consumer.instance-index: 0
```

相同 key 的消息**路由到同一分区实例**，保证**有序消费**。

### 3. 错误处理

```yaml
spring.cloud.stream.bindings.orderConsumer-in-0.consumer.max-attempts: 3
spring.cloud.stream.bindings.orderConsumer-in-0.consumer.default-retryable: true
spring.cloud.stream.kafka.binder.auto-create-topics: true
```

失败 → 退避重试 → 进入 **DLQ**（Dead Letter Queue）。

---

## 七、与 Spring Cloud Bus 的区别

| 维度 | Spring Cloud Stream | Spring Cloud Bus |
|------|---------------------|------------------|
| **定位** | 业务消息（订单 / 事件） | 集群管理消息（配置刷新 / 广播） |
| **场景** | 微服务间解耦通信 | Config 实时推送、集群事件广播 |
| **抽象** | `Supplier` / `Consumer` / `Function` | `/actuator/busrefresh` 端点 |

详见 [bus.md](bus.md)。

---

## 相关章节

- ⬅️ [返回 05 Spring Cloud](README.md)
- [Spring Cloud Bus](bus.md) — 集群事件广播
- [Config 中心](config-center.md) — 配置实时推送
- ➡️ [06 集成组件/RocketMQ](../06-integration/) — 阿里消息中间件原生 API