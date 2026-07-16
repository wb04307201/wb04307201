<!--
question:
  id: 05.security-owasp-top10
  topic: 05.security
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [05.security, OWASP, Top 10, 注入, 认证, 敏感数据, SSRF]
-->

# OWASP Top 10 面试怎么答？—— 10 大安全风险速记与防御策略

> 一句话定位：OWASP Top 10 是 Web 安全的"体检清单"——面试不是背 10 个名词，而是展示**风险评估能力**和**纵深防御思维**。完整 Web 安全见 [主模块 Web 安全](../../../04.system-design/05-security/web-security/README.md)。

> **系列定位**：经典安全面试题（大厂必问）。考察 **Top 3 风险深度理解** + **防御方案落地** + **安全左移工程实践**。

---

## 引子：一次安全审计暴露的系统性问题

```text
某 SaaS 公司过 SOC 2 审计，安全团队扫描出 47 个漏洞——
注入漏洞 12 个：用户搜索接口直接拼接 SQL
认证缺陷 8 个：JWT 永不过期 + 无黑名单
SSRF 3 个：图片上传接口接受 URL，可探测内网
敏感数据 5 个：API 返回完整用户对象含密码哈希
```

**反直觉**：注入连续 10 年 Top 3，但防御方案（参数化查询）极其简单；SSRF 在云原生时代威胁更大——可通过元数据服务获取云凭证。

---

## 一、核心原理

| # | 风险 | 防御核心 |
|---|------|---------|
| A01 | **Broken Access Control** | 最小权限 + 服务端校验 |
| A02 | **Cryptographic Failures** | TLS + AES-256 + 密钥管理 |
| A03 | **Injection** | 参数化查询 + 输入验证 |
| A04 | **Insecure Design** | 威胁建模 + 安全设计模式 |
| A05 | **Security Misconfiguration** | 安全基线 + 自动扫描 |
| A06 | **Vulnerable Components** | 依赖扫描 + 及时更新 |
| A07 | **Auth Failures** | MFA + 强密码 + Session 安全 |
| A08 | **Data Integrity Failures** | 签名验证 + 供应链安全 |
| A09 | **Logging Failures** | 集中日志 + 告警 |
| A10 | **SSRF** | URL 白名单 + 禁止内网 |

**Top 3 深度**：

- **A01 越权**：水平越权（用户 A 访问用户 B 数据 → 查询加 user_id 条件）+ 垂直越权（普通用户访问管理功能 → @PreAuthorize）
- **A03 注入**：SQL 注入（拼接 SQL → PreparedStatement）、NoSQL 注入（传入 `{"$gt":""}` → 输入类型验证）
- **A10 SSRF**：POST /api/fetch-url 传内网 URL → 泄露 AWS 元数据凭证 → URL 白名单 + 禁止内网 IP + 协议白名单

---

## 二、详解

**认证安全（A07）**：密码用 bcrypt/Argon2id + MFA（TOTP/WebAuthn）+ JWT 短过期 + Refresh Rotate + Redis 黑名单。

**安全配置（A05）**：最小化安装 + 修改默认密码 + 关闭 Debug + 目录列表关闭 + 定期安全扫描（OWASP ZAP）。

**供应链安全（A06+A08）**：Log4Shell 教训——依赖扫描（Snyk/Dependabot）+ 锁定版本（package-lock.json）+ CI/CD 签名验证 + SBOM 物料清单。

---

## 三、常见陷阱

- **只关注注入，忽视越权**：Broken Access Control 从 2017 年第 5 跃升到 2021 年第 1 → 每个 API 校验"当前用户有权操作此资源吗"
- **参数化查询不够**：`ORDER BY ${column}` 无法参数化 → 列名用白名单映射
- **SSRF 只防 HTTP**：`file:///etc/passwd`、`gopher://` 也能利用 → 协议白名单（仅 http/https）
- **日志记录敏感数据**：日志出现密码/Token → 日志脱敏（password → ***）

---

## 四、最佳实践

```
安全左移（Shift Left Security）：
  设计 → 威胁建模（STRIDE）
  编码 → SonarLint + 安全编码规范
  构建 → 依赖扫描 + SAST（静态分析）
  测试 → DAST（动态扫描）+ 渗透测试
  部署 → 容器扫描 + 安全基线检查
  运行 → WAF + RASP + 安全监控

防御速查：
  注入 → 参数化查询（MyBatis #{}）
  越权 → Spring Security @PreAuthorize
  XSS → OWASP Java Encoder + CSP
  CSRF → Token + SameSite
  SSRF → URL 白名单 + 禁内网
  弱认证 → MFA + bcrypt + 短 JWT
```

---

## 五、面试话术（90 秒版本）

> "OWASP Top 10 是 Web 安全行业标准。2021 版排名第一是越权（Broken Access Control），第三是注入（Injection），第十是 SSRF。
>
> 注入防御核心是参数化查询。越权防御在每个 API 层校验当前用户权限——水平越权加 user_id 条件，垂直越权用 @PreAuthorize。SSRF 用 URL 白名单加禁止内网 IP。认证安全要 bcrypt + MFA + 短 JWT + Refresh Rotate。
>
> 最重要的是安全左移——设计阶段威胁建模，编码用 SonarLint，CI/CD 做 SAST/DAST，运行时 WAF + RASP。不是上线后再补安全，而是从第一天融入开发流程。"

---

## 六、交叉引用

- [XSS、CSRF、CSP 三件套](../xss-csrf-csp/README.md) — A03 注入 + XSS 详解
- [JWT vs Session](../jwt-vs-session/README.md) — A07 认证安全
- [传输加密 vs 存储加密](../encryption-at-rest-transit/README.md) — A02 加密失败
- [令牌桶 vs 漏桶](../rate-limiting-algorithms/README.md) — API 安全与 DDoS 防护
- [统一权限控制系统](../access-control-design/README.md) — A01 访问控制
- [单点登录 6 大方案](../sso/README.md) — A07 认证架构
- [主模块 04.system-design/05-security](../../../04.system-design/05-security/README.md) — 安全知识体系

---

← [返回: 咬文嚼字 · 安全](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 05.security · ⭐⭐⭐⭐
