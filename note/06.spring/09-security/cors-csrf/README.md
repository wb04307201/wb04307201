<!--
module:
  parent: spring
  slug: spring/09-security/cors-csrf
  type: article
  category: 主模块子文章
  summary: CORS 跨域资源共享 + CSRF 跨站请求伪造防护，配套 Session 管理与安全 Header，构筑 Web 应用完整安全防线。
-->

# CORS 与 CSRF

> ⬅️ [返回 Spring Security](../README.md)

**CORS（跨域资源共享）** 和 **CSRF（跨站请求伪造）** 是 Web 安全的两个核心话题。Spring Security 对两者都提供了内置支持，同时还包括 Session 管理和安全 Header 等防护机制。

---

## 🎯 一句话定位

**CORS = 控制"谁能跨域访问我的 API"+ CSRF = 防止"恶意网站冒用用户身份发请求"+ Session 管理 = 控制会话安全 + 安全 Header = 防御常见 Web 攻击**——四者构成 Web 应用的完整安全防线。

---

## 一、同源策略与 CORS

### 1.1 同源策略

浏览器的同源策略（Same-Origin Policy）限制不同源之间的资源访问：

```
同源 = 协议 + 域名 + 端口 完全一致

https://api.example.com:443/users  ←→  https://web.example.com:443
  ✅ 协议相同（https）               ❌ 域名不同（api vs web）
  ✅ 端口相同（443）                 → 跨域请求，被同源策略阻止
  
http://localhost:3000  ←→  http://localhost:8080
  ✅ 协议相同                        ❌ 端口不同（3000 vs 8080）
  ✅ 域名相同                        → 跨域请求
```

### 1.2 CORS 预检请求（Preflight）

```
┌──────────┐                                    ┌──────────────┐
│  浏览器   │                                    │   服务器      │
│ web.com  │                                    │  api.com     │
└────┬─────┘                                    └──────┬───────┘
     │                                                 │
     │  ─── 简单请求（GET/POST + 简单 Header） ─────→  │
     │     Origin: https://web.com                     │
     │                                                 │
     │  ←─ Access-Control-Allow-Origin: https://web.com│
     │                                                 │
     │  ─── 复杂请求（PUT/DELETE/自定义 Header） ────→  │
     │                                                 │
     │  ① OPTIONS 预检请求                              │
     │  Origin: https://web.com                        │
     │  Access-Control-Request-Method: PUT             │
     │  Access-Control-Request-Headers: Authorization  │
     │ ──────────────────────────────────────────────→ │
     │                                                 │
     │  ② 预检响应                                     │
     │ ←── Access-Control-Allow-Origin: https://web.com│
     │     Access-Control-Allow-Methods: PUT, GET      │
     │     Access-Control-Allow-Headers: Authorization │
     │     Access-Control-Max-Age: 3600                │
     │                                                 │
     │  ③ 预检通过后，发送实际请求                       │
     │  PUT /api/data                                  │
     │  Authorization: Bearer xxx                      │
     │ ──────────────────────────────────────────────→ │
     │                                                 │
     │  ④ 实际响应                                     │
     │ ←── Access-Control-Allow-Origin: https://web.com│
     │     { "data": "ok" }                            │
```

### 1.3 简单请求 vs 复杂请求

| 条件 | 简单请求 | 复杂请求 |
|:-----|:---------|:---------|
| **方法** | GET / POST / HEAD | PUT / DELETE / PATCH 等 |
| **Content-Type** | text/plain, multipart/form-data, application/x-www-form-urlencoded | application/json 等 |
| **自定义 Header** | 无 | 有（如 Authorization） |
| **预检** | 不发 OPTIONS | 先发 OPTIONS 预检 |

---

## 二、Spring Security CORS 配置

### 2.1 基本配置

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .cors(cors -> cors
            .configurationSource(corsConfigurationSource())
        )
        // ... 其他配置
        ;
    return http.build();
}

@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    
    // 允许的源（生产环境不要用 *）
    config.setAllowedOrigins(List.of(
        "https://web.example.com",
        "https://admin.example.com"
    ));
    
    // 允许的方法
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    
    // 允许的 Header
    config.setAllowedHeaders(List.of(
        "Authorization", "Content-Type", "X-Request-Id"
    ));
    
    // 暴露给前端的 Header（前端 JS 可以读取）
    config.setExposedHeaders(List.of("X-Total-Count", "X-Request-Id"));
    
    // 允许携带 Cookie
    config.setAllowCredentials(true);
    
    // 预检缓存时间（秒）
    config.setMaxAge(3600L);
    
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}
```

### 2.2 不同环境不同策略

```java
@Profile("dev")
@Bean
public CorsConfigurationSource devCorsConfig() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOriginPatterns(List.of("*"));  // 开发环境允许所有源
    config.setAllowedMethods(List.of("*"));
    config.setAllowedHeaders(List.of("*"));
    config.setAllowCredentials(true);
    // ...
}

