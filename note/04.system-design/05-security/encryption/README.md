# 加密与密钥管理（Encryption）

> 现代应用很少需要"自己实现加密算法"，但必须**正确选型与使用**。本文按对称 / 非对称 / 哈希 / TLS / 字段级加密 / KMS 六大主题展开，附 Java 代码示例。

## 目录

- [对称加密](#对称加密)
- [非对称加密](#非对称加密)
- [哈希与 MAC](#哈希与-mac)
- [TLS / HTTPS](#tls--https)
- [字段级加密（Field-Level Encryption）](#字段级加密field-level-encryption)
- [密钥管理 KMS / HSM](#密钥管理-kms--hsm)
- [常见误区](#常见误区)
- [参考资料](#参考资料)

---

## 对称加密

**适用场景**：加密大量数据（数据库字段、文件、消息体）。加解密使用**同一把密钥**。

### 推荐算法

| 算法 | 密钥长度 | 模式 | 备注 |
|------|----------|------|------|
| **AES-GCM** | 128/256 bit | AEAD（认证加密） | **首选** |
| **AES-CBC + HMAC** | 256 bit | Encrypt-then-MAC | 老系统常用 |
| **ChaCha20-Poly1305** | 256 bit | AEAD | 移动端 / 无 AES-NI 时更快 |
| ~~DES / 3DES / AES-ECB~~ | — | — | **已淘汰** |

### 为什么 GCM 是首选

GCM（Galois/Counter Mode）同时提供**机密性 + 完整性**（AEAD = Authenticated Encryption with Associated Data），避免 CBC 模式常见的 padding oracle 攻击。

### Java 示例：AES-256-GCM

```java
public class AesGcmUtil {

    private static final int GCM_IV_LEN = 12;     // 96 bit 推荐长度
    private static final int GCM_TAG_LEN = 128;   // 128 bit 认证标签

    public static byte[] encrypt(byte[] plaintext, SecretKey key) throws Exception {
        // 1. 随机 IV（绝不重用！）
        byte[] iv = new byte[GCM_IV_LEN];
        SecureRandom random = new SecureRandom();
        random.nextBytes(iv);

        // 2. 加密
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LEN, iv);
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        byte[] ct = cipher.doFinal(plaintext);

        // 3. 返回 iv + ciphertext (iv 不需保密但必须随密文存储)
        ByteBuffer buf = ByteBuffer.allocate(iv.length + ct.length);
        buf.put(iv).put(ct);
        return buf.array();
    }

    public static byte[] decrypt(byte[] cipherBlob, SecretKey key) throws Exception {
        ByteBuffer buf = ByteBuffer.wrap(cipherBlob);
        byte[] iv = new byte[GCM_IV_LEN];
        buf.get(iv);
        byte[] ct = new byte[buf.remaining()];
        buf.get(ct);

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(GCM_TAG_LEN, iv));
        return cipher.doFinal(ct);   // 验证 GCM tag 失败时抛 AEADBadTagException
    }
}
```

> **关键约束**：AES-GCM 的 IV 绝不能在**同一密钥**下重用。重用 → 灾难性机密性 / 完整性破坏（攻击者可恢复明文异或）。

---

## 非对称加密

**适用场景**：密钥交换（TLS）、数字签名、加密小数据（密钥封装）。加解密使用**不同密钥**（公钥 + 私钥）。

### 主流算法

| 算法 | 用途 | 密钥长度 | 备注 |
|------|------|----------|------|
| **RSA** | 签名、加密 | ≥ 2048 bit（推荐 3072/4096） | 老牌，签名验签慢 |
| **ECDSA** (P-256) | 签名 | 256 bit | TLS 主流 |
| **Ed25519** | 签名 | 256 bit | **推荐**：快、安全、易用 |
| **ECDH** (X25519) | 密钥交换 | 256 bit | TLS 1.3 / Signal |
| **RSA-OAEP** | 加密 | ≥ 2048 bit | 用于加密小数据 / 封装密钥 |

### 数字签名示例（Ed25519，Java 15+）

```java
import java.security.*;
import java.security.spec.*;

public class Ed25519Example {

    public static void main(String[] args) throws Exception {
        // 1. 生成密钥对
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("Ed25519");
        KeyPair kp = kpg.generateKeyPair();

        // 2. 签名
        Signature signer = Signature.getInstance("Ed25519");
        signer.initSign(kp.getPrivate());
        signer.update("hello world".getBytes());
        byte[] sig = signer.sign();

        // 3. 验签
        Signature verifier = Signature.getInstance("Ed25519");
        verifier.initVerify(kp.getPublic());
        verifier.update("hello world".getBytes());
        boolean ok = verifier.verify(sig);   // true
    }
}
```

### TLS 中的实际用法

- **签名**：服务器用 Ed25519 私钥签证书，客户端用 CA 公钥验签
- **密钥交换**：客户端用 ECDH 算出共享密钥 → 用 HKDF 派生对称密钥 → 用于 AES-GCM

---

## 哈希与 MAC

### 加密哈希函数

| 算法 | 输出 | 状态 | 用途 |
|------|------|------|------|
| **SHA-256** | 256 bit | 安全 | 通用哈希 |
| **SHA-3 / BLAKE3** | 可变 | 安全 | 替代 SHA-2 |
| **SHA-1** | 160 bit | **已破解** | 仅用于非安全场景 |
| **MD5** | 128 bit | **已破解** | 仅用于文件指纹校验 |

### 密码哈希（特殊场景）

密码哈希需**慢 + 加盐**，防止字典攻击：

| 算法 | 推荐度 | 备注 |
|------|--------|------|
| **Argon2id** | ⭐⭐⭐ | 内存硬，可调参 |
| **bcrypt** | ⭐⭐ | 老牌稳定 |
| **scrypt** | ⭐⭐ | 内存硬 |
| PBKDF2 | ⭐ | NIST 标准化，但快 |
| SHA-256 + salt | ❌ | 太快，不安全 |

### MAC（Message Authentication Code）

确保消息**未被篡改 + 来源可信**。HMAC 是最常用的方案：

```java
public byte[] hmacSha256(byte[] message, byte[] key) throws Exception {
    Mac mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(key, "HmacSHA256"));
    return mac.doFinal(message);
}

// 验证：compare in constant time (防时序攻击)
public boolean constantTimeEquals(byte[] a, byte[] b) {
    return MessageDigest.isEqual(a, b);
}
```

> 现代 AEAD 加密（AES-GCM / ChaCha20-Poly1305）已经自带 MAC，无需额外 HMAC。

---

## TLS / HTTPS

### TLS 握手流程（简化）

```
Client                                  Server
  │                                       │
  │── ClientHello (支持的版本/密码套件) ──▶│
  │                                       │
  │◀── ServerHello + Certificate ────────│
  │◀── (ServerKeyExchange if needed) ────│
  │◀── ServerHelloDone ──────────────────│
  │                                       │
  │── ClientKeyExchange ────────────────▶│
  │── (CertificateVerify if mTLS) ──────▶│
  │── ChangeCipherSpec + Finished ──────▶│
  │                                       │
  │◀── ChangeCipherSpec + Finished ──────│
  │                                       │
  │◀══════ 加密通道 (AES-GCM) ══════════▶│
```

### 关键配置

```nginx
# Nginx TLS 1.3 推荐配置
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
ssl_ecdh_curve X25519:secp384r1;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
ssl_session_tickets off;
```

### mTLS（双向 TLS）

在微服务 / 服务网格中，**双方都验证对方证书**：

- Service Mesh（Istio / Linkerd）自动注入 mTLS
- Spring Cloud Gateway + X.509 证书

### 证书锁定（Certificate Pinning）

参考 [API 安全](../api-security/README.md#https-与证书锁定)。

---

## 字段级加密（Field-Level Encryption）

数据库中的**敏感字段**（身份证、银行卡、密码）需要单独加密，与行级 / 全盘加密不同。

### 模式 1：信封加密（推荐）

```
应用                   KMS / HSM              数据库
 │                       │                     │
 │ 1. 请求生成 DEK        │                     │
 │ ─────────────────▶   │                     │
 │ ◀── 返回 DEK ────────│                     │
 │                       │                     │
 │ 2. 用 DEK 加密数据                            │
 │ 3. 把 DEK 用 KMS 加密（加密后存入 DB）        │
 │                       │                     │
 │ 4. 写入：                                ──▶│
 │    id_card_enc, dek_enc                  ──▶│
```

详见 [secrets-management](../secrets-management/README.md#2-加密信封envelope-encryption) 章节的代码示例。

### 模式 2：确定性加密（Deterministic Encryption）

为支持**等值查询**（`WHERE id_card_hash = ?`），使用确定性加密：

- 同一明文 + 同一密钥 → 同一密文
- 但泄露后**可被频率分析**（如每年出生人数对应密文频率）

**实现方式**：

1. **HMAC 截断**：`id_card_hash = HMAC-SHA256(key, id_card)[:16]` 作为盲化索引列
2. **AES-SIV 模式**：在标准之上提供确定性 + 防滥用
3. **保序加密（OPE）**：保留顺序，但安全性弱，慎用

```java
// 模式 1 示例：HMAC 盲化索引
public String blindIndex(String plain, byte[] key) {
    Mac mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(key, "HmacSHA256"));
    byte[] hash = mac.doFinal(plain.getBytes(StandardCharsets.UTF_8));
    return Base64.getUrlEncoder().withoutPadding()
            .encodeToString(Arrays.copyOf(hash, 16));
}

// SQL 查询
// SELECT * FROM users WHERE id_card_bi = ?  // 传入 blindIndex(用户输入, key)
```

### 模式 3：透明加密（Transparent Data Encryption, TDE）

数据库自身提供的磁盘加密：

- **MySQL** InnoDB 表空间加密
- **PostgreSQL** pgcrypto
- **AWS RDS** 启用存储加密

- **优点**：零应用改造成本
- **缺点**：DBA / 备份仍可读明文；不防应用层 SQL 注入

---

## 密钥管理 KMS / HSM

### KMS（Key Management Service）

- **托管式**：密钥由云厂商保管，用户通过 API 使用
- 永远不暴露明文密钥，硬件（HSM）保护
- 主流：AWS KMS、Azure Key Vault、GCP Cloud KMS、阿里云 KMS

```java
// AWS KMS Java SDK 加密示例
public class KmsExample {

    private final KmsClient kms = KmsClient.builder().region(Region.US_EAST_1).build();

    public byte[] encrypt(byte[] plaintext, String keyId) {
        EncryptRequest req = EncryptRequest.builder()
                .keyId(keyId)            // arn:aws:kms:...
                .plaintext(SdkBytes.fromByteArray(plaintext))
                .build();
        EncryptResponse resp = kms.encrypt(req);
        return resp.ciphertextBlob().asByteArray();
    }

    public byte[] decrypt(byte[] cipherBlob) {
        DecryptResponse resp = kms.decrypt(DecryptRequest.builder()
                .ciphertextBlob(SdkBytes.fromByteArray(cipherBlob))
                .build());
        return resp.plaintext().asByteArray();
    }
}
```

### HSM（Hardware Security Module）

- 物理硬件保护密钥（防内存抓取、防侧信道）
- 比 KMS 更强，但贵且慢
- 适用：金融根证书、PKI 根 CA

### 自建 vs 云托管

| 维度 | 自建（HashiCorp Vault） | 云托管（AWS KMS 等） |
|------|-------------------------|----------------------|
| 成本 | 自建免费（运维成本高） | 按调用计费 |
| 合规 | 需自己过 SOC2 / PCI DSS | 已合规 |
| 多云 | 一致体验 | 锁定云厂商 |
| 物理保护 | 自购 HSM 接入 | 厂商 HSM 内置 |

> **建议**：上云就优先用云 KMS；多云 / 混合云考虑 Vault + 各云 KMS 适配。

---

## 常见误区

| 误区 | 为什么错 | 正确做法 |
|------|----------|----------|
| 密码加 MD5 / SHA-1 后存库 | GPU 秒破 | bcrypt / Argon2id |
| 自定义加密算法 | 99% 错 | 用标准库（AES-GCM） |
| 同一密钥 + 同一 IV 加密多个文件 | AES-GCM 灾难 | 每次随机 IV |
| 私钥放代码仓库 | 提交即泄露 | 放 Vault / KMS |
| 加密字段做 `LIKE` 查询 | 密文不可模糊匹配 | 等值用 HMAC 盲化索引 |
| 用 base64 当"加密" | 完全可逆 | AES-GCM 才是加密 |
| 自己实现 TLS | 必有漏洞 | 用 OpenSSL / BoringSSL / mbedTLS |

---

## 参考资料

- [NIST SP 800-57 - Recommendation for Key Management](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)
- [NIST SP 800-38D - GCM 模式规范](https://csrc.nist.gov/publications/detail/sp/800-38d/final)
- [RFC 7748 - Elliptic Curves for Security (X25519, Ed25519)](https://tools.ietf.org/html/rfc7748)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [AWS KMS 文档](https://docs.aws.amazon.com/kms/)
- [HashiCorp Vault Transit Engine](https://developer.hashicorp.com/vault/docs/secrets/transit)
