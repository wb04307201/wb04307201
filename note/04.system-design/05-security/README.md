# 安全篇

> 系统安全是软件的生命线。本模块涵盖鉴权、授权、API 安全、加密、密钥管理等关键主题。

## 鉴权与存储

1. [JWT 存储安全](jwt-security/README.md) — JWT 结构 / 攻击防御 / 安全存储 / Token 撤销
2. [OAuth2.0 与 OIDC](oauth2-oidc/README.md) — 授权码 / PKCE / 客户端凭证三种推荐模式

## 权限与防护

3. [访问控制](access-control/README.md) — 6 大权限模型与选型决策
   - [传统族](access-control/01-traditional/README.md)（DAC / MAC）
   - [角色属性族](access-control/02-role-and-attribute/README.md)（RBAC / ABAC）
   - [关系与混合族](access-control/03-relationship-and-hybrid/README.md)（ReBAC / RBAC+ABAC）
4. [API 安全](api-security/README.md) — 签名验证 / 防重放 / 数据脱敏 / 限流

## 应用安全与密码学

5. [OWASP Top 10](owasp-top10/README.md) — 2021 版 10 大 Web 应用安全风险
6. [加密与密钥管理](encryption/README.md) — 对称 / 非对称 / 哈希 / TLS / KMS
7. [密钥与凭据管理](secrets-management/README.md) — Vault / KMS / 轮换 / 12-Factor
