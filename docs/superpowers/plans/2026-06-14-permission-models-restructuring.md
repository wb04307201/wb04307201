# 权限模型体系重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把分散在 `04.system-design/05-security/rbac-abac/` 与 `note/09.other/permission/` 的两份权限模型文档，整合为 6 个主流模型 + 1 份选型总章的自洽小体系，落地 6 个 commit。

**Architecture:** 6 步走完，每步 1 commit：(1) 建 10 个新文件的骨架 → (2) 迁 12 张图 → (3) 填 6 个模型正文 → (4) 填总章 + 3 个族索引 → (5) 改 3 处引用方 → (6) 删 2 个旧目录。

**Tech Stack:** Markdown / Git / Bash（`mv` / `rm -rf` / `grep` / `find` / `ls`）

**Spec 参考:** [`docs/superpowers/specs/2026-06-14-permission-models-restructuring-design.md`](../../specs/2026-06-14-permission-models-restructuring-design.md)

---

## 文件结构（变更前后）

### 变更前

- `note/04.system-design/05-security/rbac-abac/README.md`（15.9KB，含 RBAC/ABAC/ReBAC + Java + SQL）
- `note/09.other/permission/README.md`（9.3KB + 12 张 png：img.png, img_1.png ... img_11.png）

### 变更后

```
note/04.system-design/05-security/access-control/
├── README.md                              ← 选型总章（5 段：谱系 / 索引 / 决策树 / 对比 / 演进）
├── 01-traditional/
│   ├── README.md                          ← 族索引
│   ├── dac.md                             ← DAC
│   └── mac.md                             ← MAC
├── 02-role-and-attribute/
│   ├── README.md                          ← 族索引
│   ├── rbac.md                            ← RBAC0/1/2/3
│   └── abac.md                            ← ABAC
└── 03-relationship-and-hybrid/
    ├── README.md                          ← 族索引
    ├── rebac.md                           ← ReBAC
    └── hybrid.md                          ← RBAC+ABAC 混合
```

- 12 张 png 全部迁到 `02-role-and-attribute/`
- `05-security/rbac-abac/` 与 `09.other/permission/` 整体删除

---

## 任务依赖

```
Task 1 (骨架) → Task 2 (迁图) ─┐
                               ├→ Task 3 (6 模型正文) → Task 4 (总章 + 族索引) → Task 5 (改引用) → Task 6 (清旧)
                               └─────────────────────────────┘
```

Task 2 和 Task 3 都需要 access-control 目录已存在（Task 1 已建）；Task 3 不依赖 Task 2 的图（图片可后续在 Task 4 之后再补），但建议保持 Task 2 → Task 3 顺序，让 Task 3 直接引用图片。

---

## Task 1：新建 access-control 目录骨架

**Files:**
- Create: `note/04.system-design/05-security/access-control/README.md`
- Create: `note/04.system-design/05-security/access-control/01-traditional/README.md`
- Create: `note/04.system-design/05-security/access-control/01-traditional/dac.md`
- Create: `note/04.system-design/05-security/access-control/01-traditional/mac.md`
- Create: `note/04.system-design/05-security/access-control/02-role-and-attribute/README.md`
- Create: `note/04.system-design/05-security/access-control/02-role-and-attribute/rbac.md`
- Create: `note/04.system-design/05-security/access-control/02-role-and-attribute/abac.md`
- Create: `note/04.system-design/05-security/access-control/03-relationship-and-hybrid/README.md`
- Create: `note/04.system-design/05-security/access-control/03-relationship-and-hybrid/rebac.md`
- Create: `note/04.system-design/05-security/access-control/03-relationship-and-hybrid/hybrid.md`

- [ ] **Step 1.1：写总章骨架 `access-control/README.md`**

用 Write 工具创建文件，内容：

```markdown
# 访问控制：6 大权限模型与选型指南

> 一句话定位：访问控制是把「谁能对什么做什么」这一决策工程化的学科。

## 1. 谱系与心智模型
（待 Task 4 填充）

## 2. 三大族索引
（待 Task 4 填充）

## 3. 选型决策树
（待 Task 4 填充）

## 4. 横向对比表
（待 Task 4 填充）

## 5. 演进路径与混合策略
（待 Task 4 填充）

## 相关章节
（待 Task 4 填充）
```

- [ ] **Step 1.2：写族索引骨架 `01-traditional/README.md`**

用 Write 工具创建文件，内容：

```markdown
# 传统访问控制：身份即权限

> 一句话定位：传统访问控制以"主体"本身作为决策依据，不引入中间抽象。

## 共同问题域
（待 Task 4 填充）

## 族内模型
- [DAC](dac.md) — 自主访问控制：资源所有者自主决定谁能访问自己的资源
- [MAC](mac.md) — 强制访问控制：基于主体与客体的密级标签，由系统强制裁决

## 相关章节
（待 Task 4 填充）
```

- [ ] **Step 1.3：写 DAC 模型骨架 `01-traditional/dac.md`**

用 Write 工具创建文件，内容：

```markdown
# DAC（Discretionary Access Control，自主访问控制）

> 一句话定位：DAC 让资源所有者自主决定谁能访问自己的资源。

## 1. 概念与起源
（待 Task 3 填充）

## 2. 核心模型图
（待 Task 3 填充）

## 3. 表/数据结构
（待 Task 3 填充）

## 4. 代码/伪代码示例
（待 Task 3 填充）

## 5. 优缺点
（待 Task 3 填充）

## 6. 适用与不适用场景
（待 Task 3 填充）

## 相关章节
（待 Task 3 填充）
```

- [ ] **Step 1.4：写 MAC 模型骨架 `01-traditional/mac.md`**

用 Write 工具创建文件。结构与 DAC 完全一致，仅替换：标题 `DAC` → `MAC`；副标题「资源所有者自主决定谁能访问自己的资源」→「基于主体与客体的密级标签，由系统强制裁决，不允许自主转让」。

- [ ] **Step 1.5：写族索引骨架 `02-role-and-attribute/README.md`**

用 Write 工具创建文件，内容：

```markdown
# 角色与属性族：把权限从人身上抽到中介

> 一句话定位：把"权限"从用户身上抽到"角色"或"属性"中介，解决 DAC/MAC 的可维护性问题。

## 共同问题域
（待 Task 4 填充）

## 族内模型
- [RBAC](rbac.md) — 基于角色的访问控制：用户→角色→权限，5 张表的经典模型
- [ABAC](abac.md) — 基于属性的访问控制：基于主体/客体/环境属性的策略表达式，灵活但复杂

## 相关章节
（待 Task 4 填充）
```