@Profile("prod")
@Bean
public CorsConfigurationSource prodCorsConfig() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://web.example.com"));
    // 严格限制
    // ...
}
```

### 2.3 @CrossOrigin 注解（方法级）

```java
@RestController
public class ApiController {

    // 单个接口配置 CORS
    @CrossOrigin(
        origins = "https://web.example.com",
        methods = {RequestMethod.GET, RequestMethod.POST},
        allowedHeaders = {"Authorization"},
        maxAge = 3600
    )
    @GetMapping("/api/data")
    public Data getData() { /* ... */ }
}
```

> ⚠️ **Spring Security CORS vs MVC CORS**：Spring Security 的 `CorsFilter` 在 Filter 链中较早执行（在 `CsrfFilter` 之前），推荐使用 Security 层的 CORS 配置。如果用 MVC 层的 `@CrossOrigin`，CORS 预检可能被 CSRF Filter 拦截。

---

## 三、CSRF 攻击原理与防御

### 3.1 CSRF 攻击原理

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CSRF 攻击流程                                   │
│                                                                        │
│  前提：用户已登录 bank.com，浏览器持有 bank.com 的 Session Cookie      │
│                                                                        │
│  1. 用户访问恶意网站 evil.com                                          │
│                                                                        │
│  2. evil.com 页面中隐藏了转账表单：                                    │
│     <form action="https://bank.com/transfer" method="POST">           │
│       <input name="to" value="attacker" />                            │
│       <input name="amount" value="10000" />                           │
│     </form>                                                            │
│     <script>document.forms[0].submit()</script>                        │
│                                                                        │
│  3. 浏览器自动携带 bank.com 的 Cookie 发送请求                         │
│     POST https://bank.com/transfer                                      │
│     Cookie: JSESSIONID=abc123  ← 浏览器自动附带                       │
│     to=attacker&amount=10000                                           │
│                                                                        │
│  4. bank.com 服务器验证 Session 有效 → 执行转账！                      │
│                                                                        │
│  结果：用户的钱被转走，而用户全程不知情                                  │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 CSRF Token 防御机制

```
┌──────────────────────────────────────────────────────────────────────┐
│                     CSRF Token 防御流程                                │
│                                                                        │
│  1. 服务器生成 CSRF Token 并关联到 Session                            │
│     Session: { JSESSIONID: abc123, csrfToken: xyz789 }               │
│                                                                        │
│  2. 渲染表单时嵌入 Token                                              │
│     <form>                                                            │
│       <input type="hidden" name="_csrf" value="xyz789" />            │
│     </form>                                                            │
│                                                                        │
│  3. 表单提交时携带 Token                                              │
│     POST /transfer                                                    │
│     Cookie: JSESSIONID=abc123                                         │
│     _csrf=xyz789 & to=attacker & amount=10000                        │
│                                                                        │
│  4. 服务器比对：Session.csrfToken == 请求._csrf ?                     │
│     ✅ 匹配 → 合法请求                                                │
│     ❌ 不匹配/缺失 → 拒绝（403）                                      │
│                                                                        │
│  恶意网站无法获取 CSRF Token（同源策略阻止读取其他域的页面内容）        │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.3 Spring Security CSRF 配置

```java
// 默认启用 CSRF（Spring Security 默认行为）
// Thymeleaf 表单自动注入 _csrf Token

@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .csrf(csrf -> csrf
            // 1. 自定义 Token 存储（Cookie 方式，SPA 适用）
            .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
            
            // 2. 忽略特定路径（REST API）
            .ignoringRequestMatchers("/api/**", "/webhook/**")
            
            // 3. 自定义请求匹配器（更精细控制）
            .requireCsrfProtectionMatcher(request -> {
                // 只对修改操作（POST/PUT/DELETE）要求 CSRF
                String method = request.getMethod();
                return !("GET".equals(method) || "HEAD".equals(method));
            })
        );

    return http.build();
}
```

### 3.4 CSRF 何时可以禁用？

| 场景 | 是否禁用 CSRF | 原因 |
|:-----|:-------------|:-----|
| **传统 Web（Session + Cookie）** | ❌ 保留 | 浏览器自动发送 Cookie，CSRF 风险存在 |
| **REST API（JWT + Header）** | ✅ 可禁用 | Token 在 Header 中，不受自动发送影响 |
| **REST API（Cookie 认证）** | ❌ 保留 | Cookie 认证仍受 CSRF 威胁 |
| **Webhook / 第三方回调** | ✅ 可禁用 | 第三方无法获取 CSRF Token |
| **公开 API（无认证）** | ✅ 可禁用 | 无 Session，无 CSRF 风险 |

