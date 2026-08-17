<!--
module:
  parent: system-design
  slug: system-design/it4it/functional-components
  type: article
  category: 主模块子文章
  summary: IT4IT 9 大功能组件：战略/治理/需求/实施/组合/目录/转换/运营/请求到保障，每组件含核心活动/数据对象/责任方/成熟度标志。
-->

# 第二章：功能组件：9 大 IT 能力 + 数据对象

> ⬅️ [返回目录](README.md) | 上一篇：[价值流：从请求到服务的 4 条路](value-streams.md) | 下一篇：[落地：IT4IT × ITIL × DevOps](in-practice.md)

---

## 🎯 一句话定位

**IT4IT 的 9 大功能组件是 IT 部门的"职能图"**——每个组件对应一组"做什么"的活动，组件之间通过**数据对象**流转。**价值流是"端到端主干道"，功能组件是"沿主干道分布的职能部门"，数据对象是"在部门之间传递的资产"**。三者结合，IT4IT 才有"骨架 + 肌肉 + 血液"。

---

## 一、9 大功能组件全景

```mermaid
graph TB
    subgraph STR["🧭 战略与治理层 (Strategy & Governance)"]
        S["Strategy 战略<br/>IT 战略与业务对齐"]
        G["Governance 治理<br/>决策、风险、合规"]
    end

    subgraph REQ["📋 需求与设计层 (Requirement & Design)"]
        D["Demand 需求<br/>业务请求评估"]
        RF["Requirement 需求规格<br/>详细需求文档"]
        DS["Design 设计<br/>架构与详细设计"]
    end

    subgraph BL["📚 资产管理层 (Asset Layer)"]
        P["Portfolio 投资组合<br/>项目组合管理"]
        C["Catalog 目录<br/>服务与组件目录"]
    end

    subgraph OPS["⚙️ 运营层 (Operations)"]
        T["Transition 转换<br/>上线与变更管理"]
        O["Operation 运营<br/>日常服务运营"]
    end

    subgraph IM["🚨 改进层 (Improvement)"]
        I["Incident 事件<br/>故障响应"]
    end

    STR --> REQ
    REQ --> BL
    BL --> OPS
    OPS --> IM
    IM -.-> STR

    classDef str fill:#f3e5f5,stroke:#6a1b9a
    classDef req fill:#e3f2fd,stroke:#1976d2
    classDef bl fill:#fff3e0,stroke:#e65100
    classDef ops fill:#e8f5e9,stroke:#2e7d32
    classDef im fill:#fce4ec,stroke:#c2185b
    class STR,S,G str
    class REQ,D,RF,DS req
    class BL,P,C bl
    class OPS,T,O ops
    class IM,I im
```text
> ⚠️ **注**：IT4IT 3.0 的 9 大组件在不同文档里有 2 种编号方式（7+2 或 9 平铺）。本章采用 **9 平铺 + 5 层分组** 方式（Strategy、Governance、Demand、Requirement、Design、Portfolio、Catalog、Transition、Operation + Incident 改进层），更便于工程理解。

---

## 二、9 大功能组件详解

### 2.1 Strategy 战略组件

| 项 | 内容 |
|----|------|
| **一句话** | "IT 该往哪走？怎么和业务对齐？" |
| **核心活动** | IT 战略制定、能力规划、技术趋势分析、预算分配 |
| **输入** | 业务战略、市场分析、技术评估 |
| **输出** | IT 战略文档、能力路线图、年度预算 |
| **责任方** | CIO + IT 战略团队 |
| **成熟度标志** | 有书面的、年度更新的 IT 战略；与业务战略显式关联 |
| **对应价值流** | R2F（顶层）、贯穿 |

> 📌 **常见误区**：把 Strategy 当成"IT 部门年度汇报"。真正的 IT 战略回答的是"未来 3 年我们要建/淘汰什么能力"。

### 2.2 Governance 治理组件

| 项 | 内容 |
|----|------|
| **一句话** | "IT 决策怎么做？风险怎么控？合规怎么达？" |
| **核心活动** | 架构评审、变更审批、合规审计、风险登记 |
| **输入** | 决策请求、变更请求、风险事件 |
| **输出** | 架构决策记录 (ADR)、审计报告、风险登记册 |
| **责任方** | 架构委员会 + PMO + 合规团队 |
| **成熟度标志** | 有清晰的决策矩阵；ADR 在 Confluence/Wiki 可查 |
| **对应价值流** | 贯穿 4 流 |