- [ ] **Step 1.6：写 RBAC 模型骨架 `02-role-and-attribute/rbac.md`**

用 Write 工具创建文件，结构与 DAC 骨架完全一致。标题：`RBAC`；副标题：「基于角色的访问控制，权限不直接分配给用户，而是分配给角色再分配给用户。」

- [ ] **Step 1.7：写 ABAC 模型骨架 `02-role-and-attribute/abac.md`**

用 Write 工具创建文件，结构与 DAC 骨架完全一致。标题：`ABAC`；副标题：「基于属性的访问控制，决策依据是主体/客体/环境/动作四类属性，由策略引擎动态评估。」

- [ ] **Step 1.8：写族索引骨架 `03-relationship-and-hybrid/README.md`**

用 Write 工具创建文件，内容：

```markdown
# 关系与混合族：关系图与实战组合

> 一句话定位：用"实体间关系"作为决策依据的模型，以及工程实战中最常见的组合。

## 共同问题域
（待 Task 4 填充）

## 族内模型
- [ReBAC](rebac.md) — 基于关系的访问控制：以实体间关系（共享、好友、协作者）作为决策依据
- [混合模型](hybrid.md) — RBAC+ABAC 实战组合：RBAC 管功能权限 + ABAC 管数据权限

## 相关章节
（待 Task 4 填充）
```

- [ ] **Step 1.9：写 ReBAC 模型骨架 `03-relationship-and-hybrid/rebac.md`**

用 Write 工具创建文件，结构与 DAC 骨架完全一致。标题：`ReBAC`；副标题：「基于关系的访问控制，以实体间关系（文档共享、好友、协作者）作为决策依据；Google Zanzibar 是经典工业实现。」

- [ ] **Step 1.10：写混合模型骨架 `03-relationship-and-hybrid/hybrid.md`**

用 Write 工具创建文件，结构与 DAC 骨架完全一致。标题：`RBAC+ABAC 混合模型`；副标题：「实战中最常见的组合：RBAC 管功能权限（能否访问订单管理），ABAC 管数据权限（能否看到这笔订单）。」

- [ ] **Step 1.11：验证文件结构**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
find note/04.system-design/05-security/access-control -type f -name '*.md' | sort
```

Expected: 恰好 10 行，按字母序：
```
note/04.system-design/05-security/access-control/01-traditional/README.md
note/04.system-design/05-security/access-control/01-traditional/dac.md
note/04.system-design/05-security/access-control/01-traditional/mac.md
note/04.system-design/05-security/access-control/02-role-and-attribute/README.md
note/04.system-design/05-security/access-control/02-role-and-attribute/abac.md
note/04.system-design/05-security/access-control/02-role-and-attribute/rbac.md
note/04.system-design/05-security/access-control/03-relationship-and-hybrid/README.md
note/04.system-design/05-security/access-control/03-relationship-and-hybrid/hybrid.md
note/04.system-design/05-security/access-control/03-relationship-and-hybrid/rebac.md
note/04.system-design/05-security/access-control/README.md
```

- [ ] **Step 1.12：验证 6 段标题完整**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
for f in note/04.system-design/05-security/access-control/01-traditional/dac.md \
         note/04.system-design/05-security/access-control/01-traditional/mac.md \
         note/04.system-design/05-security/access-control/02-role-and-attribute/rbac.md \
         note/04.system-design/05-security/access-control/02-role-and-attribute/abac.md \
         note/04.system-design/05-security/access-control/03-relationship-and-hybrid/rebac.md \
         note/04.system-design/05-security/access-control/03-relationship-and-hybrid/hybrid.md; do
  count=$(grep -c '^## [1-6]\.' "$f")
  echo "$f: $count 段"
done
```

Expected: 每个文件都返回 `6 段`。

- [ ] **Step 1.13：Commit Task 1**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
git add note/04.system-design/05-security/access-control/
git status
git commit -m "docs(perm): 新建 access-control 目录骨架" \
  -m "新增 10 个 Markdown 文件（1 总章 + 3 族索引 + 6 模型），每个模型固定 6 段式骨架。" \
  -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: 10 个新文件 staged，1 commit 创建。

---

## Task 2：迁移 12 张图到 `02-role-and-attribute/`

**Files:**
- Move: `note/09.other/permission/img.png` → `note/04.system-design/05-security/access-control/02-role-and-attribute/img.png`
- Move: 同上模式迁移 `img_1.png` 至 `img_11.png`（共 12 张）

- [ ] **Step 2.1：执行 11 次 mv**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
SRC=note/09.other/permission
DST=note/04.system-design/05-security/access-control/02-role-and-attribute
mv "$SRC"/img.png     "$DST"/img.png
mv "$SRC"/img_1.png   "$DST"/img_1.png
mv "$SRC"/img_2.png   "$DST"/img_2.png
mv "$SRC"/img_3.png   "$DST"/img_3.png
mv "$SRC"/img_4.png   "$DST"/img_4.png
mv "$SRC"/img_5.png   "$DST"/img_5.png
mv "$SRC"/img_6.png   "$DST"/img_6.png
mv "$SRC"/img_7.png   "$DST"/img_7.png
mv "$SRC"/img_8.png   "$DST"/img_8.png
mv "$SRC"/img_9.png   "$DST"/img_9.png
mv "$SRC"/img_10.png  "$DST"/img_10.png
mv "$SRC"/img_11.png  "$DST"/img_11.png
```

Expected: 无输出（mv 成功默认不输出）。

- [ ] **Step 2.2：验证图已迁到新位置**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
find note/04.system-design/05-security/access-control -name 'img*.png' | wc -l
```

Expected: 输出 `11`。

