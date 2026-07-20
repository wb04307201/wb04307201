<!--
module:
  parent: 05-security
  slug: system-design/05-security/sso
  type: deep-dive
  category: 单点登录
  summary: 单点登录（SSO）深度专题 —— 6 大实现方案对比（CAS/OAuth2/OIDC/SAML/Cookie/JWT）+ Spring Security 实战 + 选型决策
-->

# 单点登录（SSO）· 6 大实现方案深度对比

> **一句话答案**：SSO = 用户**一次登录，多系统访问**——本质是"信任传递"，6 大方案（CAS / Cookie 共享 / OAuth2 + OIDC / SAML / JWT 自建 / 代理模式）的核心都是"如何把首次登录态安全传递给其他子系统"。

← [返回: 安全设计](../README.md) · 兄弟：[OAuth2/OIDC](../oauth2-oidc/README.md) · [JWT](../jwt-security/README.md) · [访问控制](../access-control/README.md)

---

## 0. 面试高频拷问

```text
Q：什么是单点登录（SSO）？以及实现流程？
```

**回答框架（4 层递进）**：

1. **场景区分**：SSO 不是单一技术，是**设计目标**——一次登录跨多系统访问
2. **核心原理**："信任传递"——首次登录后，发"信任票据"给子系统
3. **6 大方案对比**：CAS / Cookie / OAuth2+OIDC / SAML / JWT / 代理
4. **实战选型**：电商用 OAuth2+Redis，企业内部用 SAML，跨域用 OIDC

完整 5-7 道精选面试题见 [13.split-hairs/05.security/sso](../../../13.split-hairs/05.security/sso/README.md)。

---

## 1. SSO 3 大核心问题

```text
问题 1：身份（Authentication）—— 用户是谁？
问题 2：授权（Authorization）—— 用户能干什么？
问题 3：会话（Session）—— 用户的登录状态怎么保持？
```

SSO 解决**跨多个应用的身份与会话共享**，授权可以独立处理。

---

## 2. 6 大实现方案速览

| # | 方案 | 核心思想 | 适用 | 复杂度 |
|---|------|---------|------|--------|
| 1 | **CAS（Central Authentication Service）** | 中央认证 + Ticket 票据 | 老牌企业内部 SSO | 中 |
| 2 | **同域 Cookie 共享** | 多个子域共享 Cookie | 同公司多产品（同根域）| 低 |
| 3 | **OAuth2 + OIDC** | 授权码模式 + ID Token | 现代互联网 SSO（推荐 ✅）| 中高 |
| 4 | **SAML 2.0** | XML 断言 + IdP 签名 | 企业级（金融 / 政府 / 跨国）| 高 |
| 5 | **JWT 自建** | Token + Claims 自验签 | 内部 API 认证 | 低 |
| 6 | **代理模式（nginx 同源）** | 反向代理统一鉴权 | 微服务网关层 | 中 |

---

## 3. 子章节导航

| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [SSO 概念与原理](01-sso-concept.md) | SSO 是什么？解决什么问题？ |
| 02 | [6 大方案详解](02-six-schemes-comparison.md) | CAS / Cookie / OAuth2 / SAML / JWT / 代理 详解 |
| 03 | [Spring Security 实战](03-spring-security-implementation.md) | Java 后端 Spring Authorization Server 配置 |
| 04 | [JWT + Redis Token 实战](04-jwt-implementation.md) | JWT 自建 + 黑名单 |
| 05 | [选型决策树](05-selection-decision-tree.md) | 场景化选型 + 反模式 |

---

## 4. 反直觉点

- ⚠️ **"SSO = OAuth2"是错觉** —— SSO 是设计目标，OAuth2 是实现方案之一
- ⚠️ **"JWT = SSO"是错觉** —— JWT 只是 Token 格式，可以携带 SSO 信任但不等于 SSO
- ⚠️ **"同域共享 Cookie = SSO"是反模式** —— 同源限制让跨域场景失效
- ⚠️ **"SAML 落伍"是错觉** —— 企业级（金融 / 政府）至今主流是 SAML 2.0

---

## 5. 一句话速查

```text
SSO 选型公式：
- 同公司同根域 → Cookie 共享（最简）
- 现代互联网 → OAuth2 + OIDC（最推荐）
- 老企业内部 → CAS（5 年前主流）
- 跨国/合规 → SAML 2.0（金融/政府）
- 微服务内部 → JWT + Redis 黑名单（最灵活）
```

---

## 6. 速查 · 关联资源

- **OAuth2 深度**：[oauth2-oidc](../oauth2-oidc/README.md) —— 500 行深度 + 流程图
- **JWT 深度**：[jwt-security](../jwt-security/README.md) —— 325 行深度
- **面试题**：[13.split-hairs/05.security/sso](../../../13.split-hairs/05.security/sso/README.md) —— 5-7 道精选题

---

← [返回: 安全设计](../README.md)
