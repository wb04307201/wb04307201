<!--
module:
  parent: computer-basics
  slug: computer-basics/04-https-tls
  type: article
  category: 主模块子文章
  summary: 一份按层次梳理的 HTTPS/TLS 速查手册：从对称加密到 TLS 1.3 握手的完整实战。
-->

# HTTPS 与 TLS 1.3：加密传输的完整机制

> 一份按层次梳理的 HTTPS/TLS 速查手册：从对称加密到 TLS 1.3 握手的完整实战。

---
## 引言：生产 Bug

HTTPS 与 TLS 1.3：加密传输的完整机制 的关键不是'防住'——是**出事后 5 分钟内能定位**。

本篇用真实生产场景切入：线上怎么炸、按官方文档写为什么也会错、怎么止血。

---

## 一、HTTPS = HTTP + TLS

HTTPS = HTTP over TLS/SSL，通过 TLS（Transport Layer Security）协议加密 HTTP 流量。

```
HTTP：   客户端 ←明文→ 服务端     ← 中间人可窃听
HTTPS：  客户端 ←密文→ 服务端     ← 中间人看不懂
```

---

## 二、对称加密 vs 非对称加密

| 类型 | 密钥 | 速度 | 用途 |
|------|------|------|------|
| **对称加密** | 加密解密用同一把密钥 | ⚡ 快（百倍）| 加密大量数据 |
| **非对称加密** | 公钥 + 私钥 | 🐌 慢 | 密钥交换 / 数字签名 |

**混合方案**：
1. 非对称加密传输"对称密钥"
2. 对称密钥加密实际数据

这样既安全又快。

### 常见算法

| 类型 | 算法 | 特点 |
|------|------|------|
| **对称** | AES / ChaCha20 | AES 主流 / ChaCha20 移动端 |
| **非对称** | RSA / ECC（椭圆曲线）| ECC 更快 + 密钥短 |
| **哈希** | SHA-256 / SHA-3 | 数据完整性 |

---

## 三、TLS 1.2 vs TLS 1.3 握手

### 3.1 TLS 1.2 握手（2 RTT）

```
客户端                                服务端
  │  ① ClientHello（支持的加密套件）    →
  │  ← ② ServerHello + Certificate + ServerHelloDone
  │  ③ Key Exchange（Pre-master Secret） →
  │  ← ④ Finished
  └───── 加密通道建立 ─────┘
```

**问题**：2 RTT（往返延迟）= 100-200ms 额外延迟。

### 3.2 TLS 1.3 握手（1-RTT + 0-RTT）

```
客户端                                服务端
  │  ① ClientHello + Key Share（提前带）  →
  │  ← ② ServerHello + Key Share + Certificate + Finished
  └───── 加密通道建立（1 RTT） ────┘

再次连接（0-RTT）：
  │  ClientHello + 早期数据  →
  └───── 0 RTT 握手 ─────┘
```

**改进**：
- 1-RTT（首次）：减半延迟
- 0-RTT（再次）：首次请求即可发数据

### 3.3 TLS 1.3 删除的不安全算法

| TLS 1.2 支持 | TLS 1.3 删除 |
|--------------|------------|
| ✅ RSA 密钥交换 | ❌ 删（用 ECDHE） |
| ✅ CBC 模式 | ❌ 删（只保留 AEAD） |
| ✅ MD5 / SHA-1 哈希 | ❌ 删 |
| ✅ RC4 流密码 | ❌ 删 |

---

## 四、TLS 1.3 加密套件

TLS 1.3 只支持 AEAD（带认证的加密）：

```
TLS_AES_256_GCM_SHA384          ← 主流推荐
TLS_CHACHA20_POLY1305_SHA256    ← ARM 移动端
TLS_AES_128_GCM_SHA256         ← 性能优先
```

**格式**：`TLS_<密钥交换>_<加密算法>_<哈希>`

---

## 五、数字证书

### 5.1 证书结构

```
┌─────────────────────────────────────┐
│  Version（版本）                       │
├─────────────────────────────────────┤
│  Serial Number（序列号）              │
├─────────────────────────────────────┤
│  Subject（主体：域名 / 组织）         │
├─────────────────────────────────────┤
│  Issuer（签发者：CA 名称）            │
├─────────────────────────────────────┤
│  Validity（有效期）                   │
│   Not Before: 2026-01-01            │
│   Not After:  2027-01-01            │
├─────────────────────────────────────┤
│  Public Key（公钥）                   │
├─────────────────────────────────────┤
│  Signature Algorithm（签名算法）       │
├─────────────────────────────────────┤
│  Signature（CA 的数字签名）           │
└─────────────────────────────────────┘
```

