<!--
module:
  parent: workflow
  slug: workflow/eventmesh-cloud-flow
  type: article
  category: 主模块子文章
  summary: EventMesh 云流程
-->

# EventMesh 云流程

> Apache EventMesh 在工作流/云流程场景的架构图与可视化资料

---
## 引言：架构困境

EventMesh 云流程 的关键不是'选型'——是**选完之后怎么在 5 个 trade-off 里活下来**。

本篇用'决策困境'切入，比较几种主流路径并讲清取舍。

---

## 导航

| 序号 | 主题 | 核心内容 |
|------|------|---------|
| 1 | [EventMesh 云流程架构图](#1-eventmesh-云流程架构图) | Parallel + 视频转音频/封面生成/码率转换 三分支 |

| 2 | [事件网格与业务流程集成图](#2-事件网格与业务流程集成图) | 云工作流 + FC/MNS/ECS/VOD/FNF 编排 |

| 3 | [Serverless Workflow DSL 执行流程图](#3-serverless-workflow-dsl-执行流程图) | 业务消息分组 + OSS 写入 + 压缩分支 |


---

## 知识脉络

```mermaid
graph TB
    A[EventMesh 云流程] --> B[事件网格基础设施]
    A --> C[Serverless Workflow 标准]

    B --> B1[Runtime 节点<br/>事件传输 + 工作流执行]
    B --> B2[Connector 插件<br/>Kafka/RocketMQ/Pulsar 适配]
    B --> B3[Protocol 插件<br/>CloudEvents/MQTT 协议]

    C --> C1[事件触发 State]
    C --> C2[操作 State]
    C --> C3[决策 Switch State]
```

## 阅读说明

本目录存放 **Apache EventMesh 在云流程场景的可视化架构图**，配套内容见：

- 理论 + 实战：[`事件驱动与 Serverless Workflow`](../README.md)
- 12306 案例：同上文 §五 含 EventMesh 架构图

## 核心概念

| 概念 | 一句话定义 |
|------|----------|
| **EventMesh** | 事件网格基础设施，连接 Producer/Consumer 与后端消息中间件 |
| **CloudEvents** | CNCF 事件格式标准，跨云/跨引擎可移植 |
| **Serverless Workflow** | CNCF YAML/JSON DSL 标准，事件驱动 + 函数编排 |
| **Runtime** | EventMesh 核心 Mesh 节点，事件传输 + Serverless Workflow DSL 执行 |

---

## 1. EventMesh 云流程架构图

Parallel 编排器触发 3 条并行分支：视频转音频 / 视频封面生成 / 视频码率转换，最终汇聚到 HTTP 后端。

```mermaid
flowchart TB
    Start([START]) --> Parallel{Parallel<br/>ParallelState}

    Parallel --> BranchA[视频转音频]
    Parallel --> BranchB[视频封面生成]
    Parallel --> BranchC[视频码率转换]

    BranchA --> A1[FC: Video2Audio<br/>InvokeFunction]
    A1 --> A2[AI: Intelligent Speech Sensoring<br/>AISpeechRecognition]
    A2 --> A3[MNS: Send Notification<br/>MNSSendMessage]
    A3 --> A4[FC: Storage Database<br/>InvokeFunction]

    BranchB --> Choice1{Thumbnail Choice<br/>Choice}
    Choice1 -->|Default| B0[Pass]
    Choice1 -->|$input.data.state==true| B1[FC: Thumbnail Generation Server<br/>InvokeFunction]
    B1 --> B2[AI: Intelligent Image Sensoring<br/>AIImageRecognition]
    B2 --> B3[MNS: Send Notification<br/>MNSSendMessage]
    B3 --> B4[FC: Storage Database<br/>InvokeFunction]
    B0 --> End1
    B4 --> End1

    BranchC --> Choice2{Resolution Choice<br/>Choice}
    Choice2 -->|Default| C0[FC: Transcoding 320p<br/>InvokeFunction]
    Choice2 -->|transcoding==1080P| C1[FC: Transcoding 1080p<br/>InvokeFunction]
    Choice2 -->|transcoding==720P| C2[FC: Transcoding 720p<br/>InvokeFunction]
    C0 --> End2
    C1 --> C3[AI: Intelligent Video Sensoring<br/>AIImageRecognition]
    C2 --> End2
    C3 --> C4[MNS: Send Notification<br/>MNSSendMessage]
    C4 --> C5[FC: Storage Database<br/>InvokeFunction]
    C5 --> End2

    A4 --> SendToBackend
    End1 --> SendToBackend
    End2 --> SendToBackend
    SendToBackend[HTTP: Send to Backend Server<br/>HTTPRequest]
    SendToBackend --> End([END])
```

## 2. 事件网格与业务流程集成图

云工作流与 EventMesh 集成，自建机房/ECS VPC 通过 MNS 拉取任务，公共云 FC 调用 VOD/FNF 等服务。

```mermaid
flowchart LR
    subgraph VPC["自建机房 / ECS VPC"]
        ECS[ECS<br/>拉取任务/汇报结果]
        User[/人工审批<br/>FC Function/]
    end

    subgraph CloudEnv["公共云服务环境"]
        MNS[MNS 消息队列<br/>发送消息]
        subgraph Workflow["云工作流"]
            S1[Step_1 开始]
            S2[Step_2 调度]
            S3[Step_3]
            S4[Step_4]
            S5[Step_5]
            S6[Step_6 结束]
        end
        FC1[FC 任务]
        FC2[FC 视频点播任务]
        VOD[VOD 视频点播]
        FNF[FNF 执行子流程]
    end

    S1 -->|调用 FC 任务| FC1
    S2 --> S3
    S2 --> S4
    S3 --> MNS
    MNS --> ECS
    ECS -->|汇报任务结果| S3
    S4 -->|触发视频点播任务| FC2
    FC2 --> VOD
    S4 --> S5
    S5 -->|执行子流程| FNF
    S5 --> S6
    S6 --> FC1
    FC1 --> User
    User -->|汇报任务结果| FC1
```

## 3. Serverless Workflow DSL 执行流程图

业务消息分组后写入 OSS，根据数据大小决策是否压缩。

```mermaid
flowchart TB
    Start([Start]) --> Group[业务消息分组<br/>FC:InvokeFunction]
    Group --> Iterate[迭代处理分组消息<br/>MapAnchor]
    Iterate --> OSS[消息数据写入OSS<br/>FC:InvokeFunction]
    OSS --> Choice{是否进行存储压缩<br/>Choice}
    Choice -->|object_size >= compress_threshold| Compress[存储数据块压缩<br/>FC:InvokeFunction]
    Choice -->|otherwise| Pass[不做动作<br/>Pass]
    Compress --> End1
    Pass --> End1
    End1 --> End([End])
```

---

## 相关章节

- 上游：[`事件驱动与 Serverless Workflow`](../README.md) — BPMN + 事件驱动融合
- 上游：[`07 工作流`](../../README.md) — 工作流顶层
- 关联：[`微服务编排`](../../workflow-and-microservice-orchestration/README.md) — 编舞 vs 编排
- 关联：[`流程引擎`](../../process-engine/README.md) — Camunda 7/8 / Zeebe

---

> 提示：本目录以 Mermaid 图表为主，建议结合 [事件驱动 README](../README.md) 的 §三 Apache EventMesh 与 §五 12306 案例一起阅读
