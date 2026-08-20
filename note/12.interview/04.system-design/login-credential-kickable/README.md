<!--
question:
  id: 04.system-design-login-credential-kickable
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [04.system-design, 登录凭证, Session, JWT, 踢下线, Token 失效, 系统设计]
-->

# 设计可踢下线的登录凭证 —— Session 主动失效 4 大方案

> 一句话定位：**后端 / 架构面试经典系统设计题**。考察的不是"怎么登录"，而是 **凭证存储选型 + 主动失效机制 + 多端登录管理 + 安全性与性能权衡**。深度实战见主模块安全篇 / 分布式缓存篇。

> **系列定位**：高频系统设计题（社招必考）。配套兄弟题：[缓存一致性](../cache-consistency/README.md)、[分布式锁](../distributed-lock/README.md)、[幂等性设计](../idempotency/README.md)、[微服务 vs 单体](../microservices-vs-monolith/README.md)。

⭐⭐⭐⭐ 深度级别（高级工程师 / 架构师级）
📚 前置知识：HTTP Cookie / Session / JWT / Redis / 单点登录

---

## 引子：面试经典开场

面试官："设计一个登录系统，用户在 A 设备登录后，怎么让他在 B 设备登录时把 A 设备挤下线？或者管理员强制踢某个用户下线，怎么让他的 token 立即失效？"

大多数人答："用 Redis 存 session，删除 key 就失效了。"

面试官追问：

1. JWT 是无状态的，怎么让它失效？（黑名单？refresh token？）
2. 多设备登录怎么管理？是"挤掉旧"还是"允许并存"？
3. 千万级用户在线，怎么让踢人下线的延迟 < 1s？
4. 踢下线时如何避免 CSRF / token 盗用风险？

大多数人卡在追问上。**这道题考察的不是"知道用 Redis"，而是"凭证失效机制 + 多端会话管理 + 大规模踢人性能 + 安全性"**。

---

## 一、核心问题拆解

### 1.1 什么是"踢下线"？

"踢下线"是一个口语化表达，业内更严谨的说法是"凭证主动失效"。它有 3 种典型触发场景：

- **主动失效**：管理员后台操作 → 用户凭证立即失效（如封禁、违规处理）
- **被动挤下线**：新设备登录 → 旧设备凭证失效（如微信"另一台设备登录"提示）
- **安全失效**：检测到异地/异常 → 自动失效（如异地 IP 登录、风控触发）

三者技术实现是相通的：**本质都是把"凭证 → 用户"的映射从有效状态变为无效状态**。

### 1.2 踢下线 vs 登出 vs 封号

很多人把这三者混在一起，但它们的语义完全不同：

| 操作 | 范围 | 时效 | 谁触发 | 典型场景 |
|------|------|------|--------|----------|
| **登出** | 当前设备 | 当前会话 | 用户主动 | 用户点"退出登录"按钮 |
| **踢下线** | 用户所有/指定设备 | 立即 | 管理员/系统 | 管理员封禁、异地挤下线 |
| **封号** | 用户全部凭证 | 永久 | 平台规则 | 违规封号、账号注销 |

**关键差异**：

- **登出**只能由用户触发，且只影响"自己 + 当前设备"。
- **踢下线**由系统触发，目标是"其他设备/其他会话"，当前设备无感知（甚至不知道自己被踢了）。
- **封号**是平台规则级动作，所有凭证永久失效，连密码都改不了。

面试时要先和面试官对齐"你说的是哪种？"，避免答非所问。

### 1.3 三大核心挑战

设计一个可踢下线的凭证系统，要同时解决 3 个核心问题：

1. **失效实时性**：踢人后多久生效？理想 < 1s，实际看方案能做到 10ms ~ 15min 不等。
2. **多端一致性**：手机/PC/平板多端登录如何管理？是互踢还是并存？
3. **性能与规模**：千万级用户在线，踢人操作对系统压力多大？广播延迟如何保证？

后文 4 大方案就是围绕这 3 个挑战做不同取舍。

---

## 二、4 大主流方案对比