> 📌 **与 TOGAF 的关系**：Governance 直接对应 TOGAF 第四章"架构治理"——TOGAF 讲治理的"why"，IT4IT 讲治理的"how to operate"。

### 2.3 Demand 需求组件

| 项 | 内容 |
|----|------|
| **一句话** | "业务提了什么请求？值不值得做？" |
| **核心活动** | 业务 Brief 接收、初步评估、ROI 估算、价值打分 |
| **输入** | 业务 Brief、市场信号、客户反馈 |
| **输出** | Demand 记录（包含价值/成本/风险评分） |
| **责任方** | 业务关系经理 (BRM) + 业务分析师 |
| **成熟度标志** | 所有业务请求都进入统一 Demand Pool；用统一模板打分 |
| **对应价值流** | R2F（早期） |

### 2.4 Portfolio 投资组合组件

| 项 | 内容 |
|----|------|
| **一句话** | "在有限资源下做什么/不做什么/先做什么？" |
| **核心活动** | 组合优先级排序、容量平衡、投资回报跟踪 |
| **输入** | 多个 Demand 记录、资源约束、战略目标 |
| **输出** | 排序后的 Roadmap、组合视图 |
| **责任方** | PMO + 投资委员会 |
| **成熟度标志** | 有公开的组合看板（80% 公司没有）；季度复盘 |
| **对应价值流** | R2F（中期） |

> 📌 **核心心法**：组合管理不是"做所有想做的事"，而是"放弃 70% 的想法，集中资源做 30% 高价值的事"。

### 2.5 Catalog 目录组件

| 项 | 内容 |
|----|------|
| **一句话** | "我们有什么服务？用户怎么找到？" |
| **核心活动** | 服务登记、目录维护、版本管理、状态跟踪 |
| **输入** | 上线服务、下线服务、版本变更 |
| **输出** | 服务目录条目 (Catalog Entry) |
| **责任方** | 服务所有者 + 服务台 |
| **成熟度标志** | 用户能通过门户/微信/钉钉 30 秒找到服务 |
| **对应价值流** | R2S、R2F（成果） |

### 2.6 Requirement 需求规格组件

| 项 | 内容 |
|----|------|
| **一句话** | "需求到底要做什么？验收标准是什么？" |
| **核心活动** | 需求细化、用户故事编写、验收标准定义、需求追溯 |
| **输入** | 已批准的 Demand |
| **输出** | 需求规格说明书 (SRS)、用户故事、验收标准 |
| **责任方** | 产品经理 + 业务分析师 + 架构师 |
| **成熟度标志** | 100% 需求可追溯（需求→设计→测试→上线） |
| **对应价值流** | R2F（中期） |

### 2.7 Design 设计组件

| 项 | 内容 |
|----|------|
| **一句话** | "怎么用技术实现需求？" |
| **核心活动** | 架构设计、详细设计、技术选型、接口定义 |
| **输入** | 需求规格 |
| **输出** | 架构图、详细设计文档、API 契约、ADR |
| **责任方** | 架构师 + Tech Lead |
| **成熟度标志** | 关键决策都有 ADR；架构图与代码同步 |
| **对应价值流** | R2F（后期）→ P2D（前期） |

### 2.8 Transition 转换组件

| 项 | 内容 |
|----|------|
| **一句话** | "设计怎么平滑变成生产？" |
| **核心活动** | 实施、测试、灰度、上线、回滚预案 |
| **输入** | 设计文档、需求规格 |
| **输出** | 上线 Release、Runbook、培训材料 |
| **责任方** | Tech Lead + SRE + Release Manager |
| **成熟度标志** | 全自动化部署 + 一键回滚 |
| **对应价值流** | P2D（核心） |

### 2.9 Operation 运营组件

| 项 | 内容 |
|----|------|
| **一句话** | "服务上线后怎么稳定运行？" |
| **核心活动** | 监控告警、容量管理、变更实施、SLA 监控 |
| **输入** | 上线服务 |
| **输出** | 运行报告、SLA 报告、容量规划 |
| **责任方** | SRE + 运维 + 服务所有者 |
| **成熟度标志** | 关键指标实时看板；SLA 自动计算 |
| **对应价值流** | R2S（持续） |

