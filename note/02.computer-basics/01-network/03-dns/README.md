<!--
module:
  parent: computer-basics
  slug: computer-basics/03-dns
  type: article
  category: 主模块子文章
  summary: 一份按层次梳理的 DNS 速查手册：从根域名服务器到 DNS-over-HTTPS 的完整知识体系。
-->

# DNS 协议：从域名解析到 DNS 安全完整实战

> 一份按层次梳理的 DNS 速查手册：从根域名服务器到 DNS-over-HTTPS 的完整知识体系。

---
## 引言：生产 Bug

DNS 协议：从域名解析到 DNS 安全完整实战 的关键不是'防住'——是**出事后 5 分钟内能定位**。

本篇用真实生产场景切入：线上怎么炸、按官方文档写为什么也会错、怎么止血。

---

## 一、DNS 是什么？

DNS（Domain Name System，域名系统）是互联网的"电话簿"，把人类可读的域名（www.example.com）转换为机器可读的 IP 地址（93.184.216.34）。

```text
用户输入 www.example.com
   ↓
浏览器 → 操作系统 → 本地 DNS 服务器 → 根 DNS → .com DNS → example.com DNS
   ↓
返回 IP：93.184.216.34
   ↓
浏览器访问 IP
```

---

## 二、DNS 记录类型

| 类型 | 名称 | 说明 | 示例 |
|------|------|------|------|
| **A** | Address | 域名 → IPv4 | example.com → 93.184.216.34 |
| **AAAA** | IPv6 Address | 域名 → IPv6 | example.com → 2606:2800:220:1::1 |
| **CNAME** | Canonical Name | 域名别名 | www.example.com → example.com |
| **MX** | Mail Exchange | 邮件服务器 | example.com → mail.example.com |
| **NS** | Name Server | 域名服务器 | example.com → ns1.example.com |
| **TXT** | Text | 文本记录（SPF / DKIM / 验证）| v=spf1 include:_spf.google.com ~all |
| **SOA** | Start of Authority | 区域起始授权 | 主 DNS + 管理员邮箱 |
| **PTR** | Pointer | IP → 域名（反向解析）| 34.216.184.93.in-addr.arpa → example.com |
| **SRV** | Service | 服务定位 | _sip._tcp.example.com → sipserver.example.com:5060 |
| **CAA** | CA Authorization | 允许哪些 CA 签发证书 | example.com → 0 issue "letsencrypt.org" |

---

## 三、DNS 查询过程（递归 + 迭代）

### 3.1 完整流程

```text
① 浏览器查询本地 DNS（递归查询）
   ↓
② 本地 DNS 查询根 DNS 服务器（迭代查询）
   ↓ "我不知道 www.example.com，但 .com 在 192.5.6.30"
③ 查询 .com 顶级域 DNS
   ↓ "example.com 在 ns1.example.com"
④ 查询 example.com 权威 DNS
   ↓ "www.example.com 的 A 记录是 93.184.216.34"
⑤ 返回 IP 给浏览器
```

### 3.2 递归 vs 迭代

| 类型 | 客户端 → 本地 DNS | 本地 DNS → 根 / .com / 权威 |
|------|------------------|---------------------------|
| **递归查询** | 客户端要求"必须给我最终答案" | —— |
| **迭代查询** | —— | "我告诉你下一步去哪查" |

---

## 四、DNS 层级结构

```text
根域名（.）
   ↓
顶级域（.com / .org / .cn / .net ...）
   ↓
二级域（example.com）
   ↓
子域（www.example.com / mail.example.com）
   ↓
主机（www / mail / ftp）
```

| 层级 | 示例 | 管理方 |
|------|------|--------|
| **根域** | . | ICANN（13 台根服务器） |
| **顶级域** | .com / .cn | Verisign / CNNIC |
| **二级域** | example.com | 域名注册人 |
| **子域** | www.example.com | 企业 IT |

---

## 五、DNS 服务器类型

| 类型 | 作用 |
|------|------|
| **根 DNS 服务器** | 全球 13 台（A~M），管理 .com / .org 等 |
| **顶级域 DNS** | 管理 .com / .cn 等 |
| **权威 DNS** | 域名的"权威答案"（NS 记录指向） |
| **递归 DNS（本地 DNS）** | 帮客户端查询（缓存结果）|
| **权威 + 递归分离** | 生产推荐（BIND / CoreDNS）|

---

## 六、主流 DNS 软件

| 软件 | 特点 | 适用 |
|------|------|------|
| **BIND** | 老牌 / 功能强 / 配置复杂 | 传统 |
| **CoreDNS** | 云原生 / K8s 默认 / Go 编写 | K8s 集群 |
| **Unbound** | 专注递归 / 高性能 | 递归 DNS |
| **PowerDNS** | 数据库后端 / 适合大规模 | ISP |
| **dnsmasq** | 轻量级 / 嵌入式 | 小型网络 |
| **AdGuard Home** | 去广告 / 隐私 | 家庭 / 小团队 |