### 2.1 方案 1：服务端 Session + Redis 存储（最经典）

**架构**：

```
用户登录 → 服务端生成 SessionId → Redis 存 {userId, deviceId, loginTime, expireAt}
后续请求 → Cookie 携带 SessionId → 网关查 Redis 验证
踢下线 → Redis DEL session:xxx → 下次请求 401
```

**核心数据结构**：

```redis
# session 主键
SET session:abc123 '{"userId":1001,"deviceId":"iPhone-15","loginTime":...}' EX 7200

# user → session 映射（用于多端管理）
SET user:1001:sessions '["abc123","def456"]' EX 7200
```

**优点**：

- **失效立即生效**：删除 Redis key 即可，下一次请求 401（延迟 < 10ms）。
- **实现简单**：Spring Session / Express Session 框架开箱即用。
- **多端管理灵活**：每端独立 session，删除单端不影响其他端。

**缺点**：

- **Redis 单点风险**：需要 Cluster + 持久化（AOF/RDB）保证可用性。
- **每次请求都要查 Redis**：性能开销大（QPS 高时 Redis 成为瓶颈）。
- **存储成本**：百万级在线用户常驻 Redis，内存成本不低。

**适用场景**：中小厂主流，百万级用户以下，安全性要求高的场景（如银行后台、企业 ERP）。

### 2.2 方案 2：JWT + 服务端黑名单（折中方案）

**架构**：

```
登录 → 签发 JWT（含 userId, exp, jti） → 返回前端
请求 → 携带 JWT → 服务端校验签名 + 有效期 + 查黑名单
踢下线 → 把 jti 加入 Redis 黑名单（带 TTL = 剩余有效期）
```

**关键设计点**：

1. **黑名单粒度选择**：
   - 按 `jti`（JWT ID）粒度：精准，但黑名单膨胀快（每个被踢 token 一条记录）。
   - 按 `userId` 粒度：粗粒度（一次踢掉该用户所有 token），实现简单但不够灵活。
   - **推荐**：按 `jti` + 合理 TTL。

2. **TTL 设置**：必须与 JWT `exp` 对齐。token 本身过期后，黑名单条目自然失效，避免无限增长。

3. **性能优化**：
   - 本地缓存（Caffeine / Guava）：缓存黑名单查询结果（5s TTL）。
   - 大多数请求不需要查黑名单（token 有效期内只查一次）。

**数据结构**：

```redis
# 黑名单条目
SET blacklist:jti:abc123 "1" EX 900   # 15 分钟 = Access Token 剩余有效期
```

**优点**：

- **兼容 JWT 的无状态优势**：无需服务端存储 session。
- **失效可控**：需要失效的 token 主动加入黑名单。
- **实现简单**：登录逻辑无侵入。

**缺点**：

- **黑名单查询开销**：每次请求 +1 次 Redis 查询（可用本地缓存缓解）。
- **黑名单膨胀风险**：如果 TTL 设置不当，黑名单无限增长。
- **无法踢掉"刚签发的 token"之前已签发的 token**：需要"签发时刻记录"机制。

**适用场景**：中型系统，已经上了 JWT 但需要可控失效能力的过渡方案。

### 2.3 方案 3：Refresh Token + Access Token 双 Token（推荐方案）

**架构**：

```
登录 → 签发短期 Access Token（15min）+ 长期 Refresh Token（30d）
请求 → 携带 Access Token → 服务端只校验签名 + 有效期（不查 Redis）
踢下线 → 服务端禁用 Refresh Token（Redis 标记 revoked=true）
Access Token 过期 → 用 Refresh Token 换新 → 先检查 Refresh 是否被禁用
```

**关键设计点**：

1. **Access Token 短期化**：15 分钟过期，即使泄漏也很快失效。
2. **Refresh Token 长期但可控**：30 天有效期，但服务端随时可以禁用。
3. **禁用检查点**：只在 refresh 换新时检查，所以 Access Token 验证保持无状态（高性能）。

**数据结构**：

