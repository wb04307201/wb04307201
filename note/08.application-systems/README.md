<!--
module:
  number: 08
  slug: application-systems
  topic: 业务应用系统速查
  audience: 业务 / PM / 需求
  category: 主模块
  summary: 一份按业务价值链梳理的业务系统速查手册，帮助业务/产品/需求人员快速建立完整的业务系统认知地图，并具备日常速查能力。
-->

# 业务应用系统

> 一份按业务价值链梳理的业务系统速查手册，帮助业务/产品/需求人员快速建立完整的业务系统认知地图，并具备日常速查能力。
>
> 覆盖 21 个常见业务系统：MES · ERP · SCM · WMS · APS · SCADA · PLM · PDM · QMS · CRM · EAM · SRM · OMS · SCRM · OA · MOM · TMS · LIMS · CMS · BI · PMS

## 📑 目录

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

#### PLM（产品生命周期管理）

- **核心定位**：管理产品从概念到退役的全生命周期数据与流程
- **关键能力**：BOM 中央仓库 / 工程变更 / 项目管理 / CAD 集成
- **典型场景**：汽车新车型研发、电子产品多代演进、工程变更追溯
- **上下游**：上接 CRM/CMS，下接 ERP/MES
- 📚 详见 [PLM 深读](./plm/) — 历史脉络 / 常见陷阱 / 代表案例

#### PDM（Product Data Management 产品数据管理）

- **核心定位**：PLM 的核心子集，专注于产品数据本身（文档、图纸、零部件）的管理与组织
- **关键能力**：版本管理 / 零部件库 / CAD 集成 / 检索与权限 / 变更管理 / 生命周期状态
- **典型场景**：纯研发数据管理需求、PDM 起步阶段、中小制造业（CAD 文件 1 万-10 万）
- **上下游**：上接 CAD/CAE/CAPP，下接 ERP/MES，是 PLM 的数据底层
- 📚 详见 [PDM 深读](./pdm/) — 历史脉络 / 选型指南 / 代表案例

### 📋 其他系统速览

#### CMS（Content Management System 内容管理系统）

管理网站、博客、营销内容等的创建、编辑、发布。**适用场景**：产品官网、帮助文档、营销活动页。

### 💡 本章小结

研发创新环节的核心是 PLM/PDM（管产品数据），CMS（管内容触达）是辅助。本章输出"产品主数据"流向下一章"生产制造"。

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

- **核心定位**：把 ERP 的生产计划落地为车间工单并实时跟踪执行的执行层系统，是连接计划层与控制层的"执行中枢"
- **关键能力**：工单调度 / 设备数据采集 / 质量管理 / 批次追溯 / OEE 看板 / SOP 电子化
- **典型场景**：离散制造（汽车/电子）、流程制造（化工/食品）、半导体、医疗器械、航空
- **上下游**：上接 ERP/PLM，下接 SCADA/WMS/QMS，与 APS/SCADA 横向集成
- 📚 详见 [MES 深读](./mes/) — 历史脉络 / 选型指南 / 常见陷阱 / 代表案例

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

- **核心定位**：管理仓库作业全流程（入库 → 上架 → 拣选 → 出库 → 盘点）的精细化系统，是仓储数字化的"调度中枢"
- **关键能力**：库位/批次/序列号/效期管理 + 拣选策略（波次/边拣边分/灯光拣选）+ 设备集成（RF/AGV/堆垛机/电子标签）+ 退货与差异处理
- **典型场景**：电商履约中心（日发百万单）、制造业线边仓（JIT 配送）、冷链/危险品（合规追溯）、跨境保税仓（三单对碰）、医药 GSP/医疗器械 UDI、汽车售后备件多级 DC
- **上下游**：上接 ERP/MES（出入库指令），下接 TMS（待发运）+ AGV/AMR（设备调度），横向对接海关（保税仓）/财务（库存估值）
- **关键考量**：库位编码是 WMS 的"灵魂"（无编码 = 高级进销存）；硬件投资是软件 5-10 倍（软硬一体预算）；批次/序列号/效期是医药/食品合规前提
- 📚 详见 [WMS 深读](./wms/) — 上下游 / 选型指南 / 常见陷阱

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

- **核心定位**：以客户全生命周期为主线的管理与运营平台，是企业对外经营的主入口
- **关键能力**：客户主数据 / 销售自动化 SFA（L→O→Q→C→O 漏斗）/ 市场自动化 / 客服工单 / 客户成功
- **典型场景**：B2B 大客户 / B2C 零售 / SaaS 订阅 / 经销商网络 / 金融保险代理人
- **上下游**：上接市场自动化 / SCRM / CDP，下接 ERP / OMS；横向与客服系统闭环
- **关键考量**：销售流程标准化是前提；数据质量决定价值；移动端体验关键
- 📚 详见 [CRM 深读](./crm/) — 上下游 / 选型指南 / 常见陷阱

### 📋 其他系统速览

#### SCRM（Social Customer Relationship Management 社交化客户关系管理）

