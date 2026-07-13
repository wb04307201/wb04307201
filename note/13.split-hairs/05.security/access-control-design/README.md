<!--
question:
  id: 05.security-access-control-design
  topic: 05.security
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [05.security, RBAC, ABAC, 权限系统, 系统设计, Spring-Security, 多租户]
-->

# 设计一个统一权限控制系统 —— RBAC + ABAC + 缓存 + 审计

> 一句话定位：**系统设计面试经典题**。考察的不是"RBAC 是什么"，而是**数据模型设计** + **权限判定链路** + **缓存策略** + **审计日志** + **多租户隔离**的工程落地。完整权限模型理论见 [访问控制：6 大权限模型](../../../../04.system-design/05-security/access-control/README.md)。

> **系列定位**：高频系统设计题（社招必考）。配套兄弟题：[SSO 单点登录](../sso/README.md)、[JWT 安全](../../../../04.system-design/05-security/jwt-security/README.md)。

---

⭐⭐⭐⭐⭐ 深度级别（架构师级）
📚 前置知识：RBAC / ABAC 模型 / Spring Security / Redis / JWT

---

## 引子：面试经典开场

面试官："设计一个统一权限控制系统，支撑 10 个业务系统、1000 个角色、100 万用户。"

大多数人答："用 RBAC，用户-角色-权限三张表。"

面试官追问：
1. "权限模型选 RBAC 还是 ABAC？什么时候需要混合？"
2. "权限数据怎么缓存？缓存和数据库不一致怎么办？"
3. "多租户场景下权限怎么隔离？"
4. "权限变更怎么审计？出了问题怎么溯源？"

大多数人卡在追问上。**这道题考察的不是"知道 RBAC"，而是"从数据模型到生产落地的全链路设计"。**

---

## 一、核心原理：权限模型选型

### 1.1 模型选型决策树

```
业务场景？
├─ 内部系统 + 固定组织架构 → RBAC（角色 = 岗位）
├─ 多租户 SaaS + 细粒度控制 → ABAC（属性 + 策略表达式）
├─ 文档共享 + 社交关系 → ReBAC（实体关系图）
└─ 90% 企业场景 → RBAC + ABAC 混合（粗粒度用角色，细粒度用属性）
```

> 📖 **深度阅读**：[6 大权限模型选型指南](../../../../04.system-design/05-security/access-control/README.md) — DAC / MAC / RBAC / ABAC / ReBAC / 混合

### 1.2 推荐方案：RBAC + ABAC 混合

```
用户(User)
  │
  ├── 角色(Role) ← RBAC 层：粗粒度权限（如"管理员"、"编辑者"）
  │     │
  │     └── 权限(Permission) ← 资源 + 操作（如"order:read"）
  │
  └── 属性(Attribute) ← ABAC 层：细粒度条件（如"部门=技术部"、"IP=内网"）
        │
        └── 策略(Policy) ← 动态规则（如"仅工作日 9-18 点可操作"）
```

**核心思想**：RBAC 管"谁是管理员"，ABAC 管"管理员在什么条件下能做什么"。

---

## 二、数据模型设计

### 2.1 核心表结构

```sql
-- 1. 用户表
CREATE TABLE sys_user (
    id          BIGINT PRIMARY KEY,
    username    VARCHAR(64) UNIQUE,
    tenant_id   BIGINT NOT NULL,  -- 多租户
    dept_id     BIGINT,           -- 部门（ABAC 属性）
    status      TINYINT DEFAULT 1,
    created_at  DATETIME
);

-- 2. 角色表（RBAC 层）
CREATE TABLE sys_role (
    id          BIGINT PRIMARY KEY,
    tenant_id   BIGINT NOT NULL,
    role_code   VARCHAR(64),      -- 如 "ADMIN", "EDITOR"
    role_name   VARCHAR(128),
    INDEX idx_tenant (tenant_id, role_code)
);

-- 3. 权限表
CREATE TABLE sys_permission (
    id            BIGINT PRIMARY KEY,
    resource_code VARCHAR(128),   -- 如 "order", "user", "report"
    action_code   VARCHAR(64),    -- 如 "read", "write", "delete"
    permission_code VARCHAR(256) UNIQUE  -- 如 "order:read"
);

-- 4. 用户-角色关联
CREATE TABLE sys_user_role (
    user_id  BIGINT,
    role_id  BIGINT,
    PRIMARY KEY (user_id, role_id)
);

-- 5. 角色-权限关联
CREATE TABLE sys_role_permission (
    role_id       BIGINT,
    permission_id BIGINT,
    PRIMARY KEY (role_id, permission_id)
);

-- 6. ABAC 策略表（细粒度规则）
CREATE TABLE sys_policy (
    id          BIGINT PRIMARY KEY,
    tenant_id   BIGINT NOT NULL,
    name        VARCHAR(128),
    effect      ENUM('ALLOW', 'DENY'),
    resource    VARCHAR(128),     -- 如 "order"
    action      VARCHAR(64),      -- 如 "delete"
    condition   JSON,             -- 如 {"dept":"技术部","time":"9-18"}
    priority    INT DEFAULT 0     -- 高优先级先评估
);
```