```redis
# Refresh Token 状态
SET refresh:rt_xyz789 '{"userId":1001,"deviceId":"iPhone","revoked":false}' EX 2592000

# 踢下线
SET refresh:rt_xyz789 '{"userId":1001,"deviceId":"iPhone","revoked":true}' EX 2592000
```

**Refresh Token 一次性使用（防重放）**：

```
换新流程：
1. 客户端带旧 Refresh Token 请求 /refresh
2. 服务端检查：是否被禁用？是否已被使用？
3. 如果未被使用：标记 used=true，签发新 Access + 新 Refresh
4. 如果已被使用：吊销该用户所有 Refresh（防 token 盗用）
```

**优点**：

- **Access Token 验证无状态**：90% 请求不查 Redis，性能极佳。
- **踢下线只需禁用 Refresh**：操作一次，影响所有 Access（最长 15min 生效）。
- **兼顾安全 + 性能**：业界主流方案（Auth0 / OAuth2 标准）。

**缺点**：

- **实现复杂**：双 Token 流转、前端要处理自动刷新逻辑。
- **踢下线有最长 15min 延迟**：Access Token 过期前仍然有效（可接受）。
- **Refresh Token 安全要求高**：必须 HTTPS + HttpOnly Cookie + 防重放。

**适用场景**：千万级用户，大厂主流方案（OAuth2.0 标准实践）。

### 2.4 方案 4：中心化会话服务（亿级用户）

**架构**：

```
用户 → API 网关（多节点）→ 会话服务（独立微服务，存 Redis Cluster）
会话服务 → 颁发凭证 → API 网关本地缓存 + Redis 权威存储
踢下线 → 会话服务 → MQ 广播（Kafka） → 所有 API 网关节点更新本地缓存
```

**关键设计点**：

1. **会话服务独立部署**：专门负责凭证生命周期管理（签发、验证、刷新、踢下线）。
2. **MQ 广播踢下线**：踢人操作通过 Kafka 广播到所有网关节点，更新本地缓存。
3. **网关本地缓存**：短 TTL（5s）+ Redis 权威存储，兼顾性能与一致性。

**架构示意**：

```
┌─────────────────────────────────────────────────────┐
│  API 网关 1       API 网关 2       API 网关 3        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │本地缓存  │    │本地缓存  │    │本地缓存  │      │
│  │5s TTL    │    │5s TTL    │    │5s TTL    │      │
│  └─────┬────┘    └─────┬────┘    └─────┬────┘      │
│        │              │              │             │
│        └──────────────┼──────────────┘             │
│                       │                            │
│                ┌──────▼──────┐    ┌──────────┐    │
│                │ 会话服务    │◄───┤Redis     │    │
│                │ (微服务)    │    │Cluster   │    │
│                └──────┬──────┘    └──────────┘    │
│                       │                            │
│                ┌──────▼──────┐                     │
│                │ Kafka MQ    │                     │
│                │ 踢下线广播  │                     │
│                └─────────────┘                     │
└─────────────────────────────────────────────────────┘
```

**优点**：

- **支撑亿级用户**：会话服务独立扩展，网关本地缓存减压。
- **踢下线广播延迟 < 1s**：MQ 推送 + 网关本地缓存更新。
- **业务服务无需关心会话管理**：网关统一拦截，业务透明。

**缺点**：

- **架构复杂**：会话服务 + MQ + 网关缓存，运维成本高。
- **MQ 引入新依赖**：Kafka / RocketMQ 本身的可用性要保证。
- **本地缓存一致性**：5s TTL 内可能有"已踢仍可用"的窗口期（业务可接受）。

**适用场景**：字节、阿里等亿级用户平台，电商大促、社交平台。

---

## 三、4 大方案对比矩阵

