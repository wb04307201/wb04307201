# 权限模型体系重构设计 spec

> 日期：2026-06-14
> 范围：`note/04.system-design/05-security/access-control/` 新建 + 旧文档整合
> 目标：把分散在 `04.system-design/05-security/rbac-abac/` 与 `note/09.other/permission/` 的两份权限模型文档，重构为 6 个主流模型 + 1 份选型总章的自洽小体系

---

## 1. 背景与动机

### 1.1 现状

- `note/04.system-design/05-security/rbac-abac/README.md`（15.9KB）已写好，聚焦 **RBAC / ABAC / ReBAC** 三个模型，含 SQL + Spring AOP 代码示例，位置合理（系统设计/安全下）。
- `note/09.other/permission/README.md`（9.3KB + 11 张图）覆盖 **ACL / DAC / MAC / RBAC0–3 / ABAC / Casbin**，位置在「其他」分类下，**主题归属错位**且与上一份内容**部分重复**。
- `05-security` 7 个子主题中，「权限模型」这份 4 个内容模块里最薄（README 标 4 个文档，实际 1 个 rbac-abac）。

### 1.2 问题

1. **重复维护**：RBAC、ABAC 在两个目录里都有版本，演进易分叉
2. **谱系不全**：行业 8+ 种主流权限模型只覆盖了一半（缺 DAC/MAC/混合模型体系化论述）
3. **位置错位**：`09.other/permission` 主题属"系统设计/安全"，却在"其他"分类下
4. **选型无指引**：没有从「业务特征」到「选哪个模型」的决策路径

---

## 2. 设计目标

1. **谱系完整**：覆盖 6 个主流模型 — DAC、MAC、RBAC、ABAC、ReBAC、RBAC+ABAC 混合
2. **结构家族化**：3 大家族（传统 / 角色属性 / 关系与混合），按"决策依据"分族
3. **总章可决策**：1 份选型总章，含谱系图 + 决策树 + 横向对比表 + 演进路径
4. **6 段式统一**：每个模型子文档固定 6 段结构，便于横向对比与维护
5. **图不丢**：老 09.other/permission 的 11 张图全部映射到新位置，零废弃
6. **零重复**：05-security 下不再存在「rbac-abac」平行文档

---

## 3. 目录结构（落盘形态）

```
note/04.system-design/05-security/access-control/
├── README.md                                     ← 选型总章：谱系图 / 6 模型一句话定位 / 决策树 / 横向对比表
├── 01-traditional/
│   ├── README.md                                 ← 族索引：传统三模型的共同问题域（身份即权限）
│   ├── dac.md                                    ← 自主访问控制（含 ACL 变体）
│   └── mac.md                                    ← 强制访问控制（含 BLP / Biba 简要补充）
├── 02-role-and-attribute/
│   ├── README.md                                 ← 族索引：把"权限"从用户身上抽象到「角色 / 属性」中介
│   ├── rbac.md                                   ← RBAC0/1/2/3 合并一个文档，含 SQL + Spring AOP 示例
│   └── abac.md                                   ← ABAC + PBAC / CBAC 别名说明 + 策略表达式
└── 03-relationship-and-hybrid/
    ├── README.md                                 ← 族索引：关系图与实战组合
    ├── rebac.md                                  ← Google Zanzibar + 适用场景
    └── hybrid.md                                 ← RBAC+ABAC 混合（实战主流）
```

**文件总数**：新增 10 个 Markdown（1 总章 + 3 族索引 + 6 模型正文）。

---

## 4. 6 段式内容模板

每个模型子文档统一遵循：