- [ ] **Step 2.3：验证老位置无残留**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
find note/09.other/permission -name 'img*.png' | wc -l
```

Expected: 输出 `0`。

- [ ] **Step 2.4：Commit Task 2**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
git add -A note/04.system-design/05-security/access-control/02-role-and-attribute/
git add -A note/09.other/permission/
git status
git commit -m "docs(perm): 迁移 RBAC/ABAC 配图到 02-role-and-attribute" \
  -m "把 09.other/permission/ 下的 12 张 png 整体迁到 02-role-and-attribute/，为 Task 3 模型正文引用做准备。" \
  -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: 12 张图重命名移动 staged（在 git 里表现为「renamed」），1 commit 创建。

---

## Task 3：填充 6 个模型正文（≤ 6 个子任务，可分批执行）

> **本任务最大**：6 个模型文档，每个 ≤ 400–600 行。
> 建议分 6 个独立子任务（3.1–3.6）逐个 commit；但 spec 要求 1 个 commit，所以本任务内部**所有 6 个文件改完后统一 commit 一次**。

### 共同前置：内容来源映射

| 模型 | 内容来源 |
|------|----------|
| DAC | 改写自 `note/09.other/permission/README.md` §ACL + §DAC（去除 MAC 部分） |
| MAC | 改写自 `note/09.other/permission/README.md` §AC（Mandatory）+ 补充 BLP / Biba |
| RBAC | 整合 `note/04.system-design/05-security/rbac-abac/README.md` §RBAC + 9 张图（img.png, img_2–11） + 改写自 09.other §RBAC 三要素 / RBAC0–3 |
| ABAC | 整合 `rbac-abac/README.md` §ABAC + 1 张图（img_1.png） + 改写自 09.other §ABAC 四要素 |
| ReBAC | 改写自 `rbac-abac/README.md` §ReBAC（已有较完整） |
| 混合 | 新写 |

### Step 3.1：填充 `01-traditional/dac.md`（≤ 400 行）

- [ ] **Step 3.1.1：用 Write 覆盖 `01-traditional/dac.md`**

完整内容如下（直接复制写入文件）：

```markdown
# DAC（Discretionary Access Control，自主访问控制）

> 一句话定位：DAC 让资源所有者自主决定谁能访问自己的资源，权限可随所有者意志传递。

## 1. 概念与起源

**DAC（自主访问控制）** 是最朴素也最古老的访问控制模型之一。它的核心是"所有权"：谁创建了资源，谁就拥有决定谁能访问该资源的权力，且这种权力可以"自主"地传递给其他主体。

- **历史背景**：DAC 的思想源自 1970 年代早期的分时系统（如 Multics、UNIX）。UNIX 文件系统的 `rwx` 三组权限位（owner / group / other）就是 DAC 的经典实现。
- **核心思想**：每个资源都关联一个"所有者"（owner），所有者可以授予/撤销任意用户对该资源的读、写、执行权限，且这一过程无需中央授权机构介入。

**与 ACL 的关系**：ACL（Access Control List，访问控制列表）是 DAC 的**主流实现方式**——为每个资源维护一张"主体 → 权限"的列表，权限判定时查表即可。可以说 ACL = DAC 的工程化形态。

## 2. 核心模型图

```
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
- 05-security 主题：[OAuth2.0 与 OIDC](../oauth2-oidc/README.md) — DAC 在 OAuth2 中体现为 resource owner 授权
- 05-security 主题：[API 安全](../api-security/README.md) — 接口层 DAC 校验示例
```

### Step 3.2：填充 `01-traditional/mac.md`（≤ 400 行）

- [ ] **Step 3.2.1：用 Write 覆盖 `01-traditional/mac.md`**

完整内容如下：

```markdown
# MAC（Mandatory Access Control，强制访问控制）

> 一句话定位：MAC 用主体与客体的密级标签做强制裁决，所有者不能自主转让权限。

## 1. 概念与起源

**MAC（强制访问控制）** 与 DAC 的根本区别在于：**权限不由资源所有者决定，而由系统按"密级标签"强制裁决**。每个主体和客体都被赋予一个安全级别（如"绝密 / 机密 / 秘密 / 公开"），访问能否发生取决于双方级别的数学关系。

- **历史背景**：1970 年代由美国国防部为多级安全（MLS, Multi-Level Security）系统设计。理论奠基是 **Bell-LaPadula 模型（1973）**（保密性）与 **Biba 模型（1977）**（完整性）。
- **核心思想**：系统强制执行"无上读、无下写"（BLP）或"无下读、无上写"（Biba）这类不变量，主体无法绕过。

**与 DAC 的关键区别**：DAC 中所有者可"自主"转让权限；MAC 中即使你是资源所有者，也不能把"绝密"文件授予"公开"级别的主体——系统会拒绝。

## 2. 核心模型图

```
            ┌───────────────────────────────┐
            │   密级标签（Label）            │
            │                               │
主体 S ────▶│ Clearance: 机密                │
            │                               │
客体 O ────▶│ Classification: 秘密            │
            │                               │
            │ BLP 规则: Clearance ≥ Class    │
            │ → 允许读                      │
            └───────────────────────────────┘
```

### Bell-LaPadula（保密性）

- **No Read Up（NRU）**：主体只能读 ≤ 自己密级的客体（防止高级别信息泄露给低级别主体）
- **No Write Down（NWD）**：主体只能写 ≥ 自己密级的客体（防止高级别主体把信息"下沉"给低级别客体）

### Biba（完整性）

- **No Read Down（NRD）**：主体只能读 ≥ 自己密级的客体（防止低完整性数据污染高完整性主体）
- **No Write Up（NWU）**：主体只能写 ≤ 自己密级的客体（防止高完整性主体被低完整性数据污染）

## 3. 表/数据结构

```sql
-- 主体（含安全许可级别）
CREATE TABLE mac_subject (
    id        BIGINT PRIMARY KEY AUTO_INCREMENT,
    username  VARCHAR(64) NOT NULL,
    clearance INT NOT NULL,             -- 安全许可级别，数值越大越高级
    -- 1=公开, 2=秘密, 3=机密, 4=绝密
);

-- 客体（含密级）
CREATE TABLE mac_object (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    name          VARCHAR(128) NOT NULL,
    classification INT NOT NULL,        -- 客体密级
);

-- 访问决策（通常不需要这张表，决策由函数实时计算）
-- 若需审计可加：
CREATE TABLE mac_audit (
    id         BIGINT PRIMARY KEY AUTO_INCREMENT,
    subject_id BIGINT,
    object_id  BIGINT,
    action     VARCHAR(16),
    decision   VARCHAR(8),  -- PERMIT / DENY
    ts         TIMESTAMP
);
```

## 4. 代码/伪代码示例

```java
public class MacEngine {

    /**
     * BLP 决策：能否 "读" 客体
     */
    public boolean canRead(MacSubject subject, MacObject object) {
        // No Read Up: 主体 clearance ≥ 客体 classification
        return subject.getClearance() >= object.getClassification();
    }