| 维度 | Session + Redis | JWT + 黑名单 | Refresh + Access | 中心化会话 |
|------|----------------|--------------|------------------|------------|
| **失效实时性** | < 10ms | < 10ms | Access 过期后（≤15min） | < 1s |
| **性能开销** | 每次请求查 Redis | 每次请求查黑名单 | Access 验证无状态 | 网关本地缓存 |
| **多端管理** | 灵活 | 复杂 | 需设计 | 灵活 |
| **实现复杂度** | 低 | 中 | 中高 | 高 |
| **存储成本** | 中（Redis 常驻） | 低（黑名单 TTL） | 低 | 高（多组件） |
| **适用规模** | 百万级 | 百万级 | 千万级 | 亿级 |
| **大厂实践** | 中小厂主流 | 部分中型 | **大厂主流** | 字节 / 阿里 |
| **安全性** | 高 | 中 | 高 | 高 |

**面试建议**：

- 百万级 → Session + Redis
- 千万级 → Refresh + Access Token（首选）
- 亿级 → 中心化会话服务

---

## 四、多端登录管理策略

多端管理是"踢下线"场景的核心业务问题。4 种主流模式：

### 4.1 模式 A：单端登录（互踢）

- 新登录挤掉旧登录（最严格）。
- **数据模型**：`userId → activeSessionId` 唯一映射，新登录覆盖旧值。
- **踢下线**：删除旧 session 即可。
- **适合**：银行 / 支付 / 高安全场景（用户不希望别人同时登录）。
- **代表**：支付宝、微信支付。

```java
// 伪代码：登录时挤掉旧 session
String oldSession = redis.get("user:active:" + userId);
if (oldSession != null) {
    redis.del("session:" + oldSession);  // 踢掉旧
}
redis.set("user:active:" + userId, newSessionId);  // 注册新
```

### 4.2 模式 B：多端并存

- 允许手机 / PC / 平板同时登录（最宽松）。
- **数据模型**：`userId → List<sessionId>`，登录追加、登出删除。
- **适合**：内容 / 社交 / 工具类应用（用户希望多设备无缝切换）。
- **代表**：抖音、Bilibili、微博。

```java
// 伪代码：登录时追加新 session
redis.sadd("user:sessions:" + userId, newSessionId);
redis.expire("session:" + newSessionId, 7200);
```

### 4.3 模式 C：限制数量并存（N 端）

- 最多 N 个设备同时在线（折中）。
- **数据模型**：`userId → List<sessionId>`，登录时检查数量，超过 N 拒绝新登录或踢掉最早一个。
- **适合**：付费会员 / VIP 场景（限制"账号共享"）。
- **代表**：Netflix、Spotify、QQ 会员。

```java
// 伪代码：限制 3 端登录
List<String> sessions = redis.lrange("user:sessions:" + userId, 0, -1);
if (sessions.size() >= 3) {
    String oldest = sessions.get(0);  // 踢最早登录的
    redis.del("session:" + oldest);
}
redis.rpush("user:sessions:" + userId, newSessionId);
```

### 4.4 模式 D：分级管理

- 普通账号多端、敏感操作单端。
- **数据模型**：根据操作类型动态切换验证等级。
- **适合**：电商 / 金融混合场景（普通浏览多端，支付下单单端）。
- **代表**：支付宝（普通浏览多端、付款时强制单端）。

```java
// 伪代码：敏感操作时强制单端
if (isSensitiveOperation(request)) {
    String activeSession = redis.get("user:active:" + userId);
    if (!activeSession.equals(currentSessionId)) {
        throw new "请在常用设备操作";
    }
}
```

---

## 五、踢下线的高性能实现

### 5.1 千万级用户踢下线延迟优化

核心目标：踢人操作后 < 1s 内所有节点生效。

**优化 1：本地缓存**

```java
// 网关侧：缓存 userId → 状态（valid / kicked）
LoadingCache<Long, Boolean> userStatusCache = Caffeine.newBuilder()
    .expireAfterWrite(5, TimeUnit.SECONDS)  // 5s TTL
    .build(userId -> {
        return redis.get("user:status:" + userId) != null;  // 查 Redis
    });
```

每次请求先查本地缓存，5s 内不查 Redis。

**优化 2：MQ 广播**

```
踢下线流程：
1. 管理员点击"踢人" → 会话服务
2. 会话服务写 Redis（权威状态）
3. 会话服务发 Kafka 消息（userId, kicked, timestamp）
4. 所有 API 网关节点消费消息，更新本地缓存
5. 用户下次请求 < 1s 内被拒
```