```java
// 无状态 JWT API 禁用 CSRF
http
    .csrf(csrf -> csrf.disable())
    .sessionManagement(session -> session
        .sessionCreationPolicy(SessionCreationPolicy.STATELESS));
```

---

## 四、Session 管理

### 4.1 Session 创建策略

```java
http.sessionManagement(session -> session
    .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)  // 默认
    // ALWAYS       — 每次请求都创建 Session
    // IF_REQUIRED  — 需要时才创建（默认）
    // NEVER        — 不主动创建，但使用已有 Session
    // STATELESS    — 完全不使用 Session（JWT 模式）
);
```

### 4.2 并发会话控制

```java
http.sessionManagement(session -> session
    .maximumSessions(1)                        // 最多 1 个并发会话
    .maxSessionsPreventsLogin(true)            // 达到上限时拒绝新登录（默认踢掉旧会话）
    .expiredUrl("/login?expired=true")         // 被踢掉后重定向的 URL
    .sessionRegistry(sessionRegistry())        // 自定义 SessionRegistry
);

@Bean
public SessionRegistry sessionRegistry() {
    return new SessionRegistryImpl();
}

// 需要在 web.xml 或 Spring Boot 中注册 HttpSessionEventPublisher
@Bean
public HttpSessionEventPublisher httpSessionEventPublisher() {
    return new HttpSessionEventPublisher();
}
```

### 4.3 会话固定攻击防护

```
┌─────────────────────────────────────────────────────────┐
│              会话固定攻击（Session Fixation）              │
│                                                           │
│  1. 攻击者访问网站，获得 Session ID: abc123               │
│  2. 攻击者诱导用户使用该 Session 登录                     │
│     （如：https://bank.com?JSESSIONID=abc123）            │
│  3. 用户登录后，攻击者用 abc123 即可访问用户的会话         │
│                                                           │
│  Spring Security 默认防御：                                │
│  登录成功后自动更换 Session ID（Session Migration）       │
└─────────────────────────────────────────────────────────┘
```

```java
http.sessionManagement(session -> session
    .sessionFixation(fixation -> fixation
        .migrateSession()     // 默认：登录时迁移 Session（更换 ID，保留属性）
        // .newSession()      // 登录时创建全新 Session（不保留属性）
        // .changeSessionId() // Servlet 3.1+：只更换 ID
        // .none()            // 不处理（危险！）
    )
);
```

### 4.4 Session 超时

```yaml
# application.yml
server:
  servlet:
    session:
      timeout: 30m          # Session 超时时间
      cookie:
        http-only: true     # Cookie 不可被 JS 读取
        secure: true        # 仅 HTTPS 发送
        same-site: Lax      # 防 CSRF（Lax/Strict/None）
```

---

## 五、安全 Header

Spring Security 通过 `HeaderWriterFilter` 自动添加安全响应头：

### 5.1 默认安全 Header

| Header | 值 | 防御攻击 |
|:-------|:---|:---------|
| `X-Content-Type-Options` | `nosniff` | MIME 嗅探攻击 |
| `X-Frame-Options` | `DENY` | 点击劫持（Clickjacking） |
| `X-XSS-Protection` | `0`（6.x 默认禁用） | XSS（已被 CSP 取代） |
| `Cache-Control` | `no-cache, no-store, max-age=0` | 缓存泄露 |
| `Pragma` | `no-cache` | HTTP/1.0 缓存 |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | 协议降级（HTTP 劫持） |

### 5.2 自定义安全 Header

```java
http.headers(headers -> headers
    // X-Frame-Options（点击劫持防护）
    .frameOptions(frame -> frame
        .deny()                  // 禁止 iframe 嵌入
        // .sameOrigin()         // 允许同域 iframe（如内嵌报表）
    )
    
    // Content-Security-Policy（CSP）
    .contentSecurityPolicy(csp -> csp
        .policyDirectives(
            "default-src 'self'; " +
            "script-src 'self' 'unsafe-inline' https://cdn.example.com; " +
            "style-src 'self' 'unsafe-inline'; " +
            "img-src 'self' data: https:; " +
            "font-src 'self' https://fonts.gstatic.com; " +
            "connect-src 'self' https://api.example.com"
        )
    )
    
    // HSTS（强制 HTTPS）
    .httpStrictTransportSecurity(hsts -> hsts
        .maxAgeInSeconds(31536000)     // 1 年
        .includeSubDomains(true)
        .preload(true)                 // 加入 HSTS 预加载列表
    )
    
    // Referrer-Policy
    .referrerPolicy(referrer -> referrer
        .policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN)
    )
    
    // Permissions-Policy（限制浏览器功能）
    .permissionsPolicy(permissions -> permissions
        .policy("geolocation=(), camera=(), microphone=()")
    )
    
    // 自定义 Header
    .addHeaderWriter(new StaticHeadersWriter(
        "X-Custom-Security", "enabled"
    ))
);
```

