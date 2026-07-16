<!--
question:
  id: cloud-registry-comparison
  topic: 06.spring
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 架构决策困境
  tags: [Spring Cloud, Nacos, Eureka, Consul, 服务注册发现]
-->

# Spring Cloud 注册中心选型：Nacos vs Eureka vs Consul vs Zookeeper

> 一句话定位：注册中心是微服务的"通讯录" —— 选型错误轻则运维成本高，重则服务雪崩。核心决策点在 CAP 取舍和生态适配。

> **系列定位**：经典 Spring Cloud 面试题（微服务架构、注册发现中频）。考察的不是"谁的功能多"，而是 **CAP 原理在注册中心的应用** + **健康检查机制差异** + **生产环境选型判断力**。

---

## 引子：新项目技术选型会上的四人争吵

```text
架构师 A："用 Eureka，Spring Cloud 官方推荐，Netflix 出品。"
架构师 B："Eureka 2.x 早停更了，应该用 Nacos，阿里开源，功能全面。"
架构师 C："Consul 有 DNS 支持和 KV 存储，HashiCorp 生态好。"
架构师 D："Zookeeper 用了五年了，稳定可靠，为什么要换？"

四个人四个意见，谁也说服不了谁。
```

争论的本质不是"谁更好"，而是"谁更适合你的场景"。每个注册中心都有自己的设计哲学：Eureka 追求高可用（AP），Nacos 支持 AP/CP 切换且自带配置中心，Consul 追求强一致（CP），Zookeeper 是通用协调服务而注册中心只是"副业"。

---

> 📚 **前置知识**：[CAP 定理](../../04.system-design/cap-theorem/README.md) | [微服务架构](../../04.system-design/README.md)

## 一、核心原理

### 1.1 注册中心的核心职责

服务提供者注册自己的地址 → 注册中心 → 服务消费者获取地址列表 → 直接调用。附加职责：健康检查、配置管理（Nacos/Consul）、DNS 解析（Consul）。

### 1.2 CAP 定理在注册中心的体现

| 选择 | 含义 | 代表 |
|------|------|------|
| **AP** | 网络分区时每个分区都能响应，可能返回旧数据 | Eureka、Nacos（默认） |
| **CP** | 只有多数派分区能响应，保证数据一致 | Consul、Zookeeper |

大多数微服务场景 **AP 更合适** —— 宁可返回可能过期的地址（客户端重试兜底），也不要注册中心整体不可用。

### 1.3 健康检查机制对比

| 注册中心 | 方式 | 延迟 |
|---------|------|------|
| **Eureka** | 客户端心跳（Push），30s/次，90s 无心跳移除 | 90 秒 |
| **Nacos** | 心跳（临时实例 15s）/ TCP 探测（持久实例） | 15-60 秒 |
| **Consul** | 服务端主动探测（Pull），10s/次 | 10 秒 |
| **Zookeeper** | 临时节点 + 会话超时（默认 30s） | 30 秒 |

---

## 二、代码示例：Spring Cloud + Nacos

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
```

```yaml
spring:
  application:
    name: order-service
  cloud:
    nacos:
      discovery:
        server-addr: nacos-server:8848
        namespace: prod          # 命名空间隔离（dev/test/prod）
        group: ORDER_GROUP       # 分组（业务域隔离）
        cluster-name: beijing    # 同集群优先调用
        ephemeral: true          # 临时实例（AP）vs 持久实例（CP）
        metadata:
          version: v2
```

```java
// 服务发现 + 负载均衡调用
@Bean @LoadBalanced
public RestTemplate restTemplate() { return new RestTemplate(); }

// "http://user-service" 会被 LoadBalancer 解析为实际地址
restTemplate.getForObject("http://user-service/api/user/" + id, User.class);
```

---

## 三、常见陷阱

### 陷阱 1：Eureka 自我保护导致"僵尸实例"
- **真相**：15 分钟内超 85% 心跳异常时，Eureka 进入保护模式，**不再移除任何实例**。网络长期分区时会产生大量僵尸实例，调用方反复超时。

### 陷阱 2：Nacos 命名空间和分组混淆
- **真相**：Nacos 隔离三层：`Namespace > Group > Service`。常见错误是命名空间对了但分组用默认值 `DEFAULT_GROUP`，不同业务域服务混在一起。**推荐按业务域设 Group**。

### 陷阱 3：Zookeeper 不适合做注册中心
- **真相**：ZK 是 CP 系统，Leader 选举期间（10-30 秒）所有注册发现完全不可用。微服务注册中心需要高可用（AP），短暂地址过期远好于整体不可用。Dubbo 早期用 ZK 是因为没有更好选择。

---

## 四、最佳实践

### 选型决策矩阵

| 维度 | Nacos | Eureka | Consul | Zookeeper |
|------|-------|--------|--------|-----------|
| **CAP** | AP/CP 可切换 | AP | CP | CP |
| **健康检查** | 心跳 + TCP | 客户端心跳 | 服务端探测 | 临时节点 |
| **配置中心** | ✅ 内置 | ❌ | ✅ 内置 | ⚠️ 不好用 |
| **DNS** | ❌ | ❌ | ✅ | ❌ |
| **社区状态** | ✅ 活跃 | ❌ 停更 | ✅ 活跃 | ✅ 活跃 |
| **推荐** | **新项目首选** | ❌ 不推荐 | 已有生态 | 已有 ZK 集群 |

**Eureka 为什么"死了"**：2018 年 Netflix 宣布 2.x 不再开发 → Spring Cloud Netflix 进入维护模式 → Nacos 功能覆盖 Eureka + Config + Bus → 新项目无理由选 Eureka。

**一句话选型**：新项目 → Nacos；已有 Consul → 留着用；已有 Zookeeper → 评估是否值得迁移；**绝对不推荐新项目选 Eureka**。

---

## 五、面试话术（90 秒版本）

> "注册中心选型核心看两个维度：**CAP 模型** 和 **生态集成度**。
>
> CAP 方面：Eureka 和 Nacos 默认 AP（高可用优先，网络分区时可能返回旧地址），Consul 和 Zookeeper 是 CP（一致性优先，Leader 选举期间不可用）。微服务注册中心一般 **AP 更合适** —— 短暂地址过期可客户端重试，注册中心不可用是灾难性的。
>
> 生态方面：Nacos 的优势是 **注册中心 + 配置中心二合一**，且支持 AP/CP 切换。Eureka 2.x 在 2018 年停更，Spring Cloud Netflix 进入维护模式，新项目不推荐。Consul 优势是 DNS 和强一致，适合已有 HashiCorp 生态。ZK 做注册中心是'大材小用'，Leader 选举的不可用窗口是硬伤。
>
> 健康检查也不同：Eureka 客户端推心跳，Consul 服务端主动探测（更准确），Nacos 两者都支持。**一句话：新项目选 Nacos，已有 Consul 留着用，Zookeeper 除非已有集群否则不选。**"

---

## 六、相关章节

- 同栏目：[`自动配置原理`](../auto-configuration/README.md) — Spring Boot 自动配置与 Starter 机制
- 同栏目：[`CAP 定理`](../../04.system-design/cap-theorem/README.md) — CAP 定理详解与工程实践
- 主模块：[`Spring Cloud`](../../06.spring/05-spring-cloud/README.md) — Spring Cloud 微服务全家桶
- 主模块：[`微服务架构`](../../04.system-design/README.md) — 微服务设计原则

← [返回 Spring 咬文嚼字](../README.md)
