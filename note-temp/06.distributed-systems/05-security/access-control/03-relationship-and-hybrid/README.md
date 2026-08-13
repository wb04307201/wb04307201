<!--
module:
  parent: system-design
  slug: system-design/03-relationship-and-hybrid
  type: article
  category: 主模块子文章
  summary: 关系与混合族：关系图与实战组合 本应该很简单，一句话定位：用"实体间关系"作为决策依据的模型，以及工程实战中最常见的组合
-->

# 关系与混合族：关系图与实战组合

---

> 一句话定位：用"实体间关系"作为决策依据的模型，以及工程实战中最常见的组合。

## 共同问题域

角色与属性族解决了"用户能做什么"，但在两类场景下仍力不从心：

1. **关系型权限**：文档共享给某人、协作者权限、好友可见——这些本质上是"实体间关系"
2. **实战组合**：单一模型难以兼顾"管理简单 + 数据灵活"，需要分层组合

本族给出两个补完：

- **ReBAC**：以关系图为决策依据（Zanzibar 风格）
- **混合**：RBAC+ABAC 实战组合

## 设计哲学

- **ReBAC** 假设"权限可以表达为关系查询"，追求表达力与一致性
- **混合** 假设"不同决策层用不同模型更合适"，追求工程平衡

## 族内模型

- [ReBAC](rebac.md) — 基于关系的访问控制：以实体间关系作为决策依据
- [混合模型](hybrid.md) — RBAC+ABAC 实战组合：90% 企业业务系统的最佳实践

## 与其他族的关系

```text
DAC ──→ RBAC ──→ ABAC ──→ ReBAC
              │        │
              └── 混合 ┘
```

- ReBAC 可视为 ABAC 的特例（关系是属性的子集）
- 混合是 RBAC + ABAC 的"工程级组合"

## 相关章节

- [角色与属性族](../02-role-and-attribute/README.md) — 混合模型的上游
- [传统族](../01-traditional/README.md) — 访问控制的两条根本路线
- [选型总章](../README.md#3-选型决策树) — 何时该选 ReBAC / 混合
- 05-security：[OAuth2.0 与 OIDC](../../oauth2-oidc/README.md) — OAuth2 资源共享即简化 ReBAC

← [返回 访问控制](../README.md)