### 2.10 Incident 事件组件（改进层）

| 项 | 内容 |
|----|------|
| **一句话** | "出问题了怎么快速恢复 + 防止再发？" |
| **核心活动** | 事件响应、根因分析、问题管理、改进措施跟踪 |
| **输入** | 监控告警、用户报障 |
| **输出** | Incident 记录、Problem 记录、Postmortem 报告 |
| **责任方** | SRE + Incident Commander |
| **成熟度标志** | 有 blameless postmortem 机制；改进措施闭环率 > 80% |
| **对应价值流** | D2C（核心） |

---

## 三、18 个核心数据对象

数据对象是**价值流之间、功能组件之间流转的"IT 资产"**。每个数据对象有明确的 schema、生命周期、责任人。

### 3.1 数据对象分类全景

```mermaid
graph LR
    subgraph R2F_OBJ["📋 R2F 相关对象"]
        O1["Brief 业务简报"]
        O2["Demand 需求"]
        O3["Portfolio Item 组合项"]
        O4["Requirement 需求规格"]
        O5["Solution Design 解决方案设计"]
    end

    subgraph R2S_OBJ["🎧 R2S 相关对象"]
        O6["Service Definition 服务定义"]
        O7["Service Request 服务请求"]
        O8["Service Instance 服务实例"]
        O9["Service Level Agreement SLA"]
    end

    subgraph D2C_OBJ["🔍 D2C 相关对象"]
        O10["Event 事件"]
        O11["Alert 告警"]
        O12["Incident 故障"]
        O13["Problem 问题"]
    end

    subgraph P2D_OBJ["🚀 P2D 相关对象"]
        O14["Release 发布"]
        O15["Project 项目"]
        O16["Change 变更"]
        O17["Deployment 部署"]
    end

    subgraph CAT_OBJ["📚 跨流对象"]
        O18["Catalog Item 目录项"]
    end

    classDef r2f fill:#e3f2fd,stroke:#1976d2
    classDef r2s fill:#e8f5e9,stroke:#2e7d32
    classDef d2c fill:#fff3e0,stroke:#e65100
    classDef p2d fill:#f3e5f5,stroke:#6a1b9a
    classDef cat fill:#fce4ec,stroke:#c2185b
    class R2F_OBJ,O1,O2,O3,O4,O5 r2f
    class R2S_OBJ,O6,O7,O8,O9 r2s
    class D2C_OBJ,O10,O11,O12,O13 d2c
    class P2D_OBJ,O14,O15,O16,O17 p2d
    class CAT_OBJ,O18 cat
```text
### 3.2 Top 10 高频数据对象详解

| 数据对象 | 所在流 | 关键字段 | 生命周期 | 责任人 |
|---------|:-----:|---------|---------|--------|
| **Brief** | R2F | 标题、发起人、业务价值、初步成本 | 创建→评估→转化/驳回 | BRM |
| **Demand** | R2F | 价值评分、成本评分、风险评分、状态 | 创建→评估→批准/驳回→归档 | 业务分析师 |
| **Requirement** | R2F | 用户故事、验收标准、优先级、追溯 | 创建→评审→冻结→实现→验证 | 产品经理 |
| **Service Definition** | R2S | 名称、描述、SLA、版本、所有者 | 创建→发布→更新→下线 | 服务所有者 |
| **Service Request** | R2S | 用户、申请的服务、申请时间、状态 | 创建→审批→执行→完成 | 服务台 |
| **Service Instance** | R2S | 用户、服务、配置、计费信息 | 创建→消费→退订 | 平台 |
| **SLA** | R2S | 服务、可用性目标、响应时间、违约条款 | 创建→签订→监控→续约 | 服务所有者 |
| **Incident** | D2C | 严重度、影响范围、状态、负责人 | 创建→响应→诊断→恢复→关闭 | Incident Commander |
| **Problem** | D2C | 根因、影响、临时方案、永久方案 | 创建→调查→修复→关闭 | 问题经理 |
| **Release** | P2D | 版本、变更范围、部署计划、回滚方案 | 创建→评审→部署→完成 | Release Manager |