**优化 3：批量失效**

```java
// 批量踢人（如批量封号）：用 Pipeline 而非循环
redis.pipelined()  // Redis Pipeline
    .del("session:user1")
    .del("session:user2")
    .del("session:user3")
    .exec();
```

百万级踢人操作，从"循环 100 万次"（几十分钟）优化到"批量 Pipeline"（几秒）。

### 5.2 防"踢下线风暴"

恶意场景：有人反复触发踢下线接口，消耗系统资源。

**对策**：

1. **频率限制**：单用户被踢频率限制（如每分钟最多 1 次）。
2. **批量踢人异步**：批量封号用异步任务（MQ 消费），避免阻塞主流程。
3. **审计日志**：所有踢下线操作记录审计日志（合规 + 事后追查）。

```java
// 频率限制伪代码
String rateLimitKey = "kick:rate:" + adminId;
Long currentCount = redis.incr(rateLimitKey);
redis.expire(rateLimitKey, 60);  // 1 分钟窗口
if (currentCount > 10) {
    throw new "操作过于频繁";
}
```

---

## 六、5 大反模式

### ❌ 反模式 1：JWT 永远无法失效

- **错**：JWT 一旦签发无法收回，以为加长有效期就能解决。
- **对**：用 Refresh Token + 黑名单 / 短期 Access Token。

```java
// ❌ 错：JWT 一年有效期"图省事"
String jwt = Jwts.builder()
    .setExpiration(new Date(System.currentTimeMillis() + 365 * 24 * 3600 * 1000))
    .compact();

// ✅ 对：Access 短期 + Refresh 可控
String accessToken = Jwts.builder()
    .setExpiration(new Date(System.currentTimeMillis() + 15 * 60 * 1000))  // 15 分钟
    .compact();
```

### ❌ 反模式 2：Session 存内存

- **错**：单机内存 session（如 Tomcat 自带 Session），横向扩展时 session 丢失。
- **对**：Redis Cluster / 中心化会话服务。

```java
// ❌ 错：Spring Session 默认内存模式，多节点无法共享
// application.properties:
// spring.session.store-type=none

// ✅ 对：Spring Session + Redis
// spring.session.store-type=redis
// spring.redis.host=redis-cluster
```

### ❌ 反模式 3：踢下线用循环删除

- **错**：`for` 循环 `DEL` Redis key（百万级慢，几十分钟）。
- **对**：批量 Pipeline / 异步 MQ 广播。

```java
// ❌ 错：循环删除
for (String sessionId : allSessions) {
    redis.del("session:" + sessionId);  // 1 万次 ≈ 几十秒
}

// ✅ 对：Pipeline 批量
redis.pipelined()
    .del(allSessionKeys)
    .exec();  // 1 万次 ≈ 几十毫秒
```

### ❌ 反模式 4：忽略 CSRF / token 盗用

- **错**：踢下线后旧 token 还能用（被人截获继续访问）。
- **对**：踢下线 + 强制重新认证 + token 一次性。

**token 一次性使用**（防重放攻击）：

```
Refresh Token 换新流程：
1. 客户端带旧 RT 请求 /refresh
2. 服务端检查：是否被禁用？是否已被使用？
3. 如果已使用：吊销该用户所有 RT（防 token 盗用）
```

### ❌ 反模式 5：黑名单永不过期

- **错**：黑名单无限增长，最终占满 Redis 内存。
- **对**：TTL 与原始 token `exp` 对齐，自动过期。

```java
// ❌ 错：黑名单无 TTL
redis.set("blacklist:" + jti, "1");  // 永远存在

// ✅ 对：TTL 与 exp 对齐
long ttl = jwtExpireTimestamp - System.currentTimeMillis();
redis.set("blacklist:" + jti, "1", SetArgs.ex(ttl / 1000));  // 自动过期
```

---

## 七、面试高频追问

### Q1：JWT 怎么踢人下线？

