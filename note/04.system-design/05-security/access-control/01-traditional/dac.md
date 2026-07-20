# DAC（Discretionary Access Control，自主访问控制）

> 一句话定位：DAC 让资源所有者自主决定谁能访问自己的资源，权限可随所有者意志传递。

## 1. 概念与起源

**DAC（自主访问控制）** 是最朴素也最古老的访问控制模型之一。它的核心是"所有权"：谁创建了资源，谁就拥有决定谁能访问该资源的权力，且这种权力可以"自主"地传递给其他主体。

- **历史背景**：DAC 的思想源自 1970 年代早期的分时系统（如 Multics、UNIX）。UNIX 文件系统的 `rwx` 三组权限位（owner / group / other）就是 DAC 的经典实现。
- **核心思想**：每个资源都关联一个"所有者"（owner），所有者可以授予/撤销任意用户对该资源的读、写、执行权限，且这一过程无需中央授权机构介入。

**与 ACL 的关系**：ACL（Access Control List，访问控制列表）是 DAC 的**主流实现方式**——为每个资源维护一张"主体 → 权限"的列表，权限判定时查表即可。可以说 ACL = DAC 的工程化形态。

## 2. 核心模型图

```text
┌────────┐                ┌──────────────────┐
│ 主体 S │ ──请求访问───▶ │  资源 O 的 ACL   │
│ (用户) │                │  [S1: r/w]       │
└────────┘                │  [S2: r]         │
                          │  [G1: r/w/x]     │
                          └────────┬─────────┘
                                   │ 检查 S 是否在 ACL 且权限足够
                                   ▼
                          ┌──────────────────┐
                          │  PERMIT / DENY   │
                          └──────────────────┘
```

**与同族 MAC 的关键区别**：MAC 中主体对客体的权限不可被主体自主转让；DAC 中所有者可以"自主"地把权限授予任何人。

## 3. 表/数据结构

```sql
-- 主体（用户/组）表
CREATE TABLE sys_user (
    id        BIGINT PRIMARY KEY AUTO_INCREMENT,
    username  VARCHAR(64) NOT NULL UNIQUE
);

-- 资源表
CREATE TABLE sys_resource (
    id        BIGINT PRIMARY KEY AUTO_INCREMENT,
    name      VARCHAR(128) NOT NULL,
    owner_id  BIGINT NOT NULL,           -- 资源所有者（DAC 的关键字段）
    FOREIGN KEY (owner_id) REFERENCES sys_user(id)
);

-- 访问控制列表（ACL）：每个资源一张
CREATE TABLE acl_entry (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    resource_id  BIGINT NOT NULL,
    principal_id BIGINT NOT NULL,        -- 主体（用户或组的 id）
    principal_type VARCHAR(16) NOT NULL, -- 'USER' 或 'GROUP'
    permission   VARCHAR(16) NOT NULL,   -- 'READ' / 'WRITE' / 'EXECUTE'
    UNIQUE KEY uk_acl (resource_id, principal_id, principal_type, permission),
    FOREIGN KEY (resource_id) REFERENCES sys_resource(id)
);
```

## 4. 代码/伪代码示例

```java
public class AclService {

    /**
     * DAC 检查：当前主体对资源是否有指定权限
     */
    public boolean isAllowed(Long userId, Long resourceId, String permission) {
        // 1. 资源所有者直接放行
        Resource res = resourceMapper.findById(resourceId);
        if (res.getOwnerId().equals(userId)) {
            return true;
        }
        // 2. 查 ACL：用户本人权限
        if (aclMapper.exists(resourceId, userId, "USER", permission)) {
            return true;
        }
        // 3. 查 ACL：用户所属组的权限
        List<Long> groupIds = groupMapper.findGroupIdsByUserId(userId);
        for (Long gid : groupIds) {
            if (aclMapper.exists(resourceId, gid, "GROUP", permission)) {
                return true;
            }
        }
        return false;
    }
}
```

## 5. 优缺点

**优点**:
- 实现简单，三张表（用户/资源/ACL）即可落地
- 灵活，所有者可随时调整授权
- 与文件系统心智模型一致（UNIX、Windows NTFS 都是 DAC）
- 权限传递自然，适合协作场景（文档共享、共享盘）

**缺点**:
- **安全性弱**：所有者权限过大，可能把敏感资源随意分享
- **权限蔓延**：长期运行的系统会出现"谁都能访问一切"的局面，难以审计
- **无法表达组织级策略**：没有"敏感数据必须 2 人审批"这种约束
- **木马风险**：用户 A 的程序被植入木马后，木马可以读取 A 有权访问的所有资源
- **合规性差**：金融、医疗、政务等场景的合规要求（DAC 难以满足）

## 6. 适用与不适用场景

**适用**:
- 个人电脑、文件服务器（UNIX/Linux 文件权限就是 DAC）
- 文档协作工具（Google Docs 早期、Dropbox 的共享链接）
- 内部 wiki / 知识库的页面级权限
- 资源所有权清晰、所有者有能力判断该给谁授权的场景

**不适用**:
- 多用户共用敏感数据的数据库（需 MAC 或 ABAC）
- 金融系统的"四眼原则"（需 RBAC + 约束）
- 跨组织的资源隔离（多租户 SaaS 需 RBAC+ABAC）
- 合规审计要求严格的环境（HIPAA / PCI-DSS）

## 相关章节

- 族内：[MAC](mac.md) — DAC 的"反命题"，用密级标签 + 系统强制取代所有者自主
- 05-security 主题：[OAuth2.0 与 OIDC](../../oauth2-oidc/README.md) — DAC 在 OAuth2 中体现为 resource owner 授权
- 05-security 主题：[API 安全](../../api-security/README.md) — 接口层 DAC 校验示例