CRM 的社交化延伸，集成微信/小红书/抖音等社交触点，把"粉丝"转化为可运营客户。**适用场景**：消费品零售、网红营销、私域运营。

#### OMS（Order Management System 订单管理系统）

订单全生命周期管理（创建/拆分/合并/路由/状态），是连接 CRM 与 ERP/WMS/TMS 的中枢。**适用场景**：多渠道订单（电商+门店+经销商）统一管理。

### 💡 本章小结

销售服务的核心是 CRM（客户主数据），OMS 协调订单履约，SCRM 是社交化补充。本章输出"客户+订单"信息给运营管理章节的 ERP。

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

- **核心定位**：整合企业核心业务流程（财务、采购、库存、销售、生产）于一体，是企业数字化的"中枢系统"
- **关键能力**：财务（总账/应收应付/固定资产/成本）/采购 PO+GR+IR 三单匹配/库存批次序列号/MRP 运算/多组织合并
- **典型场景**：大型集团（SAP/Oracle）、中型制造（用友 U9/金蝶云·星空）、小型（金蝶云·星辰）、零售/项目型
- **上下游**：上接 CRM/PLM，下接 MES/WMS/SCM，横向与 HR/财务/BI 双向同步
- **关键考量**：行业 Know-how 比品牌重要；实施周期 1-3 年；数据迁移占成本 30-40%；主数据治理必须先行
- 📚 详见 [ERP 深读](./erp/) — 上下游 / 选型指南 / 常见陷阱 / 代表案例

### 📋 其他系统速览

- **BI**（商业智能）：数据分析、报表、可视化；**适用场景**：管理驾驶舱、自助分析
- **EAM**（企业资产管理）：物理资产全生命周期 + 维护（预防性维护、检修工单）；**适用场景**：资产密集行业（电力、轨交、物业）
- **OA**（办公自动化）：行政办公流程（审批、文档、协同），国内代表有泛微/致远/钉钉/企业微信；**适用场景**：企业内部流程审批、文档协作
- **QMS**（质量管理系统）：产品质量（来料/过程/成品检验、不良品处理、质量分析）；**适用场景**：制造业（IATF 16949）、食品医药（GMP）

### 💡 本章小结

运营管理的核心是 ERP（中枢），BI 给决策者看数据，EAM/OA/QMS 是企业运营不同侧面的支撑。本章把整条价值链的数据汇聚成可衡量、可管控的经营指标。

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

- **核心定位**：管理实验室样品、检测数据、报告、仪器、资源的信息系统，是实验室合规与数字化的核心
- **关键能力**：样品登记与流转 / 检测方法与结果录入 / 仪器连接与数据自动采集 / 报告生成与审核 / 合规（GLP/GMP/ISO 17025）
- **典型场景**：制药/化工研发实验室、环境监测/食品检测第三方实验室、医院/疾控临床检验
- **关键考量**：行业监管严格，合规要求决定选型

#### PMS（Project Management System 项目管理系统）

- **核心定位**：管理项目全生命周期（立项、计划、执行、监控、收尾）的协作系统，是组织级项目协同的工具
- **关键能力**：任务分解（WBS）/ 甘特图 / 关键路径 / 资源分配与预算 / 风险与问题管理 / 协作（评论、@、文档）
- **典型场景**：工程类项目（土建、IT 集成、咨询）、研发项目（与 PLM 偏管理部分重叠）、营销/活动项目
- **关键考量**：与 OA/PLM 的边界需明确，避免重复录入

### 💡 本章小结

专项支持系统服务于特定场景。LIMS 偏实验室合规，PMS 偏项目协作。

---

## 🔌 系统集成模式

> 业务系统从来不是孤立的——它们需要"对话"。本章讲解系统间如何集成，从最底层的"通信方式"到上层的"组织模式"再到具体的"主链场景"。

### 集成方式（"怎么连"）

- **API/REST**：同步、实时、契约清晰 — 现代云原生系统、跨企业开放接口
- **消息队列**：异步、解耦、削峰 — 高并发场景（Kafka/RabbitMQ）、事件驱动
- **中间件/ESB**：集中路由、协议转换 — 传统企业集成（IBM Integration Bus/MuleSoft/自研）
- **文件交换/EDI**：跨企业、跨行业、批处理 — 供应链上下游（EDI 标准）、银企直联
- **数据库直连**：应急/过渡方案 — 不推荐生产环境（老系统接口缺失时临时用）

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

| 模式 | 适用 |
|---|---|
| **点对点** | 系统数量少（≤3），简单直接 |
| **ESB 总线** | 传统大型企业，集中管控/协议转换 |
| **事件驱动** | 现代微服务/云原生，松耦合可扩展 |
| **主数据管理（MDM）** | 数据标准不统一的大型企业，先治理再集成 |

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

#### 数据主链（PLM→BI）

```mermaid
flowchart LR
    A[PLM<br/>BOM] --> B[ERP<br/>MRP] --> C[MES<br/>工单] --> D[BI<br/>分析]
```

