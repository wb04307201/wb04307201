# RESTful

REST（Representational State Transfer，表述性状态转移）是一种软件架构风格，广泛应用于 Web 服务（特别是 HTTP API）的设计中。RESTful API 是遵循 REST 原则构建的 Web API。

---

## 一、核心原则

1. **统一接口（Uniform Interface）**
    - 所有资源通过统一的接口进行操作。
    - 使用标准 HTTP 方法（动词）表示操作语义。
    - 资源通过 URI（统一资源标识符）唯一标识。

2. **无状态（Stateless）**
    - 每个请求必须包含处理该请求所需的全部信息。
    - 服务器不保存客户端上下文（Session），会话状态由客户端管理。

3. **可缓存（Cacheable）**
    - 响应应明确标明是否可缓存（如通过 HTTP 头 `Cache-Control`），以提升性能。

4. **客户端-服务器分离（Client-Server）**
    - 客户端与服务器关注点分离：客户端负责 UI/UX，服务器负责数据和业务逻辑。

5. **分层系统（Layered System）**
    - 客户端无需知道是否直接连接到最终服务器，中间可有代理、网关、负载均衡等。

6. **按需代码（Code on Demand，可选）**
    - 服务器可临时向客户端发送可执行代码（如 JavaScript），但不常用。

---

## 二、资源设计（核心）

- **资源（Resource）**：任何可命名的实体（如用户、订单、文章）。
- **URI 命名规范**：
    - 使用名词（复数）表示资源集合，如 `/users`、`/orders`。
    - 避免动词，操作语义由 HTTP 方法表达。
    - 使用层级表示从属关系，如 `/users/123/orders`。
    - 小写、中划线（-）或下划线（_）分隔单词（推荐小写+中划线，如 `/api/v1/user-profiles`）。
    - 避免文件扩展名（如 `.json`），改用 `Accept` 头指定格式。

---

## 三、HTTP 方法语义

| HTTP 方法 | 语义 | 幂等性 | 安全性 |
|----------|------|--------|--------|
| `GET`    | 获取资源 | 是 | 是 |
| `POST`   | 创建资源 或 执行非幂等操作 | 否 | 否 |
| `PUT`    | 替换整个资源（需提供完整数据） | 是 | 否 |
| `PATCH`  | 部分更新资源 | 否 | 否 |
| `DELETE` | 删除资源 | 是 | 否 |
| `HEAD`   | 获取资源元信息（如 headers） | 是 | 是 |
| `OPTIONS`| 获取资源支持的 HTTP 方法 | 是 | 是 |

> ✅ **安全方法（Safe）**：不会改变服务器状态（如 GET、HEAD）。  
> ✅ **幂等方法（Idempotent）**：多次执行效果与一次执行相同（GET、PUT、DELETE、HEAD、OPTIONS）。

---

## 四、状态码（HTTP Status Code）

- `200 OK`：请求成功（GET、PUT、PATCH）。
- `201 Created`：资源创建成功，通常在 POST 后返回，包含 `Location` 头。
- `204 No Content`：操作成功但无返回内容（如 DELETE）。
- `400 Bad Request`：客户端参数错误。
- `401 Unauthorized`：未认证。
- `403 Forbidden`：无权限访问。
  / `404 Not Found`：资源不存在。
- `405 Method Not Allowed`：该资源不支持此 HTTP 方法。
- `422 Unprocessable Entity`：语义正确但无法处理（如验证失败）。
- `500 Internal Server Error`：服务器内部错误。

---

## 五、请求与响应格式

- **请求体（Request Body）**：通常为 JSON（`Content-Type: application/json`）。
- **响应体（Response Body）**：
  ```json
  {
    "id": 123,
    "name": "Alice",
    "email": "alice@example.com"
  }
  ```
- 支持 HATEOAS（可选）：在响应中包含相关链接，使 API 可导航。
  ```json
  {
    "id": 123,
    "name": "Alice",
    "_links": {
      "self": { "href": "/users/123" },
      "orders": { "href": "/users/123/orders" }
    }
  }
  ```

---

## 六、版本控制（Versioning）

- URI 路径：`/api/v1/users`
- 请求头：`Accept: application/vnd.myapi.v1+json`
- 查询参数：`/users?version=1`（不推荐）

> 推荐使用 URI 路径方式，简单直观。

---

## 七、分页、过滤、排序、搜索

- **分页**：`GET /users?page=2&size=20`
- **过滤**：`GET /users?status=active&role=admin`
- **排序**：`GET /users?sort=name,asc&sort=created_at,desc`
- **搜索**：`GET /users?q=alice`

---

## 八、安全性

- 使用 HTTPS。
- 身份认证（如 JWT、OAuth 2.0）。
- 避免在 URL 中暴露敏感信息（如密码）。
- 实施速率限制（Rate Limiting）。
- 输入验证与防注入。

---

## 九、示例

```http
GET /api/v1/users
→ 200 OK + 用户列表

POST /api/v1/users
{ "name": "Bob", "email": "bob@example.com" }
→ 201 Created + Location: /api/v1/users/456

GET /api/v1/users/456
→ 200 OK + 用户详情

PUT /api/v1/users/456
{ "name": "Robert", "email": "robert@example.com" }
→ 200 OK

DELETE /api/v1/users/456
→ 204 No Content
```

---

## 十、常见误区

- 在 URI 中使用动词：❌ `/getUser/123` → ✅ `/users/123`
- 混淆 PUT 与 PATCH：PUT 是全量替换，PATCH 是局部更新。
- 忽略 HTTP 状态码语义。
- 返回不一致的错误格式。

---

遵循 RESTful 设计风格，可使 API 更清晰、可预测、易用且易于维护。虽然 REST 是一种“风格”而非严格标准，但业界已形成广泛共识的最佳实践。