### 3.3 数据对象的"ID 与状态"是 IT 集成的命脉

| 集成场景 | 涉及对象 | 必须保证 |
|---------|---------|---------|
| "上线一个新服务" | Service Definition + Catalog Item + SLA | 三者 ID 关联，可双向追溯 |
| "业务方提了新需求" | Brief → Demand → Requirement → Design | 四者 ID 关联，可双向追溯 |
| "故障影响了哪些服务" | Incident ← Service Instance ← Service Definition | 故障 → 服务的反向追溯 |
| "上线版本影响哪些需求" | Release ← Deployment ← Change ← Requirement | 上线 → 需求的反向追溯 |

> 📌 **IT4IT 3.0 Service Backbone 的本质**：把所有数据对象的 ID 关联打通，实现**全链路双向追溯**。

### 3.4 Service Definition 实体示例（Java）

> 📌 **为什么用 Java**：IT4IT 的 R2S 价值流最终落地多为面向服务的后端系统（Spring Boot / Micronaut / Quarkus），实体类风格与日常编码对齐，可直接拷贝到 Service Catalog 微服务骨架。

```java
// 为什么用 Lombok + Java Record：减少样板代码，重点体现 IT4IT 数据对象的"身份 + 生命周期 + SLA"
// 字段全部对应 IT4IT 3.0 规范的 ServiceDefinitionSchema
package com.example.it4it.catalog.domain;

import java.time.Instant;
import java.util.List;

/**
 * IT4IT R2S 价值流的"服务定义"数据对象。
 * <p>
 * 对应 IT4IT 3.0 规范中的 Service Definition 数据对象，是 Catalog Item 的父模板。
 * 一个 ServiceDefinition 可被实例化多次（ServiceInstance），每个实例有自己的 SLA。
 *
 * @author wb04307201
 * @since 2026.07
 */
public record ServiceDefinition(
        String id,                        // 全局唯一 ID，跨价值流追溯的"主键"
        String name,                      // 服务名称（如 "支付清算服务"）
        String version,                   // 语义化版本（SemVer）
        ServiceCategory category,         // 服务分类：INFRASTRUCTURE / PLATFORM / APPLICATION
        List<ServiceLevelObjective> slos, // 为什么用 List：SLA 可由多个 SLO 复合（可用性 + 延迟 + 错误率）
        ServiceStatus status,             // 生命周期：DESIGN / ACTIVE / DEPRECATED / RETIRED
        String ownerTeam,                 // 服务所有者（团队 ID），对应 IT4IT Catalog 组件的"责任方"
        Instant publishedAt,              // 上线时间
        Instant retiredAt                 // 下线时间，null = 仍在服务
) {
    /**
     * 判断服务是否"在用户可消费状态"。
     * 为什么有这个方法：IT4IT Catalog 组件的"成熟度标志"是"30 秒找到可消费服务"，
     * 服务目录的查询接口会过滤该方法返回 true 的记录。
     */
    public boolean isConsumable() {
        return status == ServiceStatus.ACTIVE
                && retiredAt == null
                && !slos.isEmpty();
    }
}
```java
```java
// 为什么 SLO 用单独类：SLA 是法律/合同概念，SLO 是技术指标；IT4IT 规范里两者是独立数据对象
package com.example.it4it.catalog.domain;

import java.time.Duration;

/**
 * 服务级目标（Service Level Objective）— SLA 的可度量技术指标。
 * <p>
 * IT4IT SLA 数据对象的内部结构。一个 ServiceDefinition 必须至少 1 个 SLO 才"可消费"。
 */
public record ServiceLevelObjective(
        String metric,           // "availability" / "p99_latency_ms" / "error_rate"
        String comparator,       // ">=" / "<=" / "<"
        double threshold,        // 阈值（如 99.95 / 200 / 0.001）
        Duration measurementWindow // 测量窗口（如 30 天滚动）
) {}
```text
```java
// 为什么枚举单独定义：IT4IT 3.0 严格规定服务生命周期 4 状态，避免状态机混乱
package com.example.it4it.catalog.domain;

public enum ServiceStatus {
    /** 设计中 — Catalog 中不可见 */
    DESIGN,
    /** 已激活 — 用户可消费 */
    ACTIVE,
    /** 已弃用 — 新用户不能申请，老用户继续服务至下线日 */
    DEPRECATED,
    /** 已下线 — 完全从目录移除，但保留历史以供追溯 */
    RETIRED
}
```text
### 3.5 Catalog Item 持久化示例（伪代码 + SQL）

