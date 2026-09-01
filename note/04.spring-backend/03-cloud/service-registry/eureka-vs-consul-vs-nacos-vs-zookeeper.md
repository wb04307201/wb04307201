<!--
module:
  parent: 04.spring-backend
  slug: 04.spring-backend/03-cloud/service-registry/eureka-vs-consul-vs-nacos-vs-zookeeper
  type: article
  category: 主模块子文章
  summary: 服务注册与发现中心对比
  depth: ⭐⭐⭐
-->

# 服务注册与发现中心对比

> 🎯 **一句话定位**：对比 Eureka、Consul、Zookeeper、Nacos 四大注册中心在 CAP、健康检查、多数据中心等 11 维度的差异，给出选型建议。

| **对比维度**       | **Eureka**                          | **Consul**                          | **Zookeeper**                      | **Nacos**                            |
|--------------------|-------------------------------------|-------------------------------------|-------------------------------------|-------------------------------------|
| **开发语言**       | Java                                | Go                                  | Java                                | Java                                |
| **服务注册&发现**  | ✅ 支持                              | ✅ 支持                              | ✅ 支持                              | ✅ 支持                              |
| **健康检查**       | ⚠️ 有限支持（仅心跳）                | ✅ 支持（TCP/HTTP/脚本等）           | ✅ 支持（基于临时节点）              | ✅ 支持                              |
| **配置管理**       | ❌ 不支持                            | ⚠️ 有限支持（KV存储）                | ❌ 不支持                            | ✅ 支持（动态配置管理）              |
| **分布式一致性算法**| ❌ 未明确（默认AP）                  | ✅ Raft                              | ✅ Zab                               | ❌ 未明确（默认CP，可切换AP）        |
| **高可用**         | ✅ 支持（Peer-to-Peer）              | ✅ 支持（Raft共识）                  | ✅ 支持（Leader选举）                | ✅ 支持（集群/多集群）               |
| **多数据中心支持**  | ❌ 不直接支持                        | ✅ 支持（Wan Gossip协议）            | ❌ 不直接支持                        | ✅ 支持（Naming + Config分离部署）   |
| **KV存储**         | ❌ 不支持                            | ✅ 支持（强一致性）                  | ❌ 不支持（仅ZNode结构）             | ✅ 支持（AP/CP模式可选）             |
| **流量控制**       | ❌ 不支持                            | ❌ 不支持                            | ❌ 不支持                            | ✅ 支持（熔断、限流）                |
| **界面与API**      | ✅ Web界面 + RESTful API              | ✅ Web界面 + RESTful API + CLI       | ⚠️ 命令行 + 客户端API                | ✅ Web界面 + RESTful API + SDK       |
| **应用场景**       | 微服务架构（Spring Cloud）           | 微服务/服务网格（K8s、Spring Cloud）| 分布式协调（Hadoop、Kafka）         | 微服务/容器化（K8s、Service Mesh） |
| **CAP理论**       | 🔵 AP（优先可用性）                  | 🔴 CP（优先一致性）                  | 🔴 CP（强一致性）                    | 🟡 可选CP/AP（默认CP）               |
| **运行模式**       | ▶️ Server/Client                    | ▶️ Agent模式（Sidecar）              | ▶️ 单点/集群模式                     | ▶️ 单点/集群/多集群模式              |
| **开发者**         | Netflix                             | HashiCorp                           | Apache                              | Alibaba                             |

---

### **补充说明**：
1. **Eureka**
   - 适合纯 **Spring Cloud** 生态，已进入维护模式（推荐迁移至 **Nacos/Consul**）。
   - 健康检查依赖客户端心跳，无法主动探测服务状态。
   - 🎯 **场景推荐**：遗留 Spring Cloud 项目维护；新项目不建议选用。

2. **Consul**
   - 天然支持 **多数据中心** 和 **服务网格**（如 Istio 集成）。
   - 提供 **KV存储** 和 **Secret管理**（适合安全敏感场景）。
   - 🎯 **场景推荐**：需要服务网格 / 多数据中心部署 / 安全合规要求高的系统。

3. **Zookeeper**
   - 适合 **分布式协调**（如 Hadoop、Kafka），但 **不适合高并发写场景**（Zab协议性能瓶颈）。
   - 服务发现需依赖第三方工具（如 Dubbo 的 Registry 扩展）。
   - 🎯 **场景推荐**：遗留 Dubbo 系统 / Hadoop 生态 / 强一致性协调需求。

4. **Nacos**
   - 阿里开源，兼顾 **服务发现** 和 **配置中心**，支持 **动态 DNS** 和 **流量管理**。
   - 提供 **AP/CP 模式切换**（通过 `nacos.core.protocol.raft.data.consistency.type` 配置）。
   - 🎯 **场景推荐**：纯 Spring Cloud 新项目首选；需要服务发现 + 配置中心一体化方案。

---

## Nacos 快速接入示例

```yaml
# application.yml（Spring Cloud Alibaba Nacos 配置）
spring:
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        namespace: dev
        group: DEFAULT_GROUP
      config:
        server-addr: 127.0.0.1:8848
        file-extension: yaml
```

```java
// 启用服务注册与发现
@SpringBootApplication
@EnableDiscoveryClient
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}
```

---

## 反向链

- ⬅️ [返回: 03-cloud](../README.md) — 微服务与云原生总览
- ⬅️ [返回: 服务注册与发现](README.md) — 注册中心章节导航
- ➡️ [配置中心](../config-center.md) — Nacos 同时承担配置中心角色
- ➡️ [负载均衡](../load-balancer.md) — 注册中心与服务发现联动
