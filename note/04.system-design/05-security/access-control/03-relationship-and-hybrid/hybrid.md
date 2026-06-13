# RBAC + ABAC 混合模型

> 一句话定位：RBAC 管"功能权限"（能否访问订单管理），ABAC 管"数据权限"（能否看到这笔订单）—— 这是工程实战中的黄金组合。

## 1. 概念与起源

**为什么需要混合**：纯 RBAC 解决"用户能访问哪些功能"，但解决不了"用户能看到哪些数据"；纯 ABAC 太重、性能差、维护成本高。实战经验沉淀出的最佳实践是**两层组合**：

- **第一层 RBAC**：粗粒度，决定用户能否进入某个功能模块
- **第二层 ABAC**：细粒度，决定用户在该模块内能操作哪些具体数据

- **历史背景**：从 2010 年代开始，随着 SaaS 与多租户系统普及，单一模型难以兼顾"组织管理简单 + 数据隔离灵活"，业界逐渐沉淀出"RBAC 粗 + ABAC 细"的双层模式
- **核心思想**：分层授权，每层用最合适的模型

## 2. 核心模型图

```
请求 → RBAC 检查(功能权限) → ABAC 检查(数据权限) → 允许/拒绝
         "能否访问订单管理？"     "能否看到这笔订单？"
                │                          │
                ▼                          ▼
         hasRole("order_mgr")    subject.dept == resource.owner_dept
                                       AND
                                  subject.level >= resource.sensitivity
```

## 3. 表/数据结构

混合模型在数据层 = RBAC 表 + ABAC 表 + 一个"权限上下文"中间层

```sql
-- RBAC 部分（5 张核心表，复用 rbac.md §3）
-- sys_user, sys_role, sys_permission, sys_user_role, sys_role_permission

-- ABAC 上下文：补充"数据范围"维度
CREATE TABLE data_scope_rule (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_id     BIGINT NOT NULL,         -- 关联角色
    scope_type  VARCHAR(32) NOT NULL,    -- 'DEPT' / 'SELF' / 'CUSTOM' / 'ALL'
    scope_value VARCHAR(255),            -- 具体值（部门 ID / 自定义 SQL 片段）
    FOREIGN KEY (role_id) REFERENCES sys_role(id)
);
```

## 4. 代码/伪代码示例

```java
// 双层检查
public class HybridPermissionChecker {

    public boolean check(Long userId, String resourceCode, Long resourceId) {
        // 第一层：RBAC 功能权限
        if (!rbacService.hasPermission(userId, resourceCode)) {
            return false;
        }
        // 第二层：ABAC 数据权限
        return abacService.evaluateDataScope(userId, resourceCode, resourceId);
    }
}

// 典型场景：销售订单列表
public class OrderService {

    public List<Order> listOrders(Long currentUserId) {
        // RBAC：是否有 order:list 权限
        if (!permChecker.check(currentUserId, "order:list", null)) {
            throw new AccessDeniedException();
        }
        // ABAC：根据用户数据范围过滤
        DataScope scope = dataScopeService.getScope(currentUserId, "order");
        return switch (scope.getType()) {
            case ALL   -> orderMapper.findAll();
            case DEPT  -> orderMapper.findByDept(scope.getValue());
            case SELF  -> orderMapper.findByOwner(currentUserId);
            case CUSTOM -> orderMapper.findByCustomSql(scope.getValue());
        };
    }
}
```

## 5. 优缺点

**优点**:
- 兼顾管理简单性（RBAC）与表达灵活性（ABAC）
- 性能可控：RBAC 是快速失败，ABAC 只在 RBAC 通过后才执行
- 团队技能门槛低：只需具备 RBAC 基础 + 简单 ABAC 表达式
- 适合 90% 内部业务系统的真实场景

**缺点**:
- 两套机制需要协调（缓存、审计、调试）
- 数据权限的"自定义 SQL"容易成为安全漏洞（需严格审查）
- 跨层组合时容易出现"RBAC 通过但 ABAC 通过"看似正确实则不合理的情况
- 文档/培训成本：需同时讲两套模型

## 6. 适用与不适用场景

**适用**:
- **90% 的企业级业务系统**：CRM、ERP、OA、HR
- 多租户 SaaS（RBAC 管租户内功能，ABAC 管跨租户数据隔离）
- 有"数据归属"概念的协作工具（销售订单、客服工单、项目任务）
- 团队对 RBAC 熟悉、但偶尔需要细粒度控制

**不适用**:
- 极简场景（纯 RBAC 就够）
- 极复杂场景（需要 ReBAC + ABAC + Zanzibar 分布式授权）
- 高频热路径（ABAC 评估的 RTT 不可接受）

## 演进路径建议

```
阶段 1（系统 < 100 角色）         → 纯 RBAC0
阶段 2（系统 100–1000 角色）     → RBAC1 + 角色继承
阶段 3（出现"只能看自己的"）     → RBAC + ABAC 混合（本模型）
阶段 4（出现"共享/协作者"需求）  → 引入 ReBAC（与 RBAC/ABAC 并存）
阶段 5（多产品统一权限）         → 引入 Zanzibar 风格的 ReBAC 中台
```

## 主流实现

- **MyBatis-Plus DataPermissionInterceptor**：国内最常见的 RBAC+ABAC 落地模式
- **Spring Security + SpEL**：项目内轻量混合
- **Casbin**：支持 RBAC/ABAC/ReBAC 多种模型的统一引擎

## 相关章节

- 族内：[ReBAC](rebac.md) — 复杂协作场景的进一步升级
- 跨族：[RBAC](../02-role-and-attribute/rbac.md) / [ABAC](../02-role-and-attribute/abac.md)
- 总章：[选型决策树](../README.md#3-选型决策树) — 何时该用本混合模型
