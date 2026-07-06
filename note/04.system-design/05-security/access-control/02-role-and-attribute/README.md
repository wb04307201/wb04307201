<!--
module:
  parent: system-design
  slug: system-design/02-role-and-attribute
  type: article
  category: 主模块子文章
  summary: 角色与属性族：把权限从人身上抽到中介 的一句话定位：把"权限"从用户身上抽到"角色"或"属性"中介，解决 DAC/MAC 的可维护性问题
-->

# 角色与属性族：把权限从人身上抽到中介

## 引言：生产 Bug

角色与属性族：把权限从人身上抽到中介 的关键不是'防住'——是**出事后 5 分钟内能定位**。

本篇用真实生产场景切入：线上怎么炸、按官方文档写为什么也会错、怎么止血。

---

> 一句话定位：把"权限"从用户身上抽到"角色"或"属性"中介，解决 DAC/MAC 的可维护性问题。

## 共同问题域

传统族的痛点：用户-资源关系直接绑定，权限管理复杂度随用户数 × 资源数线性增长。

角色与属性族通过引入**间接层**解决这个问题：

- **RBAC**：引入"角色"作为用户与权限的中介（用户 → 角色 → 权限）
- **ABAC**：引入"属性"作为决策依据（属性 + 策略表达式 → 决策）

## 设计哲学

- **RBAC** 假设"权限可以按角色分类"，追求简单稳定
- **ABAC** 假设"权限需要按上下文动态计算"，追求灵活表达

**80% 的企业业务系统，RBAC 就够**；剩下 20% 需要在 RBAC 基础上加 ABAC（混合模型）。

## 族内模型

- [RBAC](rbac.md) — 基于角色的访问控制：用户→角色→权限，5 张表的经典模型
- [ABAC](abac.md) — 基于属性的访问控制：基于主体/客体/环境属性的策略表达式，灵活但复杂

## 与其他族的关系

```
DAC ──→ RBAC ──→ ABAC ──→ ReBAC
              │        │
              └── 混合 ┘
```

- RBAC 是 DAC 的"中介化"
- ABAC 是 RBAC 的"动态化"
- 混合模型是 RBAC + ABAC 的"工程组合"

## 相关章节

- [传统族](../01-traditional/README.md) — RBAC/ABAC 的"前传"
- [关系与混合族](../03-relationship-and-hybrid/README.md) — 进一步演进
- [选型总章](../README.md#3-选型决策树) — 何时该选 RBAC/ABAC
- 05-security：[OAuth2.0 与 OIDC](../../oauth2-oidc/README.md) — OAuth2 scope 是简化版 RBAC
- 05-security：[JWT 存储安全](../../jwt-security/README.md) — Token 中的 role / claim

← [返回: 系统设计 · 02-role-and-attribute](README.md)