> 📌 **为什么给 SQL 而不是 JPA 注解**：IT4IT 规范对 Catalog 数据结构有明确字段约束（Open Group 标准），SQL 表达更直接，便于 DBA / 数据架构师 review schema 是否符合规范。

```sql
-- Catalog Item 表，对应 IT4IT 3.0 Catalog 组件的"目录条目"
-- 为什么用 JSONB 存 slos：SLO 指标会随业务演化（先有可用性、再加延迟），JSONB 比拆表灵活
CREATE TABLE catalog_item (
    id              VARCHAR(64) PRIMARY KEY,        -- 全局唯一 ID（UUID 或 Snowflake）
    name            VARCHAR(255) NOT NULL,          -- 服务名
    definition_id   VARCHAR(64) NOT NULL,           -- 外键 → service_definition.id
    version         VARCHAR(32)  NOT NULL,          -- SemVer
    category        VARCHAR(32)  NOT NULL,          -- INFRASTRUCTURE / PLATFORM / APPLICATION
    slos            JSONB        NOT NULL,          -- SLO 列表（JSONB）
    status          VARCHAR(16)  NOT NULL,          -- DESIGN / ACTIVE / DEPRECATED / RETIRED
    owner_team      VARCHAR(64)  NOT NULL,          -- 服务所有者团队 ID
    published_at    TIMESTAMPTZ,                    -- 上线时间
    retired_at      TIMESTAMPTZ,                    -- 下线时间（NULL = 在服务）
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 为什么 unique 约束：同一服务定义 + 版本只能出现一次（防止重复上线）
    CONSTRAINT uq_catalog_item_def_version UNIQUE (definition_id, version)
);

-- 索引：服务目录查询的 2 个高频场景
CREATE INDEX idx_catalog_item_status ON catalog_item(status) WHERE status = 'ACTIVE';
CREATE INDEX idx_catalog_item_category ON catalog_item(category);

-- 为什么加 status 过滤索引：Catalog 80% 查询是"找 ACTIVE 服务"，部分索引省空间
```text
```text
# Catalog Item 持久化的"插入 + 查询"伪代码（Spring Boot 风格）

# 1. 服务上线时插入 Catalog Item（Transition 组件的输出 → Catalog 组件的输入）
@Transactional
fun publishToCatalog(serviceDef: ServiceDefinition) {
    val item = CatalogItem(
        id = UUID.random().toString(),
        definitionId = serviceDef.id,
        version = serviceDef.version,
        category = serviceDef.category.name,
        slos = objectMapper.writeValueAsString(serviceDef.slos),  // JSONB
        status = ServiceStatus.ACTIVE.name,
        ownerTeam = serviceDef.ownerTeam,
        publishedAt = Instant.now()
    )
    catalogRepository.save(item)
    // 触发 ServiceBackbone 事件：CatalogItemPublished
    // → R2S 价值流订阅该事件，更新 ServiceInstance 可消费列表
}

# 2. 用户查目录（Catalog 组件的查询接口）
fun searchConsumableServices(category: String?): List<CatalogItem> {
    return catalogRepository.findByStatusAndCategory(
        status = "ACTIVE",
        category = category,
        retiredAtIsNull = true
    )
    // 100% 走索引（idx_catalog_item_status 部分索引）
}
```text
### 3.6 Request to Fulfill（R2F）9 阶段完整流程图

> 📌 **为什么用 sequenceDiagram**：R2F 是"接力赛"——9 个阶段顺序推进、责任方轮换，sequenceDiagram 比 flowchart 更直观表达"谁在何时做什么"。

