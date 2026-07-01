<!--
module:
  parent: system-design
  slug: system-design/secrets-management
  type: article
  category: 主模块子文章
  summary: "Secrets" 指的是系统中所有需要保密的字符串：数据库密码、API Key、加密私钥、JWT 签名密钥、云厂商 AccessKey、TLS 证书……本文介...
-->

# 密钥与凭据管理（Secrets Management）

> "Secrets" 指的是系统中所有需要保密的字符串：数据库密码、API Key、加密私钥、JWT 签名密钥、云厂商 AccessKey、TLS 证书……本文介绍生产环境应如何**安全存储、动态注入、定期轮换**这些凭据。

## 目录

- [为什么绝不能硬编码密钥](#为什么绝不能硬编码密钥)
- [密钥存储方案对比](#密钥存储方案对比)
- [12-Factor App 与环境变量](#12-factor-app-与环境变量)
- [密钥轮换（Rotation）模式](#密钥轮换rotation模式)
- [加密密钥的派生（Key Derivation）](#加密密钥的派生key-derivation)
- [运行时密钥注入最佳实践](#运行时密钥注入最佳实践)
- [参考资料](#参考资料)

---
## 引言：反直觉代码

密钥与凭据管理（Secrets Management） 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 为什么绝不能硬编码密钥

### 真实案例

- 某公司在 GitHub 公开仓库误提交了 AWS AccessKey，几分钟内被矿工利用，账单爆掉。
- 某项目把数据库密码写在 `application.yml` 里提交到 Git，半年后被离职员工卖给竞争对手。
- Log4j 的 `${env:...}` 占位符让很多人意识到：日志里**也不应输出密钥**。

### 硬编码的常见形式

| 形式 | 风险 |
|------|------|
| `application.yml` 明文 `password: 123456` | 提交即泄露 |
| `private static final String SECRET = "abc"` | 反编译即可读 |
| 前端 `.env.production` 推到公网仓库 | 与上面同理 |
| Wiki / Confluence 明文密码 | 离职员工 / 外包可见 |
| Slack 私聊里贴明文密钥 | 日志可被审计、第三方应用可读 |

**核心原则**：

> **密钥不进 Git**、**密钥不进镜像**、**密钥不进日志**、**密钥不进前端**。

---

## 密钥存储方案对比

| 方案 | 适用规模 | 加密方式 | 密钥轮换 | 访问控制 | 成本 |
|------|----------|----------|----------|----------|------|
| 环境变量 / 配置文件 | 单机玩具 | 无（明文） | 手动 | OS 权限 | 免费 |
| 加密配置文件（如 jasypt） | 中小 | 应用密钥加密 | 手动 | 弱 | 免费 |
| **HashiCorp Vault** | 中大 | AES-256 + HSM | 动态 | 租户 + 策略 + Token | 自建免费 / 商业版收费 |
| **AWS Secrets Manager** | AWS 生态 | KMS | 自动 | IAM Policy | 按密钥/月计费 |
| **Azure Key Vault** | Azure 生态 | HSM 备份 | 自动 | RBAC | 按操作计费 |
| **GCP Secret Manager** | GCP 生态 | 默认加密 | 自动 | IAM | 按版本计费 |
| **Kubernetes Secrets + KMS** | K8s | etcd 加密 + KMS | 需插件 | RBAC | 免费 / KMS 计费 |

### HashiCorp Vault 核心概念

```
┌─────────────────────────────────────────────┐
│                  Vault                       │
│  ┌──────────────┐  ┌──────────────────┐    │
│  │  KV v2 引擎   │  │  Database 引擎   │    │
│  │  (通用 KV)   │  │ (动态生成 DB 账户)│    │
│  └──────────────┘  └──────────────────┘    │
│  ┌──────────────┐  ┌──────────────────┐    │
│  │ Transit 引擎  │  │  PKI 引擎         │    │
│  │ (加解密即服务)│  │ (动态签发证书)    │    │
│  └──────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────┘
        ▲                            ▲
        │ 读 / 动态签发              │
        │                            │
  ┌─────┴──────┐               ┌────┴─────┐
  │ App Server │               │ CI / CD  │
  └────────────┘               └──────────┘
```

**Java 集成示例**（Spring Cloud Vault）：

```java
// 1. 添加依赖
// org.springframework.cloud:spring-cloud-starter-vault-config

// 2. bootstrap.yml
spring:
  application:
    name: order-service
  cloud:
    vault:
      uri: https://vault.example.com
      token: ${VAULT_TOKEN}   # 由 Sidecar / k8s ServiceAccount 注入
      kv:
        enabled: true
        backend: secret
        default-context: order-service

// 3. 注入到配置
@RestController
public class PaymentController {

    @Value("${payment.api.key}")
    private String apiKey;   // 从 Vault 读取

    @PostMapping("/pay")
    public Result pay(@RequestBody PayRequest req) {
        return paymentClient.charge(apiKey, req);
    }
}
```

### 动态数据库凭据

Vault **Database 引擎**能为每个应用实例生成一个**短时效**的数据库账户，TTL 到期自动撤销：

```bash
# 请求一个 1 小时有效的 DB 凭据
$ vault read database/creds/order-service-app
Key                Value
---                -----
lease_id           database/creds/order-service-app/abc123
username           v-token-order-service-app-xyz
password           8f7H-2kLm-9pQr
```

应用启动时拿这个凭据连 DB，1 小时后自动失效——即使泄露，窗口期也极短。

---

## 12-Factor App 与环境变量

[12-Factor](https://12factor.net/) 推荐：

- 配置（包含密钥）通过**环境变量**注入
- 不同环境（dev/staging/prod）的配置完全隔离
- 不区分本地 vs 线上，只是**配置来源不同**

```yaml
# application.yml 使用占位符
spring:
  datasource:
    password: ${DB_PASSWORD}
jwt:
  secret: ${JWT_SECRET}
```

**环境变量注入方式**：

| 场景 | 方式 |
|------|------|
| 本地开发 | `.env` 文件（加入 `.gitignore`）+ IDE 启动参数 |
| Docker | `docker run -e DB_PASSWORD=xxx` 或 `docker-compose` 的 `environment` |
| Kubernetes | `Secret` 资源 + `envFrom` |
| CI/CD | GitHub Actions Secrets / GitLab CI Variables |

> **注意**：环境变量**不是加密的**，只是隔离。真正的密钥仍应在 Vault / KMS 中，App 启动时去拉。

---

## 密钥轮换（Rotation）模式

### 1. 单密钥定期轮换

- 每 30/90 天由 Vault 自动生成新版本
- 旧版本保留 N 天（用于验签 / 解密历史数据）
- 旧版本过期后销毁

```
密钥版本：
  v1: 2025-01-01 ~ 2025-04-01  (写入新数据请用 v2)
  v2: 2025-04-01 ~ 至今
  v1: 2025-04-01 ~ 2025-05-01  (只读，用于验签)
  v1: 销毁
```

### 2. 加密信封（Envelope Encryption）

KMS 主密钥（KEK，Key Encryption Key）不直接加密数据，而是加密**数据密钥（DEK，Data Encryption Key）**：

```
KEK（存 KMS，从不离开硬件）    ← 永远不会泄露
   ↓ 加密
DEK（存数据库 / 文件）         ← 即使泄露，没 KEK 解不开
   ↓ 加密
业务数据
```

轮换 KEK 时，只需重新加密 DEK，无需重加密所有业务数据。

```java
public class EnvelopeEncryption {

    private final KmsClient kms;

    public EncryptedBlob encrypt(String plaintext) {
        // 1. 随机生成 DEK
        SecretKey dek = new SecretKeySpec(
                SecureRandom.getInstanceStrong().generateSeed(32), "AES");
        // 2. 用 DEK 加密数据
        byte[] ct = aesGcmEncrypt(dek, plaintext);
        // 3. 用 KMS 加密 DEK
        byte[] encryptedDek = kms.encrypt("alias:my-kek", dek.getEncoded());
        return new EncryptedBlob(encryptedDek, ct);
    }

    public String decrypt(EncryptedBlob blob) {
        byte[] dekBytes = kms.decrypt("alias:my-kek", blob.encryptedDek);
        SecretKey dek = new SecretKeySpec(dekBytes, "AES");
        return aesGcmDecrypt(dek, blob.ct);
    }
}
```

### 3. 主动轮换触发条件

- 定期：每 90 天
- 事件驱动：员工离职、密钥疑似泄露、合规审计

---

## 加密密钥的派生（Key Derivation）

不要把"用户密码"直接当加密密钥——密码熵低。应使用**密钥派生函数（KDF）**：

| KDF | 适用 | 速度 |
|-----|------|------|
| **PBKDF2** | 用户密码派生 | 中 |
| **bcrypt / scrypt** | 用户密码哈希 | 慢（设计目的） |
| **Argon2id** | 用户密码派生（推荐） | 可调 |
| **HKDF** | 高熵输入 → 多用途子密钥 | 快 |
| **TLS 1.3 HKDF-Expand-Label** | TLS 握手 | 快 |

```java
// Argon2id：用户密码 → 加密密钥
public byte[] deriveKeyFromPassword(String password, byte[] salt) {
    Argon2BytesGenerator gen = new Argon2BytesGenerator();
    gen.init(new Argon2Parameters.Builder(Argon2Parameters.ARGON2_id)
            .withSalt(salt)
            .withIterations(3)
            .withMemoryAsKB(65536)
            .withParallelism(4)
            .build());
    byte[] key = new byte[32];
    gen.generateBytes(password.toCharArray(), key);
    return key;
}

// HKDF：高熵 master key → 多个子密钥
public byte[] deriveSubKey(byte[] masterKey, String info, int len) {
    HKDFParameters params = new HKDFParameters(masterKey, /*salt*/ null, info.getBytes());
    HKDFBytesGenerator gen = new HKDFBytesGenerator();
    gen.init(params);
    return gen.generateBytes(len);
}
```

---

## 运行时密钥注入最佳实践

1. **不写代码、不写配置**：
   - `application.yml` 中密钥全部用 `${ENV_VAR}` 占位符
   - 启动时由编排平台（K8s / ECS）注入

2. **Sidecar 注入**：
   - K8s 使用 [Vault Agent Injector](https://developer.hashicorp.com/vault/docs/platform/k8s/injector) 自动挂载 Secret
   - 应用看到的还是文件 / 环境变量，**无感知**

3. **避免日志泄露**：
   ```java
   // 错误
   log.info("Using DB password: {}", password);
   // 正确
   log.info("Connecting to DB host={}, user={}", host, user);
   ```

4. **定期审计**：
   - 跑 `gitleaks` / `trufflehog` 在 CI 中扫描历史 commit
   - 用 [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning) 自动告警

5. **应急响应**：
   - 密钥泄露后**第一时间**轮换，不是明天
   - 准备 runbook：发现 → 撤销 → 轮换 → 通知相关方

---

## 参考资料

- [HashiCorp Vault 官方文档](https://developer.hashicorp.com/vault/docs)
- [AWS Secrets Manager 文档](https://docs.aws.amazon.com/secretsmanager/)
- [Azure Key Vault 文档](https://learn.microsoft.com/azure/key-vault/)
- [12-Factor App: Config](https://12factor.net/config)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [NIST SP 800-57 - Key Management](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)
- [gitleaks - Git 历史密钥扫描](https://github.com/gitleaks/gitleaks)