**答**：JWT 本身无状态，但可通过 3 种方式实现失效：

1. **黑名单**（Redis 存被踢 token 的 jti，TTL 与 exp 对齐）。
2. **Refresh Token 控制**（Access 短期、Refresh 长期可禁用）。
3. **版本号机制**（user 表加 `tokenVersion`，签发时记录，踢人时 +1，验证时比对）。

最推荐 **Refresh + Access 双 Token** 方案，兼顾性能与可控性。

### Q2：多设备登录怎么挤掉旧的？

**答**：3 种策略：

1. **单端模式**：`userId → sessionId` 唯一映射，新登录覆盖旧值（适合银行）。
2. **N 端模式**：维护 `userId → List<sessionId>`，超过 N 踢最早（适合会员）。
3. **并存模式**：所有 session 共存（适合内容平台）。

### Q3：千万用户在线，踢人延迟怎么保证 < 1s？

**答**：3 层优化：

1. **本地缓存**：网关 Caffeine 缓存 5s TTL。
2. **MQ 广播**：Kafka 推送踢人消息到所有网关节点。
3. **批量操作**：踢人用 Pipeline 而非循环单操作。

### Q4：踢下线如何避免 token 盗用？

**答**：4 道防线：

1. **HTTPS**：传输加密。
2. **HttpOnly Cookie**：防 XSS 窃取。
3. **Refresh Token 一次性**：被截获后无法重放（已使用则吊销所有 RT）。
4. **设备指纹**：token 绑定 deviceId，异地 IP 自动失效。

### Q5：如何设计"限制 3 端登录"的方案？

**答**：Redis List 存储 active sessions：

```
登录时：
1. LPUSH user:1001:sessions newSessionId
2. 检查 LRANGE user:1001:sessions 0 -1 长度
3. 如果 > 3：LREM 最早的 + DEL 对应 session

登出时：
LREM user:1001:sessions 1 sessionId
DEL session:sessionId
```

进阶：考虑设备类型分类（PC / 手机 / 平板各算 1 端）。

---

## 八、实战案例

### 案例 1：电商平台"账号共享检测"

某电商平台想打击"一个账号多人共享"。方案：

1. 每次登录记录 deviceId + IP + GPS。
2. 检测到"短时间多设备多 IP 登录" → 触发踢下线。
3. 踢下线前要求"短信验证"（防误踢）。
4. 踢下线后强制重新登录 + 风控问卷。

### 案例 2：企业 SaaS "管理员踢人"

企业管理员踢出某个离职员工的所有会话：

1. 管理员后台 → 输入员工 ID → 点击"踢下线"。
2. 后端查 Redis：该用户所有 sessionId。
3. Pipeline 批量 DEL。
4. 返回成功（延迟 < 100ms）。

### 案例 3：社交 App "异地登录挤下线"

用户在北京登录后，又在上海登录：

1. 上海登录请求 → 检测到异地。
2. 发送"账号在其他设备登录"通知到北京设备。
3. 北京设备收到通知，提示"已被挤下线"。
4. 北京设备的 Refresh Token 被禁用（最长 15min 内自动失效）。

---

## 相关章节

- [缓存一致性](../cache-consistency/README.md) — Redis 缓存失效机制
- [分布式锁](../distributed-lock/README.md) — 单端登录互斥实现
- [幂等性设计](../idempotency/README.md) — 踢下线操作的幂等保证
- [微服务 vs 单体](../microservices-vs-monolith/README.md) — 中心化会话服务架构

## 📚 参考来源

1. [OAuth 2.0 Refresh Token 规范 - RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
2. [JWT 主动失效方案对比 - 阿里云开发者社区](https://developer.aliyun.com/)
3. [千万级用户踢下线延迟优化 - 字节跳动技术博客](https://tech.bytedance.net/)
4. [Redis Cluster 在会话管理中的应用 - 美团技术团队](https://tech.meituan.com/)
5. [Auth0 Refresh Token 实践指南](https://auth0.com/docs/secure/tokens/refresh-tokens)

← [返回: 系统设计咬文嚼字](../../README.md)