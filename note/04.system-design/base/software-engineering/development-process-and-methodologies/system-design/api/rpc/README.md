# RPC

以下是关于 **RPC API 设计风格** 的核心原则和最佳实践，适用于现代分布式系统（如微服务架构）。设计良好的 RPC API 需兼顾**清晰性、性能、可维护性**和**跨语言兼容性**。

---

### 一、核心设计原则
1. **面向动作（Action-Oriented）**  
   RPC 的核心是 **“执行远程操作”**，接口设计应围绕**动词+名词**（如 `CreateUser`, `GetOrderStatus`），而非 REST 的资源（Resource）导向。  
   ❌ 避免 REST 风格的 `/users/{id}` 路径设计，✅ 应使用显式方法名（如 `UserService.GetUser`）。

2. **强类型契约（Schema-First）**  
   **强制使用 IDL（接口定义语言）** 定义请求/响应格式，确保类型安全和跨语言兼容性：
    - **gRPC**: Protocol Buffers（推荐）
    - **Thrift**: Apache Thrift IDL
    - **通用场景**: JSON Schema + OpenAPI（适用于 JSON-RPC）

   ```protobuf
   // 示例：gRPC Protocol Buffers 定义
   message CreateUserRequest {
     string username = 1;
     string email = 2;
   }
   message User {
     string id = 1;
     string username = 2;
   }
   service UserService {
     rpc CreateUser (CreateUserRequest) returns (User);
   }
   ```

3. **无状态设计**  
   每个 RPC 调用必须包含完整上下文，服务端不存储客户端状态（与 HTTP Session 无关）。  
   → 通过 Token（如 JWT）或请求头传递身份/上下文信息。

---

### 二、关键设计细节
#### 1. **方法命名规范**
- **清晰表达意图**：使用动词明确操作类型（`Create`, `Update`, `Delete`, `Query`, `BatchGet`）。
- **避免歧义**：  
  ❌ `GetUser`（可能被误解为获取单个或列表）  
  ✅ `GetUserById` / `ListUsers`
- **批量操作**：统一后缀（如 `BatchCreateOrders`），限制单次请求的数据量防止滥用。

#### 2. **参数设计**
- **扁平化参数**：避免深层嵌套，减少序列化开销（尤其对二进制协议）。
- **必需/可选字段**：在 IDL 中显式标记（如 Protobuf 的 `optional` 字段）。
- **分页与过滤**：
  ```protobuf
  message ListUsersRequest {
    int32 page_size = 1; // 明确分页参数
    string page_token = 2; // 用于游标分页
    string filter = 3;     // 结构化过滤条件（如 "status=active"）
  }
  ```

#### 3. **错误处理**
- **标准化错误码**：
    - gRPC 使用 [Status Codes](https://grpc.github.io/grpc/core/md_doc_statuscodes.html)（如 `NOT_FOUND`, `INVALID_ARGUMENT`）
    - 自定义业务错误码需在响应体中携带（如 `error.code = "USER_ALREADY_EXISTS"`）。
- **人类可读错误信息**：`error.message` 用于日志/调试，**不暴露敏感信息**。
- **异常与业务错误分离**：网络超时、服务不可用属于异常；参数校验失败属于业务错误。

#### 4. **版本控制**
- **优先兼容性设计**：通过**非破坏性变更**避免版本升级（如新增字段、废弃旧字段而非删除）。
- **版本标识策略**（按优先级排序）：
    1. **方法级版本**：`CreateUserV2`（推荐，最清晰）
    2. **包/命名空间版本**：`v1.UserService`（gRPC 常用）
    3. **请求头/元数据**：`api-version: v1`（避免 URL 路径污染）

#### 5. **性能与效率**
- **二进制序列化**：优先选择 Protobuf/Thrift 而非 JSON（体积小 3-5 倍，解析快 10 倍）。
- **流式传输**：
    - 大数据集：服务端流（`stream Orders`）
    - 高频上报：客户端流（`stream SensorData`）
    - 双向通信：聊天/实时协作场景（`stream ChatMessage`）
- **压缩**：启用 gRPC 的 `gzip` 压缩（对文本数据效果显著）。

---

### 三、安全与可观测性
1. **认证与授权**
    - 通过拦截器/中间件统一处理（如 JWT 验签、RBAC 权限校验）。
    - **敏感操作**：强制二次验证（如删除账户需短信确认）。

2. **超时与重试**
    - 客户端设置**合理超时**（避免阻塞线程）。
    - 服务端实现**幂等性**（通过 `request_id` 去重），仅对 `GET`/`Query` 等安全操作自动重试。

3. **可观测性**
    - 透传 TraceID（如 OpenTelemetry Context），串联全链路日志。
    - 关键指标监控：请求量、错误率、P99 延迟、饱和度（队列积压）。

---

### 四、框架选型建议
| 场景                | 推荐框架          | 优势                          |
|---------------------|-------------------|-----------------------------|
| 高性能内部微服务     | **gRPC**          | Protobuf + HTTP/2, 多语言支持完善 |
| 跨公网/浏览器调用   | **JSON-RPC 2.0**  | 轻量、易调试、兼容 Web          |
| 极致性能（C++/Java）| **Apache Thrift** | 多传输协议（二进制/内存）、成熟稳定 |
| 混合云/多协议支持   | **Twirp**         | 简化 gRPC 的 HTTP/JSON 兼容方案 |

---

### 五、反模式（Anti-Patterns）
1. **“大而全”的单接口**  
   ❌ 一个方法处理创建/更新/查询（如 `ManageUser`）  
   ✅ 拆分为 `CreateUser`, `UpdateUser`, `GetUser`。

2. **过度嵌套的响应结构**  
   ❌ 多层包装：`{ data: { result: { user: { ... } } } }`  
   ✅ 扁平化：`{ id, name, created_at }`。

3. **忽略向后兼容**  
   ❌ 直接删除字段或修改枚举值  
   ✅ 标记 `reserved` 字段，用新方法替代旧逻辑。

---

### 六、工具链推荐
- **IDL 生成代码**: `protoc`（gRPC）、`thrift` 编译器
- **API 测试**: BloomRPC（gRPC GUI 客户端）、Postman（JSON-RPC）
- **文档生成**: `protoc-gen-doc`、Swagger（JSON-RPC）
- **监控**: Prometheus + Grafana（gRPC 指标）、Jaeger（链路追踪）

---

**总结**：现代 RPC API 设计 = **强类型契约 + 明确语义 + 兼容性优先 + 全链路可观测**。  
**何时用 RPC 而非 REST？**
- 内部服务通信（性能敏感）
- 需要流式传输/双向通信
- 严格类型约束（如金融/物联网场景）
- 跨语言生态（Protobuf/Thrift 天然支持多语言）

> 附：Google API 设计指南（[google.aip.dev](https://google.aip.dev/)）是权威参考，虽侧重 REST，但错误处理、分页等原则通用。