### 5.2 证书层级（CA 信任链）

```
根 CA（Root CA）
   ├─ 中间 CA（Intermediate CA）
   │    ├─ example.com 证书
   │    └─ other.com 证书
   └─ 其他中间 CA
```

- **根 CA**：操作系统 / 浏览器预装（信任锚）
- **中间 CA**：跨中间人签发（隔离风险）
- **叶子证书**：用户实际使用的证书

---

## 六、Let's Encrypt 免费证书

### 6.1 安装 certbot

```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# 申请证书（自动配 Nginx）
sudo certbot --nginx -d example.com -d www.example.com

# 申请证书（手动）
sudo certbot certonly --standalone -d example.com
```

### 6.2 自动续期

```bash
# 测试自动续期
sudo certbot renew --dry-run

# 添加 cron 任务（每月 1 号检查）
0 0 1 * * sudo certbot renew --quiet
```

### 6.3 DNS 验证（泛域名证书）

```bash
# 用 acme-dns / certbot-dns-cloudflare / certbot-dns-aliyun
sudo certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials ~/.secrets/cloudflare.ini \
  -d example.com -d "*.example.com"
```

**优势**：泛域名证书（`*.example.com`）覆盖所有子域名。

---

## 七、HTTPS 配置实战

### 7.1 Nginx

```nginx
server {
  listen 443 ssl http2;
  server_name example.com;

  ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

  ssl_protocols       TLSv1.2 TLSv1.3;
  ssl_ciphers         HIGH:!aNULL:!MD5;
  ssl_prefer_server_ciphers on;
  ssl_session_cache shared:SSL:10m;
  ssl_session_timeout 1d;
  ssl_session_tickets off;

  # HSTS（强制 HTTPS）
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

  # OCSP Stapling
  ssl_stapling on;
  ssl_stapling_verify on;
}
```

### 7.2 Spring Boot

```yaml
# application.yml
server:
  ssl:
    enabled: true
    key-store: classpath:keystore.p12
    key-store-password: changeit
    key-store-type: PKCS12
    key-alias: tomcat
```

### 7.3 内网 HTTPS（私有 CA）

```bash
# 1. 创建私有 CA
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt

# 2. 服务端证书
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365

# 3. 客户端信任私有 CA
# 把 ca.crt 导入客户端的受信任根证书
```

---

## 八、性能优化

### 8.1 TLS False Start

- TLS 1.3 引入 0-RTT，首个请求可立即发送
- 比 TLS 1.2 节省 1 RTT

### 8.2 Session Resumption（会话恢复）

```
首次连接：完整握手（1 RTT）
再次连接：
  ├── Session ID（服务端缓存）
  └── Session Ticket（客户端缓存，扩展性更好）
```

### 8.3 OCSP Stapling

```
传统：客户端 → 查询 CA 的 OCSP 服务器 → 验证证书状态（额外延迟）
Stapling：服务端定期查询 OCSP → 把结果"装订"在 TLS 握手响应里
  → 客户端零额外查询
```

### 8.4 TLS 1.3 0-RTT

```http
# 客户端在第一个请求里就可以发数据
GET / HTTP/1.1
Early-Data: 1
```

**风险**：0-RTT 数据可能被重放攻击，**不要用于非幂等请求**。

---

## 九、TLS 在云原生时代的演进

| 演进 | 说明 |
|------|------|
| **mTLS** | 双向 TLS（服务间认证）|
| **SPIFFE / SPIRE** | 工作负载身份标准 |
| **cert-manager** | K8s 自动证书管理 |
| **Istio Mesh** | 自动 mTLS |

详见 [`kubernetes/08-operator-and-gitops`](../../05.tools/kubernetes/08-operator-and-gitops/README.md)

---

## 十、最佳实践

1. **强制 HTTPS**：禁用 HTTP，启用 HSTS
2. **TLS 1.3 优先**：性能 + 安全性都更好
3. **强加密套件**：禁用 RC4 / CBC / SHA-1
4. **OCSP Stapling**：减少证书验证延迟
5. **自动续期**：certbot / cert-manager + cron
6. **0-RTT 谨慎用**：仅用于幂等 GET 请求
7. **会话恢复**：减少重复握手
8. **监控证书**：过期前 30 天告警

---

← [返回计算机基础总览](../../README.md) · 📅 2026-06-28