### 2.2 权限判定流程

```
用户请求（user_id=100, resource="order", action="delete"）
    │
    ▼ 1. 查询用户角色
SELECT r.role_code FROM sys_user_role ur
JOIN sys_role r ON ur.role_id = r.id
WHERE ur.user_id = 100
    │
    ▼ 2. 查询角色权限
SELECT p.permission_code FROM sys_role_permission rp
JOIN sys_permission p ON rp.permission_id = p.id
WHERE rp.role_id IN (用户角色IDs)
AND p.resource_code = 'order' AND p.action_code = 'delete'
    │
    ▼ 3. RBAC 判定：有 "order:delete" 权限？
    │
    ├─ 无 → DENY（角色层拒绝）
    │
    └─ 有 → 4. ABAC 策略评估
         SELECT * FROM sys_policy
         WHERE resource = 'order' AND action = 'delete'
         AND tenant_id = 用户租户ID
         ORDER BY priority DESC
         │
         ▼ 逐条评估条件
         ├─ 条件满足 + effect=ALLOW → ALLOW
         ├─ 条件满足 + effect=DENY → DENY
         └─ 无匹配策略 → 默认 DENY
```

---

## 三、7 道精选面试题

### Q1：权限数据怎么缓存？缓存不一致怎么办？

**答**：3 层缓存策略——

```
层 1：本地缓存（Caffeine，5 分钟 TTL）
  → 用户权限集合 Set<String>，每次请求直接查本地

层 2：Redis 分布式缓存（30 分钟 TTL）
  → Key: "perm:{userId}" → Set<String> permissions
  → Key: "role:{roleId}" → Set<String> permissions

层 3：数据库（兜底）
```

**缓存一致性**：
- 权限变更时发布 MQ 消息 → 所有服务节点清除本地缓存 + Redis 缓存
- 用 Redis Pub/Sub 或 MQ broadcast 模式通知所有节点
- 兜底：TTL 过期自动刷新（最大 5 分钟延迟）

```java
// 权限变更 → 清除缓存
@EventListener
public void onPermissionChanged(PermissionChangedEvent event) {
    Long userId = event.getUserId();
    caffeineCache.evict("perm:" + userId);
    redisTemplate.delete("perm:" + userId);
    // 发布给其他节点
    mqTemplate.send("perm-cache-invalidate", userId);
}
```

### Q2：多租户权限怎么隔离？

**答**：3 种方案——

| 方案 | 实现 | 适用 |
|------|------|------|
| **字段隔离** | 每张表加 `tenant_id`，SQL 自动拼接 | 中小规模（首选） |
| **Schema 隔离** | 每个租户独立 Schema | 中大规模 |
| **实例隔离** | 每个租户独立数据库 | 超大客户 / 合规要求 |

**字段隔离实现**（MyBatis 拦截器自动注入）：

```java
// 拦截器自动给 SQL 加 WHERE tenant_id = ?
@Intercepts(@Signature(type = StatementHandler.class, method = "prepare"))
public class TenantInterceptor implements Interceptor {
    public void intercept(Invocation invocation) {
        String sql = statementHandler.getBoundSql().getSql();
        // 自动拼接 AND tenant_id = #{tenantId}
        String newSql = sql + " AND tenant_id = " + TenantContext.get();
        // 替换 SQL
    }
}
```

### Q3：Spring Security 怎么集成？

**答**：核心 3 步——

```java
// 1. 实现 UserDetailsService（从数据库加载用户 + 权限）
@Service
public class MyUserDetailsService implements UserDetailsService {
    public UserDetails loadUserByUsername(String username) {
        User user = userRepo.findByUsername(username);
        Set<String> perms = permissionService.getUserPermissions(user.getId());
        return new MyUserDetails(user, perms);
    }
}

// 2. 配置 HTTP 安全（URL → 权限映射）
@Configuration
public class SecurityConfig {
    @Bean
    SecurityFilterChain filterChain(HttpSecurity http) {
        http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/orders/**").hasAuthority("order:read")
            .requestMatchers("/api/admin/**").hasRole("ADMIN")
            .anyRequest().authenticated()
        );
        return http.build();
    }
}

// 3. 方法级权限（@PreAuthorize）
@PreAuthorize("hasAuthority('order:delete')")
public void deleteOrder(Long orderId) { ... }
```

### Q4：权限审计怎么做？出了问题怎么溯源？

**答**：4 层审计——

```
层 1：操作日志（每次权限判定记录）
  → who: user_id, what: resource:action, when: timestamp
  → result: ALLOW/DENY, reason: role/ABAC/默认拒绝

层 2：变更日志（权限配置变更记录）
  → who changed what, old value → new value, when

层 3：登录日志（认证记录）
  → 登录时间 / IP / 设备 / 成功失败

层 4：异常告警
  → 同一用户 5 分钟内 DENY > 10 次 → 告警（可能暴力试探）
```

