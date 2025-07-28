# Spring Cloud 微服务架构笔记

## 一、Spring Cloud 概述
Spring Cloud 是基于 Spring Boot 实现的微服务架构开发工具集，提供服务发现、配置管理、断路器、智能路由等核心功能。

### 核心组件
```plantuml
@startmindmap
* Spring Cloud
** 服务发现: Eureka/Nacos
** 配置中心: Config/Nacos
** API网关: Gateway/Zuul
** 负载均衡: Ribbon/LoadBalancer
** 断路器: Hystrix/Sentinel
** 链路追踪: Sleuth+Zipkin
** 消息总线: Bus
@endmindmap
```

## 二、服务注册与发现（Eureka示例）

### 1. 架构示意图
```plantuml
@startuml
actor 客户端
rectangle 服务集群 {
    [服务A实例1]
    [服务A实例2]
    [服务B实例]
}
rectangle EurekaServer {
    [注册中心]
}

客户端 -> EurekaServer : 服务发现请求
服务A实例1 --> EurekaServer : 心跳注册
服务A实例2 --> EurekaServer : 心跳注册
服务B实例 --> EurekaServer : 心跳注册
@enduml
```

### 2. 核心配置
```yaml
# application.yml 示例
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    prefer-ip-address: true
    lease-renewal-interval-in-seconds: 10
```

## 三、服务调用（Feign+Ribbon）

### 1. 调用流程
```plantuml
@startuml
[Client] -> [Feign接口]: @FeignClient注解
[Feign接口] -> [Ribbon]: 负载均衡选择
[Ribbon] -> [Eureka]: 获取服务列表
[Ribbon] -> [TargetService]: 发起调用
@enduml
```

### 2. 代码示例
```java
@FeignClient(name = "user-service")
public interface UserClient {
    @GetMapping("/users/{id}")
    User getUser(@PathVariable("id") Long id);
}

// 配置类（Ribbon负载均衡策略）
@Configuration
public class RibbonConfig {
    @Bean
    public IRule ribbonRule() {
        return new RandomRule(); // 随机策略
    }
}
```

## 四、熔断降级（Hystrix）

### 1. 工作原理
```plantuml
@startuml
skinparam sequenceArrowThickness 2
actor 用户
participant "调用方" as caller
participant "Hystrix" as hystrix
participant "服务提供方" as provider

用户 -> caller: 发起请求
caller -> hystrix: 执行命令
alt 正常情况
    hystrix -> provider: 调用服务
    provider --> hystrix: 返回结果
    hystrix --> caller: 返回结果
else 服务不可用
    hystrix -> hystrix: 触发熔断
    hystrix --> caller: 返回降级数据
end
@enduml
```

### 2. 注解使用
```java
@HystrixCommand(fallbackMethod = "getDefaultUser")
public User getUser(Long id) {
    // 远程调用逻辑
}

public User getDefaultUser(Long id) {
    return new User(0L, "默认用户");
}
```

## 五、配置中心（Spring Cloud Config）

### 1. 架构组成
```plantuml
@startuml
cloud "Git仓库" as git {
    [config-repo]
}

rectangle "Config Server" as server {
    [配置服务]
}

rectangle "Microservices" as micro {
    [服务A]
    [服务B]
}

git --> server : 配置文件
server --> micro : 动态推送
@enduml
```

### 2. 配置刷新
```bash
# 手动刷新端点（需配合@RefreshScope）
POST http://service-a/actuator/refresh
```

## 六、API网关（Spring Cloud Gateway）

### 1. 路由规则示例
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
          filters:
            - RewritePath=/api/users/(?<segment>.*), /$\{segment}
```

### 2. 过滤器流程
```plantuml
@startuml
[Request] --> [GlobalFilter1]
[GlobalFilter1] --> [GlobalFilter2]
[GlobalFilter2] --> [RouteFilter1]
[RouteFilter1] --> [RouteFilter2]
[RouteFilter2] --> [TargetService]
@enduml
```

## 七、最佳实践建议

1. **服务拆分原则**：
    - 单一职责原则
    - 服务粒度适中（建议不超过10个方法）
    - 避免双向依赖

2. **配置管理**：
    - 开发环境：本地配置优先
    - 生产环境：集中配置覆盖
    - 敏感信息使用Vault管理

3. **监控体系**：
   ```plantuml
   @startuml
   [Microservices] --> [Prometheus]: 指标采集
   [Prometheus] --> [Grafana]: 可视化
   [Microservices] --> [ELK]: 日志收集
   [Microservices] --> [Zipkin]: 链路追踪
   @enduml
   ```

## 八、版本演进建议

| 组件       | 2020.x 版本 | 2021.x 版本 | 替代方案       |
|------------|-------------|-------------|----------------|
| 服务发现   | Eureka      | Nacos       | Consul/Zookeeper|
| 熔断       | Hystrix     | Resilience4j | Sentinel        |
| 配置中心   | Config      | Nacos       | Apollo          |

> 提示：Spring Cloud 2022.x开始采用年号版本命名（如2022.0.0），建议新项目直接使用最新稳定版。
