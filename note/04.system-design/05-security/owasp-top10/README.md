<!--
module:
  parent: system-design
  slug: system-design/owasp-top10
  type: article
  category: 主模块子文章
  summary: OWASP（Open Worldwide Application Security Project）Top 10 是业界公认最权威的 Web 应用安全风险清单，...
-->

# OWASP Top 10（2021）

> OWASP（Open Worldwide Application Security Project）Top 10 是业界公认最权威的 Web 应用安全风险清单，每隔几年更新一次。本文基于 **2021 版**（最新一版）逐项解读，并给出代码层防御建议。完整列表见 <https://owasp.org/Top10/>。

## 目录

- [A01: 失效的访问控制（Broken Access Control）](#a01-失效的访问控制broken-access-control)
- [A02: 加密失败（Cryptographic Failures）](#a02-加密失败cryptographic-failures)
- [A03: 注入（Injection）](#a03-注入injection)
- [A04: 不安全设计（Insecure Design）](#a04-不安全设计insecure-design)
- [A05: 安全配置错误（Security Misconfiguration）](#a05-安全配置错误security-misconfiguration)
- [A06: 易受攻击和过时的组件（Vulnerable Components）](#a06-易受攻击和过时的组件vulnerable-components)
- [A07: 身份识别和认证失败（Authentication Failures）](#a07-身份识别和认证失败authentication-failures)
- [A08: 软件和数据完整性故障（Software & Data Integrity Failures）](#a08-软件和数据完整性故障software--data-integrity-failures)
- [A09: 安全日志和监控故障（Logging & Monitoring Failures）](#a09-安全日志和监控故障logging--monitoring-failures)
- [A10: 服务端请求伪造（SSRF）](#a10-服务端请求伪造ssrf)
- [参考资料](#参考资料)

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

OWASP Top 10（2021） 本应该很简单，OWASP（Open Worldwide Application Security Project）Top 10 是业界公认最权威的 Web 应用安全风险清单，每隔几年更新一次。本文基于 **2021 版**（最新一版）逐项解读，并给出代码

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## A01: 失效的访问控制（Broken Access Control）

**风险描述**：用户在已认证的情况下，越权访问其他用户的资源或执行未授权操作。常见表现：水平越权、垂直越权、IDOR。

**示例攻击**：

```
正常用户 Alice 登录后看到：
GET /api/users/1001/orders        # 自己的订单

攻击：
GET /api/users/1002/orders        # 越权查看 Bob 的订单
```

**代码层防御**：

```java
@GetMapping("/users/{userId}/orders")
public List<Order> getOrders(@PathVariable Long userId, Authentication auth) {
    // 1. 始终校验资源归属
    if (!userId.equals(((UserPrincipal) auth.getPrincipal()).getId())) {
        throw new AccessDeniedException("无权访问他人资源");
    }
    // 2. 或使用 @PreAuthorize 声明式
    return orderService.findByUserId(userId);
}

// 推荐：声明式
@PreAuthorize("@ownershipCheck.isOwner(#userId, authentication)")
@GetMapping("/users/{userId}/orders")
public List<Order> getOrders(@PathVariable Long userId) {
    return orderService.findByUserId(userId);
}
```

更多内容见 [权限模型 RBAC / ABAC](../access-control/02-role-and-attribute/README.md)。

---

## A02: 加密失败（Cryptographic Failures）

**风险描述**：未加密的敏感数据、弱算法、错误的密钥管理。表现：明文存储密码、HTTP 传输敏感数据、MD5/SHA1 散列密码。

**示例攻击**：

- 数据库泄露后，明文密码 / 弱散列密码（MD5）可被彩虹表秒破
- HTTP 中间人攻击窃听登录态

**代码层防御**：

```java
// 错误：MD5 散列密码
String hashed = DigestUtils.md5Hex(password);

// 正确：BCrypt（自适应 cost）
BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);
String hashed = encoder.encode(password);
boolean ok = encoder.matches(password, hashed);

// 敏感字段加密（AES-GCM）
public String encrypt(String plaintext, SecretKey key) {
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    byte[] iv = new byte[12];
    SecureRandom random = new SecureRandom();
    random.nextBytes(iv);
    GCMParameterSpec spec = new GCMParameterSpec(128, iv);
    cipher.init(Cipher.ENCRYPT_MODE, key, spec);
    byte[] ct = cipher.doFinal(plaintext.getBytes(StandardCharsets.UTF_8));
    return Base64.getEncoder().encodeToString(iv) + ":" + Base64.getEncoder().encodeToString(ct);
}
```

---

## A03: 注入（Injection）

**风险描述**：将不可信输入拼接进解释器命令或查询中。SQL 注入、NoSQL 注入、LDAP 注入、OS 命令注入。

**示例攻击**：

```sql
-- 拼接 SQL
SELECT * FROM users WHERE name = '${name}' AND password = '${pwd}'
-- 攻击：name = ' OR '1'='1
```

**代码层防御**：

```java
// 错误：字符串拼接
String sql = "SELECT * FROM users WHERE name = '" + name + "'";

// 正确：参数化预编译
PreparedStatement ps = conn.prepareStatement(
    "SELECT * FROM users WHERE name = ? AND password = ?");
ps.setString(1, name);
ps.setString(2, pwd);

// ORM（JPA / MyBatis）默认参数化
@Query("SELECT u FROM User u WHERE u.name = :name")
User findByName(@Param("name") String name);

// OS 命令：避免拼接；用 ProcessBuilder + 白名单
ProcessBuilder pb = new ProcessBuilder("ls", "-l", validatedDir);
```

---

## A04: 不安全设计（Insecure Design）

**风险描述**：设计层面的安全缺失——缺乏威胁建模、无安全控制、信任边界模糊。不同于"实现 bug"，是"架构缺陷"。

**示例**：

- 密码重置链接使用可猜测的 token（递增 ID）
- 抽奖 / 秒杀无风控
- 业务关键操作（转账）无二次确认

**代码层防御**：

- 在设计阶段引入**威胁建模（STRIDE）**
- 关键操作强制**二次验证 / 多因素认证**
- 业务层做**限流 + 风控**，不能只靠网关

```java
// 关键操作需二次确认
@PostMapping("/transfer")
@PreAuthorize("hasRole('USER')")
public Result transfer(@RequestBody TransferRequest req,
                       @RequestHeader("X-2FA-Token") String twoFaToken) {
    if (!twoFactorService.verify(req.getUserId(), twoFaToken)) {
        throw new AccessDeniedException("需要二次验证");
    }
    if (riskControlService.isHighRisk(req)) {
        throw new BusinessException("交易触发风控，请人工审核");
    }
    return accountService.transfer(req);
}
```

---

## A05: 安全配置错误（Security Misconfiguration）

**风险描述**：默认配置未改、错误页暴露堆栈、开放多余端口、CORS 配置过宽、目录列表开启、调试模式在线上启用。

**示例**：

- Spring Boot Actuator 的 `/env`、`/heapdump` 未鉴权
- 生产环境启用 `show_errors=On` 暴露堆栈
- 跨域 `Access-Control-Allow-Origin: *` 配合 `Allow-Credentials: true`

**代码层防御**：

```yaml
# application-prod.yml
server:
  error:
    include-stacktrace: never
    include-message: never

management:
  endpoints:
    web:
      exposure:
        include: health, info
  endpoint:
    env:
      enabled: false        # 关闭 /env
    heapdump:
      enabled: false        # 关闭 /heapdump
```

```java
// CORS 严格配置
@Bean
public CorsConfigurationSource corsSource() {
    CorsConfiguration cfg = new CorsConfiguration();
    cfg.setAllowedOrigins(List.of("https://app.example.com"));
    cfg.setAllowedMethods(List.of("GET", "POST"));
    cfg.setAllowCredentials(true);
    cfg.setMaxAge(3600L);
    UrlBasedCorsConfigurationSource src = new UrlBasedCorsConfigurationSource();
    src.registerCorsConfiguration("/api/**", cfg);
    return src;
}
```

---

## A06: 易受攻击和过时的组件（Vulnerable Components）

**风险描述**：使用了含有已知漏洞的第三方库、框架、运行时。Log4Shell、Spring4Shell 等都是典型案例。

**代码层防御**：

1. **依赖管理**：
   - 使用 BOM（Bill of Materials）锁定版本
   - CI 跑 `mvn dependency-check` / `npm audit`

```xml
<!-- pom.xml 中锁定 Spring 版本 -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>3.2.5</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

2. **镜像仓库**：使用内部 Nexus / Artifactory 镜像，避免拉取外部不可信包。
3. **及时升级**：建立 SCA（Software Composition Analysis）流程。
4. **运行时隔离**：容器化部署可限制爆炸半径。

---

## A07: 身份识别和认证失败（Authentication Failures）

**风险描述**：弱密码策略、缺少多因素、Session ID 泄露、密码爆破、凭证填充攻击（Credential Stuffing）。

**示例攻击**：

- 撞库：拿已知泄露的邮箱/密码去尝试登录
- 暴力破解：脚本不断 POST 登录接口

**代码层防御**：

```java
@PostMapping("/login")
public LoginResult login(@RequestBody @Valid LoginRequest req,
                         HttpServletRequest request) {
    // 1. 限流（防爆破）
    if (!rateLimiter.tryAcquire("login:" + req.getUsername(), 5, 60_000)) {
        throw new RateLimitException("尝试次数过多，请稍后再试");
    }
    // 2. 校验（防 SQL 注入 / 注入 null 字节）
    if (!StringUtils.hasText(req.getUsername()) || !StringUtils.hasText(req.getPassword())) {
        throw new BadCredentialsException("凭证错误");
    }
    // 3. 认证
    Authentication auth = authenticationManager.authenticate(
        new UsernamePasswordAuthenticationToken(req.getUsername(), req.getPassword()));
    // 4. 失败计数（账户锁定）
    loginAttemptService.recordFailure(req.getUsername());
    // 5. 会话固定防护：登录成功后生成新 Session ID
    request.changeSessionId();
    return new LoginResult(jwtService.issue(auth));
}
```

更多内容见 [JWT 存储安全](../jwt-security/README.md)。

---

## A08: 软件和数据完整性故障（Software & Data Integrity Failures）

**风险描述**：未验证 CI/CD 流水线、应用插件的完整性和来源。SolarWinds 事件、依赖混淆攻击（Dependency Confusion）是典型。

**示例攻击**：

- 内部 Maven 私有仓库命名 `com.company:utils`，攻击者上传同名包到 Maven Central
- 反序列化不可信数据 → 远程代码执行

**代码层防御**：

```xml
<!-- Maven: 限定仓库优先级 -->
<repositories>
    <repository>
        <id>internal-nexus</id>
        <url>https://nexus.example.com/repository/maven-internal/</url>
        <releases><enabled>true</enabled></releases>
    </repository>
    <!-- 关闭 / 限制 Maven Central -->
</repositories>
```

```java
// 反序列化：使用白名单 + 完整性校验
ObjectInputStream ois = new ObjectInputStream(input) {
    @Override
    protected Class<?> resolveClass(ObjectStreamClass desc) {
        if (!ALLOWED_CLASSES.contains(desc.getName())) {
            throw new InvalidClassException("Unauthorized deserialization");
        }
        return super.resolveClass(desc);
    }
};

// 推荐：使用 JSON（Jackson）替代 Java 序列化
```

---

## A09: 安全日志和监控故障（Logging & Monitoring Failures）

**风险描述**：缺少审计日志、登录失败、权限提升等关键事件未记录；无告警；日志被攻击者清除。

**代码层防御**：

```java
@Aspect
@Component
public class SecurityAuditAspect {

    private static final Logger AUDIT = LoggerFactory.getLogger("SECURITY_AUDIT");

    @AfterReturning("@annotation(auditLog)")
    public void auditSuccess(JoinPoint jp, AuditLog auditLog) {
        AUDIT.info("action={} user={} target={} result=success ts={}",
                auditLog.action(),
                SecurityContext.getCurrentUserId(),
                Arrays.toString(jp.getArgs()),
                Instant.now());
    }

    @AfterThrowing(pointcut = "@annotation(auditLog)", throwing = "ex")
    public void auditFailure(JoinPoint jp, AuditLog auditLog, Throwable ex) {
        AUDIT.warn("action={} user={} result=fail reason={} ts={}",
                auditLog.action(),
                SecurityContext.getCurrentUserId(),
                ex.getMessage(),
                Instant.now());
        alertingService.send("security-audit", "Operation failed: " + auditLog.action());
    }
}
```

- 日志集中到 ELK / Loki，开启告警（短时间内大量失败登录）
- 日志本身**不可被应用修改**（写入 append-only 存储或 SIEM）

---

## A10: 服务端请求伪造（SSRF）

**风险描述**：服务端接收用户输入的 URL 并发起请求，攻击者诱导服务端访问内网资源、读取本地文件、攻击云元数据服务（`169.254.169.254`）。

**示例攻击**：

```
POST /api/avatar/fetch
{ "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/" }
→ 服务端把云 IAM 凭据回显给攻击者
```

**代码层防御**：

```java
public byte[] fetchImage(String url) {
    URI uri = URI.create(url);
    String host = uri.getHost();

    // 1. 协议白名单
    if (!"https".equalsIgnoreCase(uri.getScheme())) {
        throw new IllegalArgumentException("仅允许 HTTPS");
    }

    // 2. 解析 IP 后检查是否在黑名单
    InetAddress addr = InetAddress.getByName(host);
    if (addr.isLoopbackAddress() || addr.isSiteLocalAddress()
            || addr.isAnyLocalAddress() || addr.isLinkLocalAddress()) {
        throw new SecurityException("禁止访问内网地址");
    }
    // 云元数据 IP：169.254.169.254
    if ("169.254.169.254".equals(addr.getHostAddress())) {
        throw new SecurityException("禁止访问云元数据");
    }

    // 3. DNS 解析后再做一次 IP 检查（防 DNS rebinding）
    // 4. 设置连接超时 & 最大字节数
    HttpURLConnection conn = (HttpURLConnection) uri.toURL().openConnection();
    conn.setConnectTimeout(3000);
    conn.setReadTimeout(3000);
    conn.setInstanceFollowRedirects(false);
    // 5. 限制响应大小
    InputStream in = conn.getInputStream();
    byte[] buf = in.readNBytes(1024 * 1024);  // max 1MB
    return buf;
}
```

更多云原生场景下的 SSRF 见相关安全规范。

---

## 参考资料

- [OWASP Top 10 官网（2021）](https://owasp.org/Top10/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
- [NIST SP 800-53 Security Controls](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