```sql
CREATE TABLE audit_log (
    id          BIGINT PRIMARY KEY,
    tenant_id   BIGINT,
    user_id     BIGINT,
    resource    VARCHAR(128),
    action      VARCHAR(64),
    result      ENUM('ALLOW', 'DENY'),
    reason      VARCHAR(256),     -- "role:ADMIN" / "policy:dept-match"
    ip          VARCHAR(45),
    created_at  DATETIME,
    INDEX idx_tenant_time (tenant_id, created_at)
);
```

### Q5：前端怎么根据权限控制 UI？

**答**：后端返回权限列表 → 前端用指令/组件控制显隐。

```json
// 登录后返回
{
    "user": { "id": 100, "name": "张三" },
    "permissions": ["order:read", "order:write", "user:read"]
}
```

```html
<!-- Vue 自定义指令 -->
<button v-permission="'order:delete'">删除订单</button>
<!-- 无 order:delete 权限时按钮隐藏 -->

<!-- React 权限组件 -->
<PermissionGate permission="order:delete">
    <button>删除订单</button>
</PermissionGate>
```

**注意**：前端控制只是 UI 层优化，后端接口必须做权限校验（防止绕过前端直接调用 API）。

### Q6：高频权限判定怎么优化性能？

**答**：5 层优化——

| 层次 | 优化 | 效果 |
|------|------|------|
| 本地缓存 | Caffeine 缓存权限集合 | 避免网络调用 |
| Redis | 分布式缓存 | 跨节点共享 |
| 预计算 | 启动时加载全量权限到内存 | 适合权限总量 < 10 万 |
| 批量查询 | 一次请求查多个资源权限 | 减少 DB 查询次数 |
| 异步审计 | 审计日志写 MQ 异步消费 | 不阻塞请求 |

### Q7：RBAC 的粒度不够细怎么办？

**答**：RBAC + ABAC 混合——

```
粗粒度（RBAC）：角色 "订单管理员" → 权限 "order:*"
细粒度（ABAC）：策略 "订单管理员只能删除自己创建的订单"
```

```java
// ABAC 策略示例
{
    "name": "订单管理员-限本人",
    "effect": "ALLOW",
    "resource": "order",
    "action": "delete",
    "condition": {
        "rule": "order.creator == user.id"
    }
}
```

---

## 四、5 大反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| **权限硬编码** | `if (user.isAdmin())` 散落各处 | 用注解 `@PreAuthorize` 集中管理 |
| **不做缓存** | 每次请求查 DB | 本地 + Redis 双层缓存 |
| **只控后端** | 前端不隐藏无权限按钮 | 后端 + 前端双重控制 |
| **不记审计** | 出问题无法溯源 | 每次权限判定都记日志 |
| **权限不版本化** | 变更无法回滚 | 权限配置加版本号 / 变更日志 |

---

## 五、面试话术（30 秒版）

> "统一权限控制系统用 RBAC + ABAC 混合模型：RBAC 管角色到权限的粗粒度映射，ABAC 用策略表达式做细粒度条件控制。
>
> 数据模型 6 张核心表：用户、角色、权限、用户-角色、角色-权限、ABAC 策略。权限判定流程：先查用户角色 → 查角色权限（RBAC 层）→ 评估 ABAC 策略条件 → 返回 ALLOW/DENY。
>
> 性能靠 3 层缓存：本地 Caffeine（5 分钟）+ Redis（30 分钟）+ DB 兜底。权限变更时通过 MQ 广播清除所有节点缓存。
>
> 多租户用字段隔离（每张表 tenant_id + MyBatis 拦截器自动注入）。审计 4 层：操作日志 + 变更日志 + 登录日志 + 异常告警。
>
> Spring Security 集成 3 步：自定义 UserDetailsService 加载权限、SecurityFilterChain 配 URL 映射、@PreAuthorize 方法级控制。"

---

## 六、交叉引用

- **权限模型理论**：[6 大权限模型](../../../../04.system-design/05-security/access-control/README.md) — DAC / MAC / RBAC / ABAC / ReBAC / 混合
- **RBAC 深度**：[RBAC 详解](../../../../04.system-design/05-security/access-control/02-role-and-attribute/rbac.md) — 角色继承 / 约束 / 权限分配
- **ABAC 深度**：[ABAC 详解](../../../../04.system-design/05-security/access-control/02-role-and-attribute/abac.md) — 策略引擎 / 属性表达式
- **SSO**：[SSO 单点登录](../sso/README.md) — 6 大方案选型
- **JWT**：[JWT 安全](../../../../04.system-design/05-security/jwt-security/README.md) — Token 签发与验证
- **API 安全**：[API 安全](../../../../04.system-design/05-security/api-security/README.md) — 限流 / 签名 / 防重放
- **主模块**：[`04.system-design/05-security`](../../../../04.system-design/05-security/README.md) — 安全知识体系

## 相关章节

- 深度阅读：[`04.system-design`](../../04.system-design/README.md) — 系统设计主模块

← [返回: 咬文嚼字 · access-control-design](README.md)
