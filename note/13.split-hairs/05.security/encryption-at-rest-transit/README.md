<!--
question:
  id: 05.security-encryption-at-rest-transit
  topic: 05.security
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [05.security, TLS, AES, 传输加密, 存储加密, KMS, HSM]
-->

# 传输加密 vs 存储加密怎么选？—— 数据全生命周期加密策略

> 一句话定位：传输加密保护"数据在路上"，存储加密保护"数据在磁盘上"——两者**必须同时部署**，关键差异在密钥管理。完整加密体系见 [主模块加密](../../../04.system-design/05-security/encryption/README.md)。

> **系列定位**：经典安全架构面试题。考察 **Data at Rest vs In Transit 分层** + **信封加密** + **KMS/HSM 密钥管理**。

---

## 引子：一次数据库泄露暴露的加密盲区

```text
某金融公司宣称"全链路加密"——HTTPS + TLS 1.3 ✅、磁盘加密 ✅
但：DBA 可以直接 SELECT * 看到明文密码和身份证号
真相：磁盘加密（LUKS/TDE）防的是"偷硬盘"，防不了 DBA 查看数据
```

**反直觉**：传输加密结束的瞬间（TLS 终止后），数据在内存中是**明文**；真正的存储加密要做到**应用层加密**，密钥不在数据库服务器上。

---

## 一、核心原理

| 维度 | 传输加密（In Transit） | 存储加密（At Rest） |
|------|----------------------|-------------------|
| 保护对象 | 网络传输中的数据 | 磁盘 / 备份中的数据 |
| 典型技术 | TLS 1.2/1.3、IPsec | AES-256、TDE、应用层加密 |
| 密钥生命周期 | 会话级（短） | 长期（需轮换） |
| 密钥管理 | 证书体系（CA） | KMS / HSM |

**对称 vs 非对称**：AES-256（对称）速度快适合大数据量；RSA/ECDSA（非对称）慢 100-1000 倍仅用于密钥交换。实战组合：**非对称交换密钥 → 对称加密数据**（信封加密）。

**信封加密**：① 生成随机 DEK → ② DEK 加密数据（快）→ ③ KEK 加密 DEK → ④ 存储加密数据 + 加密 DEK。密钥轮换时只需重加密 DEK，不用重加密数据。

---

## 二、代码示例

```java
// 应用层字段加密（AES-256-GCM）
@Component
public class FieldEncryptor {
    @Value("${encryption.key}") // 从 KMS 获取，不硬编码
    private SecretKey key;

    public String encrypt(String plaintext) {
        byte[] iv = SecureRandom.getInstanceStrong().generateSeed(12);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
        byte[] ct = cipher.doFinal(plaintext.getBytes());
        return Base64.getEncoder().encodeToString(iv) + ":" +
               Base64.getEncoder().encodeToString(ct);
    }
}
// DB 存储密文，DBA 无法直接读取
```

---

## 三、常见陷阱

- **磁盘加密 = 数据安全**：LUKS/TDE 只防物理盗窃 → 敏感字段必须应用层加密
- **密钥硬编码在代码中**：源码泄露 = 全部数据可解密 → 用 KMS/Vault 动态获取
- **不做密钥轮换**：长期同一密钥，泄露影响面巨大 → KEK 每年轮换
- **TLS 终止后内网明文**：负载均衡解密后内网可嗅探 → 内网也做 mTLS（Istio 管理）

---

## 四、最佳实践

```
全链路加密策略：
  外部流量：HTTPS / TLS 1.3
  内部流量：mTLS（服务网格自动管理）
  磁盘数据：TDE / LUKS（防物理盗窃）
  敏感字段：应用层 AES-256-GCM（防 DBA / 备份泄露）
  密钥管理：KMS（AWS KMS / HashiCorp Vault）

密钥管理决策树：
  金融 / 政府 → HSM（FIPS 140-2 Level 3）
  互联网企业 → KMS（AWS KMS / 阿里云 KMS）
  创业团队 → HashiCorp Vault

密码存储：用 bcrypt/Argon2id（单向哈希），不用 AES（可逆），绝不用 MD5/SHA-256
```

---

## 五、面试话术（90 秒版本）

> "传输加密和存储加密必须同时部署。传输加密用 TLS 保护网络数据，TLS 1.3 提供前向安全。存储加密分层级：磁盘级（TDE/LUKS）防物理盗窃，应用层字段加密（AES-256-GCM）防 DBA 和备份泄露。
>
> 密钥管理是关键：不能硬编码，要用 KMS 或 HSM。推荐信封加密——KMS 保护 KEK，KEK 加密 DEK，DEK 加密数据。密钥轮换只需重加密 DEK。密码存储用 bcrypt/Argon2id 单向哈希而非可逆加密。内网流量推荐 mTLS，通过 Istio 自动管理证书。"

---

## 六、交叉引用

- [HTTPS 握手性能优化](../https-handshake/README.md) — TLS 性能优化详解
- [JWT vs Session](../jwt-vs-session/README.md) — Token 传输安全
- [OWASP Top 10](../owasp-top10/README.md) — 敏感数据暴露防护
- [主模块 04.system-design/05-security](../../../04.system-design/05-security/README.md) — 安全知识体系

---

← [返回: 咬文嚼字 · 安全](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 05.security · ⭐⭐⭐⭐