    /**
     * BLP 决策：能否 "写" 客体
     */
    public boolean canWrite(MacSubject subject, MacObject object) {
        // No Write Down: 主体 clearance ≤ 客体 classification
        return subject.getClearance() <= object.getClassification();
    }
}
```

### 现实例子：SELinux

```bash
# SELinux 是 Linux 内核的 MAC 实现
# 给文件打标签
chcon -t httpd_sys_content_t /var/www/html/index.html

# 给进程（主体）授权
setsebool -P httpd_read_user_content 1
```

## 5. 优缺点

**优点**:
- **安全性最强**：系统强制执行，主体无法绕过
- **抗木马**：即使主体被植入木马，也无法读取更高密级信息
- **可证明性**：基于形式化模型（BLP/Biba），可通过数学证明安全性
- **合规友好**：满足军方、政务、金融的高安全要求

**缺点**:
- **实现工作量大**：每个主体/客体都要打标签
- **灵活性差**：新增业务维度（如"只能编辑自己创建的文档"）需新增标签维度
- **运维成本高**：用户无法自助授权，所有授权需走流程
- **不适合互联网产品**：用户量级大、场景多变，标签管理会爆炸

## 6. 适用与不适用场景

**适用**:
- 军事 / 政务系统的涉密数据
- 金融核心系统的"四类用户"分级
- 医疗系统的 HIPAA 合规
- SELinux / AppArmor 等操作系统级强制访问控制

**不适用**:
- 互联网产品的 C 端用户（量级与灵活度不匹配）
- 协作型 SaaS（用户需要自主分享）
- 快速迭代的内部业务系统（标签跟不上变化）
- 需要"按时间/IP 限制访问"的场景（用 ABAC）

## 相关章节

- 族内：[DAC](dac.md) — DAC 与 MAC 是访问控制的两条根本路线
- 05-security 主题：[加密与密钥管理](../encryption/README.md) — 加密是 MAC 之外的另一道防线
- 05-security 主题：[OWASP Top 10](../owasp-top10/README.md) — A01 失效的访问控制
```

### Step 3.3：填充 `02-role-and-attribute/rbac.md`（≤ 600 行，整合 rbac-abac + 9 张图 + 0–3 变体）

- [ ] **Step 3.3.1：用 Write 覆盖 `02-role-and-attribute/rbac.md`**

完整内容如下（直接复制）：

```markdown
# RBAC（Role-Based Access Control，基于角色的访问控制）

> 一句话定位：RBAC 把权限从用户身上抽到"角色"中介，权限不直接分配给用户，而是分配给角色再分配给用户。

## 1. 概念与起源

**RBAC** 是 1990 年代由美国 NIST（David Ferraiolo 与 Rick Kuhn）系统化的访问控制模型，2004 年成为 ANSI INCITS 359 标准。它的核心洞察是：**权限数量远远小于"用户 × 资源"笛卡尔积，把权限先绑定到"角色"再把角色分配给用户，可以指数级降低管理成本**。

- **历史背景**：1992 年 Ferraiolo & Kuhn 论文；2004 年 ANSI RBAC 标准；2007 年 NIST 给出 RBAC 参考模型
- **核心思想**：用户（User）→ 角色（Role）→ 权限（Permission）三层间接，权限不直接落到用户

## 2. 核心模型图

### RBAC0（基线模型）

![标准 RBAC 模型](img_5.png)

### RBAC1（角色继承）

![RBAC1 角色继承](img_6.png)

### RBAC2（角色约束）

![RBAC2 角色互斥](img_7.png)

### RBAC3（用户组 + 组织 + 职位）

![理想 RBAC 模型](img_2.png)

![用户组](img_10.png)

![权限可分组](img_9.png)

![组织与数据权限](img_11.png)

![RBAC3 职位映射](img_8.png)

## 3. 表/数据结构

### 最小版（RBAC0）

![标准 RBAC 表设计](img_4.png)

### 完整版（含组织/职位/用户组）

![理想 RBAC 表设计](img_3.png)

### SQL 落地（核心 5 张表）

```sql
CREATE TABLE sys_user (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(64) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    status      TINYINT DEFAULT 1
);

