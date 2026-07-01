# 06 集成组件

> 最后更新: 2026-06-14
> ⬅️ [返回 Spring 顶层](../README.md)

---
## 引言：反直觉代码

06 集成组件 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 🎯 一句话定位

**Spring 集成组件 = 业务级 Spring 子项目**——解决特定业务场景（校验/重试/状态机/批处理）的独立框架，本章讲清"什么场景用什么、怎么用、关键点"。

---

## 📚 章节导航

| 组件 | 文件 | 适用场景 | 建议时长 |
|:----:|:----|:---------|:--------:|
| **Validation 校验** | [validation/](validation/) | Controller/Service 参数校验 | 25 min |
| ├─ 注解与使用 | [annotations-and-usage.md](validation/annotations-and-usage.md) | JSR-303/380 注解、Hibernate Validator | 15 min |
| ├─ 自定义验证器 | [custom-validator.md](validation/custom-validator.md) | 自定义业务规则注解 | 15 min |
| └─ 跨字段校验 | [cross-field.md](validation/cross-field.md) | 多字段组合、容器元素校验 | 10 min |
| **Retry 重试** | [retry.md](retry.md) | 瞬时故障自动重试（网络/数据库） | 20 min |
| **StateMachine 状态机** | [statemachine.md](statemachine.md) | 复杂状态流转（订单/工作流/设备控制） | 25 min |
| **Batch 批处理** | [batch.md](batch.md) | 数据迁移/ETL/定时报表（含分区并行） | 40 min |

---

## 🧭 选型速查

| 业务问题 | 推荐组件 | 理由 |
|:---------|:---------|:-----|
| 参数校验 | Validation | JSR-303 标准，注解驱动 |
| 瞬时故障 | Retry | 声明式 + 多种退避策略 |
| 订单/工作流 | StateMachine | 状态流转可配置、可视化 |
| 大数据量导入 | Batch | 支持分区并行、错误恢复 |

---

## ⚡ 核心概念速查

| 概念 | 一句话定义 | 章节 |
|------|----------|:----:|
| **@Valid / @Validated** | 触发参数校验的注解 | [校验](validation/annotations-and-usage.md) |
| **@NotNull / @NotBlank** | 基础校验注解 | [校验](validation/annotations-and-usage.md) |
| **@Retryable** | 声明式重试注解 | [重试](retry.md) |
| **@Recover** | 重试失败后的兜底方法 | [重试](retry.md) |
| **State / Event / Transition** | 状态机的三要素 | [状态机](statemachine.md) |
| **Guard / Action** | 转换的条件判断与副作用 | [状态机](statemachine.md) |
| **Job / Step** | 批处理的任务与步骤 | [批处理](batch.md) |
| **ItemReader / Processor / Writer** | 批处理的三段式数据流 | [批处理](batch.md) |
| **Partition** | 批处理分区并行（大数据量） | [批处理](batch.md) |

---

## 🤔 思考

1. **@Valid 和 @Validated 区别？** @Valid (JSR-303) 不支持分组；@Validated (Spring) 支持分组。
2. **重试和熔断的区别？** 重试是"再试一次"，熔断是"试太多次后放弃"。
3. **什么时候用状态机？** 状态 ≥ 4 个、转换规则复杂、需可视化/审计的业务流。
4. **批处理和消息队列的区别？** 批处理适合"周期性大批量"，消息队列适合"实时小批量"。

---

## 相关章节

- ⬅️ [返回 Spring 顶层](../README.md)
- ⬅️ [01 核心容器](../01-core/README.md) — 集成组件都基于 IoC/AOP
- ⬅️ [02 Web 层](../02-web/README.md) — Validation 大量用于 Controller
- ➡️ [07 可观测性](../07-observability/README.md) — Batch 监控指标接入 Micrometer/Actuator
- [08 注解速查](../08-annotations/README.md) — 相关注解索引

---

> 🚀 从 [Validation 校验](validation/annotations-and-usage.md) 开始