```mermaid
sequenceDiagram
    autonumber
    participant BRM as 🧑‍💼 业务关系经理
    participant BA as 📊 业务分析师
    participant PMO as 📋 PMO / 投资委员会
    participant PM as 🎯 产品经理
    participant ARCH as 🏗️ 架构师
    participant TECH as 👨‍💻 Tech Lead
    participant SRE as ⚙️ SRE

    Note over BRM,SRE: R2F 价值流：从业务请求到服务交付

    BRM->>BA: 1️⃣ Brief 提交<br/>业务简报（标题/价值/成本）
    BA->>BA: 2️⃣ Demand 评估<br/>价值/成本/风险评分
    BA->>PMO: 3️⃣ 提交投资决策<br/>带评分的 Demand 记录
    PMO->>PMO: 4️⃣ Portfolio 排序<br/>多 Demand 优先级竞争
    PMO-->>BRM: 5️⃣ 决策反馈<br/>批准 / 驳回 / 暂缓
    alt 批准
        PMO->>PM: 6️⃣ Requirement 启动<br/>已批准的 Demand 转需求
        PM->>ARCH: 7️⃣ Design 启动<br/>需求规格 + 约束
        ARCH->>ARCH: 架构设计 + ADR
        ARCH->>TECH: 8️⃣ Transition 启动<br/>设计 → 实施
        TECH->>TECH: 编码 + 测试 + 灰度
        TECH->>SRE: 9️⃣ 上线 Release<br/>部署到生产
        SRE-->>BRM: 服务上线通知<br/>回到 R2S 价值流入口
    else 驳回
        PMO-->>BRM: 驳回原因<br/>归档 Demand
    end

    Note over BRM,SRE: 每个阶段产物都有唯一 ID，可双向追溯（Service Backbone 核心）
```text
---

## 四、4 层参考架构（Reference Architecture）

IT4IT 3.0 引入了**第 4 层实现层**，把抽象的功能组件映射到具体技术实现：

```mermaid
graph TB
    L1["📊 Information Layer<br/>信息层<br/>数据对象的 schema 与 生命周期"]
    L2["⚙️ Functional Layer<br/>功能层<br/>9 大功能组件的活动与接口"]
    L3["🔌 Integration Layer<br/>集成层<br/>组件间的数据交换协议"]
    L4["🖥️ Implementation Layer<br/>实现层<br/>具体工具选型与部署模式"]

    L1 --> L2
    L2 --> L3
    L3 --> L4

    classDef l1 fill:#e3f2fd,stroke:#1976d2
    classDef l2 fill:#e8f5e9,stroke:#2e7d32
    classDef l3 fill:#fff3e0,stroke:#e65100
    classDef l4 fill:#f3e5f5,stroke:#6a1b9a
    class L1 l1
    class L2 l2
    class L3 l3
    class L4 l4
```text
### 4.1 4 层关系

| 层 | 关注问题 | 产出物 | 谁关心 |
|----|---------|--------|-------|
| **信息层** | 数据对象是什么？长什么样？ | 数据 schema、生命周期图、状态机 | 数据架构师、BA |
| **功能层** | 每个功能组件做什么？输入输出？ | 功能接口、事件流、SLA | IT 部门负责人 |
| **集成层** | 组件之间怎么连？用什么协议？ | API 契约、消息格式、集成模式 | 集成架构师 |
| **实现层** | 用什么工具落地？ | 工具选型、部署架构、运维手册 | SRE、运维 |

### 4.2 实现层是 IT4IT 3.0 的关键升级

| 实现层关键主题 | 描述 |
|---------------|------|
| **服务网格 (Service Mesh)** | R2S 价值流的服务消费基础设施 |
| **可观测性 (Observability)** | D2C 价值流的监控告警统一平台 |
| **GitOps** | P2D 价值流的持续部署模式 |
| **多云/混合云** | 实现层的部署模式选择 |
| **AIOps** | D2C 价值流的智能告警与根因分析 |
| **平台工程 (Platform Engineering)** | 内部开发者平台 (IDP)，支撑 R2S 与 P2D |

> 📌 **记忆口诀**：**"信息层定数据、功能层定行为、集成层定协议、实现层定工具"**。

---

## 五、组件与价值流的对应关系

| 功能组件 | 主要价值流 | 支撑价值流 | 备注 |
|---------|:---------:|:---------:|------|
| Strategy | 贯穿 | - | 顶层 |
| Governance | 贯穿 | - | 横切 |
| Demand | R2F | - | R2F 入口 |
| Portfolio | R2F | - | R2F 中期 |
| Catalog | R2S | R2F | 服务登记/查询 |
| Requirement | R2F | P2D | R2F 规格化 |
| Design | R2F | P2D | R2F 设计 → P2D 实施 |
| Transition | P2D | - | P2D 核心 |
| Operation | R2S | D2C | R2S + D2C 双支撑 |
| Incident | D2C | R2S | D2C 核心 |