```
# <模型中文名>（<英文全称 / 缩写>）

> 一句话定位：本模型用「什么」作为授权决策的核心依据。

## 1. 概念与起源
- 历史背景（一句话即可：哪一年、谁提出、解决什么问题）
- 核心思想（一段话，不超过 100 字）

## 2. 核心模型图
- 主体 / 客体 / 动作 / 决策 的关系图（ASCII / 图片 / Mermaid 任选其一）
- 与同族其他模型的差异点（用一段话点出"和 X 的关键区别在于……"）

## 3. 表/数据结构
- 关键实体清单（用户/角色/权限/资源/策略/关系）
- 至少给出 DDL 或等价的实体关系说明
- 重点表加 1–2 行字段注释

## 4. 代码/伪代码示例
- 关键决策点 1 段代码（Spring / Java 优先；冷门模型用伪代码）
- 关键调用片段 ≤ 30 行，不堆模板

## 5. 优缺点
- 优点 3–5 条
- 缺点 3–5 条（必须包含"什么时候会痛"的具体场景）

## 6. 适用与不适用场景
- 适用：3 条典型场景 + 一句话理由
- 不适用：3 条典型场景 + 一句话理由

## 相关章节
- 族内其他模型（链接）
- 05-security 关联主题（JWT / OAuth2 / API 安全 / OWASP）
```

### 4.1 统一约束

- 6 段标题用 1/2/3/4/5/6 编号；末段固定叫「相关章节」
- 每段独立可被引用（标题可作为锚点）
- 全文长度目标：dac/mac/rebac ≤ 400 行；rbac/abac ≤ 600 行（rbac0–3 + abac 表达式内容多）；hybrid ≤ 350 行
- 禁用绝对路径链接；统一相对路径 `../02-role-and-attribute/rbac.md` 风格

---

## 5. 总章 `access-control/README.md` 结构

```
# 访问控制：6 大权限模型与选型指南

> 一句话定位：访问控制是把「谁能对什么做什么」这一决策工程化的学科。

## 1. 谱系与心智模型
- 一张图：6 个模型按"决策依据"分布的家族图（族 = 思维范式）
- 一张表：6 个模型 × { 决策依据 / 粒度 / 实现复杂度 / 典型场景 } 横向对比

## 2. 三大族索引
- 传统族：身份即权限 → [01-traditional](01-traditional/README.md)
- 角色属性族：把权限从人身上抽到中介 → [02-role-and-attribute](02-role-and-attribute/README.md)
- 关系与混合族：关系图与实战组合 → [03-relationship-and-hybrid](03-relationship-and-hybrid/README.md)

## 3. 选型决策树
  问 1: 业务有清晰组织架构吗？
    └─ 是 → 问 2
    └─ 否 → 问 4
  问 2: 权限规则可以全部用"角色"表达吗？
    └─ 是 → RBAC
    └─ 否 → 问 3
  问 3: 规则依赖"谁/什么/何时/何地"中除"谁"以外的因素吗？
    └─ 是 → ABAC
    └─ 否 → RBAC + 数据范围补充
  问 4: 权限依赖"实体间关系"（文档共享、好友、协作者）吗？
    └─ 是 → ReBAC
    └─ 否 → 问 5
  问 5: 是在做内部系统还是对外产品？
    └─ 内部系统 → RBAC（80% 情况）
    └─ 对外产品 + 合规 → RBAC+ABAC 混合

## 4. 横向对比表
- 复用 §1 的对比表 + 扩充 2 列：「主流实现 / 代表产品」
  - RBAC: Spring Security / Casbin
  - ABAC: Open Policy Agent (OPA) / AWS IAM
  - ReBAC: Google Zanzibar (SpiceDB) / Auth0 FGA
  - DAC/MAC: 操作系统 / SELinux

## 5. 演进路径与混合策略
- 演进图：DAC → RBAC → ABAC → ReBAC（什么场景下升级）
- 实战黄金组合：RBAC 做功能权限 + ABAC 做数据权限（详见 hybrid.md）

## 相关章节
- 05-security 主题：JWT / OAuth2 / API 安全 / OWASP / 加密 / 密钥管理
```

**总章与 6 段式的关键差异**：6 段式针对**单个模型**写「是什么 / 怎么用 / 利弊」；总章针对**模型之间**写「谱系 / 选谁 / 怎么演进」，不重复 6 段式的细节。

---

## 6. 与 05-security 现有结构的关系

