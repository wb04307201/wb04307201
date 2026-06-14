# Spring Cloud Bus 集群事件总线

> 最后更新: 2026-06-14
> ⬅️ [返回 05 Spring Cloud](README.md) | [Stream](stream.md) | [Config 中心](config-center.md)

**Spring Cloud Bus** 用**轻量级消息代理**（Kafka / RabbitMQ）连接分布式系统的**所有节点**，通过单一指令触发**全集群广播**。最经典用途：**Spring Cloud Config 配置实时刷新**。

---

## 一、用途

| 场景 | 说明 |
|------|------|
| **Config 实时推送** | Git 仓库配置变更后，触发一次 `/actuator/busrefresh`，全集群节点收到通知并刷新 `@RefreshScope` Bean |
| **集群广播** | 自定义事件投递到所有实例（如缓存清理、灰度指令） |
| **运维指令** | 批量重启、热加载证书、动态日志级别 |

---

## 二、传输依赖

```xml
<!-- Kafka transport -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-bus-kafka</artifactId>
</dependency>

<!-- 或 RabbitMQ transport -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-bus-amqp</artifactId>
</dependency>
```

二者**二选一**，不可同时引入。

---

## 三、配置

```yaml
spring:
  cloud:
    bus:
      enabled: true
      destination: spring-cloud-bus   # 默认 topic / exchange 名
      ack:
        enabled: true                # 开启 ack 确认
  kafka:
    bootstrap-servers: localhost:9092

management:
  endpoints:
    web:
      exposure:
        include: busrefresh,busenv   # 暴露 actuator 端点
```

---

## 四、关键端点

| 端点 | 方法 | 作用 |
|------|------|------|
| `/actuator/busrefresh` (POST) | 全集群刷新配置 | 所有节点重新拉取 Config |
| `/actuator/busrefresh/{destination}` | 指定服务刷新 | 仅 `service-id:**` 节点刷新 |
| `/actuator/busevent/{event}` (POST) | 自定义事件广播 | 投递任意 JSON 到所有节点 |

### 示例：触发刷新

```bash
# 触发全集群配置刷新
curl -X POST http://config-server:8080/actuator/busrefresh

# 仅刷新 order-service 实例
curl -X POST http://config-server:8080/actuator/busrefresh/order-service:**
```

---

## 五、与 Nacos Config 长轮询对比

| 维度 | Spring Cloud Bus | Nacos Config |
|------|------------------|--------------|
| **传输** | Kafka / RabbitMQ | Nacos Server（HTTP 长轮询） |
| **触发方式** | 调用 `/actuator/busrefresh` 主动推送 | 客户端长轮询自动感知变更 |
| **运维依赖** | 需额外部署 Kafka / RabbitMQ | 仅需 Nacos（注册+配置二合一） |
| **延迟** | 100ms ~ 数秒 | 取决于轮询间隔（默认 30s 长轮询） |
| **适合场景** | Spring Cloud Config 配套、已有 Kafka | 国内主流、追求一站式 |

**结论**：2026 年新项目**首选 Nacos Config**（详见 [config-center.md](config-center.md)），Bus 仅在已有 Kafka 基础设施 + 使用 Spring Cloud Config 时推荐。

---

## 六、自定义事件广播

```java
// 1. 自定义事件
public class CacheClearEvent extends RemoteApplicationEvent {
    private String cacheName;
    // getters/setters...
}

// 2. 发布事件
@Resource
private BusProperties busProperties;

public void clearCache(String name) {
    CacheClearEvent event = new CacheClearEvent(this, busProperties.getId(),
            new HashMap<>());
    event.setCacheName(name);
    applicationEventPublisher.publishEvent(event);
}

// 3. 监听事件
@Component
public class CacheClearListener {
    @EventListener
    public void onEvent(CacheClearEvent event) {
        log.info("收到集群广播: 清空缓存 {}", event.getCacheName());
        cacheManager.getCache(event.getCacheName()).clear();
    }
}
```

---

## 相关章节

- ⬅️ [返回 05 Spring Cloud](README.md)
- [Config 中心](config-center.md) — Spring Cloud Config + Bus 经典组合
- [Spring Cloud Stream](stream.md) — 业务消息驱动
- [Spring Cloud 与 Alibaba 关系](README.md#spring-cloud-与-spring-cloud-alibaba-关系)