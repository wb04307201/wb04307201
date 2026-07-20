<!--
module:
  parent: 04.system-design/05-security/sso
  slug: system-design/05-security/sso/05-decision-tree
  type: topic
  category: 选型决策
  summary: SSO 6 大方案场景化选型 + checklist + 反模式速查
-->

# SSO 选型决策树 · 6 大方案场景化

> **一句话**：SSO 6 大方案没有"最好"——只有"场景 × 团队 × 时代"3 维约束下的最优。一张「5 分钟决策树」+「checklist」搞定 80% 场景。

← [返回: SSO 总目录](../README.md)

---

## 1. 5 分钟决策树

```text
Q1：跨主域吗（同根域 vs 跨主域）？
├─ 同根域 → Cookie 共享（最简）
└─ 跨主域 ↓

Q2：现代互联网产品（Web + iOS + Android）？
├─ 是 → OAuth2 + OIDC（推荐 ✅）
└─ 否 ↓

Q3：跨国企业 / 金融 / 政府？
├─ 是 → SAML 2.0
└─ 否 ↓

Q4：10+ 年 Java EE 老系统？
├─ 是 → CAS
└─ 否 ↓

Q5：内部微服务 API 调用？
├─ 是 → JWT 自建 + Redis 黑名单
└─ 否 ↓

Q6：Spring 框架生态？
├─ 是 → Spring Authorization Server
└─ 否 → Keycloak / Authing

默认推荐：OAuth2 + OIDC + Spring Authorization Server（80% 场景）
```

---

## 2. 6 大方案配置矩阵

| 场景 | 第一选择 | 第二选择 | 理由 |
|------|---------|---------|------|
| 同公司多产品（同根域）| Cookie 共享 | JWT 自建 | 实现最简 |
| 互联网产品（跨域）| OAuth2 + OIDC | Keycloak | 跨平台 |
| 老企业内部（Java EE）| CAS | OAuth2 | 历史兼容 |
| 跨国/合规（金融/政府）| SAML 2.0 | OAuth2 + OIDC | 国际标准 |
| 微服务内部 API | JWT + Redis 黑名单 | OAuth2 Client | 性能最优 |
| Spring 全家桶 | Spring Authorization Server | Keycloak | 集成度 |
| 多语言企业 | Keycloak | Auth0 | 全产品 |

---

## 3. 实施 Checklist

### 3.1 设计阶段

- [ ] 选 SSO 方案（6 选 1）
- [ ] 决策 IdP（Spring Authorization Server / Keycloak）
- [ ] 决策 Token 类型（JWT / Reference Token）
- [ ] 决策 Scope 设计
- [ ] 决策 IdP 高可用方案

### 3.2 工程阶段

- [ ] **必须 HTTPS**（OAuth2 强制）
- [ ] PKCE 强制启用（公网客户端）
- [ ] Access Token 短 + Refresh Token Rotate
- [ ] Token 颁发限流（防爆破）
- [ ] CORS 配置
- [ ] 资源服务器 JWT 验签
- [ ] 业务接口 @PreAuthorize / hasAuthority

### 3.3 运维阶段

- [ ] IdP 集群（≥ 2 实例 + 多 AZ）
- [ ] 数据库主从（用户数据）
- [ ] Redis 集群（黑名单 / Session）
- [ ] 监控：Token 颁发量 / 验签失败率 / 撤销次数
- [ ] 告警：IdP 不可达 → 短信值班人
- [ ] 定期演练"IdP 挂"场景

---

## 4. 反模式速查（5 个最常错）

| 反模式 | 场景 | 修复 |
|--------|------|------|
| **SSO = OAuth2** | "我们要 SSO，用 OAuth2" | OIDC 必须配合 |
| **JWT 永不过期** | 用户永不被踢出 | 短 Access + Refresh Rotate |
| **同根域跨主域** | Cookie 共享跨主域失败 | 跨主域必须 OAuth2/CAS |
| **IdP 单实例** | IdP 挂全部 SP 不可登 | IdP 集群 + DB 主从 |
| **没有登出** | 只实现登录 | OIDC backchannel logout |

---

## 5. 反向决策 · 5 个错误信号

| 错误信号 | 含义 |
|---------|------|
| Cookie 共享跨主域 | 必须 OAuth2/OIDC |
| JWT 设 30 天 | 违规，最长 1h |
| IdP 单实例 | 必须集群 |
| Refresh Token 不 Rotate | 泄露后风险扩大 |
| 没实现登出 | 用户离职仍有访问 |

---

## 6. 决策树精简版

```text
┌──────────────────────────────────┐
│  Step 1：跨主域？                │
│    同根域 → Cookie 共享          │
│    跨主域 ↓                      │
│                                  │
│  Step 2：现代互联网？            │
│    是 → OAuth2 + OIDC           │
│    否 ↓                          │
│                                  │
│  Step 3：跨国 / 合规？           │
│    是 → SAML 2.0                │
│    否 ↓                          │
│                                  │
│  Step 4：Java EE 老系统？        │
│    是 → CAS                      │
│    否 ↓                          │
│                                  │
│  Step 5：微服务内部 API？         │
│    是 → JWT 自建                 │
│    否 → OAuth2 + OIDC             │
│                                  │
│  默认：OAuth2 + OIDC              │
└──────────────────────────────────┘
```

---

## 7. 一句话总结

> **SSO 选型公式：现代互联网 = OAuth2+OIDC；跨国/合规 = SAML；微服务内部 = JWT；老系统 = CAS；同公司 = Cookie。80% 场景是 OAuth2+OIDC + Spring Authorization Server。**

---

← [返回: SSO 总目录](../README.md) · 上一章：[04-jwt-implementation](04-jwt-implementation.md) · 专题结束