---

## 六、IT4IT vs ITIL vs COBIT vs DevOps：何时用哪个？

> 📌 **为什么写这一节**：企业 IT 治理领域有 4 大"通用名词"——IT4IT、ITIL、COBIT、DevOps，但**它们不互斥也不重叠**，常见误区是"二选一"或"混为一谈"。本节给出一张"适用场景决策表"。

### 6.1 四者定位对比

| 框架 | 性质 | 关注层 | 维护方 | 最新版本 | 输出物 |
|------|------|--------|--------|----------|--------|
| **IT4IT** | 参考架构（Reference Architecture） | IT 运营层 | The Open Group | 3.0（2024） | 价值流、功能组件、数据对象 |
| **ITIL** | 最佳实践（Best Practice） | ITSM 流程层 | Axelos / PeopleCert | ITIL 4（2019） | 34 个管理实践、服务价值系统 |
| **COBIT** | 治理框架（Governance Framework） | IT 治理 + 控制层 | ISACA | COBIT 2019 | 治理目标、流程、控制目标 |
| **DevOps** | 工程文化 + 实践 | 研发工程层 | Linux Foundation / CNCF | 持续演进（无版本号） | CI/CD、监控、协作文化 |

### 6.2 ❌ 误区 vs ✅ 正确用法

| ❌ 常见误区 | ✅ 正确理解 |
|------------|------------|
| ❌ **"IT4IT 是 ITIL 的替代品"** | ✅ IT4IT 是**架构层**（参考架构），ITIL 是**流程层**（最佳实践）；两者是 Open Group 与 Axelos 的互补标准，IT4IT 3.0 显式参考 ITIL 4 的实践 |
| ❌ **"用了 ITIL 4 就不用 IT4IT"** | ✅ ITIL 4 关注"做什么流程"（如事件管理、变更管理），IT4IT 关注"流程如何衔接 + 数据如何流转"——IT4IT 是 ITIL 的"骨架补完" |
| ❌ **"COBIT 和 IT4IT 重复了"** | ✅ COBIT 是**治理层**（谁有权做什么决策、合规如何达成），IT4IT 是**运营层**（决策后具体怎么执行）；COBIT 管"该不该做"，IT4IT 管"怎么做" |
| ❌ **"DevOps 能替代 IT4IT"** | ✅ DevOps 是**工程实践**（CI/CD、SRE、自动化），IT4IT 是**架构骨架**（4 价值流）；DevOps 是 IT4IT 中 P2D 价值流的**主要实现方式**，不是替代 |
| ❌ **"上 IT4IT = 抛弃 ITIL 4 流程文档"** | ✅ IT4IT 的功能组件可以直接**复用** ITIL 4 的 34 个实践作为内部活动——IT4IT 3.0 文档明确推荐这种组合 |
| ❌ **"DevOps = 工具栈（Jenkins/K8s/Docker）"** | ✅ DevOps 是**文化 + 流程 + 工具**三位一体；工具只是载体，核心是"开发与运维的协作方式"——这恰是 IT4IT P2D 价值流要打通的事 |

### 6.3 适用场景决策表

| 你的场景 | 推荐组合 | 理由 |
|---------|---------|------|
| **新公司搭建 IT 部门骨架** | **IT4IT 3.0 + ITIL 4** | IT4IT 给"4 价值流 + 9 组件"骨架，ITIL 4 给每个组件内的具体实践 |
| **上市公司，需合规审计** | **COBIT 2019 + IT4IT 3.0** | COBIT 满足"治理 + 控制 + 合规"硬要求，IT4IT 提供运营层落地 |
| **互联网产品研发为主** | **IT4IT 3.0 + DevOps** | IT4IT 的 P2D 价值流天然契合 CI/CD；DevOps 是 P2D 的主要实现方式 |
| **传统企业（金融/制造）转型** | **ITIL 4 + IT4IT 3.0 + COBIT** | ITIL 4 流程成熟、COBIT 合规可控、IT4IT 提供端到端追溯 |
| **创业公司（< 50 人）** | **DevOps 即可** | 团队小、流程轻，IT4IT/ITIL/COBIT 都太重；先把 DevOps 文化做扎实 |
| **云原生 + 微服务架构** | **IT4IT 3.0 + DevOps + DDD** | IT4IT 的 Service Backbone 对应微服务的服务治理，DDD 提供业务边界 |
| **多云/混合云治理** | **IT4IT 3.0 + Cloud Center of Excellence** | IT4IT Implementation Layer 显式支持多云 |

