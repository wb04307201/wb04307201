# 高可用篇

> 高可用(High Availability)指系统在面对各种异常和故障时，仍能持续提供服务的能力。本模块涵盖流量控制、容错机制、冗余架构等关键主题。

## 流量控制

1. [限流](rate-limiting/README.md) — 固定窗口/滑动窗口/漏桶/令牌桶算法
2. [熔断](circuit-break/README.md) — Closed/Open/Half-Open 三态状态机
3. [重试](retry/README.md) — 重试策略与退避算法
4. [超时控制](timeout/README.md) — 超时设置与级联超时
5. [服务降级](service-degradation/README.md) — 降级策略与降级开关

## 冗余与容灾

6. [冗余设计](redundancy-design/README.md) — [集群部署](redundancy-design/cluster/README.md) | [多活架构](redundancy-design/multi-site-active-active/README.md)
7. [弹性架构](elastic-architecture/README.md) — 自动扩缩容与弹性设计
8. [混沌工程](chaos-engineering/README.md) — Chaos Mesh/故障注入/容灾演练 🆕

## 质量保障

9. [代码质量](code-quality/README.md) — [28 原则](code-quality/28/README.md)
