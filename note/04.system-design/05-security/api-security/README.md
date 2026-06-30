<!--
module:
  parent: system-design
  slug: system-design/api-security
  type: article
  category: 主模块子文章
  summary: API 是系统对外暴露的入口，安全设计是 API 设计的第一要务。本文涵盖签名验证、防重放、数据脱敏、限流等 API 安全核心主题。
-->

# API 安全

> API 是系统对外暴露的入口，安全设计是 API 设计的第一要务。本文涵盖签名验证、防重放、数据脱敏、限流等 API 安全核心主题。

## 目录

- [API 签名验证](#api-签名验证)
- [防重放攻击](#防重放攻击)
- [数据脱敏](#数据脱敏)
- [API 限流与防刷](#api-限流与防刷)
- [HTTPS 与证书锁定](#https-与证书锁定)
- [API 安全检查清单](#api-安全检查清单)

---
## 引言：生产 Bug（[AUTO] 自动生成，待人工 review）

API 安全 的API 是系统对外暴露的入口，安全设计是 API 设计的第一要务。本文涵盖签名验证、防重放、数据脱敏、限流等 API 安全核心主题

**但实际**：常被攻击或出 Bug 后背锅。本篇用'生产场景'切入：
线上怎么炸、有没有上线过的坑、为什么按官方文档写也会错。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## API 签名验证

### 为什么需要签名

API 签名用于保证：
1. **完整性**：请求在传输过程中未被篡改
2. **身份认证**：请求确实来自合法的客户端
3. **不可抵赖**：发送方无法否认发送过该请求

### 签名参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `AppKey` | 客户端唯一标识 | `ak_20250101_001` |
| `AppSecret` | 客户端密钥（**绝不传输**） | `sk_xxxxx` |
| `Timestamp` | 请求时间戳（毫秒），防重放 | `1678897634000` |
| `Nonce` | 随机字符串，防重放 | `a1b2c3d4e5` |
| `Signature` | 签名值 | `hex(HMAC-SHA256(...))` |

### 签名生成算法

```
签名串 = AppKey + "\n" + Timestamp + "\n" + Nonce + "\n" + RequestBody
签名   = HMAC-SHA256(签名串, AppSecret)
```

### Java 实现（HMAC-SHA256）

```java
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;

public class ApiSignatureUtil {

    private static final String HMAC_SHA256 = "HmacSHA256";

    /**
     * 生成 API 签名
     *
     * @param appKey      客户端标识
     * @param appSecret   客户端密钥
     * @param timestamp   时间戳
     * @param nonce       随机串
     * @param requestBody 请求体（可为空）
     * @return 十六进制签名字符串
     */
    public static String sign(String appKey, String appSecret,
                               long timestamp, String nonce, String requestBody) {
        try {
            // 1. 拼接待签名字符串
            String stringToSign = appKey + "\n"
                    + timestamp + "\n"
                    + nonce + "\n"
                    + (requestBody != null ? requestBody : "");

            // 2. HMAC-SHA256 计算
            Mac mac = Mac.getInstance(HMAC_SHA256);
            SecretKeySpec keySpec = new SecretKeySpec(
                    appSecret.getBytes(StandardCharsets.UTF_8), HMAC_SHA256);
            mac.init(keySpec);
            byte[] hash = mac.doFinal(stringToSign.getBytes(StandardCharsets.UTF_8));

            // 3. 转为十六进制
            return bytesToHex(hash);
        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            throw new RuntimeException("签名生成失败", e);
        }
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    /**
     * 验证签名
     */
    public static boolean verify(String appKey, String appSecret,
                                  long timestamp, String nonce,
                                  String requestBody, String expectedSignature) {
        String actualSignature = sign(appKey, appSecret, timestamp, nonce, requestBody);
        return actualSignature.equalsIgnoreCase(expectedSignature);
    }
}
```

### Spring 拦截器集成

```java
@Component
public class ApiSignatureInterceptor implements HandlerInterceptor {

    @Autowired
    private AppKeyRepository appKeyRepo;

    @Override
    public boolean preHandle(HttpServletRequest request,
                              HttpServletResponse response, Object handler) {
        String appKey = request.getHeader("X-App-Key");
        String timestamp = request.getHeader("X-Timestamp");
        String nonce = request.getHeader("X-Nonce");
        String signature = request.getHeader("X-Signature");

        // 1. 检查必填参数
        if (anyBlank(appKey, timestamp, nonce, signature)) {
            throw new ApiException(401, "缺少签名参数");
        }

        // 2. 验证 AppKey 有效性
        AppKey entity = appKeyRepo.findByAppKey(appKey);
        if (entity == null || !entity.isEnabled()) {
            throw new ApiException(401, "无效的 AppKey");
        }

        // 3. 验证时间戳（防重放，见下方）
        long ts = Long.parseLong(timestamp);
        if (Math.abs(System.currentTimeMillis() - ts) > 5 * 60 * 1000) {
            throw new ApiException(401, "请求已过期");
        }

        // 4. 验证 Nonce（防重放）
        if (nonceRepo.exists(nonce)) {
            throw new ApiException(401, "Nonce 已使用");
        }

        // 5. 验证签名
        String body = readRequestBody(request);
        if (!ApiSignatureUtil.verify(appKey, entity.getAppSecret(),
                ts, nonce, body, signature)) {
            throw new ApiException(401, "签名验证失败");
        }

        // 6. 记录 Nonce
        nonceRepo.save(nonce);

        return true;
    }
}
```

---

## 防重放攻击

### 什么是重放攻击

攻击者截获合法的 API 请求后，原封不动地再次发送，导致系统重复执行操作（如重复转账、重复下单）。

### Timestamp + Nonce 方案

这是最常见的防重放方案，结合签名使用：

```
请求参数:
  X-Timestamp: 当前时间戳
  X-Nonce:     随机字符串（UUID 或随机字符串）
  X-Signature: 包含 Timestamp 和 Nonce 的签名

服务端验证:
  1. 检查 Timestamp 是否在允许的时间窗口内（如 ±5 分钟）
  2. 检查 Nonce 是否已使用过
  3. 验证签名
  4. 将 Nonce 存入缓存，设置 TTL = 时间窗口
```

### 实现细节

```java
@Service
public class NonceService {

    @Autowired
    private StringRedisTemplate redisTemplate;

    private static final long WINDOW_SECONDS = 300; // 5 分钟

    /**
     * 检查 Nonce 是否已使用
     * 使用 Redis SETNX 实现原子操作
     */
    public boolean tryUseNonce(String nonce) {
        String key = "api:nonce:" + nonce;
        // setIfAbsent 返回 true 表示该 Nonce 首次出现
        Boolean success = redisTemplate.opsForValue()
                .setIfAbsent(key, "1", WINDOW_SECONDS, TimeUnit.SECONDS);
        return Boolean.TRUE.equals(success);
    }
}
```

### 时间窗口选择

| 窗口大小 | 优点 | 缺点 |
|----------|------|------|
| 1 分钟 | 安全性高 | 时钟偏差可能导致合法请求被拒 |
| 5 分钟 | 平衡安全性和容错性 | 需要缓存 5 分钟的 Nonce |
| 10 分钟 | 容错性最好 | 攻击窗口较长 |

**推荐**: 5 分钟，同时要求客户端时钟与 NTP 服务器同步。

---

## 数据脱敏

### 脱敏规则

| 数据类型 | 脱敏规则 | 示例 |
|----------|----------|------|
| 手机号 | 保留前 3 后 4，中间 4 位脱敏 | `138****5678` |
| 身份证号 | 保留前 6 后 4，中间脱敏 | `110105********1234` |
| 邮箱 | 保留首字符和 @ 后域名 | `z***@example.com` |
| 银行卡号 | 保留前 4 后 4，中间 8 位分两组脱敏 | `6222 **** **** 1234` |
| 姓名 | 保留首字，其余脱敏 | `张**` |
| 地址 | 保留省市区，详细地址脱敏 | `北京市朝阳区***` |

### Java 脱敏工具类

```java
import org.apache.commons.lang3.StringUtils;

public class DataMaskingUtil {

    /**
     * 手机号脱敏: 138****5678
     */
    public static String maskPhone(String phone) {
        if (StringUtils.isBlank(phone) || phone.length() < 7) {
            return phone;
        }
        return phone.substring(0, 3) + "****" + phone.substring(phone.length() - 4);
    }

    /**
     * 身份证号脱敏: 110105********1234
     */
    public static String maskIdCard(String idCard) {
        if (StringUtils.isBlank(idCard) || idCard.length() < 10) {
            return idCard;
        }
        return idCard.substring(0, 6)
                + "********"
                + idCard.substring(idCard.length() - 4);
    }

    /**
     * 邮箱脱敏: z***@example.com
     */
    public static String maskEmail(String email) {
        if (StringUtils.isBlank(email) || !email.contains("@")) {
            return email;
        }
        String[] parts = email.split("@", 2);
        String localPart = parts[0];
        String domain = parts[1];
        if (localPart.length() <= 1) {
            return localPart + "***@" + domain;
        }
        return localPart.charAt(0) + "***@" + domain;
    }

    /**
     * 银行卡号脱敏: 6222 **** **** 1236
     * 输出共 4 段：前 4 + 2 组 * 4 + 后 4
     */
    public static String maskBankCard(String bankCard) {
        if (StringUtils.isBlank(bankCard)) {
            return bankCard;
        }
        String cleaned = bankCard.replaceAll("\\s+", "");
        if (cleaned.length() < 8) {
            return bankCard;
        }
        return cleaned.substring(0, 4)
                + " " + "**** " + "**** "
                + cleaned.substring(cleaned.length() - 4);
    }

    /**
     * 姓名脱敏: 张**
     */
    public static String maskName(String name) {
        if (StringUtils.isBlank(name)) {
            return name;
        }
        if (name.length() == 1) {
            return name;
        }
        return name.charAt(0) + "**";
    }

    /**
     * 通用脱敏: 保留前N后M
     */
    public static String mask(String value, int prefixLen, int suffixLen) {
        if (StringUtils.isBlank(value)) {
            return value;
        }
        if (value.length() <= prefixLen + suffixLen) {
            return value;
        }
        return value.substring(0, prefixLen)
                + "****"
                + value.substring(value.length() - suffixLen);
    }
}
```

### Jackson 序列化脱敏（返回给前端时自动脱敏）

```java
// 自定义 Jackson 注解
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
@JacksonAnnotationsInside
@JsonSerialize(using = MaskingSerializer.class)
public @interface Masked {
    MaskType value();
}

public enum MaskType {
    PHONE, ID_CARD, EMAIL, BANK_CARD, NAME
}

public class MaskingSerializer extends JsonSerializer<String> {
    @Override
    public void serialize(String value, JsonGenerator gen,
                           SerializerProvider provider) throws IOException {
        Masked annotation = provider.getCurrentValue()
                .getClass()
                .getDeclaredField(gen.getOutputContext().getCurrentName())
                .getAnnotation(Masked.class);
        // 根据注解类型调用对应脱敏方法
        String masked = switch (annotation.value()) {
            case PHONE -> DataMaskingUtil.maskPhone(value);
            case ID_CARD -> DataMaskingUtil.maskIdCard(value);
            case EMAIL -> DataMaskingUtil.maskEmail(value);
            case BANK_CARD -> DataMaskingUtil.maskBankCard(value);
            case NAME -> DataMaskingUtil.maskName(value);
        };
        gen.writeString(masked);
    }
}

// 使用
public class UserVO {
    @Masked(MaskType.PHONE)
    private String phone;

    @Masked(MaskType.ID_CARD)
    private String idCard;

    @Masked(MaskType.EMAIL)
    private String email;
}
```

---

## API 限流与防刷

### 限流的目的

- 防止恶意刷接口（如短信轰炸、爬虫）
- 保护后端服务不被突发流量击垮
- 保障服务公平使用

### 常见限流算法

| 算法 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| 计数器（固定窗口） | 单位时间内计数，超限拒绝 | 实现简单 | 临界点问题（突刺） |
| 滑动窗口 | 将窗口切分为小格子，滑动计算 | 更平滑 | 内存消耗较大 |
| 漏桶（Leaky Bucket） | 固定速率处理请求 | 平滑输出 | 无法应对突发流量 |
| 令牌桶（Token Bucket） | 按固定速率放令牌，取令牌消费 | 支持突发，最常用 | 实现稍复杂 |

### Guava RateLimiter（令牌桶）

```java
// 单机限流：每秒 100 个请求
RateLimiter rateLimiter = RateLimiter.create(100);

public Response handleRequest(Request req) {
    if (!rateLimiter.tryAcquire()) {
        throw new RateLimitException("请求过于频繁");
    }
    // 处理业务
}
```

### Redis + Lua 分布式限流

基于滑动窗口的 Redis 限流，Lua 脚本保证 ZREMRANGEBYSCORE → ZCARD → ZADD → EXPIRE 的**原子性**。

```java
// Lua 脚本
String luaScript = """
    local key = KEYS[1]
    local limit = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])

    -- 移除窗口外的记录
    redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

    -- 当前窗口内的请求数
    local count = redis.call('ZCARD', key)

    if count < limit then
        -- 记录当前请求
        redis.call('ZADD', key, now, now .. '_' .. math.random())
        redis.call('EXPIRE', key, window)
        return 1  -- 允许
    else
        return 0  -- 拒绝
    end
    """;
```

### Java 调用示例（Spring Data Redis）

```java
@Service
public class RedisRateLimiter {

    @Autowired
    private StringRedisTemplate redisTemplate;

    private final DefaultRedisScript<Long> rateLimitScript;

    public RedisRateLimiter() {
        this.rateLimitScript = new DefaultRedisScript<>();
        this.rateLimitScript.setScriptText(LUA_SCRIPT);
        this.rateLimitScript.setResultType(Long.class);
    }

    /**
     * @param key   限流维度（IP / userId / 接口名）
     * @param limit 窗口内允许的最大请求数
     * @param windowMs 窗口大小（毫秒）
     */
    public boolean tryAcquire(String key, int limit, long windowMs) {
        List<String> keys = Collections.singletonList("rl:" + key);
        long now = System.currentTimeMillis();

        Long result = redisTemplate.execute(
                rateLimitScript,
                keys,
                String.valueOf(limit),
                String.valueOf(windowMs),
                String.valueOf(now)
        );
        return result != null && result == 1L;
    }
}
```

### 故障降级（Fail-Open vs Fail-Closed）

如果 Redis 不可用，应 fail-open（放行）还是 fail-closed（拒绝）？通常 **fail-open 更安全**（避免因限流组件故障导致业务不可用），但需要监控告警。

```java
public boolean tryAcquireSafe(String key, int limit, long windowMs) {
    try {
        return tryAcquire(key, limit, windowMs);
    } catch (RedisConnectionFailureException e) {
        // 告警：限流组件不可用
        metrics.counter("rate_limiter.degraded").increment();
        return true;  // fail-open
    }
}
```

| 策略 | 行为 | 适用场景 |
|------|------|----------|
| **Fail-Open** | 限流组件挂掉时放行全部请求 | 绝大多数业务，优先保证可用性 |
| **Fail-Closed** | 限流组件挂掉时拒绝全部请求 | 极敏感场景（支付、转账防刷），但需谨慎评估雪崩风险 |

### Redis 高可用：Sentinel vs Cluster

| 方案 | 主从复制 | 自动故障转移 | 分片支持 | 适用规模 |
|------|----------|--------------|----------|----------|
| 主从 + Sentinel | ✅ | ✅（秒级） | ❌ | 中小规模（< 数十 GB） |
| Redis Cluster | ✅ | ✅（集群内） | ✅（16384 slot） | 大规模（> 数十 GB / 高 QPS） |

- **Sentinel**：1 主 N 从 + 3 Sentinel 节点，主挂后自动选主，对应用透明。**限流场景推荐 Sentinel**（业务简单、延迟敏感）。
- **Cluster**：数据分片到多主，适合大数据量场景；Lua 脚本需保证 key 在同一 slot（使用 hash tag，如 `rl:{user:1001}`）。

---

## HTTPS 与证书锁定

### 为什么必须使用 HTTPS

- 加密传输数据，防止中间人窃听
- 保证数据完整性，防止篡改
- 身份认证，确保连接的是正确的服务器
- **所有生产环境 API 必须使用 HTTPS**

### 证书锁定（Certificate Pinning）

证书锁定是一种增强安全性的技术，客户端在建立 HTTPS 连接时，不仅验证证书链的有效性，还将服务器证书的公钥（或证书本身）与预存的预期值进行比对。

```
普通 HTTPS:
  客户端 → 验证证书链 → 信任 CA 签发的任何证书

证书锁定:
  客户端 → 验证证书链 → 比对锁定证书/公钥 → 必须匹配
```

### 适用场景

- 移动 App（防止抓包和中间人攻击）
- 微服务之间的 mTLS 通信
- 金融/支付等高安全场景

### 实现方式

```java
// OkHttp 证书锁定示例（Android/Java 客户端）
String pinnedHash = "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";

CertificatePinner certificatePinner = new CertificatePinner.Builder()
    .add("api.example.com", pinnedHash)
    .build();

OkHttpClient client = new OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build();
```

---

## API 安全检查清单

| # | 检查项 | 说明 | 优先级 |
|---|--------|------|--------|
| 1 | **HTTPS** | 所有 API 强制 HTTPS | 必须 |
| 2 | **身份认证** | JWT / OAuth2 等有效 Token | 必须 |
| 3 | **API 签名** | 关键接口使用签名验证 | 高 |
| 4 | **防重放** | Timestamp + Nonce 机制 | 高 |
| 5 | **限流** | 按 IP / 用户 / 接口维度限流 | 高 |
| 6 | **数据脱敏** | 敏感数据返回前脱敏 | 高 |
| 7 | **参数校验** | 输入参数合法性校验（JSR-303） | 必须 |
| 8 | **SQL 注入防护** | 使用预编译语句 / ORM | 必须 |
| 9 | **XSS 防护** | 输出编码 / CSP 头 | 高 |
| 10 | **CSRF 防护** | Token 验证 / SameSite Cookie | 高 |
| 11 | **错误处理** | 不暴露堆栈信息 / 内部错误码 | 必须 |
| 12 | **请求体大小限制** | 防止超大请求导致 OOM | 高 |
| 13 | **日志记录** | 记录关键操作日志（脱敏后） | 高 |
| 14 | **CORS 配置** | 不配置 `Access-Control-Allow-Origin: *` | 高 |
| 15 | **敏感 Header** | 不暴露 `Server`、`X-Powered-By` 等 | 中 |
| 16 | **API 版本控制** | URL 或 Header 中体现版本号 | 中 |
| 17 | **审计日志** | 记录谁在何时做了什么操作 | 高 |
| 18 | **Token 过期** | Access Token 短期有效 + Refresh Token | 必须 |

## 相关章节

- [JWT 存储安全](../jwt-security/README.md) — Token 的安全存储与撤销
- [OAuth2.0 与 OIDC](../oauth2-oidc/README.md) — 访问令牌的签发与生命周期
- [权限模型 RBAC / ABAC](../access-control/02-role-and-attribute/README.md) — 接口背后的权限决策
- [OWASP Top 10](../owasp-top10/README.md) — 应用安全风险全景
- [加密与密钥管理](../encryption/README.md) — HTTPS / 签名背后的密码学基础
- [Spring Cloud Gateway JWT 鉴权实现](../../../06.spring/05-spring-cloud/gateway.md) — 网关层接入点与上下文透传实战

## 参考资料

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [RFC 2104 - HMAC](https://tools.ietf.org/html/rfc2104)
- [Spring Security Documentation](https://docs.spring.io/spring-security/reference/)
