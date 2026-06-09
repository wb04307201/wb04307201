# 权限模型：RBAC vs ABAC

> 访问控制是系统安全的核心组成部分。本文对比两种主流权限模型：RBAC（基于角色的访问控制）和 ABAC（基于属性的访问控制）。

## 目录

- [访问控制概述](#访问控制概述)
- [RBAC — 基于角色的访问控制](#rbac--基于角色的访问控制)
- [ABAC — 基于属性的访问控制](#abac--基于属性的访问控制)
- [RBAC vs ABAC 对比](#rbac-vs-abac-对比)
- [选型建议](#选型建议)
- [ReBAC — 基于关系的访问控制](#rebac--基于关系的访问控制)

---

## 访问控制概述

**访问控制（Access Control）** 是限制已认证用户能够访问哪些资源、执行哪些操作的机制。它是信息安全三要素 CIA（机密性、完整性、可用性）中**机密性**的核心保障。

### 访问控制决策要素

```
┌──────────┐     ┌───────────────┐     ┌──────────┐
│  主体     │────▶│  访问控制引擎  │────▶│  允许/拒绝 │
│ (Subject)│     │  (PDP/PEP)   │     │ (Decision)│
└──────────┘     └───────────────┘     └──────────┘
     │                    ▲
     │                    │
     │              ┌─────┴──────┐
     └─────────────▶│  策略/规则   │
                    │ (Policies)  │
                    └────────────┘
```

一个访问控制决策通常考虑三个要素：
- **主体（Subject）**：谁在请求？（用户、服务、角色）
- **客体（Object）**：请求什么？（资源、数据、功能）
- **动作（Action）**：做什么？（读、写、删除、执行）

---

## RBAC — 基于角色的访问控制

### 概念

**RBAC（Role-Based Access Control）** 通过**角色**作为中介来管理权限。权限不直接分配给用户，而是分配给角色，再将角色分配给用户。

### 核心模型

```
用户(User) ───N:M───▶ 角色(Role) ───N:M───▶ 权限(Permission)
```

- 一个用户可以拥有多个角色
- 一个角色可以分配给多个用户
- 一个角色可以包含多个权限
- 一个权限可以属于多个角色

### 数据库表设计

```sql
-- 用户表
CREATE TABLE sys_user (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(64) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    status      TINYINT DEFAULT 1
);

-- 角色表
CREATE TABLE sys_role (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_code   VARCHAR(64) NOT NULL UNIQUE,  -- 如 ADMIN, EDITOR
    role_name   VARCHAR(128) NOT NULL,
    description VARCHAR(255)
);

-- 权限表
CREATE TABLE sys_permission (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    perm_code   VARCHAR(128) NOT NULL UNIQUE, -- 如 user:read, user:write
    perm_name   VARCHAR(128) NOT NULL,
    resource    VARCHAR(128),                 -- 资源标识
    action      VARCHAR(32),                  -- 操作类型: read/write/delete
    description VARCHAR(255)
);

-- 用户-角色关联表
CREATE TABLE sys_user_role (
    id      BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    UNIQUE KEY uk_user_role (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES sys_user(id),
    FOREIGN KEY (role_id) REFERENCES sys_role(id)
);

-- 角色-权限关联表
CREATE TABLE sys_role_permission (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_id       BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    UNIQUE KEY uk_role_perm (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES sys_role(id),
    FOREIGN KEY (permission_id) REFERENCES sys_permission(id)
);
```

### Java 示例代码

```java
// 权限检查注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface RequirePermission {
    String value(); // 如 "user:delete"
}

// AOP 权限拦截器
@Aspect
@Component
public class PermissionInterceptor {

    @Autowired
    private PermissionService permissionService;

    @Around("@annotation(requirePermission)")
    public Object checkPermission(ProceedingJoinPoint pjp,
                                   RequirePermission requirePermission) throws Throwable {
        String requiredPerm = requirePermission.value();
        Long userId = SecurityContext.getCurrentUserId();

        if (!permissionService.hasPermission(userId, requiredPerm)) {
            throw new AccessDeniedException("无权执行操作: " + requiredPerm);
        }

        return pjp.proceed();
    }
}

// 权限检查服务
@Service
public class PermissionService {

    @Autowired
    private UserMapper userMapper;

    /**
     * 检查用户是否拥有指定权限
     */
    public boolean hasPermission(Long userId, String permCode) {
        // 1. 查询用户的所有角色
        List<Role> roles = userMapper.findRolesByUserId(userId);

        // 2. 查询这些角色的所有权限
        Set<String> permissions = new HashSet<>();
        for (Role role : roles) {
            permissions.addAll(userMapper.findPermissionsByRoleId(role.getId()));
        }

        // 3. 检查是否包含所需权限
        return permissions.contains(permCode);
    }

    /**
     * 优化: 使用单次 SQL 查询
     * SELECT DISTINCT p.perm_code
     * FROM sys_user_role ur
     * JOIN sys_role_permission rp ON ur.role_id = rp.role_id
     * JOIN sys_permission p ON rp.permission_id = p.id
     * WHERE ur.user_id = ?
     */
}
```

### 使用示例

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    @RequirePermission("user:read")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }

    @PostMapping
    @RequirePermission("user:write")
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }

    @DeleteMapping("/{id}")
    @RequirePermission("user:delete")
    public void deleteUser(@PathVariable Long id) {
        userService.deleteById(id);
    }
}
```

### RBAC 的变体

| 模型 | 说明 |
|------|------|
| RBAC0 | 基础 RBAC：用户-角色-权限 |
| RBAC1 | 引入**角色继承**（Senior Role ⊃ Junior Role） |
| RBAC2 | 引入**角色约束**（互斥角色：一个人不能同时拥有 A 和 B） |
| RBAC3 | 同时包含继承和约束 |

### 优缺点

**优点**:
- 模型简单直观，易于理解和实现
- 减少权限管理复杂度（N 个用户 × M 个权限 → 通过角色中间层简化）
- 适合组织架构明确的场景
- 审计方便（谁拥有什么角色一目了然）

**缺点**:
- **角色爆炸**：复杂场景下角色数量急剧膨胀
- **难以表达细粒度规则**：如"只能编辑自己创建的文档"
- **上下文不敏感**：不考虑时间、地点、设备等环境因素
- **维护成本高**：新增业务维度时需要新增大量角色

---

## ABAC — 基于属性的访问控制

### 概念

**ABAC（Attribute-Based Access Control）** 基于**属性**来定义访问控制策略。策略引擎在每次访问时动态评估主体属性、客体属性、环境属性和动作，决定允许或拒绝。

### 属性分类

| 属性类型 | 示例 |
|----------|------|
| 主体属性（Subject） | 用户ID、部门、职级、角色、会员等级 |
| 客体属性（Object/Resource） | 资源类型、所有者、标签、数据分类、密级 |
| 环境属性（Environment） | 时间、IP 地址、地理位置、设备类型、网络 |
| 动作属性（Action） | 读、写、删除、审批、导出 |

### 策略表达式

ABAC 使用策略表达式（Policy Expression）来定义规则：

```
策略示例 1: 工作时间限制
─────────────────────────
PERMIT IF
  subject.role == "employee"
  AND action == "access"
  AND environment.time BETWEEN "09:00" AND "18:00"
  AND environment.day IN ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

策略示例 2: 数据访问限制
─────────────────────────
PERMIT IF
  subject.department == resource.owner_department
  AND subject.security_clearance >= resource.classification_level

策略示例 3: 敏感操作
─────────────────────────
PERMIT IF
  action == "delete"
  AND subject.role IN ["admin", "owner"]
  AND environment.mfa_verified == true
  AND environment.ip NOT IN blacklist
```

### 伪代码实现

```java
// ABAC 策略引擎
public class AbacEngine {

    /**
     * 评估访问请求
     */
    public boolean evaluate(AbacRequest request) {
        // 1. 加载匹配的策略
        List<Policy> policies = policyRepository
            .findByResourceType(request.getResource().getType());

        // 2. 按优先级排序
        policies.sort(Comparator.comparingInt(Policy::getPriority));

        // 3. 逐条评估
        for (Policy policy : policies) {
            AccessDecision decision = policy.evaluate(request);
            if (decision != AccessDecision.NOT_APPLICABLE) {
                // DENY 优先（deny-override 模式）
                if (decision == AccessDecision.DENY) {
                    return false;
                }
                if (decision == AccessDecision.PERMIT) {
                    return true;
                }
            }
        }

        // 默认拒绝
        return false;
    }
}

// 策略评估
public class Policy {
    private String name;
    private int priority;
    private Expression condition; // SpEL, MVEL 等表达式
    private AccessDecision effect; // PERMIT / DENY

    public AccessDecision evaluate(AbacRequest request) {
        // 使用表达式引擎评估条件
        EvaluationContext context = new EvaluationContext();
        context.setVariable("subject", request.getSubject());
        context.setVariable("resource", request.getResource());
        context.setVariable("action", request.getAction());
        context.setVariable("environment", request.getEnvironment());

        boolean matches = expressionEvaluator.evaluate(condition, context);
        return matches ? effect : AccessDecision.NOT_APPLICABLE;
    }
}
```

### 适用场景

| 场景 | 说明 |
|------|------|
| 金融行业 | 基于客户资产等级、风险等级的差异化数据访问 |
| 医疗行业 | HIPAA 合规，基于患者同意状态的数据共享 |
| 多租户 SaaS | 租户隔离 + 组织内角色 + 资源归属的复合规则 |
| 文档协作 | 只能编辑/删除自己创建的文档 |
| 地理围栏 | 特定 IP 范围或地理位置才能访问敏感资源 |
| 时间敏感操作 | 仅在工作时间可执行管理操作 |

### 优缺点

**优点**:
- 极高的灵活性，可以表达任意复杂的访问规则
- 支持上下文感知（时间、地点、设备等）
- 减少角色数量，策略即代码
- 天然支持细粒度权限控制

**缺点**:
- 实现复杂度高，需要策略引擎和表达式引擎
- 性能开销较大（每次访问都要评估策略）
- 策略难以直观理解和审计
- 策略冲突难以排查（多条策略可能同时匹配）
- 对开发人员要求较高

---

## RBAC vs ABAC 对比

| 维度 | RBAC | ABAC |
|------|------|------|
| **决策依据** | 用户所属的角色 | 主体、客体、环境的多种属性 |
| **粒度** | 粗到中等（角色级别） | 细粒度（属性级别） |
| **策略数量** | 角色数量通常有限 | 策略数量可多可少，灵活 |
| **上下文感知** | 不支持 | 支持（时间、地点、设备等） |
| **实现复杂度** | 简单，标准 SQL 即可 | 复杂，需要策略引擎 |
| **性能** | 高（查表即可） | 中（需评估策略表达式） |
| **可维护性** | 角色多时管理复杂 | 策略多时调试困难 |
| **审计** | 容易（角色-权限映射清晰） | 较难（策略逻辑复杂） |
| **适用场景** | 组织架构明确的内部系统 | 需要细粒度控制的复杂场景 |

---

## 选型建议

### 何时选择 RBAC

- 组织架构清晰，角色定义明确（如企业内部管理系统）
- 权限规则相对简单，主要基于功能菜单和操作
- 团队规模较小，没有专门的权限管理团队
- 追求快速上线和易维护性
- **80% 的场景 RBAC 就足够了**

### 何时选择 ABAC

- 需要基于数据内容本身的权限（如"只能看自己的订单"）
- 需要环境上下文（时间、IP、地理位置）
- 多租户 SaaS，租户之间有复杂的隔离需求
- 合规要求严格（金融、医疗等行业）
- 角色数量爆炸，RBAC 已无法管理

### 混合方案（RBAC + ABAC）

在实践中，最常见的方案是**混合使用**：

1. **RBAC 做粗粒度控制**：确定用户可以访问哪些功能模块
2. **ABAC 做细粒度控制**：在功能内部，确定用户可以操作哪些具体数据

```
请求 ──▶ RBAC检查(功能权限) ──▶ ABAC检查(数据权限) ──▶ 允许/拒绝
         "能否访问订单管理？"     "能否看到这笔订单？"
```

---

## ReBAC — 基于关系的访问控制

**ReBAC（Relationship-Based Access Control）** 是基于实体之间**关系**的访问控制模型。典型例子：

- Google Docs 的共享机制："文档所有者可以邀请协作者"
- 社交网络："仅好友可见"
- GitHub："仓库的 Collaborator 可以 Push"

ReBAC 可以看作是 ABAC 的一个子集，其中关系本身就是一种属性。Zanzibar（Google 的统一权限系统）是 ReBAC 的经典实现。

### 三者关系

```
            ┌──────────────────┐
            │   访问控制        │
            │  Access Control   │
            └────────┬─────────┘
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   ┌───────┐   ┌──────────┐  ┌──────────┐
   │ RBAC  │   │   ABAC   │  │  ReBAC   │
   │ 角色  │   │   属性   │  │  关系    │
   └───────┘   └──────────┘  └──────────┘
                     │
              ReBAC 可视为
              ABAC 的特例
```

## 相关章节

- [JWT 存储安全](../jwt-security/README.md) — Token 中的 role / scope 如何从客户端传递到后端
- [OAuth2.0 与 OIDC](../oauth2-oidc/README.md) — scope / claim 设计与权限映射
- [API 安全](../api-security/README.md) — 接口层权限拦截与签名验证
- [OWASP Top 10](../owasp-top10/README.md) — A01 失效的访问控制详解

## 参考资料

- [NIST RBAC Standard](https://csrc.nist.gov/projects/role-based-access-control)
- [NIST ABAC Guide](https://csrc.nist.gov/pubs/sp/800/162/final)
- [Google Zanzibar Paper](https://research.google/pubs/zanzibar-googles-access-control-system/)
- [XACML - eXtensible Access Control Markup Language](https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=xacml)
- [CASBIN - 强大的访问控制库](https://casbin.org/)
