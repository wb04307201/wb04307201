<!--
module:
  parent: computer-basics
  slug: computer-basics/tcp-ip-model
  type: article
  category: 主模块子文章
  summary: TCP/IP 是互联网的**事实标准**，由 DARPA 于 20 世纪 70 年代开发，1983 年成为互联网标准。采用四层结构，强调**端到端**通信理念。
-->

# TCP/IP 四层模型

> TCP/IP 是互联网的**事实标准**，由 DARPA 于 20 世纪 70 年代开发，1983 年成为互联网标准。采用四层结构，强调**端到端**通信理念。

---
---

## 四层架构

```text
┌─────────────────────────────────────────────────┐
│ 应用层        HTTP/HTTPS/DNS/FTP/SMTP/SSH        │  消息
│ 传输层        TCP（可靠）/ UDP（快速）             │  段/数据报
│ 网络层        IP/ICMP/IGMP + OSPF/BGP/NAT        │  数据包
│ 链路层        Ethernet/WiFi/PPP + ARP            │  帧
└──────────────────────────────────────────────────┘
```

### 1. 链路层（Link Layer）
- **职责** — 物理网络硬件数据传输，帧封装/解封装，MAC 寻址，CRC 错误检测
- **数据单元** — 帧（Frame）
- **核心协议** — Ethernet、PPP、WiFi（802.11）、ARP（IP→MAC 映射）
- **设备** — 网卡、网桥、二层交换机

### 2. 网络层（Internet Layer）
- **职责** — 跨网络路由与转发，IP 逻辑寻址
- **数据单元** — 数据包（Packet）
- **核心协议** — IP（无连接/不可靠）、ICMP（网络诊断）、IGMP（组播）
- **关键技术** — 子网划分、NAT、路由算法（OSPF/BGP）
- **设备** — 路由器、三层交换机

### 3. 传输层（Transport Layer）
- **职责** — 端到端通信服务，端口号区分进程
- **数据单元** — TCP 段（Segment）/ UDP 数据报（Datagram）

| 特性 | TCP | UDP |
|------|-----|-----|
| 连接方式 | 面向连接（三次握手） | 无连接 |
| 可靠性 | 确认/重传/排序/流量控制 | 不保证 |
| 头部大小 | 20 字节+ | 8 字节 |
| 典型场景 | 网页/邮件/文件下载 | 视频直播/DNS/游戏 |

### 4. 应用层（Application Layer）
- **职责** — 面向用户的网络服务接口
- **数据单元** — 消息（Message）
- **常见协议** — HTTP/HTTPS、FTP、SMTP/POP3、DNS、DHCP、SSH

---

## 数据封装过程

```text
应用数据
  ↓ + TCP/UDP 头部（源端口 + 目的端口）
传输层段
  ↓ + IP 头部（源IP + 目的IP）
网络层数据包
  ↓ + 帧头部（源MAC + 目的MAC）+ CRC尾部
链路层帧
  ↓ 转换为电信号/光信号
物理介质传输
```

接收端则**从下向上逐层解封装**，剥离各层头部信息。

---

## 核心设计原则

| 原则 | 说明 |
|------|------|
| **端到端** | 复杂功能由端系统实现，网络核心只做快速转发 |
| **分层独立** | 各层可独立替换（如 IPv4 → IPv6） |
| **开放标准** | 协议公开，跨平台/跨厂商互联 |
| **可扩展** | 支持新协议无缝接入（如 HTTP/3 基于 QUIC） |

## 与 OSI 的对比总结

| 维度 | OSI 模型 | TCP/IP 模型 |
|------|---------|------------|
| 层数 | 7 层 | 4 层 |
| 定位 | 理论参考框架 | 实际互联网标准 |
| 上层处理 | 会话层/表示层独立 | 合并到应用层 |
| 下层处理 | 物理层/数据链路层独立 | 合并到链路层 |
| 实用性 | 教学/分析价值高 | 工程实现基础 |

---

**深入学习：** [核心协议详解](../protocols/) · [OSI 七层模型](../osi-model/)

---

**相关面试题**：[`TCP 三次握手四次挥手`](../../../13.split-hairs/02.computer-basics/tcp-handshake-teardown/README.md) — 状态机 + TIME_WAIT/CLOSE_WAIT 排查

← [返回 计算机网络](../README.md)

## 边界情况补充：网络层异常

| 异常 | 触发条件 | 默认行为 | 故障排查命令 |
|------|----------|----------|-------------|
| **MTU 分片** | IP 包 > 链路 MTU（通常 1500B） | 自动分片（IPv4），发送 ICMP Fragmentation Needed（IPv6 无分片） | `ping -M do -s 1500 <dst>` 测试路径 MTU |
| **TTL=0** | 包经过 N 跳路由后 TTL 减为 0 | 路由器丢弃包 + 发送 ICMP Time Exceeded | `traceroute <dst>` 跟踪路径 |
| **SYN Flood** | 大量半开连接占满 SYN backlog | TCP backlog 满后丢弃新 SYN | `netstat -s \| grep SYNs` 看 dropped |
| **ICMP Redirect** | 路由器发现更优路径 | 主机更新路由表 + ICMP 通知原路由器 | `sysctl net.ipv4.conf.all.accept_redirects` |
| **Port Unreachable** | UDP 目标端口无服务 | 发送 ICMP Port Unreachable 给源 | `tcpdump icmp` 抓包验证 |

## TCP 握手 RTT 量化对比

| 场景 | RTT | 握手时间（3-way） | 数据传输开始时间 |
|------|-----|------------------|------------------|
| 同机房（同 pod 互通） | ~0.5 ms | ~1 ms | 1 ms |
| 同城 IDC（光纤 5 km） | ~0.1 ms | ~0.3 ms | 0.3 ms |
| 跨城 BGP（200 km） | ~2 ms | ~6 ms | 6 ms |
| 跨国海底光缆（8000 km） | ~80 ms | ~240 ms | 240 ms |
| 卫星（LEO 800 km） | ~5 ms | ~15 ms | 15 ms |
| 卫星（GEO 36000 km） | ~240 ms | ~720 ms | 720 ms |

**关键启示**：
- 跨城应用**3-way 握手已占首屏 6ms**，对延迟敏感 API 应启用 TCP Fast Open (TFO) 减少 1 RTT
- 跨国应用**首次请求 720ms GEO 卫星**，应使用 CDN 或边缘计算
- TCP 重传超时 (RTO) 至少 = SRTT + 4*RTTVAR，跨城场景重传代价高
