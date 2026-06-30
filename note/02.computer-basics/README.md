<!--
module:
  number: 02
  slug: computer-basics
  topic: 计算机基础
  audience: 工程师 / SRE
  category: 主模块
  summary: 系统性整理计算机科学基础知识，涵盖网络、算法、系统运维、知识产权等核心领域。
-->

# 计算机基础

> 系统性整理计算机科学基础知识，涵盖网络、算法、系统运维、知识产权等核心领域。

---

## 目录导航

| 模块 | 内容 | 说明 |
|------|------|------|
| [01-网络](01-network/) | OSI/TCP/IP 模型 · 协议族 · HTTP 演进 · WCAG | 计算机网络体系结构与核心协议 |
| [02-算法](02-algorithms/) | 算法概述 · 时间/空间复杂度 · 取舍策略 | 算法基础理论与分析方法 |
| [03-Linux](03-linux/) | 常用命令 · curl 详解 | Linux 服务器管理与网络工具 |
| [04-运维](04-operations/) | 服务器性能指标 · 云服务模式 | 系统监控与云计算架构 |
| [05-知识产权](05-ipr/) | 专利 vs 软件著作权 | 技术成果保护策略 |

---

## 知识脉络

```mermaid
graph TB
    Base["计算机基础"]
    Base --> Net["01 网络<br/>OSI/TCP/IP · HTTP 演进"]
    Base --> Algo["02 算法<br/>复杂度分析 · 取舍策略"]
    Base --> Linux["03 Linux<br/>常用命令 · curl"]
    Base --> Ops["04 运维<br/>性能指标 · 云服务"]
    Base --> IPR["05 知识产权<br/>专利 vs 软著"]

    Net --> P["协议族<br/>IP/TCP/UDP/HTTP"]
    Algo --> A["算法基础<br/>时间/空间复杂度"]
    Linux --> L["服务器管理<br/>系统/文件/进程"]
    Ops --> O["监控与云<br/>IaaS/PaaS/SaaS"]
```

## 速查表

| 概念 | 核心要点 | 典型场景 |
|------|---------|---------|
| **OSI 七层** | 物理→数据链路→网络→传输→会话→表示→应用 | 网络故障分层排查 |
| **TCP/IP 四层** | 网络接口→网际→传输→应用 | 实际互联网通信 |
| **TCP 三次握手** | SYN → SYN+ACK → ACK，建立可靠连接 | HTTP 连接建立 |
| **TCP 四次挥手** | FIN → ACK → FIN → ACK，TIME_WAIT 2MSL | 连接释放 |
| **HTTP vs HTTPS** | HTTPS = HTTP + TLS，端口 443 vs 80 | 安全传输 |
| **HTTP/2 特性** | 多路复用、头部压缩、服务器推送 | 高性能 Web |
| **HTTP/3 (QUIC)** | 基于 UDP，0-RTT，解决队头阻塞 | 移动端弱网 |
| **时间复杂度** | O(1) < O(log n) < O(n) < O(n log n) < O(n²) | 算法效率评估 |
| **Linux 权限** | rwx (4+2+1)，chmod/chown/ugo | 文件安全 |
| **IaaS/PaaS/SaaS** | 基础设施/平台/软件即服务 | 云服务选型 |

## 学习路径

- **基础必修**：网络 → 算法 → Linux
- **运维方向**：Linux → 运维 → 网络（深入协议）
- **速查定位**：按需查阅各模块

## 相关章节

- 上游：本模块是所有技术模块的基础
- 关联：[`04.system-design`](../04.system-design/) — 系统设计（网络/运维知识的上层应用）
- 关联：[`05.tools`](../05.tools/) — 工具链（Git/Docker/Nginx 等实操工具）

---

← [返回笔记目录](../README.md)