```
05-security/
├── README.md                ← 改：增加「访问控制」一族索引，保留 6 主题分块
├── jwt-security/            ← 不动（鉴权凭证）
├── oauth2-oidc/             ← 不动（鉴权协议）
├── api-security/            ← 不动（接口层防护）
├── owasp-top10/             ← 不动（应用安全）
├── encryption/              ← 不动（密码学）
├── secrets-management/      ← 不动（密钥管理）
├── rbac-abac/               ← 删除（被 access-control/02-role-and-attribute/rbac.md 替代）
└── access-control/          ← 新增（本次重构主体）
    ├── README.md
    ├── 01-traditional/
    ├── 02-role-and-attribute/
    └── 03-relationship-and-hybrid/
```

**对外引用面改动清单**：

| 文件 | 改动 |
|------|------|
| `05-security/README.md` | 「权限与防护」段：3 号"权限模型"替换为 4 个链接（总章 + 3 族） |
| `04.system-design/README.md` | 「安全」模块导航行：1 行扩成 1 行 + 4 个子链接（总章 + 3 族） |
| `note/README.md` | 第四节表格第 5 行"安全"展开为"安全 / 访问控制"；第九节删除 `09.other/permission` 整条引用 |

---

## 7. 老文档资源归宿（11 张图，零废弃）

| 老图 | 去向 | 段落 |
|------|------|------|
| img.png（RBAC 概览） | `02-role-and-attribute/rbac.md` | §1 概念 |
| img_1.png（ABAC 关系图） | `02-role-and-attribute/abac.md` | §2 核心模型图 |
| img_2.png（理想 RBAC 模型） | `02-role-and-attribute/rbac.md` | §2 核心模型图（RBAC3） |
| img_3.png（理想 RBAC 表设计） | `02-role-and-attribute/rbac.md` | §3 表设计（完整版） |
| img_4.png（标准 RBAC 表设计） | `02-role-and-attribute/rbac.md` | §3 表设计（最小版） |
| img_5.png（标准 RBAC 模型） | `02-role-and-attribute/rbac.md` | §2 核心模型图（RBAC0） |
| img_6.png（RBAC1 角色继承） | `02-role-and-attribute/rbac.md` | §2 核心模型图（RBAC1） |
| img_7.png（RBAC2 角色互斥） | `02-role-and-attribute/rbac.md` | §2 核心模型图（RBAC2） |
| img_8.png（RBAC3 职位映射） | `02-role-and-attribute/rbac.md` | §2 核心模型图（RBAC3 职位） |
| img_9.png（权限可分组） | `02-role-and-attribute/rbac.md` | §2 核心模型图（RBAC3 用户组-权限） |
| img_10.png（用户组） | `02-role-and-attribute/rbac.md` | §2 核心模型图（RBAC3 用户组） |
| img_11.png（组织与数据权限） | `02-role-and-attribute/rbac.md` | §2 核心模型图（RBAC3 组织） |

**物理迁移**：`mv note/09.other/permission/img*.png note/04.system-design/05-security/access-control/02-role-and-attribute/`

---

## 8. 实施顺序（6 步，每步 1 commit）

| 步骤 | 操作 | 涉及文件 | 提交粒度 |
|------|------|----------|----------|
| 1 | 新建 access-control 目录骨架 + 10 个新文件的占位骨架（仅标题与 6 段标题） | 10 个新 .md | 1 commit：`docs(perm): 新建 access-control 目录骨架` |
| 2 | 把 11 张图从 `09.other/permission/` 迁到 `02-role-and-attribute/` | 11 张 png | 1 commit：`docs(perm): 迁移 RBAC/ABAC 配图到 02-role-and-attribute` |
| 3 | 按 6 段式填充 6 个模型正文（rbac.md 整合 05-security/rbac-abac 全部内容 + 9 张图 + 0–3 变体；abac.md 整合 rbac-abac 的 ABAC + 1 张图） | 6 个新文件 | 1 commit：`docs(perm): 填充 6 个模型正文` |
| 4 | 填充总章 README + 3 个族索引 README | 4 个新文件 | 1 commit：`docs(perm): 填充总章与族索引` |
| 5 | 改 3 个引用方（05-security/README、04.system-design/README、note/README） | 3 个改动 | 1 commit：`docs(perm): 更新 3 处索引引用` |
| 6 | 删除 `04.system-design/05-security/rbac-abac/` 与 `note/09.other/permission/` | 2 个目录删除 | 1 commit：`docs(perm): 清理已迁移的旧目录` |

