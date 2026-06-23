# 业务应用系统 note/08.application-systems 重组 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `note/09.other/common-systems/` 提升为 `note/08.application-systems/` 一级目录，按业务价值链重写 README，覆盖 21 个常见业务系统（5 详 16 略），删除 `note/09.other/`。

**Architecture:** 6 章价值链（研发/生产/供应链/销售服务/运营/专项支持）+ 4 个辅助章节（快速入口/全景图/集成模式/速查表/学习路线），全部用 mermaid，不引用任何 png。分 12 个 commit 推进，每章独立成提交，便于 review 和回滚。

**Tech Stack:** git (Windows 11 / bash shell)、Markdown、Mermaid（语法通过 GitHub 渲染验证）

**Spec:** `docs/superpowers/specs/2026-06-24-application-systems-design.md`

---

## 文件结构总览（完成后）

```
note/
├── 08.application-systems/             ← 新建（搬迁目标）
│   └── README.md                       ← 唯一文件（合并原 erp/、pdm/、common-systems/README.md）
└── 09.other/                           ← 完成后删除（无内容）
```

---

## Task 1: 创建目录与 README 骨架

**Files:**
- Create: `note/08.application-systems/README.md`（仅含标题、引言、目录占位）

- [ ] **Step 1.1: 创建新目录**

Run:
```bash
cd "C:/developer/IdeaProjects/wb04307201"
mkdir -p note/08.application-systems
```
Expected: 命令静默成功

- [ ] **Step 1.2: 写入 README 骨架**

Create file `note/08.application-systems/README.md` with:

```markdown
# 业务应用系统

> 一份按业务价值链梳理的业务系统速查手册，帮助业务/产品/需求人员快速建立完整的业务系统认知地图，并具备日常速查能力。
>
> 覆盖 21 个常见业务系统：MES · ERP · SCM · WMS · APS · SCADA · PLM · PDM · QMS · CRM · EAM · SRM · OMS · SCRM · OA · MOM · TMS · LIMS · CMS · BI · PMS

## 📑 目录

<!-- TODO: 由后续任务填充 -->

1. [🚀 快速入口](#-快速入口)
2. [🗺️ 业务价值链全景图](#-业务价值链全景图)
3. [01 研发创新（PLM · PDM · CMS）](#01-研发创新)
4. [02 生产制造（MES · MOM · APS · SCADA）](#02-生产制造)
5. [03 供应链（SCM · SRM · WMS · TMS）](#03-供应链)
6. [04 销售服务（CRM · SCRM · OMS）](#04-销售服务)
7. [05 运营管理（ERP · BI · EAM · OA · QMS）](#05-运营管理)
8. [06 专项支持（LIMS · PMS）](#06-专项支持)
9. [🔌 系统集成模式](#-系统集成模式)
10. [📋 系统速查表](#-系统速查表)
11. [🛤️ 学习路线](#-学习路线)

---

<!-- TODO: 由后续任务填充各章节 -->
```

- [ ] **Step 1.3: 校验文件存在**

Run:
```bash
ls -la note/08.application-systems/
wc -l note/08.application-systems/README.md
```
Expected: 看到 `README.md` 一行文件；行数约 25 行

- [ ] **Step 1.4: Commit**

Run:
```bash
git add note/08.application-systems/README.md
git commit -m "feat(note): scaffold 08.application-systems README skeleton

详见 docs/superpowers/specs/2026-06-24-application-systems-design.md

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 出现 `1 file changed, 25 insertions(+)` 之类

---

## Task 2: 写入快速入口 + 全景图

**Files:**
- Modify: `note/08.application-systems/README.md`（在 TODO 占位上方插入两个章节）

- [ ] **Step 2.1: 在 TODO 上方插入快速入口与全景图**

用 Edit 工具，把文件中的：

```markdown
---

<!-- TODO: 由后续任务填充各章节 -->
```

替换为：

```markdown
---

## 🚀 快速入口