> 📌 **一句话总结**：**COBIT 管"该不该做"，IT4IT 管"怎么做 + 数据怎么流"，ITIL 管"流程细节"，DevOps 管"工程实现"**。成熟 IT 部门往往四者**叠加使用**，而非二选一。

---

## 七、本章小结

1. **9 大功能组件 = IT 部门的"职能图"**：Strategy / Governance / Demand / Portfolio / Catalog / Requirement / Design / Transition / Operation / Incident
2. **18 个数据对象 = 价值流之间的"资产"**：每条价值流的"流动的血液"是数据对象；ServiceDefinition 是 R2S 的"心脏"
3. **4 层参考架构 = "自上而下看 IT"**：信息层 → 功能层 → 集成层 → 实现层
4. **组件 + 数据对象 + 参考架构** = IT4IT 的完整结构
5. **核心创新是 Service Backbone**：打通所有数据对象的 ID 关联，实现全链路双向追溯
6. **与 ITIL/COBIT/DevOps 不互斥**：四者是治理/架构/流程/工程的不同切面，成熟企业往往**叠加使用**

---

## 八、章节思考

1. **你的 Service Definition 实体能否反查 SLA？** 试着用 Spring Data JPA 写一个 `findBySloThresholdGreaterThanEqual(99.95)`，看看目录查询能不能直接过滤"高可用服务"。
2. **R2F 9 阶段在你的团队里有几步是断的？** 例如 PMO 排序是否真的按"价值×差距"打分，还是"老板拍板"。
3. **四框架决策**：你的公司在用 ITIL 4、COBIT 2019、IT4IT 3.0、DevOps 中的哪几个？是叠加还是二选一？
4. **数据对象 ID 贯通**：Service Definition 与 Incident 是否能双向追溯？故障发生时能否在 5 分钟内定位"哪个服务被影响"？

---

## 📂 相关章节

- ⬅️ [返回 IT4IT 目录](README.md)
- ⬅️ [上一篇：第一章 价值流：从请求到服务的 4 条路](value-streams.md)
- ➡️ [下一篇：第三章 落地：IT4IT × ITIL × DevOps](in-practice.md)
- [企业架构 TOGAF 10](../togaf/README.md) — Governance 组件对应 TOGAF 第四章"架构治理"
- [架构描述语言 ArchiMate 3.2](../archimate/README.md) — IT4IT 数据对象可用 ArchiMate "Data Object" 视点表达
- [领域驱动设计 DDD](../ddd/README.md) — Catalog 服务的内部建模（聚合根 = ServiceDefinition）
- [微服务架构](../microservices/README.md) — R2S 价值流的服务消费 ≈ 微服务的服务注册与发现
- [面向对象设计 OOD](../ood/README.md) — ServiceDefinition 实体类的字段切分依据 SOLID 原则

## 📖 外部参考

- [The Open Group IT4IT 官方页](https://www.opengroup.org/it4it-forum)
- [IT4IT 3.0 规范下载](https://pubs.opengroup.org/it4it/it4it-v3-doc/)
- [IT4IT Service Backbone 解读](https://pubs.opengroup.org/it4it/it4it-v3-doc/) — 数据对象 ID 贯通的官方定义
- [ITIL 4 与 IT4IT 关系白皮书](https://pubs.opengroup.org/it4it/it4it-vs-itil/)
- [COBIT 2019 框架概览](https://www.isaca.org/resources/cobit)

---

> ➡️ 下一篇：[第三章：落地：IT4IT × ITIL × DevOps](in-practice.md)

## 反向链

- [business-capability](../togaf/business-capability.md)

← [返回 IT4IT 目录](README.md) | ← [返回系统设计基础](../README.md)

<!-- TODO: 拆分候选 (610 行 / 12 个 H2，超 500+8 阈值） -->