---

## 七、DNS 安全

### 7.1 常见攻击

| 攻击 | 说明 |
|------|------|
| **DNS 劫持** | 篡改 DNS 响应（路由器 / 运营商） |
| **DNS 投毒** | 伪造 DNS 响应（缓存污染） |
| **DNS 欺骗** | 钓鱼 + 仿冒域名 |
| **DNS DDoS** | UDP 洪水攻击 DNS 服务器 |
| **DNS 隧道** | 通过 DNS 协议传数据（绕过防火墙） |

### 7.2 DNSSEC（DNS 安全扩展）

- 用数字签名验证 DNS 响应真实性
- 防止 DNS 劫持 / 投毒
- 但部署率仍较低（< 30%）

### 7.3 DNS-over-HTTPS（DoH） / DNS-over-TLS（DoT）

```text
传统 DNS：明文 UDP/TCP（运营商可监听）
DoH (RFC 8484)：DNS over HTTPS（443 端口，TLS 加密）
DoT (RFC 7858)：DNS over TLS（853 端口）
```

| 协议 | 端口 | 特点 |
|------|------|------|
| DNS | 53 | 明文 |
| DoT | 853 | TLS 加密 |
| DoH | 443 | HTTPS 加密 + 难被防火墙识别 |

**支持**：Cloudflare `1.1.1.1` / Google `8.8.8.8` / Quad9 `9.9.9.9` 均支持 DoH/DoT。

---

## 八、DNS 性能优化

### 8.1 缓存策略

```text
浏览器缓存 → 操作系统缓存 → 本地 DNS 缓存 → 权威 DNS
   ↓             ↓              ↓                ↓
 几分钟        几分钟         几小时            真实数据
```

### 8.2 TTL 设置建议

| 记录类型 | TTL 建议 |
|---------|---------|
| A / AAAA | 5 分钟 - 24 小时 |
| CNAME | 与目标 A 记录一致 |
| MX | 1 - 12 小时 |
| NS | 24 - 48 小时 |

### 8.3 DNS 预取（DNS Prefetch）

```html
<!-- 提前解析页面中的外链 -->
<link rel="dns-prefetch" href="https://cdn.example.com">
<link rel="preconnect" href="https://cdn.example.com" crossorigin>
```

### 8.4 智能 DNS（GSLB）

```text
根据用户 IP 地理位置，返回最近服务器 IP
   ↓
北方用户 → 北京机房
南方用户 → 上海机房
海外用户 → 新加坡机房
```

实现：阿里云 DNS / 腾讯云 DNS / Cloudflare

---

## 九、CoreDNS 实战（K8s 默认）

### 9.1 K8s 中 DNS 工作原理

```text
Pod 内的 DNS 配置：
  nameserver 10.96.0.10          # CoreDNS Service IP
  search default.svc.cluster.local
  ndots: 5

Pod 查询 "my-service"：
   ↓
CoreDNS（K8s 默认 DNS）自动补全：
  my-service.default.svc.cluster.local → Service IP
```

### 9.2 CoreDNS 自定义

```yaml
# Corefile
.:53 {
  errors
  health {
    lameduck 5s
  }
  ready
  kubernetes cluster.local in-addr.arpa ip6.arpa {
    pods insecure
    fallthrough in-addr.arpa ip6.arpa
  }
  forward . 1.1.1.1
  cache 30
  loop
  reload
  loadbalance
}
```

---

## 十、命令速查

```bash
# 查询 A 记录
dig example.com
nslookup example.com
host example.com

# 指定 DNS 服务器
dig @8.8.8.8 example.com

# 查询 MX 记录
dig example.com MX

# 反向解析（IP → 域名）
dig -x 93.184.216.34

# 追踪 DNS 解析路径
dig +trace example.com

# 测试 DNS 响应时间
dig example.com | grep "Query time"
```

---

## 十一、最佳实践

1. **启用 DoH/DoT**：防止运营商监听 / 劫持
2. **多 DNS 备份**：主 DNS + 备用 DNS（如 1.1.1.1 + 8.8.8.8）
3. **DNS 缓存**：本地缓存 + CDN 缓存
4. **TTL 合理**：太短增加查询压力，太长变更不生效
5. **智能 DNS**：跨地域业务必备
6. **DNS 监控**：解析失败告警（业务受损前发现）
7. **DNSSEC**：政府 / 金融必启用
8. **避免 DNS 隧道**：防火墙拦截异常 DNS 流量

---

← [返回计算机网络](../README.md) · 📅 2026-06-28