### 5.3 CSP（Content Security Policy）详解

CSP 是防御 XSS 攻击的最有效手段：

```
┌─────────────────────────────────────────────────────────┐
│              CSP 指令速查                                  │
├──────────────────────┬──────────────────────────────────┤
│ default-src 'self'   │ 默认只允许同源资源                │
│ script-src 'self'    │ JS 只允许同源                    │
│ 'unsafe-inline'      │ 允许内联脚本（不推荐）            │
│ 'unsafe-eval'        │ 允许 eval()（不推荐）             │
│ 'nonce-abc123'       │ 允许带指定 nonce 的脚本           │
│ style-src 'self'     │ CSS 只允许同源                   │
│ img-src 'self' data: │ 图片允许同源和 data URI           │
│ connect-src 'self'   │ XHR/fetch 只允许同源             │
│ frame-ancestors 'none'│ 禁止 iframe 嵌入（替代 X-Frame） │
│ report-uri /csp-report│ 违规报告上报地址                 │
└──────────────────────┴──────────────────────────────────┘
```

```java
// 生产级 CSP 配置
String cspPolicy = String.join("; ",
    "default-src 'self'",
    "script-src 'self' 'nonce-{nonce}'",     // 使用 nonce 代替 unsafe-inline
    "style-src 'self' 'unsafe-inline'",      // CSS 框架可能需要 unsafe-inline
    "img-src 'self' data: https:",
    "font-src 'self' https://fonts.gstatic.com",
    "connect-src 'self' https://api.example.com wss://ws.example.com",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "report-uri /api/csp-report"
);
```

---

## 六、综合安全配置模板

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class ProductionSecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // 1. CORS
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            
            // 2. CSRF（REST API 禁用）
            .csrf(csrf -> csrf.disable())
            
            // 3. 安全 Header
            .headers(headers -> headers
                .frameOptions(frame -> frame.deny())
                .contentSecurityPolicy(csp -> csp
                    .policyDirectives("default-src 'self'"))
                .httpStrictTransportSecurity(hsts -> hsts
                    .maxAgeInSeconds(31536000)
                    .includeSubDomains(true))
            )
            
            // 4. Session（无状态 JWT 模式）
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            
            // 5. 授权规则
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/auth/**", "/public/**", "/health").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.DELETE, "/api/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            
            // 6. JWT 认证
            .addFilterBefore(jwtAuthenticationFilter, 
                UsernamePasswordAuthenticationFilter.class)
            
            // 7. 异常处理
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint((request, response, authException) -> {
                    response.setContentType("application/json");
                    response.setStatus(HttpStatus.UNAUTHORIZED.value());
                    response.getWriter().write(
                        "{\"error\":\"unauthorized\",\"message\":\"请先登录\"}");
                })
                .accessDeniedHandler((request, response, accessDeniedException) -> {
                    response.setContentType("application/json");
                    response.setStatus(HttpStatus.FORBIDDEN.value());
                    response.getWriter().write(
                        "{\"error\":\"forbidden\",\"message\":\"权限不足\"}");
                })
            );

        return http.build();
    }
}
```

---

## 七、面试要点

| 问题 | 核心答案 |
|:-----|:---------|
| CORS 预检请求什么时候触发？ | 非简单请求（PUT/DELETE/自定义 Header/非简单 Content-Type）触发 OPTIONS 预检 |
| `allowedOrigins("*")` 和 `allowCredentials(true)` 能同时使用吗？ | 不能，浏览器会报错。需要用 `allowedOriginPatterns("*")` 替代 |
| CSRF Token 为什么能防 CSRF？ | 恶意网站无法读取其他域的页面内容（同源策略），因此拿不到 CSRF Token |
| JWT 认证为什么不需要 CSRF？ | JWT 放在 Header 中，不在 Cookie 中，浏览器不会自动发送 |
| `SameSite=Strict` 和 `SameSite=Lax` 的区别？ | `Strict` 禁止所有跨域请求携带 Cookie；`Lax` 允许顶级导航（如链接跳转）携带 |
| CSP 的 `nonce` 和 `unsafe-inline` 哪个更安全？ | `nonce` 更安全——每个请求生成唯一 nonce，只允许带匹配 nonce 的脚本执行 |

---

← [返回: Spring Security](../README.md)
