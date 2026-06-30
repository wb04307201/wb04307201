# 访问控制：6 大权限模型与选型指南

## 引言：生产 Bug（[AUTO] 自动生成，待人工 review）

访问控制：6 大权限模型与选型指南 的一句话定位：访问控制是把「谁能对什么做什么」这一决策工程化的学科

**但实际**：常被攻击或出 Bug 后背锅。本篇用'生产场景'切入：
线上怎么炸、有没有上线过的坑、为什么按官方文档写也会错。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---


> 一句话定位：访问控制是把「谁能对什么做什么」这一决策工程化的学科。

## 1. 谱系与心智模型

访问控制模型按"决策依据"形成 3 大家族：

```
                  访问控制（Access Control）
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
  ┌──────────┐      ┌──────────┐      ┌──────────┐
  │ 传统族    │      │ 角色属性族│      │ 关系混合族│
  │ 身份即权限│      │ 中介间接  │      │ 关系图+组合│
  └────┬─────┘      └────┬─────┘      └────┬─────┘
       │                 │                 │
       ▼                 ▼                 ▼
   DAC / MAC        RBAC / ABAC        ReBAC / 混合
```

| 模型 | 决策依据 | 粒度 | 实现复杂度 | 典型场景 |
|------|----------|------|------------|----------|
| DAC | 资源所有者的意志 | 粗-中 | 简单 | 个人电脑、文件共享 |
| MAC | 主体/客体密级标签 | 中-细 | 复杂 | 军方、政务、合规系统 |
| RBAC | 用户所属角色 | 粗-中 | 简单 | 企业内部系统 |
| ABAC | 主体/客体/环境属性 | 细 | 复杂 | 多租户 SaaS、文档协作 |
| ReBAC | 实体间关系 | 细 | 复杂 | 文档共享、社交网络 |
| 混合 | RBAC+ABAC 双层 | 中-细 | 中 | 90% 企业业务系统 |

## 2. 三大族索引

- **传统族**：身份即权限，不引入中间抽象 → [01-traditional](01-traditional/README.md)
- **角色属性族**：把权限从人身上抽到中介（角色/属性）→ [02-role-and-attribute](02-role-and-attribute/README.md)
- **关系与混合族**：关系图与实战组合 → [03-relationship-and-hybrid](03-relationship-and-hybrid/README.md)

## 3. 选型决策树

```
问 1: 业务有清晰组织架构吗？
  ├─ 是 → 问 2
  └─ 否 → 问 4
问 2: 权限规则可以全部用"角色"表达吗？
  ├─ 是 → RBAC
  └─ 否 → 问 3
问 3: 规则依赖"谁/什么/何时/何地"中除"谁"以外的因素吗？
  ├─ 是 → ABAC
  └─ 否 → RBAC + 数据范围补充（混合模型）
问 4: 权限依赖"实体间关系"（文档共享、好友、协作者）吗？
  ├─ 是 → ReBAC
  └─ 否 → 问 5
问 5: 是在做内部系统还是对外产品？
  ├─ 内部系统 → RBAC（80% 情况）
  └─ 对外产品 + 合规 → RBAC+ABAC 混合
```

**速记口诀**：

- 想"简单" → RBAC
- 想"灵活" → ABAC
- 想"协作" → ReBAC
- 想"不踩坑" → 混合

## 4. 横向对比表（含主流实现）

| 模型 | 主流实现 / 代表产品 |
|------|---------------------|
| DAC | UNIX 文件权限 / Windows NTFS / Web 资源 owner |
| MAC | SELinux / AppArmor / Windows Mandatory Integrity Control |
| RBAC | Spring Security / Casbin / Apache Shiro |
| ABAC | Open Policy Agent (OPA) / AWS IAM / Cerbos |
| ReBAC | Google Zanzibar (SpiceDB) / Auth0 FGA / Permify |
| 混合 | MyBatis-Plus DataPermission / Spring Security + SpEL |

## 5. 演进路径与混合策略

### 演进路径

```
DAC ──→ RBAC ──→ ABAC ──→ ReBAC
                       │
                       └──→ 混合（RBAC+ABAC，最常见实战）
```

**何时升级**：
- 角色数量超过 50，且仍在增长 → 考虑 ABAC
- 出现"共享给某人/某团队"的需求 → 考虑 ReBAC
- 需要"只能看自己创建的"等数据归属 → 引入 ABAC 或混合

### 黄金组合

**RBAC 做功能权限 + ABAC 做数据权限**（详见 [hybrid](03-relationship-and-hybrid/hybrid.md)）：

```
请求 ──▶ RBAC 检查（能否访问订单管理？）──▶ ABAC 检查（能否看到这笔订单？）──▶ 允许/拒绝
```

这是 90% 企业业务系统的最佳实践起点。

## 相关章节

- 05-security 主题：
  - [JWT 存储安全](../jwt-security/README.md) — Token 中的 role / scope 传递
  - [OAuth2.0 与 OIDC](../oauth2-oidc/README.md) — 鉴权协议层的 scope / claim
  - [API 安全](../api-security/README.md) — 接口层权限拦截
  - [OWASP Top 10](../owasp-top10/README.md) — A01 失效的访问控制
  - [加密与密钥管理](../encryption/README.md)
  - [密钥与凭据管理](../secrets-management/README.md)
- 04-system-design：[分布式 ID](../../02-distributed/distributed-id/README.md) — 权限实体常用雪花 ID