| 你是谁 | 看什么 |
|---|---|
| 完全没接触过业务系统 | 业务价值链全景图 + [学习路线 - 入门段](#-学习路线)（5 分钟） |
| 已经听说过某系统 | [📋 系统速查表](#-系统速查表) 查到该系统所在价值链章节 |
| 想理解系统间怎么集成 | [🔌 系统集成模式](#-系统集成模式) |
| 想按业务问题查 | 按目录跳到对应价值链章节 |

---

## 🗺️ 业务价值链全景图

```mermaid
flowchart LR
    A[01 研发创新<br/>PLM · PDM · CMS] --> B[02 生产制造<br/>MES · MOM · APS · SCADA]
    B --> C[03 供应链<br/>SCM · SRM · WMS · TMS]
    C --> D[04 销售服务<br/>CRM · SCRM · OMS]
    D --> E[05 运营管理<br/>ERP · BI · EAM · OA · QMS]
    E --> F[06 专项支持<br/>LIMS · PMS]
```

业务价值链从"研发创新"出发，经"生产制造 → 供应链 → 销售服务"，收敛到"运营管理"，最后挂载"专项支持"作为跨场景补充。

---

<!-- TODO: 由后续任务填充各章节 -->
```

- [ ] **Step 2.2: 校验章节插入**

Run:
```bash
grep -n "## 🚀 快速入口\|## 🗺️ 业务价值链全景图\|flowchart LR" note/08.application-systems/README.md
```
Expected: 三行匹配，分别对应三个新章节标题和 mermaid 起始

- [ ] **Step 2.3: 校验 mermaid 语法节点数**

Run:
```bash
grep -cE '^\s*[A-F]\[' note/08.application-systems/README.md
```
Expected: 输出 `6`（A 到 F 共 6 个价值链节点）

- [ ] **Step 2.4: Commit**

Run:
```bash
git add note/08.application-systems/README.md
git commit -m "feat(note): add quick entry + value chain panorama to 08.application-systems

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 出现 `1 file changed, 30 insertions(+), 1 deletion(-)` 之类

---

## Task 3: 写入 01 研发创新 章节（PLM · PDM · CMS）

**Files:**
- Modify: `note/08.application-systems/README.md`

- [ ] **Step 3.1: 在 TODO 上方插入 01 研发创新章节**

Edit 工具，把：

```markdown
---

<!-- TODO: 由后续任务填充各章节 -->
```

替换为：

```markdown
---

## 01 研发创新

> 本章关注"从产品创意到上市"阶段所需的能力与系统。研发是价值链的源头，决定了后续生产、供应链、销售的全部基础数据（BOM、图纸、工艺）。

### 📌 全景图

```mermaid
flowchart LR
    A((客户/市场需求)) --> B[CMS<br/>内容触达]
    A --> C[PLM<br/>生命周期]
    C --> D[PDM<br/>数据]
    C --> E((下游生产))
    D -.共享数据.-> C
```

### 🔑 核心系统详讲

#### PLM（Product Lifecycle Management 产品生命周期管理）

- **定义**：管理产品从概念、设计、工艺、生产、销售到退役的全生命周期数据与流程的系统，是企业研发数字化的主干。
- **核心能力**：
  - 产品数据中央仓库（BOM、CAD 图纸、技术文档）
  - 工作流与审批（工程变更、签审流程）
  - 项目管理（项目计划、里程碑、资源）
  - 与 CAD/CAE/CAPP 工具集成
- **典型场景**：
  - 汽车/装备制造的新车型研发项目
  - 电子产品的多代产品演进管理
  - 工程变更（ECN）的全流程追溯
- **上下游关系**：
  - 上游：接 CRM（市场需求）、CMS（产品资料）
  - 下游：向 ERP 输出 BOM、向 MES 输出工艺路线
- **关键考量**：
  - 选型时关注与现有 CAD（SolidWorks/CATIA/UG）的兼容性
  - 数据治理（版本、权限、归档）是实施难点

#### PDM（Product Data Management 产品数据管理）

- **定义**：PLM 的核心子集，专注于产品数据本身（文档、图纸、零部件）的管理与组织，是 PLM 早期阶段的形态。
- **核心能力**：
  - 文档与图纸版本管理
  - 零部件库与结构管理（EBOM → MBOM）
  - 检索与权限
- **典型场景**：纯研发数据管理需求、企业 PDM 起步阶段
- **与 PLM 的关系**：PDM ⊂ PLM，PDM 管"数据"，PLM 管"数据 + 流程 + 资源"
- **历史脉络**（来自原 pdm/README.md 整合）：
  - 60-70 年代：CAD/CAM 单点工具 → 信息孤岛
  - 80 年代：与 CAD 集成的纯数据管理 PDM
  - 90 年代：加入工作流/变更/项目的过程集成 PDM
  - 90 年代末：跨企业协同 → 演化为 PLM
- **关键考量**：现代场景下单独上 PDM 较少，多作为 PLM 子模块实施

### 📋 其他系统速览

#### CMS（Content Management System 内容管理系统）

管理网站、博客、营销内容等的创建、编辑、发布。**适用场景**：产品官网、帮助文档、营销活动页。

### 💡 本章小结

研发创新环节的核心是 PLM/PDM（管产品数据），CMS（管内容触达）是辅助。本章输出"产品主数据"流向下一章"生产制造"。

---

<!-- TODO: 由后续任务填充各章节 -->
```

- [ ] **Step 3.2: 校验章节内容**

Run:
```bash
grep -nE "^## 01 研发创新|^### .*PLM|^### .*PDM|^### .*CMS|^#### 上下游关系|^#### 历史脉络" note/08.application-systems/README.md
```
Expected: 至少 6 行匹配，覆盖章节 + 3 个系统 + 上下游关系 + 历史脉络

- [ ] **Step 3.3: 校验 BOM 关键词**

Run:
```bash
grep -c "BOM\|PLM\|PDM" note/08.application-systems/README.md
```
Expected: ≥ 10（多次出现 PLM/PDM/BOM 关键词）

- [ ] **Step 3.4: Commit**

Run:
```bash
git add note/08.application-systems/README.md
git commit -m "feat(note): 08.application-systems - add chapter 01 R&D (PLM, PDM, CMS)

PLM/PDM 详讲，CMS 速览。PDM 历史脉络整合自原 pdm/README.md。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 1 file changed，约 +85 insertions

---

## Task 4: 写入 02 生产制造 章节（MES · MOM · APS · SCADA）

**Files:**
- Modify: `note/08.application-systems/README.md`

- [ ] **Step 4.1: 在 TODO 上方插入 02 生产制造章节**

Edit 工具，把：

```markdown
---

<!-- TODO: 由后续任务填充各章节 -->
```

替换为：

```markdown
---

## 02 生产制造

> 本章关注"把研发设计的产品制造出来"阶段所需的能力与系统。生产环节是制造型企业价值链的核心，决定交付能力、成本与质量。

### 📌 全景图

```mermaid
flowchart LR
    A((上游<br/>PLM/ERP)) --> B[MES<br/>执行]
    B --> C[MOM<br/>运营管理]
    C --> D((下游<br/>WMS/BI))
    B -.采集.-> E[SCADA<br/>设备数据]
    F[APS<br/>排程] --> B
    F --> C
```

### 🔑 核心系统详讲

#### MES（Manufacturing Execution System 制造执行系统）

- **定义**：聚焦车间层的实时生产管理系统，把 ERP 的生产计划落地为工单并跟踪执行。
- **核心能力**：
  - 工单下达与调度
  - 生产进度实时跟踪（与 SCADA 集成）
  - 质量数据采集与追溯
  - 在制品（WIP）与设备状态
  - 物料齐套检查
- **典型场景**：
  - 离散制造（机械、电子）的车间管理
  - 流程制造（化工、食品）的批次管理
  - 多工厂、多车间的集中可视
- **上下游关系**：
  - 上游：接 ERP（工单/物料）、APS（排程）
  - 下游：向 WMS 报完工入库、向 BI 输出 OEE 数据
  - 横向：与 SCADA 集成采集设备数据
- **关键考量**：
  - 行业属性极强（离散 vs 流程 vs 混合），选型必须看行业模板
  - 与 ERP/PLM 的集成质量是实施成败关键

### 📋 其他系统速览

#### MOM（Manufacturing Operation Management 制造运营管理）

MOM 是 MES 的上位概念，覆盖制造运营全过程（生产、质量、维护、库存），MES 实际是 MOM 的执行子集。**适用场景**：集团级制造运营管控、MES + 周边系统一体化平台。

#### APS（Advanced Planning and Scheduling 高级计划与排程）

在 MRP 基础上做精细化排程（资源约束、工序顺序、换线时间），输出可执行的工时级计划。**适用场景**：多品种小批量、产能受限、订单优先级频繁调整。

#### SCADA（Supervisory Control And Data Acquisition 监督控制与数据采集）

监控和控制工业设备（PLC/DCS）并采集实时数据，是 MES 采集现场数据的"耳目"。**适用场景**：工业自动化产线、远程设备监控。

### 💡 本章小结

生产制造的核心是 MES（执行），MOM 是上位管理框架，APS 解决排程，SCADA 解决数据采集。本章输出"完工入库"事件给下游供应链。

---

<!-- TODO: 由后续任务填充各章节 -->
```

- [ ] **Step 4.2: 校验章节内容**

Run:
```bash
grep -nE "^## 02 生产制造|^#### MES|^#### MOM|^#### APS|^#### SCADA|^### .*核心系统详讲" note/08.application-systems/README.md
```
Expected: 至少 6 行匹配

- [ ] **Step 4.3: 校验关键术语**

Run:
```bash
grep -c "MES\|MOM\|APS\|SCADA\|工单\|排程\|SCADA" note/08.application-systems/README.md
```
Expected: ≥ 15

- [ ] **Step 4.4: Commit**

Run:
```bash
git add note/08.application-systems/README.md
git commit -m "feat(note): 08.application-systems - add chapter 02 manufacturing (MES, MOM, APS, SCADA)

MES 详讲，其余速览。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 1 file changed，约 +60 insertions

---

## Task 5: 写入 03 供应链 章节（SCM · SRM · WMS · TMS）

**Files:**
- Modify: `note/08.application-systems/README.md`

- [ ] **Step 5.1: 在 TODO 上方插入 03 供应链章节**

Edit 工具，把：

```markdown
---

<!-- TODO: 由后续任务填充各章节 -->
```

替换为：

```markdown
---

## 03 供应链

> 本章关注"把产品送到客户手中"的全链路（计划→采购→仓储→运输）。供应链能力决定订单履约时效与成本。

### 📌 全景图

```mermaid
flowchart LR
    A((上游<br/>MES/ERP)) --> B[SCM<br/>供应链计划]
    B --> C[SRM<br/>供应商]
    C --> D((供应商))
    B --> E[WMS<br/>仓储]
    B --> F[TMS<br/>运输]
    E --> F
    F --> G((客户))
```

### 🔑 核心系统详讲

#### WMS（Warehouse Management System 仓储管理系统）

- **定义**：管理仓库作业（入库、上架、拣货、出库、盘点）的系统，是仓储数字化的核心。
- **核心能力**：
  - 库存实时准确（库位/批次/效期）
  - 作业策略（先进先出、批次管理、波次拣货）
  - 设备集成（条码枪/RFID/AGV/立体仓）
  - 盘点与差异处理
- **典型场景**：
  - 电商履约中心（日发百万单）
  - 制造业线边仓与中央仓
  - 三方物流（3PL）的多货主管理
- **上下游关系**：
  - 上游：接 ERP（入库指令）、MES（完工入库）
  - 下游：向 TMS 输出待运货物、向 BI 输出库存周转
- **关键考量**：
  - 与自动化设备（AGV/立体库）的深度集成是核心壁垒
  - 多货主/多仓/跨境场景复杂度差异大

### 📋 其他系统速览

#### SCM（Supply Chain Management 供应链管理）

覆盖从供应商到客户的端到端供应链计划（需求/供应/分销计划），与 ERP 共享物料和库存信息。**适用场景**：多级供应链协同、需求预测优化。

#### SRM（Supplier Relationship Management 供应商关系管理）

管理供应商全生命周期（寻源/资质/绩效/协同），与 ERP 互补，专注"供应商侧"深度管理。**适用场景**：供应商数量多、采购品类复杂的企业。

#### TMS（Transportation Management System 运输管理系统）

管理运输全过程（运力调度/路径规划/在途跟踪/签收回单），与 WMS 衔接发货环节。**适用场景**：自有车队、3PL 管理、多式联运。

### 💡 本章小结

供应链的核心是 WMS（仓储执行），SCM 管计划、SRM 管供应商、TMS 管运输，四者协同完成"原料入厂→成品送达客户"的全链路。

---

<!-- TODO: 由后续任务填充各章节 -->
```

- [ ] **Step 5.2: 校验章节内容**

Run:
```bash
grep -nE "^## 03 供应链|^#### WMS|^#### SCM|^#### SRM|^#### TMS" note/08.application-systems/README.md
```
Expected: 至少 5 行匹配

- [ ] **Step 5.3: Commit**

Run:
```bash
git add note/08.application-systems/README.md
git commit -m "feat(note): 08.application-systems - add chapter 03 supply chain (SCM, SRM, WMS, TMS)

WMS 详讲，其余速览。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 1 file changed，约 +55 insertions

---

## Task 6: 写入 04 销售服务 章节（CRM · SCRM · OMS）

**Files:**
- Modify: `note/08.application-systems/README.md`

- [ ] **Step 6.1: 在 TODO 上方插入 04 销售服务章节**

Edit 工具，把：

```markdown
---

<!-- TODO: 由后续任务填充各章节 -->
```

替换为：

```markdown
---

## 04 销售服务

> 本章关注"接触客户、达成交易、订单履约"阶段的系统。CRM 是客户主数据源，OMS 是订单履约协调器，SCRM 是社交化延伸。

### 📌 全景图

```mermaid
flowchart LR
    A((客户)) --> B[CRM<br/>关系]
    A --> C[SCRM<br/>社交]
    B --> D[OMS<br/>订单]
    D --> E((下游<br/>ERP/WMS))
    C -.线索.-> B
```

### 🔑 核心系统详讲

#### CRM（Customer Relationship Management 客户关系管理）

- **定义**：管理客户全生命周期（线索→商机→订单→服务→复购）的系统，是企业对外经营的主入口。
- **核心能力**：
  - 客户主数据（客户/联系人/账户视图）
  - 销售流程（线索、商机、报价、合同）
  - 营销自动化（活动、群发、归因）
  - 客户服务（工单、知识库）
- **典型场景**：
  - B2B 大客户销售（项目型销售过程管理）
  - B2C 零售（会员体系、营销自动化）
  - 售后服务（呼叫中心、现场服务）
- **上下游关系**：
  - 上游：接市场活动（广告投放、官网注册）
  - 下游：向 OMS 推送订单、向 ERP 同步客户主数据
- **关键考量**：
  - SaaS 化趋势明显（Salesforce/HubSpot/纷享销客）
  - 与营销工具（MA）、呼叫中心的对接是常见集成点

### 📋 其他系统速览

#### SCRM（Social Customer Relationship Management 社交化客户关系管理）

CRM 的社交化延伸，集成微信/小红书/抖音等社交触点，把"粉丝"转化为可运营客户。**适用场景**：消费品零售、网红营销、私域运营。

#### OMS（Order Management System 订单管理系统）

订单全生命周期管理（创建/拆分/合并/路由/状态），是连接 CRM 与 ERP/WMS/TMS 的中枢。**适用场景**：多渠道订单（电商+门店+经销商）统一管理。

### 💡 本章小结

销售服务的核心是 CRM（客户主数据），OMS 协调订单履约，SCRM 是社交化补充。本章输出"客户+订单"信息给运营管理章节的 ERP。

---

<!-- TODO: 由后续任务填充各章节 -->
```

- [ ] **Step 6.2: 校验章节内容**

Run:
```bash
grep -nE "^## 04 销售服务|^#### CRM|^#### SCRM|^#### OMS" note/08.application-systems/README.md
```
Expected: 至少 4 行匹配

- [ ] **Step 6.3: Commit**

Run:
```bash
git add note/08.application-systems/README.md
git commit -m "feat(note): 08.application-systems - add chapter 04 sales & service (CRM, SCRM, OMS)

CRM 详讲，其余速览。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 1 file changed，约 +50 insertions

---

## Task 7: 写入 05 运营管理 章节（ERP · BI · EAM · OA · QMS）

**Files:**
- Modify: `note/08.application-systems/README.md`

- [ ] **Step 7.1: 在 TODO 上方插入 05 运营管理章节**

Edit 工具，把：

```markdown
---

<!-- TODO: 由后续任务填充各章节 -->
```

替换为：

```markdown
---

## 05 运营管理

> 本章关注"企业经营管理的核心系统"。ERP 是企业数字化的"中枢"，BI 提供决策支持，EAM/OA/QMS 是周边支撑。

### 📌 全景图

```mermaid
flowchart LR
    A((上游各系统)) --> B[ERP<br/>中枢]
    B --> C[BI<br/>决策]
    B --> D[EAM<br/>资产]
    B --> E[OA<br/>办公]
    B --> F[QMS<br/>质量]
    C -.指标.-> A
```

### 🔑 核心系统详讲

#### ERP（Enterprise Resource Planning 企业资源计划）

- **定义**：集成企业所有核心业务（财务、采购、库存、销售、生产）于一体的管理软件，是企业数字化的中枢。
- **核心功能模块**：
  - **财务模块**：总账、应收应付、固定资产、成本核算
  - **采购模块**：采购申请、订单、收货、发票、付款
  - **销售模块**：销售订单、发货、开票、收入确认
  - **库存模块**：入库、出库、调拨、盘点
  - **生产模块**：MRP 运算、工单、产能
  - **人力资源**：组织、薪酬、考勤（部分 ERP 含）
- **典型场景**：
  - 制造业（SAP S/4HANA、Oracle EBS、用友 U9、金蝶 EAS）
  - 商贸业（进销存 + 财务一体）
  - 服务业（项目型 ERP + 财务）
- **上下游关系**（ERP 是中枢，几乎所有系统都和 ERP 集成）：
  - 上游：接 CRM（订单）、SRM（采购订单）、MES（生产工单）
  - 下游：向 BI 输出财务/业务数据、向 BI 同步主数据
  - 横向：与 WMS/TMS/PLM/QMS 等深度集成
- **关键考量**：
  - **行业属性强**：制造业 ERP 不能简单套用到服务业
  - **实施周期长**：6-18 个月，必须有强项目管理
  - **数据迁移**：历史数据清洗是头号风险
  - **二次开发**：要警惕厂商绑定

### 📋 其他系统速览

#### BI（Business Intelligence 商业智能）

提供数据分析、报表、可视化能力，支持管理决策。**适用场景**：管理驾驶舱、自助分析、数据驱动决策。

#### EAM（Enterprise Asset Management 企业资产管理）

管理物理资产（设备、设施）的全生命周期，侧重维护（预防性维护、检修工单）。**适用场景**：资产密集行业（电力、轨交、物业）。

#### OA（Office Automation 办公自动化）

管理行政办公流程（审批、文档、协同），国内代表有泛微、致远、钉钉/企业微信。**适用场景**：企业内部流程审批、文档协作。

#### QMS（Quality Management System 质量管理系统）

管理产品质量（来料/过程/成品检验、不良品处理、质量分析），是合规与品牌保障。**适用场景**：制造业（IATF 16949）、食品医药（GMP）。

### 💡 本章小结

运营管理的核心是 ERP（中枢），BI 给决策者看数据，EAM/OA/QMS 是企业运营不同侧面的支撑。本章把整条价值链的数据汇聚成可衡量、可管控的经营指标。

---

<!-- TODO: 由后续任务填充各章节 -->
```

- [ ] **Step 7.2: 校验章节内容**

Run:
```bash
grep -nE "^## 05 运营管理|^#### ERP|^#### BI|^#### EAM|^#### OA|^#### QMS" note/08.application-systems/README.md
```
Expected: 至少 6 行匹配

- [ ] **Step 7.3: 校验 ERP 模块清单**

Run:
```bash
grep -c "财务模块\|采购模块\|销售模块\|库存模块\|生产模块" note/08.application-systems/README.md
```
Expected: ≥ 5

- [ ] **Step 7.4: Commit**

Run:
```bash
git add note/08.application-systems/README.md
git commit -m "feat(note): 08.application-systems - add chapter 05 operations (ERP, BI, EAM, OA, QMS)

ERP 详讲（合并原 erp/README.md 内容 + 六大模块清单），其余速览。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 1 file changed，约 +70 insertions

---

## Task 8: 写入 06 专项支持 章节（LIMS · PMS）

**Files:**
- Modify: `note/08.application-systems/README.md`

- [ ] **Step 8.1: 在 TODO 上方插入 06 专项支持章节**

Edit 工具，把：

```markdown
---

<!-- TODO: 由后续任务填充各章节 -->
```

替换为：

```markdown
---

## 06 专项支持

> 本章关注"通用价值链之外的专项系统"。这些系统服务于特定行业或场景（实验室、项目管理），不适用于所有企业，但一旦需要就不可替代。

### 📌 全景图

```mermaid
flowchart LR
    A[研发创新] -.实验数据.-> B[LIMS<br/>实验室]
    C[运营管理] -.项目执行.-> D[PMS<br/>项目]
    B -.检测结果.-> A
    D -.项目交付.-> C
```

### 📋 专项系统速览

#### LIMS（Laboratory Information Management System 实验室信息管理系统）

- **定义**：管理实验室样品、检测数据、报告、仪器、资源的信息系统。
- **核心能力**：
  - 样品登记与流转（接收、分配、检测、归档）
  - 检测方法与结果录入
  - 仪器连接与数据自动采集
  - 报告生成与审核
  - 合规（GLP/GMP/ISO 17025）
- **典型场景**：
  - 制药/化工的研发实验室
  - 环境监测/食品检测的第三方实验室
  - 医院/疾控的临床检验
- **关键考量**：行业监管严格，合规要求决定选型

#### PMS（Project Management System 项目管理系统）

- **定义**：管理项目全生命周期（立项、计划、执行、监控、收尾）的协作系统。
- **核心能力**：
  - 任务分解（WBS）、甘特图、关键路径
  - 资源分配、预算、进度跟踪
  - 风险与问题管理
  - 协作（评论、@提及、文档共享）
- **典型场景**：
  - 工程类项目（土建、IT 集成、咨询）
  - 研发项目（与 PLM 部分重叠，但 PMS 偏管理、PLM 偏数据）
  - 营销/活动项目
- **关键考量**：与 OA/PLM 的边界需明确，避免重复录入

### 💡 本章小结

专项支持系统服务于特定场景。LIMS 偏实验室合规，PMS 偏项目协作。

---

<!-- TODO: 由后续任务填充各章节 -->
```

- [ ] **Step 8.2: 校验章节内容**

Run:
```bash
grep -nE "^## 06 专项支持|^#### LIMS|^#### PMS" note/08.application-systems/README.md
```
Expected: 至少 3 行匹配

- [ ] **Step 8.3: Commit**

Run:
```bash
git add note/08.application-systems/README.md
git commit -m "feat(note): 08.application-systems - add chapter 06 specialized (LIMS, PMS)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 1 file changed，约 +50 insertions

---

## Task 9: 写入系统集成模式章节

**Files:**
- Modify: `note/08.application-systems/README.md`

- [ ] **Step 9.1: 在 TODO 上方插入集成模式章节**

Edit 工具，把：

```markdown
---

<!-- TODO: 由后续任务填充各章节 -->
```

替换为：

```markdown
---

## 🔌 系统集成模式

> 业务系统从来不是孤立的——它们需要"对话"。本章讲解系统间如何集成，从最底层的"通信方式"到上层的"组织模式"再到具体的"主链场景"。

### 集成方式（"怎么连"）

| 方式 | 特点 | 典型场景 |
|---|---|---|
| **API/REST** | 同步、实时、契约清晰 | 现代云原生系统、跨企业开放接口 |
| **消息队列** | 异步、解耦、削峰 | 高并发场景（Kafka/RabbitMQ）、事件驱动 |
| **中间件/ESB** | 集中路由、协议转换 | 传统企业集成（IBM Integration Bus/MuleSoft/自研） |
| **文件交换/EDI** | 跨企业、跨行业、批处理 | 供应链上下游（EDI 标准）、银企直联 |
| **数据库直连** | 应急/过渡方案 | 不推荐生产环境；老系统接口缺失时的临时方案 |

### 集成模式（"怎么组织"）

```mermaid
flowchart LR
    subgraph 点对点
      A1[系统A] --- B1[系统B]
      A1 --- C1[系统C]
      B1 --- C1
    end
    subgraph ESB总线
      A2[系统A] --> E[ESB]
      B2[系统B] --> E
      C2[系统C] --> E
    end
    subgraph 事件驱动
      A3[系统A] --> K[Kafka]
      K --> B3[系统B]
      K --> C3[系统C]
    end
```

| 模式 | 优点 | 缺点 | 适用 |
|---|---|---|---|
| **点对点** | 简单直接 | 难维护、网状依赖 | 系统数量少（≤3） |
| **ESB 总线** | 集中管控、协议转换 | 单点故障、贵 | 传统大型企业 |
| **事件驱动** | 松耦合、可扩展 | 事件溯源难 | 现代微服务/云原生 |
| **主数据管理（MDM）** | 先治理数据再集成 | 实施重 | 数据标准不统一的大型企业 |

### 关键集成场景

#### 订单主链

```mermaid
flowchart LR
    A[CRM<br/>客户下单] --> B[OMS<br/>订单路由]
    B --> C[ERP<br/>订单确认]
    C --> D[WMS<br/>出库]
    D --> E[TMS<br/>运输]
    E --> F((客户))
    D -.回传.-> A
```

#### 供应链主链

```mermaid
flowchart LR
    A[SRM<br/>供应商] --> B[SCM<br/>计划]
    B --> C[ERP<br/>采购]
    C --> D[MES<br/>生产]
    D --> E[WMS<br/>入库]
    E --> F((发货))
```

#### 数据主链（产品数据从研发到决策）

```mermaid
flowchart LR
    A[PLM<br/>BOM] --> B[ERP<br/>MRP]
    B --> C[MES<br/>工单]
    C --> D[BI<br/>分析]
```

---

<!-- TODO: 由后续任务填充各章节 -->
```

- [ ] **Step 9.2: 校验章节内容**

Run:
```bash
grep -nE "^## 🔌 系统集成模式|^### 集成方式|^### 集成模式|^### 关键集成场景|^#### 订单主链|^#### 供应链主链|^#### 数据主链" note/08.application-systems/README.md
```
Expected: 至少 7 行匹配

- [ ] **Step 9.3: Commit**

Run:
```bash
git add note/08.application-systems/README.md
git commit -m "feat(note): 08.application-systems - add integration patterns chapter

覆盖集成方式 / 集成模式 / 3 个关键主链场景（订单/供应链/数据）。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 1 file changed，约 +70 insertions

---

## Task 10: 写入速查表 + 学习路线

**Files:**
- Modify: `note/08.application-systems/README.md`

- [ ] **Step 10.1: 替换最后一个 TODO 为速查表 + 学习路线 + 收尾**

Edit 工具，把：

```markdown
---

<!-- TODO: 由后续任务填充各章节 -->
```

替换为：

```markdown
---

## 📋 系统速查表

21 个系统按缩写字母排序：

| 缩写 | 全称 | 一句话定位 | 价值链章节 |
|---|---|---|---|
| APS | Advanced Planning and Scheduling | 高级计划与排程 | 02 生产制造 |
| BI | Business Intelligence | 商业智能/数据分析 | 05 运营管理 |
| CMS | Content Management System | 内容管理 | 01 研发创新 |
| CRM | Customer Relationship Management | 客户关系管理 | 04 销售服务 |
| EAM | Enterprise Asset Management | 企业资产管理 | 05 运营管理 |
| ERP | Enterprise Resource Planning | 企业资源计划（核心） | 05 运营管理 |
| LIMS | Laboratory Information Management System | 实验室信息管理 | 06 专项支持 |
| MES | Manufacturing Execution System | 制造执行系统 | 02 生产制造 |
| MOM | Manufacturing Operation Management | 制造运营管理 | 02 生产制造 |
| OA | Office Automation | 办公自动化 | 05 运营管理 |
| OMS | Order Management System | 订单管理 | 04 销售服务 |
| PDM | Product Data Management | 产品数据管理 | 01 研发创新 |
| PLM | Product Lifecycle Management | 产品生命周期管理 | 01 研发创新 |
| PMS | Project Management System | 项目管理 | 06 专项支持 |
| QMS | Quality Management System | 质量管理 | 05 运营管理 |
| SCADA | Supervisory Control And Data Acquisition | 设备监控与数据采集 | 02 生产制造 |
| SCRM | Social Customer Relationship Management | 社交化客户关系 | 04 销售服务 |
| SCM | Supply Chain Management | 供应链管理 | 03 供应链 |
| SRM | Supplier Relationship Management | 供应商关系管理 | 03 供应链 |
| TMS | Transportation Management System | 运输管理 | 03 供应链 |
| WMS | Warehouse Management System | 仓储管理 | 03 供应链 |

---

## 🛤️ 学习路线

### 入门（1-2 天）

1. [🗺️ 业务价值链全景图](#-业务价值链全景图) — 5 分钟建立全局观
2. [ERP 详讲](#erpenterprise-resource-planning-企业资源计划) — 最核心、最容易遇到
3. [CRM 详讲](#crmcustomer-relationship-management-客户关系管理) — 最常见的需求来源

### 进阶（3-5 天）

4. [MES 详讲](#mesmanufacturing-execution-system-制造执行系统) — 制造企业的命脉
5. [PLM 详讲](#plmproduct-lifecycle-management-产品生命周期管理) — 研发数字化主干
6. [WMS 详讲](#wmswarehouse-management-system-仓储管理系统) — 物流与电商核心
7. [🔌 系统集成模式](#-系统集成模式) — 理解系统间怎么对话
8. [📋 系统速查表](#-系统速查表) — 日常查询

### 高级（专项深入）

9. MOM + SCADA — 智能制造方向
10. SRM + APS — 供应链优化方向
11. BI — 数据驱动决策方向

---
```

- [ ] **Step 10.2: 校验 21 个系统全部出现**

Run:
```bash
for sys in APS BI CMS CRM EAM ERP LIMS MES MOM OA OMS PDM PLM PMS QMS SCADA SCRM SCM SRM TMS WMS; do
  count=$(grep -c "\b$sys\b" note/08.application-systems/README.md)
  if [ "$count" -lt 2 ]; then
    echo "MISSING or TOO FEW: $sys (count=$count)"
  fi
done
echo "DONE"
```
Expected: 仅输出 `DONE`，无 `MISSING` 行

- [ ] **Step 10.3: 校验总行数与 png 引用**

Run:
```bash
wc -l note/08.application-systems/README.md
grep -c '\.png\|\.jpg\|\.jpeg' note/08.application-systems/README.md
```
Expected: 行数 900-1200；png 引用次数 = 0

- [ ] **Step 10.4: Commit**

Run:
```bash
git add note/08.application-systems/README.md
git commit -m "feat(note): 08.application-systems - add system cheatsheet + learning path

21 系统速查表（字母排序）+ 入门/进阶/高级 三段学习路线。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 1 file changed，约 +60 insertions

---

## Task 11: 更新 note/README.md 索引

**Files:**
- Modify: `note/README.md`

- [ ] **Step 11.1: 定位索引位置**

Run:
```bash
grep -n "07\.workflow\|08\.\|10\.big-data" note/README.md | head -10
```
Expected: 找到 07.workflow 和 10.big-data 的索引行（夹在中间的 08/09 位置就是要插入/编辑的地方）

- [ ] **Step 11.2: 读取上下文**

Read 工具读 `note/README.md` 中相关位置（约 ±15 行）确认插入点。

- [ ] **Step 11.3: 插入 08.application-systems 索引行**

在 07.workflow 和 10.big-data 之间插入（具体文字以 11.2 读到的实际内容为准，章节简介保持一致长度）：

```markdown
| [08 业务应用系统](08.application-systems/README.md) | 21 | ERP/MES/CRM/SCM/PLM 等 21 个常见业务系统，按业务价值链组织，业务/产品/需求人员速查手册 |
```

如果原 README 索引格式不同，按对应格式调整（保持与原表格一致风格）。

- [ ] **Step 11.4: 删除 09.other 索引行（如果存在）**

如果 11.1 输出中有 09.other 相关行，用 Edit 工具删除。

- [ ] **Step 11.5: 校验索引**

Run:
```bash
grep -n "08\.application-systems\|09\.other" note/README.md
```
Expected: 至少 1 行匹配 `08.application-systems`；`09.other` 行数 = 0

- [ ] **Step 11.6: Commit**

Run:
```bash
git add note/README.md
git commit -m "docs(note): update top README index - add 08.application-systems, drop 09.other

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 1 file changed，约 +1 -1

---

## Task 12: 删除 09.other 目录 + 最终验收

**Files:**
- Delete: `note/09.other/`

- [ ] **Step 12.1: 删除 09.other 目录**

Run:
```bash
ls note/09.other/
rm -rf note/09.other
```
Expected: 第一个 ls 列出 `common-systems` 一行；rm 静默成功

- [ ] **Step 12.2: 校验删除结果**

Run:
```bash
ls note/ | grep -E "08\.application-systems|09\.other"
ls note/08.application-systems/
```
Expected:
- 第一行：仅 `08.application-systems`
- 第二行：仅 `README.md`

- [ ] **Step 12.3: 校验 git 状态干净**

Run:
```bash
git status --short
```
Expected: 看到 `D  note/09.other/common-systems/README.md` 等若干 D 状态行，**不应**有 `??`（untracked）或 `M`（modified，README.md 之外）行

- [ ] **Step 12.4: 最终验收对照清单**

Run:
```bash
echo "=== 1. 新 README 存在 ==="
test -f note/08.application-systems/README.md && echo "OK" || echo "FAIL"

echo "=== 2. 09.other 已删除 ==="
test ! -d note/09.other && echo "OK" || echo "FAIL"

echo "=== 3. 21 个系统全覆盖 ==="
for sys in APS BI CMS CRM EAM ERP LIMS MES MOM OA OMS PDM PLM PMS QMS SCADA SCRM SCM SRM TMS WMS; do
  if ! grep -q "\b$sys\b" note/08.application-systems/README.md; then
    echo "FAIL: $sys missing"
  fi
done
echo "done"

echo "=== 4. 6 价值链章节齐全 ==="
for ch in "01 研发创新" "02 生产制造" "03 供应链" "04 销售服务" "05 运营管理" "06 专项支持"; do
  grep -q "^## $ch" note/08.application-systems/README.md || echo "FAIL: $ch missing"
done
echo "done"

echo "=== 5. 4 个辅助章节齐全 ==="
for aux in "🚀 快速入口" "🗺️ 业务价值链全景图" "🔌 系统集成模式" "📋 系统速查表" "🛤️ 学习路线"; do
  grep -q "^## $aux" note/08.application-systems/README.md || echo "FAIL: $aux missing"
done
echo "done"

echo "=== 6. 无 png 引用 ==="
png_count=$(grep -c '\.png\|\.jpg\|\.jpeg' note/08.application-systems/README.md)
[ "$png_count" -eq 0 ] && echo "OK" || echo "FAIL: $png_count images"

echo "=== 7. note/README.md 已加索引 ==="
grep -q "08\.application-systems" note/README.md && echo "OK" || echo "FAIL"
```
Expected: 所有项 `OK` / `done`；**不应**出现任何 `FAIL`

- [ ] **Step 12.5: Commit 最终删除**

Run:
```bash
git add -A note/09.other
git commit -m "feat(note): remove 09.other - all content migrated to 08.application-systems

详见 docs/superpowers/specs/2026-06-24-application-systems-design.md

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 多个 file changed（包含 common-systems/README.md 和 pdm/、erp/ 子目录的所有文件）

- [ ] **Step 12.6: 最终 git log 校验**

Run:
```bash
git log --oneline -15
```
Expected: 看到本任务链的 12 个 commit（从 Task 1 scaffold 到 Task 12 删除 09.other），顺序递增

---

## 任务完成标准

✅ `note/08.application-systems/README.md` 存在，内容覆盖 21 个系统
✅ `note/09.other/` 已删除
✅ `note/README.md` 索引已加 `08.application-systems` 链接
✅ 所有图都是 mermaid，无 png 引用
✅ git 历史清晰，每章独立成 commit，便于回滚与 review