CREATE TABLE sys_role (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_code   VARCHAR(64) NOT NULL UNIQUE,
    role_name   VARCHAR(128) NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE sys_permission (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    perm_code   VARCHAR(128) NOT NULL UNIQUE, -- 如 user:read, user:write
    perm_name   VARCHAR(128) NOT NULL,
    resource    VARCHAR(128),
    action      VARCHAR(32),
    description VARCHAR(255)
);

CREATE TABLE sys_user_role (
    id      BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    UNIQUE KEY uk_user_role (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES sys_user(id),
    FOREIGN KEY (role_id) REFERENCES sys_role(id)
);

CREATE TABLE sys_role_permission (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_id       BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    UNIQUE KEY uk_role_perm (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES sys_role(id),
    FOREIGN KEY (permission_id) REFERENCES sys_permission(id)
);
```

## 4. 代码/伪代码示例

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

    /**
     * 优化: 使用单次 SQL 查询
     * SELECT DISTINCT p.perm_code
     * FROM sys_user_role ur
     * JOIN sys_role_permission rp ON ur.role_id = rp.role_id
     * JOIN sys_permission p ON rp.permission_id = p.id
     * WHERE ur.user_id = ?
     */
    public boolean hasPermission(Long userId, String permCode) {
        return permissionMapper.countUserPermissions(userId, permCode) > 0;
    }
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

    @DeleteMapping("/{id}")
    @RequirePermission("user:delete")
    public void deleteUser(@PathVariable Long id) {
        userService.deleteById(id);
    }
}
```

## 5. 优缺点

**优点**:
- 模型简单直观，5 张表即可落地
- 大幅降低管理复杂度（N 个用户 × M 个权限 → N + M）
- 适合组织架构明确的内部系统
- 审计清晰（角色-权限映射一目了然）

**缺点**:
- **角色爆炸**：复杂场景下角色数量急剧膨胀（销售一部经理、销售二部经理、销售三部经理...）
- **难以表达细粒度规则**："只能编辑自己创建的文档"无法用纯角色表达
- **上下文不敏感**：不考虑时间、地点、设备
- **数据权限弱**：纯 RBAC 不解决"销售 A 只能看自己的客户"问题（需配合 ABAC）

## 6. 适用与不适用场景

**适用**:
- 企业内部管理系统（OA、ERP、CRM）
- 权限规则主要基于功能菜单和操作
- 团队规模较小，没有专门的权限管理团队
- 追求快速上线和易维护性

**不适用**:
- 权限依赖"只能看自己创建的"等数据归属（用 ABAC）
- 权限依赖时间/IP 等环境因素（用 ABAC）
- 多租户 SaaS，租户之间有复杂隔离（用 RBAC+ABAC）
- 角色数量爆炸的复杂场景（用 ABAC）

## RBAC 的 4 个变体

| 模型 | 关键扩展 | 典型场景 |
|------|----------|----------|
| RBAC0 | 用户-角色-权限基础模型 | 80% 内部系统 |
| RBAC1 | 增加角色继承（Senior ⊃ Junior） | 经理 / 主管 / 员工分层 |
| RBAC2 | 增加角色约束（互斥、基数、先决条件） | "出纳"与"会计"互斥 |
| RBAC3 | RBAC1 + RBAC2 综合 | 复杂组织 |

### 三要素（核心概念）

- **用户（User）**：系统中的所有账户
- **角色（Role）**：一系列权限的集合
- **权限（Permission）**：菜单、按钮、数据的增删改查

## 相关章节

- 族内：[ABAC](abac.md) — RBAC 的"细粒度 + 上下文感知"升级版
- 05-security 主题：[OAuth2.0 与 OIDC](../oauth2-oidc/README.md) — OAuth2 的 scope 是"角色化权限"的一种
- 05-security 主题：[API 安全](../api-security/README.md) — 接口层 RBAC 拦截
- 05-security 主题：[OWASP Top 10](../owasp-top10/README.md) — A01 失效的访问控制
```

### Step 3.4：填充 `02-role-and-attribute/abac.md`（≤ 600 行）

- [ ] **Step 3.4.1：用 Write 覆盖 `02-role-and-attribute/abac.md`**

完整内容如下：

```markdown
# ABAC（Attribute-Based Access Control，基于属性的访问控制）

> 一句话定位：ABAC 基于主体/客体/环境/动作四类属性，由策略引擎动态评估，灵活度最高。

## 1. 概念与起源

**ABAC** 又称 **PBAC（Policy-Based Access Control）** 或 **CBAC（Claims-Based Access Control）**。它的核心思想是：**不再把权限绑死到"角色"，而是基于"属性 + 策略表达式"在每次访问时动态评估**。

- **历史背景**：2000 年代由 OASIS 的 XACML（eXtensible Access Control Markup Language）标准化；2014 年 NIST 发布 SP 800-162 指南
- **核心思想**：策略即代码，决策 = `eval(策略表达式, 主体属性 ∪ 客体属性 ∪ 环境属性 ∪ 动作属性)`

**与 RBAC 的关键区别**：RBAC 用"角色"这一个间接层；ABAC 用"任意属性"作为决策依据，理论上可表达任意复杂规则。

## 2. 核心模型图

![ABAC 关系图](img_1.png)

### 四要素

- **对象（Subject）**：当前请求访问资源的用户。属性包括 ID、个人资源、角色、部门、组织成员身份
- **资源（Object/Resource）**：当前用户要访问的资产或对象。属性包括类型、所有者、标签、数据分类、密级
- **操作（Action）**：用户试图对资源进行的操作（读取、写入、编辑、复制、删除）
- **环境（Environment）**：访问请求的上下文（时间、位置、设备、通信协议、加密强度）

## 3. 表/数据结构

```sql
-- 用户属性
CREATE TABLE user_attribute (
    id        BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id   BIGINT NOT NULL,
    attr_key  VARCHAR(64) NOT NULL,   -- 如 'department' / 'level' / 'clearance'
    attr_val  VARCHAR(255) NOT NULL,
    UNIQUE KEY uk_user_attr (user_id, attr_key)
);

-- 资源属性
CREATE TABLE resource_attribute (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    resource_id  BIGINT NOT NULL,
    attr_key     VARCHAR(64) NOT NULL,
    attr_val     VARCHAR(255) NOT NULL,
    UNIQUE KEY uk_res_attr (resource_id, attr_key)
);

-- 策略
CREATE TABLE abac_policy (
    id        BIGINT PRIMARY KEY AUTO_INCREMENT,
    name      VARCHAR(128) NOT NULL,
    effect    VARCHAR(8) NOT NULL,    -- 'PERMIT' / 'DENY'
    priority  INT DEFAULT 0,
    condition TEXT NOT NULL,          -- 策略表达式（SpEL / Rego / JSON Logic）
    enabled   TINYINT DEFAULT 1
);
```

## 4. 代码/伪代码示例

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

        // 3. 逐条评估（deny-override 模式）
        for (Policy policy : policies) {
            AccessDecision decision = policy.evaluate(request);
            if (decision == AccessDecision.DENY) {
                return false;
            }
            if (decision == AccessDecision.PERMIT) {
                return true;
            }
        }
        return false; // 默认拒绝
    }
}

// 策略评估
public class Policy {
    private String name;
    private int priority;
    private Expression condition; // SpEL / MVEL / OPA Rego
    private AccessDecision effect;

    public AccessDecision evaluate(AbacRequest request) {
        EvaluationContext ctx = new EvaluationContext();
        ctx.setVariable("subject", request.getSubject());
        ctx.setVariable("resource", request.getResource());
        ctx.setVariable("action", request.getAction());
        ctx.setVariable("environment", request.getEnvironment());

        boolean matches = expressionEvaluator.evaluate(condition, ctx);
        return matches ? effect : AccessDecision.NOT_APPLICABLE;
    }
}
```

### 策略表达式示例（XACML / Rego 风格）

```
策略 1: 工作时间限制
─────────────────────────
PERMIT IF
  subject.role == "employee"
  AND action == "access"
  AND environment.time BETWEEN "09:00" AND "18:00"
  AND environment.day IN ["Monday", ..., "Friday"]

策略 2: 数据访问限制（"销售只能看自己部门客户"）
─────────────────────────
PERMIT IF
  subject.department == resource.owner_department
  AND subject.security_clearance >= resource.classification_level

策略 3: 敏感操作（删除）
─────────────────────────
PERMIT IF
  action == "delete"
  AND subject.role IN ["admin", "owner"]
  AND environment.mfa_verified == true
  AND environment.ip NOT IN blacklist
```

## 5. 优缺点

**优点**:
- 极高的灵活性，可表达任意复杂规则
- 上下文感知（时间、地点、设备、网络）
- 减少"角色爆炸"问题，策略即代码
- 天然支持细粒度（数据级、字段级）权限

**缺点**:
- 实现复杂度高，需要策略引擎和表达式引擎
- 性能开销（每次访问都评估策略）
- 策略难以直观理解（vs 角色-权限映射）
- 策略冲突排查困难（多条策略可能同时匹配）
- 对开发/运维要求高

## 6. 适用与不适用场景

**适用**:
- 金融行业（基于客户资产等级、风险等级的差异化数据访问）
- 医疗行业（HIPAA 合规，基于患者同意状态的数据共享）
- 多租户 SaaS（租户隔离 + 组织内角色 + 资源归属的复合规则）
- 文档协作（只能编辑/删除自己创建的文档）
- 地理围栏（特定 IP 范围或地理位置才能访问敏感资源）
- 时间敏感操作（仅工作时间可执行管理操作）

**不适用**:
- 简单 CRUD 的内部系统（RBAC 足矣）
- 性能极敏感的热路径（每次策略评估都是开销）
- 团队不具备表达式/策略调试能力

## 主流实现

- **Open Policy Agent (OPA)**：CNCF 毕业项目，Rego 语言，云原生事实标准
- **AWS IAM**：策略文档即 ABAC
- **Cerbos**：开源 ABAC 服务
- **Spring Security 表达式**：项目内轻量 ABAC

## 相关章节

- 族内：[RBAC](rbac.md) — ABAC 是 RBAC 的"细粒度 + 上下文"升级
- 跨族：[混合模型](../03-relationship-and-hybrid/hybrid.md) — 实战黄金组合：RBAC + ABAC
- 05-security 主题：[OAuth2.0 与 OIDC](../oauth2-oidc/README.md) — OAuth2 的 claim 即 ABAC 的"主体属性"
- 05-security 主题：[API 安全](../api-security/README.md)
```

### Step 3.5：填充 `03-relationship-and-hybrid/rebac.md`（≤ 400 行）

- [ ] **Step 3.5.1：用 Write 覆盖 `03-relationship-and-hybrid/rebac.md`**

完整内容如下：

```markdown
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
```

### Step 3.6：填充 `03-relationship-and-hybrid/hybrid.md`（≤ 350 行）

- [ ] **Step 3.6.1：用 Write 覆盖 `03-relationship-and-hybrid/hybrid.md`**

完整内容如下：

```markdown
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
```

- [ ] **Step 3.7：验证 6 段完整 + 行数合规**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
for f in note/04.system-design/05-security/access-control/01-traditional/dac.md \
         note/04.system-design/05-security/access-control/01-traditional/mac.md \
         note/04.system-design/05-security/access-control/02-role-and-attribute/rbac.md \
         note/04.system-design/05-security/access-control/02-role-and-attribute/abac.md \
         note/04.system-design/05-security/access-control/03-relationship-and-hybrid/rebac.md \
         note/04.system-design/05-security/access-control/03-relationship-and-hybrid/hybrid.md; do
  count=$(grep -c '^## [1-6]\.' "$f")
  lines=$(wc -l < "$f")
  echo "$f: $count 段, $lines 行"
done
```

Expected:
- dac.md: 6 段, ≤ 400 行
- mac.md: 6 段, ≤ 400 行
- rbac.md: 6 段, ≤ 600 行
- abac.md: 6 段, ≤ 600 行
- rebac.md: 6 段, ≤ 400 行
- hybrid.md: 6 段, ≤ 350 行

- [ ] **Step 3.8：验证图片引用已生效**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
grep -rn '!\[' note/04.system-design/05-security/access-control/ | wc -l
```

Expected: 至少 9（rbac.md 引用 9 张图）+ 1（abac.md 引用 1 张）= 10 张图引用。

- [ ] **Step 3.9：验证图片文件都存在**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
for img in img.png img_1.png img_2.png img_3.png img_4.png img_5.png img_6.png img_7.png img_8.png img_9.png img_10.png img_11.png; do
  [ -f "note/04.system-design/05-security/access-control/02-role-and-attribute/$img" ] && echo "✓ $img" || echo "✗ $img MISSING"
done
```

Expected: 11 行 `✓ ...`，无 `MISSING`。

- [ ] **Step 3.10：Commit Task 3**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
git add note/04.system-design/05-security/access-control/01-traditional/dac.md \
        note/04.system-design/05-security/access-control/01-traditional/mac.md \
        note/04.system-design/05-security/access-control/02-role-and-attribute/rbac.md \
        note/04.system-design/05-security/access-control/02-role-and-attribute/abac.md \
        note/04.system-design/05-security/access-control/03-relationship-and-hybrid/rebac.md \
        note/04.system-design/05-security/access-control/03-relationship-and-hybrid/hybrid.md
git status
git commit -m "docs(perm): 填充 6 个模型正文" \
  -m "dac/mac/rebac/hybrid 新写；rbac 整合 05-security/rbac-abac 全部内容 + 9 张图 + RBAC0-3 变体；abac 整合 rbac-abac ABAC + 1 张图。" \
  -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: 6 个文件修改 staged，1 commit 创建。

---

## Task 4：填充总章 README + 3 个族索引 README

**Files:**
- Modify: `note/04.system-design/05-security/access-control/README.md`（覆盖骨架）
- Modify: `note/04.system-design/05-security/access-control/01-traditional/README.md`（覆盖骨架）
- Modify: `note/04.system-design/05-security/access-control/02-role-and-attribute/README.md`（覆盖骨架）
- Modify: `note/04.system-design/05-security/access-control/03-relationship-and-hybrid/README.md`（覆盖骨架）

- [ ] **Step 4.1：填充总章 `access-control/README.md`**

用 Write 覆盖，内容如下：

```markdown
# 访问控制：6 大权限模型与选型指南

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
- 04-system-design：[分布式 ID](../02-distributed/distributed-id/README.md) — 权限实体常用雪花 ID
```

- [ ] **Step 4.2：填充族索引 `01-traditional/README.md`**

用 Write 覆盖，内容如下：

```markdown
# 传统访问控制：身份即权限

> 一句话定位：传统访问控制以"主体"本身作为决策依据，不引入中间抽象。

## 共同问题域

传统族解决的是"最早的访问控制"问题：在没有"角色"或"属性"这类间接抽象时，权限该如何组织？它有两个根本分支：

- **DAC（自主访问控制）**：所有者说了算
- **MAC（强制访问控制）**：系统按密级强制裁决

## 设计哲学

传统族的核心假设是"系统用户数量小、资源数量少、关系简单"。在这种假设下：

- DAC 让"最懂资源的人（所有者）"做授权决策，符合直觉
- MAC 用"密级标签"这种最纯粹的属性做强制判决，安全性最高

一旦系统规模膨胀、组织层级加深，传统族就会让位给 RBAC / ABAC。

## 族内模型

- [DAC](dac.md) — 自主访问控制：资源所有者自主决定谁能访问自己的资源
- [MAC](mac.md) — 强制访问控制：基于主体与客体的密级标签，由系统强制裁决

## 与其他族的关系

```
DAC ──→ RBAC（"所有者"被"角色"取代）
MAC ──→ ABAC（"密级标签"是属性的一种特例）
```

DAC 是 RBAC 的"前传"，MAC 是 ABAC 的"前身"。

## 相关章节

- [角色与属性族](../02-role-and-attribute/README.md) — 现代系统的首选
- [关系与混合族](../03-relationship-and-hybrid/README.md) — 进一步演进
- [选型总章](../README.md#3-选型决策树) — 何时该选 DAC/MAC
- 05-security：[OWASP Top 10](../owasp-top10/README.md) — A01 失效的访问控制
```

- [ ] **Step 4.3：填充族索引 `02-role-and-attribute/README.md`**

用 Write 覆盖，内容如下：

```markdown
# 角色与属性族：把权限从人身上抽到中介

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
- 05-security：[OAuth2.0 与 OIDC](../oauth2-oidc/README.md) — OAuth2 scope 是简化版 RBAC
- 05-security：[JWT 存储安全](../jwt-security/README.md) — Token 中的 role / claim
```

- [ ] **Step 4.4：填充族索引 `03-relationship-and-hybrid/README.md`**

用 Write 覆盖，内容如下：

```markdown
# 关系与混合族：关系图与实战组合

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

```
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
- 05-security：[OAuth2.0 与 OIDC](../oauth2-oidc/README.md) — OAuth2 资源共享即简化 ReBAC
```

- [ ] **Step 4.5：验证总章含决策树 + 对比表**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
f=note/04.system-design/05-security/access-control/README.md
echo "=== 决策树 ==="
grep -c "问 [0-9]" "$f"
echo "=== 对比表行数 ==="
grep -c "^|" "$f"
echo "=== 主流实现表 ==="
grep -A 7 "主流实现 / 代表产品" "$f" | head -10
```

Expected:
- 决策树至少出现 5 次"问 N"
- 对比表行数 ≥ 10
- "主流实现 / 代表产品" 表完整

- [ ] **Step 4.6：验证族索引包含族内模型链接**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
for d in 01-traditional 02-role-and-attribute 03-relationship-and-hybrid; do
  f=note/04.system-design/05-security/access-control/$d/README.md
  count=$(grep -c '\[.*\](.*\.md)' "$f")
  echo "$d/README.md: $count 个内部链接"
done
```

Expected: 每个族索引至少 4 个内部链接（族内 2 个模型 + 跨族 3 个 + 总章 1 个）。

- [ ] **Step 4.7：Commit Task 4**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
git add note/04.system-design/05-security/access-control/README.md \
        note/04.system-design/05-security/access-control/01-traditional/README.md \
        note/04.system-design/05-security/access-control/02-role-and-attribute/README.md \
        note/04.system-design/05-security/access-control/03-relationship-and-hybrid/README.md
git status
git commit -m "docs(perm): 填充总章与族索引" \
  -m "总章含谱系图 / 决策树 / 横向对比表 / 演进路径；3 个族索引分别解释族内模型的设计哲学与跨族血缘。" \
  -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: 4 个 README 修改 staged，1 commit 创建。

---

## Task 5：更新 3 处引用方

**Files:**
- Modify: `note/04.system-design/05-security/README.md`
- Modify: `note/04.system-design/README.md`
- Modify: `note/README.md`

- [ ] **Step 5.1：更新 `05-security/README.md` 的"权限与防护"段**

读取当前文件后，把"权限与防护"段从：

```markdown
## 权限与防护

3. [权限模型](rbac-abac/README.md) — RBAC / ABAC / ReBAC 对比与实现
4. [API 安全](api-security/README.md) — 签名验证 / 防重放 / 数据脱敏 / 限流
```

改为：

```markdown
## 权限与防护

3. [访问控制](access-control/README.md) — 6 大权限模型与选型决策
   - [传统族](access-control/01-traditional/README.md)（DAC / MAC）
   - [角色属性族](access-control/02-role-and-attribute/README.md)（RBAC / ABAC）
   - [关系与混合族](access-control/03-relationship-and-hybrid/README.md)（ReBAC / RBAC+ABAC）
4. [API 安全](api-security/README.md) — 签名验证 / 防重放 / 数据脱敏 / 限流
```

- [ ] **Step 5.2：更新 `05-security/README.md` 文件头部"鉴权与存储"段中的顺序（如需要）**

保持原 1/2/3/4/5/6/7 顺序不变；只改第 3 项的链接。

- [ ] **Step 5.3：更新 `04.system-design/README.md` 安全模块的说明**

读取当前文件，把"05 安全"对应行（位于"📂 模块导航"表格第 5 行）从：

```markdown
| [05 安全篇](05-security/README.md) | 4 | JWT、OAuth2、权限模型、API安全 |
```

改为：

```markdown
| [05 安全篇](05-security/README.md) | 7 | JWT、OAuth2、API安全、OWASP、加密、密钥管理、访问控制 |
```

并把表格后的知识地图 ASCII 图（§1）"05 安全"分支下的"权限模型"扩展为：

```
JWT/OAuth2
RBAC/API安全
权限模型
```

保持原样（权限模型仍在分支节点上）。也可不动 ASCII 图，仅改表格行。

- [ ] **Step 5.4：更新 `note/README.md` 第四节表格第 5 行**

读取当前文件，把第四节"四、[系统设计]"的表格第 5 行从：

```markdown
| 5 | [安全](04.system-design/05-security/README.md) | API 安全、加密、JWT、OAuth2、OWASP Top 10、RBAC/ABAC、密钥管理 |
```

改为：

```markdown
| 5 | [安全](04.system-design/05-security/README.md) | API 安全、加密、JWT、OAuth2、OWASP Top 10、密钥管理 |
| 5a | [访问控制](04.system-design/05-security/access-control/README.md) | 6 大权限模型（DAC/MAC/RBAC/ABAC/ReBAC/混合）与选型决策 |
```

- [ ] **Step 5.5：更新 `note/README.md` 第九节：删除 `09.other/permission` 整条引用**

读取当前文件，删除：

```markdown
## [权限控制](09.other/permission/README.md)
```

如果该行前后有空行，也要一并清理（保持 README.md 的"## 其他"段落整洁）。

- [ ] **Step 5.6：验证 3 处引用方已更新**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
echo "=== 05-security 残留 rbac-abac ==="
grep -n 'rbac-abac' note/04.system-design/05-security/README.md || echo "✓ 无残留"
echo "=== 04-system-design 残留 rbac-abac ==="
grep -n 'rbac-abac' note/04.system-design/README.md || echo "✓ 无残留"
echo "=== note/README 残留 09.other/permission ==="
grep -n '09.other/permission' note/README.md || echo "✓ 无残留"
echo "=== 05-security 访问控制 链接 ==="
grep -n 'access-control' note/04.system-design/05-security/README.md
echo "=== note/README 访问控制 链接 ==="
grep -n 'access-control' note/README.md
```

Expected:
- 前三行全输出 `✓ 无残留`
- 后两行各至少 1 行匹配

- [ ] **Step 5.7：Commit Task 5**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
git add note/04.system-design/05-security/README.md \
        note/04.system-design/README.md \
        note/README.md
git status
git commit -m "docs(perm): 更新 3 处索引引用" \
  -m "05-security/README 把权限模型指向新 access-control；04-system-design/README 安全模块内容数 4→7；note/README 第四节拆出访问控制 5a 子项；第九节删除 09.other/permission 引用。" \
  -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: 3 个文件修改 staged，1 commit 创建。

---

## Task 6：清理已迁移的旧目录

**Files:**
- Delete: `note/04.system-design/05-security/rbac-abac/`（整目录）
- Delete: `note/09.other/permission/`（整目录）

- [ ] **Step 6.1：删除 rbac-abac 目录**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
rm -rf note/04.system-design/05-security/rbac-abac
ls note/04.system-design/05-security/ | grep rbac-abac && echo "✗ 残留" || echo "✓ 已删除"
```

Expected: 输出 `✓ 已删除`。

- [ ] **Step 6.2：删除 09.other/permission 目录**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
rm -rf note/09.other/permission
ls note/09.other/ 2>&1 | grep permission && echo "✗ 残留" || echo "✓ 已删除"
```

Expected: 输出 `✓ 已删除`。

- [ ] **Step 6.3：全仓交叉引用最终扫描**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
echo "=== rbac-abac 残留 ==="
grep -rn 'rbac-abac' note/ docs/ 2>/dev/null || echo "✓ 全仓无残留"
echo "=== 09.other/permission 残留 ==="
grep -rn '09.other/permission' note/ docs/ 2>/dev/null || echo "✓ 全仓无残留"
echo "=== 12 张图都在新位置 ==="
find note/04.system-design/05-security/access-control -name 'img*.png' | wc -l
```

Expected:
- 前两行都输出 `✓ 全仓无残留`
- 最后一行输出 `11`

- [ ] **Step 6.4：验证最终目录结构**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
echo "=== access-control 完整结构 ==="
find note/04.system-design/05-security/access-control -type f | sort
echo "=== 05-security 主题列表 ==="
ls note/04.system-design/05-security/
echo "=== 09.other 主题列表（应不含 permission）==="
ls note/09.other/
```

Expected:
- access-control 下含 10 个 .md + 12 张 .png = 21 个文件
- 05-security 下含：access-control, api-security, encryption, jwt-security, oauth2-oidc, owasp-top10, secrets-management（不含 rbac-abac）
- 09.other 下含其他主题（不含 permission）

- [ ] **Step 6.5：Commit Task 6**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
git add -A
git status
git commit -m "docs(perm): 清理已迁移的旧目录" \
  -m "删除 04.system-design/05-security/rbac-abac/ 与 09.other/permission/。12 张图已迁至 access-control/02-role-and-attribute/，6 个模型正文已迁至 access-control/ 下对应子目录。" \
  -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: 2 个目录删除 staged（git 显示 D 开头），1 commit 创建。

---

## 验收检查（6 个 commit 全部 push 后跑一次）

```bash
cd "C:/developer/IdeaProjects/wb04307201"

echo "=== 1. 6 个 commit 都存在 ==="
git log --oneline -6

echo "=== 2. 10 个新 Markdown 都在 ==="
find note/04.system-design/05-security/access-control -name '*.md' | wc -l

echo "=== 3. 每个模型都有 6 段 ==="
for f in $(find note/04.system-design/05-security/access-control -name '*.md' -not -name 'README.md'); do
  c=$(grep -c '^## [1-6]\.' "$f")
  [ "$c" = "6" ] && echo "✓ $f ($c 段)" || echo "✗ $f ($c 段)"
done

echo "=== 4. 12 张图都在新位置 ==="
find note/04.system-design/05-security/access-control -name 'img*.png' | wc -l

echo "=== 5. 旧目录已清 ==="
[ ! -d note/04.system-design/05-security/rbac-abac ] && echo "✓ rbac-abac 已清" || echo "✗ rbac-abac 残留"
[ ! -d note/09.other/permission ] && echo "✓ 09.other/permission 已清" || echo "✗ 09.other/permission 残留"

echo "=== 6. 全仓无 rbac-abac 残留 ==="
grep -rn 'rbac-abac' note/ docs/ 2>/dev/null && echo "✗ 残留" || echo "✓ 干净"

echo "=== 7. 全仓无 09.other/permission 残留 ==="
grep -rn '09.other/permission' note/ docs/ 2>/dev/null && echo "✗ 残留" || echo "✓ 干净"
```

Expected: 全部 ✓。

---

## 风险与回滚

| 风险 | 触发条件 | 回滚命令 |
|------|----------|----------|
| 6 段式骨架不实用 | Task 1 完成后 30 分钟内人工审阅 | `git reset --hard HEAD~6`（回到 Task 1 之前） |
| 图迁移后老 README 还引用图 | `09.other/permission/README.md` 仍存在且引用图 | Step 6.2 删除 09.other/permission 时一并消除 |
| 3 处引用方漏改 | 验证 Step 5.6 失败 | 在 Step 5.1–5.5 中补改对应 README |
| 内容长度超限 | Step 3.7 验证失败 | 在对应模型的 6 段式最后一段前加 `> 详见 [完整版](...)` 外链（YAGNI 内联不推荐） |

每步 1 commit，回滚粒度最小。
