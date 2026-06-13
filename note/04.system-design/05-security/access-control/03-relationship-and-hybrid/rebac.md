# ReBAC（Relationship-Based Access Control，基于关系的访问控制）

> 一句话定位：ReBAC 以实体间关系（共享、好友、协作者）作为决策依据，Google Zanzibar 是工业级经典实现。

## 1. 概念与起源

**ReBAC** 把"权限"建模为**实体间的关系图**——回答"用户 S 与资源 R 之间是否存在一条满足条件的关系路径"。它是 ABAC 的特例（关系本身就是一种属性），但在分布式授权场景中独立成族。

- **历史背景**：2019 年 Google 发表《Zanzibar: Google's Consistent, Global Authorization System》论文，公开支撑 Google Docs / Drive / Cloud 等全部产品的统一权限系统
- **核心思想**：权限 = `Check(user, relation, object)`，决策依据是关系图上的可达性

**与 ABAC 的关键区别**：ABAC 用"属性 + 策略表达式"；ReBAC 用"关系图 + 关系查询"。ReBAC 表达"Alice 共享了 doc:1 给 Bob 的整个团队"很自然，ABAC 需要复杂表达式。

## 2. 核心模型图

```
        ┌──────────────┐
        │   User:alice │
        └──────┬───────┘
               │ owner
               ▼
        ┌──────────────┐
        │   Doc:readme │
        └──────┬───────┘
               │ viewer
        ┌──────┴───────┐
        ▼              ▼
  ┌──────────┐   ┌──────────────┐
  │User:bob  │   │Group:editor  │
  └──────────┘   └──────┬───────┘
                       │ member
                       ▼
                ┌──────────────┐
                │ User:carol   │
                └──────────────┘

决策: Check(alice, viewer, doc:readme) ?
       alice → owner(doc:readme) → 有 viewer 权限 → PERMIT
```

## 3. 表/数据结构

### 关系表（最朴素实现）

```sql
CREATE TABLE rebac_relation (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    subject_type  VARCHAR(32) NOT NULL,  -- 'user' / 'group' / 'org'
    subject_id    VARCHAR(64) NOT NULL,
    relation      VARCHAR(64) NOT NULL,  -- 'owner' / 'viewer' / 'editor' / 'member'
    object_type   VARCHAR(32) NOT NULL,  -- 'doc' / 'folder' / 'project'
    object_id     VARCHAR(64) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_subject (subject_type, subject_id),
    INDEX idx_object (object_type, object_id, relation)
);
```

### Zanzibar 风格：把每条关系建模为 (object#relation@user) 元组

```
doc:readme#owner@user:alice
doc:readme#viewer@user:bob
group:editor#member@user:carol
doc:readme#viewer@group:editor#member
```

## 4. 代码/伪代码示例

```java
// 朴素 ReBAC：递归查询关系图
public class RebacEngine {

    public boolean check(String subject, String relation, String object) {
        // 1. 直接关系
        if (relationRepo.exists(subject, relation, object)) {
            return true;
        }
        // 2. 通过组继承（如 viewer@group → member@user）
        List<GroupMembership> memberships = groupRepo.findByUser(subject);
        for (GroupMembership m : memberships) {
            String groupSubject = m.getGroupType() + ":" + m.getGroupId();
            if (relationRepo.exists(groupSubject, relation, object)) {
                return true;
            }
        }
        return false;
    }
}
```

### SpiceDB（Zanzibar 开源实现）调用

```java
// 客户端
client = SpiceDBClient.builder()
    .endpoint("localhost:50051")
    .token("dev-token")
    .build();

PermissionResponse resp = client.check(
    CheckRequest.newBuilder()
        .setSubject(SubjectReference.newBuilder()
            .setObject(ObjectReference.newBuilder()
                .setObjectType("user").setObjectId("alice")))
        .setPermission("viewer")
        .setResource(ObjectReference.newBuilder()
            .setObjectType("doc").setObjectId("readme"))
        .build()
);
// resp.getPermissionship() == Permissionship.PERMISSIONSHIP_HAS_PERMISSION
```

## 5. 优缺点

**优点**:
- 表达"共享、好友、协作者"等关系型权限最自然
- 支持关系继承（用户继承所在组的权限）
- 可形式化校验（一致性、封闭性）
- 适合分布式系统（Google 每天处理数十亿次 Check 调用）

**缺点**:
- 实现复杂（图遍历、缓存、一致性）
- 关系爆炸时性能下降（需精心设计索引与缓存）
- 不适合表达"工作时间内"等环境属性（用 ABAC）
- 学习成本高（团队需理解 Zanzibar / SpiceDB 概念）

## 6. 适用与不适用场景

**适用**:
- 文档协作（Google Docs、Notion、飞书文档）
- 社交网络（"仅好友可见"）
- 代码托管（GitHub 仓库的 Collaborator / Team 权限）
- 多层级组织（母公司→子公司→部门→员工的资源继承）
- 需要"细粒度资源级权限"的产品

**不适用**:
- 简单 CRUD 内部系统（RBAC 足矣）
- 高频低延迟 API 网关层鉴权（Zanzibar 调用有 RTT）
- 只需"是 / 否"二值权限的简单场景

## 主流实现

- **Google Zanzibar**：论文 + 工业实现（不对外）
- **SpiceDB**：Authzed 维护的开源 Zanzibar 实现
- **OpenFGA**：Auth0 开源，Zanzibar-inspired
- **Permify**：另一个开源 ReBAC 服务

## 相关章节

- 族内：[混合模型](hybrid.md) — ReBAC 与 RBAC/ABAC 的组合用法
- 跨族：[RBAC](../02-role-and-attribute/rbac.md) / [ABAC](../02-role-and-attribute/abac.md)
- 05-security 主题：[OAuth2.0 与 OIDC](../oauth2-oidc/README.md) — OAuth2 scope 是简化版 ReBAC