---

## 📋 系统速查表

| 缩写 | 全称 | 一句话定位 | 价值链章节 | 📚 深读 |
|---|---|---|---|---|
| APS | Advanced Planning and Scheduling | 高级计划与排程 | 02 生产制造 | — |
| BI | Business Intelligence | 商业智能/数据分析 | 05 运营管理 | — |
| CMS | Content Management System | 内容管理 | 01 研发创新 | — |
| CRM | Customer Relationship Management | 客户关系管理 | 04 销售服务 | [深读](./crm/) |
| EAM | Enterprise Asset Management | 企业资产管理 | 05 运营管理 | — |
| ERP | Enterprise Resource Planning | 企业资源计划（核心） | 05 运营管理 | [深读](./erp/) |
| LIMS | Laboratory Information Management System | 实验室信息管理 | 06 专项支持 | — |
| MES | Manufacturing Execution System | 制造执行系统 | 02 生产制造 | [深读](./mes/) |
| MOM | Manufacturing Operation Management | 制造运营管理 | 02 生产制造 | — |
| OA | Office Automation | 办公自动化 | 05 运营管理 | — |
| OMS | Order Management System | 订单管理 | 04 销售服务 | — |
| PDM | Product Data Management | 产品数据管理 | 01 研发创新 | [深读](./pdm/) |
| PLM | Product Lifecycle Management | 产品生命周期管理 | 01 研发创新 | [深读](./plm/) |
| PMS | Project Management System | 项目管理 | 06 专项支持 | — |
| QMS | Quality Management System | 质量管理 | 05 运营管理 | — |
| SCADA | Supervisory Control And Data Acquisition | 设备监控与数据采集 | 02 生产制造 | — |
| SCRM | Social Customer Relationship Management | 社交化客户关系 | 04 销售服务 | — |
| SCM | Supply Chain Management | 供应链管理 | 03 供应链 | — |
| SRM | Supplier Relationship Management | 供应商关系管理 | 03 供应链 | — |
| TMS | Transportation Management System | 运输管理 | 03 供应链 | — |
| WMS | Warehouse Management System | 仓储管理 | 03 供应链 | [深读](./wms/) |

---

## 🏆 最佳实践

| 场景 | 实践要点 |
|------|---------|
| **系统选型** | 先明确业务价值链位置（研发/生产/供应链/销售/运营）；中小企业用一体化 ERP（SAP/用友/金蝶）；制造业核心抓 MES + WMS |
| **系统集成** | 优先 API 网关统一入口；异步场景用消息队列（Kafka/RabbitMQ）；跨系统数据同步用 CDC（Canal/Debezium） |
| **数据流设计** | 主数据管理（MDM）统一编码；ETL/ELT 工具（DataX/Flink CDC）分层处理；数据血缘可追溯 |
| **实施方法论** | 分阶段上线（先核心再扩展）；蓝图设计 → 配置开发 → 集成测试 → 上线切换 → 持续优化 |
| **国产化替代** | ERP → 用友/金蝶/浪潮；MES → 盘古/摩尔元山；数据库 → TiDB/OceanBase；中间件 → RocketMQ/Nacos |

---

## 🛤️ 学习路线

- **入门（1-2 天）**：[业务价值链全景图](#-业务价值链全景图) → [ERP 详讲](#erpenterprise-resource-planning-企业资源计划) → [CRM 详讲](#crmcustomer-relationship-management-客户关系管理)
- **进阶（3-5 天）**：[MES 详讲](#mesmanufacturing-execution-system-制造执行系统) → [PLM 详讲](#plmproduct-lifecycle-management-产品生命周期管理) → [WMS 详讲](#wmswarehouse-management-system-仓储管理系统) → [系统集成模式](#-系统集成模式) → [系统速查表](#-系统速查表)
- **高级（专项深入）**：MOM+SCADA（智能制造）/ SRM+APS（供应链优化）/ BI（数据驱动决策）

### 高级（专项深入）

9. MOM + SCADA — 智能制造方向
10. SRM + APS — 供应链优化方向
11. BI — 数据驱动决策方向

---

## 相关章节

- 技术实现：[`06.spring`](../06.spring/README.md) — 业务系统的 Java/Spring 技术栈
- 数据层：[`03.database`](../03.database/README.md) — 业务系统的数据存储、事务、缓存设计
- 架构设计：[`04.system-design`](../04.system-design/README.md) — 分布式、高可用、高性能设计模式
- 流程引擎：[`07.workflow`](../07.workflow/README.md) — BPMN 工作流（ERP/MES/CRM 中的审批流、业务流）
- 大数据：[`10.big-data`](../10.big-data/README.md) — 数据仓库、BI、数据治理（支撑 BI/ERP 数据分析）
- 前端：[`09.front-end`](../09.front-end/README.md) — 业务系统前端工程化
- 深化：[`13.split-hairs`](../13.split-hairs/README.md) — 高频面试题（系统设计、数据库等）

---

---

← [返回笔记目录](../README.md)