---

## 9. 验证标准

| 检查项 | 方法 | 通过条件 |
|--------|------|----------|
| 链接可达 | `grep -rEn '\]\(\.\./' access-control/` + `grep -rEn '\]\(\.\.' 05-security/ access-control/ 04.system-design/ note/` | 无 `../xxx` 形式的死链；所有相对路径目标文件存在 |
| 6 段完整性 | 对 6 个模型 .md 跑：`grep -c '^## [1-6]\.'` | 每个文件都返回 6（6 段全在） |
| 图未丢失 | `find access-control -name 'img*.png' \| wc -l` 与 `find 09.other/permission -name 'img*.png' \| wc -l` | 新位置 11 张；老位置 0 张 |
| 引用方更新 | `grep -n 'rbac-abac\|09.other/permission' 05-security/README.md 04.system-design/README.md note/README.md` | 三处全无匹配（除 05-security/README 中"访问控制"族的新链接） |
| 旧目录已清 | `ls 04.system-design/05-security/rbac-abac note/09.other/permission` | 两个目录都 `No such file or directory` |
| 顶层 README 引用 | `note/README.md` 第九节 + 第四节 | 权限控制那一行从有变无；表格中安全行变成"安全 / 访问控制"展开形式 |
| 文档可读 | 人工扫一遍总章 → 族索引 → 模型正文 | 横向跳转、纵向跳转（图、代码、决策树）都通顺 |

---

## 10. 风险与对策

| 风险 | 触发条件 | 对策 |
|------|----------|------|
| 老 09.other/permission 的图可能引自第三方有版权顾虑 | 重新审视图源说明 | 老 README 没标版权来源，统一当作"自有图"使用；如需严谨在总章加一句"图源：作者绘制" |
| 05-security/rbac-abac 里的 Spring AOP 代码与 09.other 的图在叙述节奏上打架 | 填充 rbac.md 时发现重复或矛盾 | 以 6 段式为骨架，图与代码按段落对位插入；冲突内容**以 6 段式为准**改写，不留两套说法 |
| 13.split-hairs 下的 `04.system-design` 节点可能有引用 | grep 后发现 | 同步在那个 split-hairs 子页加一行"主文档已迁至 04.system-design/05-security/access-control/"的脚注 |
| 外部 GitHub / Gitee 链接指向 09.other/permission | grep 整个仓库 | 没有（grep 全仓） |

---

## 11. 不做的事（明确划界）

- **不**改 OAuth2、JWT、API 安全、OWASP、加密、密钥管理 6 个 05-security 邻居主题
- **不**在 13.split-hairs 下新增权限面试题（避免 scope 蔓延）
- **不**为 6 个模型各做一个 demo 工程（Gitee 仓库）；文档里用代码片段 + SQL 就够
- **不**翻译成英文版本（保持单语）
- **不**做权限模型历史考据（什么"1969 年 Biba 论文第几页"那种，违反 6 段式"一句话起源"约束）

---

## 12. 验收口径

6 个 commit 全部 push 后，本次重构视为完成。**完成定义**：

- [ ] 10 个新 Markdown 文件存在且每篇 ≥ 100 行（总章 4 段 + 决策树；族索引 50 行；模型正文 6 段）
- [ ] 11 张 png 全部迁到 `02-role-and-attribute/`，老位置无残留
- [ ] 6 个模型子文档均通过 6 段完整性检查
- [ ] 3 处引用方（05-security、04.system-design、note）已更新
- [ ] 2 个旧目录（rbac-abac、09.other/permission）已 `rm -rf`
- [ ] 9 个验证标准全部通过
