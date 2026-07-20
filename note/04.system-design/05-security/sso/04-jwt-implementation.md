<!--
module:
  parent: 04.system-design/05-security/sso
  slug: system-design/05-security/sso/04-jwt-implementation
  type: topic
  category: JWT 实战
  summary: JWT 自建 + Redis 黑名单 + Refresh Token + 5 大反模式
-->

# JWT 自建 SSO · Token + Redis 黑名单实战

> **一句话**：JWT 自建 = 自签自验 + 黑名单撤销——简单但 IdP 缺位，需配合 Redis 黑名单 + Refresh Token Rotate 弥补。

← [返回: SSO 总目录](../README.md)

---

## 1. JWT vs IdP 模式对比

| 维度 | JWT 自建 | OAuth2 + OIDC |
|------|---------|--------------|
| 颁发 | 自建服务 | 第三方 IdP（Keycloak 等）|
| 验证 | 子系统本地验签 | 子系统本地验签 JWT |
| 撤销 | 需 Redis 黑名单 | IdP 集中失效 |
| 集中登录 | 需自建 | 内置 |
| 复杂度 | 低 | 中 |
| 适合 | 微服务内部 | 互联网 SSO |

---

## 2. JWT 3 段结构

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsIm5hbWUiOiJaaGFuZ3NhbiIsInJvbGUiOiJBRE1JTiIsImV4cCI6MTY5MzAwMDAwMH0.7s5fz3Ik_vd3P0Eq5TLfBTjKxE5dUKj-7wDJr5L4c1Q
└─────── Header ──────────┘  └────────────── Payload (Claims) ──────────────┘  └───── Signature ─────┘
```

| 段 | 内容 | 示例 |
|----|------|------|
| **Header** | 算法 + 类型 | `{"alg":"HS256","typ":"JWT"}` |
| **Payload** | Claims（用户信息 + 元数据）| `{"sub":"user-123","role":"ADMIN","exp":...}` |
| **Signature** | HMAC(header.payload, secret) | 数字签名 |

---

## 3. JWT 实战代码

### 3.1 颁发 JWT

```java
@Service
public class JwtService {
    private static final String SECRET = "your-256-bit-secret-key-change-in-production";
    private static final long ACCESS_TOKEN_TTL = 3600_000;        // 1h
    private static final long REFRESH_TOKEN_TTL = 7 * 24 * 3600_000; // 7d
    
    public TokenPair issueTokens(String username, List<String> roles) {
        Date now = new Date();
        
        // Access Token
        String accessToken = Jwts.builder()
            .setSubject(username)
            .claim("roles", roles)
            .setIssuedAt(now)
            .setExpiration(new Date(now.getTime() + ACCESS_TOKEN_TTL))
            .signWith(SignatureAlgorithm.HS256, SECRET)
            .compact();
        
        // Refresh Token（独立 secret + 长 TTL）
        String refreshToken = Jwts.builder()
            .setSubject(username)
            .setIssuedAt(now)
            .setExpiration(new Date(now.getTime() + REFRESH_TOKEN_TTL))
            .signWith(SignatureAlgorithm.HS256, REFRESH_SECRET)  // 独立 secret
            .compact();
        
        return new TokenPair(accessToken, refreshToken, "Bearer", ACCESS_TOKEN_TTL);
    }
}
```

### 3.2 验签 JWT

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse resp, FilterChain chain) {
        String token = extractToken(req);  // 从 Authorization: Bearer xxx 取
        if (token == null) {
            chain.doFilter(req, resp);
            return;
        }
        
        try {
            // Step 1: 验签
            Claims claims = Jwts.parser()
                .setSigningKey(SECRET)
                .parseClaimsJws(token)
                .getBody();
            
            // Step 2: 检查黑名单（防止已撤销 token）
            if (tokenBlacklist.isBlacklisted(token)) {
                throw new JwtException("Token has been revoked");
            }
            
            // Step 3: 检查过期（parseClaimsJws 默认检查，但可手动）
            if (claims.getExpiration().before(new Date())) {
                throw new JwtException("Token expired");
            }
            
            // Step 4: 设置 Authentication
            List<SimpleGrantedAuthority> authorities = ((List<String>) claims.get("roles")).stream()
                .map(role -> new SimpleGrantedAuthority("ROLE_" + role))
                .toList();
            UsernamePasswordAuthenticationToken auth = 
                new UsernamePasswordAuthenticationToken(claims.getSubject(), null, authorities);
            SecurityContextHolder.getContext().setAuthentication(auth);
            
        } catch (JwtException e) {
            // 不通过，过滤链继续（Spring Security 会拒绝）
            SecurityContextHolder.clearContext();
        }
        
        chain.doFilter(req, resp);
    }
}
```

### 3.3 Refresh Token 刷新

```java
@PostMapping("/refresh")
public ResponseEntity<TokenPair> refresh(@RequestBody RefreshRequest req) {
    Claims claims = Jwts.parser()
        .setSigningKey(REFRESH_SECRET)
        .parseClaimsJws(req.getRefreshToken())
        .getBody();
    
    // 黑名单：旧 Refresh Token 加入黑名单（Rotate）
    tokenBlacklist.add(req.getRefreshToken(), 24 * 3600_000);  // TTL = refresh 剩余有效期
    
    // 颁发新 Access + Refresh
    return ResponseEntity.ok(jwtService.issueTokens(claims.getSubject(), claims.get("roles")));
}
```

---

## 4. 5 大反模式

### ⚠️ 反模式 1：JWT 一旦颁发，无法撤销

- **错**：JWT 默认无黑名单机制
- **真**：JWT 在过期前都有效（泄露即风险）
- **正解**：Redis 黑名单（撤销后写入，TTL = 剩余有效期）

### ⚠️ 反模式 2：Access Token 设超长有效期（30 天）

- **错**：用户希望"一个月不登录"
- **真**：泄露后 30 天都能用
- **正解**：Access Token 1h + Refresh Token 7d + Rotate

### ⚠️ 反模式 3：把密码放 JWT Claims

- **错**：`claims.put("password", "xxx")`
- **真**：JWT 是 Base64 编码，**任何人都能解码读**
- **正解**：Claims 只放必要信息（sub / role / email）

### ⚠️ 反模式 4：HS256 + 单 secret

- **错**：所有子系统共享 1 个 HS256 secret
- **真**：1 个子系统泄露 = 全部泄露
- **正解**：用 RS256（RSA 密钥对），IdP 私钥签，子系统公钥验

### ⚠️ 反模式 5：Refresh Token 永远不过期 + 不 Rotate

- **错**：Refresh Token 设 1 年有效，且不 Rotate
- **真**：Refresh Token 泄露，攻击者能持续换 Access Token
- **正解**：每次 Refresh 换新 Token（旧 Token 加入黑名单）

---

## 5. Redis 黑名单设计

### 5.1 选型：为什么用 Redis

- 内存 KV 存储，TTL 自动过期
- 高性能（毫秒级）
- 集群支持
- 单点 IdP 可共享

### 5.2 黑名单服务

```java
@Service
public class TokenBlacklistService {
    
    @Autowired
    private StringRedisTemplate redis;
    
    private static final String BLACKLIST_KEY = "jwt:blacklist:";
    
    /**
     * 加入黑名单（撤销 token）
     * @param token JWT token
     * @param remainingTtlMs 剩余有效期（毫秒）
     */
    public void add(String token, long remainingTtlMs) {
        redis.opsForValue().set(
            BLACKLIST_KEY + token.hashCode(),
            "revoked",
            Duration.ofMillis(remainingTtlMs)
        );
    }
    
    /**
     * 检查 token 是否被撤销
     */
    public boolean isBlacklisted(String token) {
        return redis.hasKey(BLACKLIST_KEY + token.hashCode());
    }
}
```

### 5.3 用户主动登出

```java
@PostMapping("/logout")
public ResponseEntity<?> logout(HttpServletRequest req) {
    String token = extractToken(req);
    if (token != null) {
        Claims claims = Jwts.parser()
            .setSigningKey(SECRET)
            .parseClaimsJws(token)
            .getBody();
        long remaining = claims.getExpiration().getTime() - System.currentTimeMillis();
        if (remaining > 0) {
            tokenBlacklist.add(token, remaining);
        }
    }
    return ResponseEntity.ok().build();
}
```

---

## 6. JwtFilter + Spring Security 整合

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/auth/login").permitAll()
                .requestMatchers("/auth/refresh").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter(), 
                              UsernamePasswordAuthenticationFilter.class)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(c -> c.disable());  // JWT 系统不需要 CSRF
        return http.build();
    }
    
    @Bean
    public JwtAuthenticationFilter jwtAuthenticationFilter() {
        return new JwtAuthenticationFilter();
    }
}
```

---

## 7. JWT vs OAuth2 + OIDC 选型

| 维度 | JWT 自建 | OAuth2 + OIDC |
|------|---------|--------------|
| **完整 SSO** | ❌（需自建登录页 / 用户管理） | ✅ |
| **集中失效** | ❌（需自建黑名单） | ✅（IdP 控制） |
| **Token 撤销** | ⚠️（黑名单） | ✅（Token Introspection） |
| **实现简单** | ✅ | ⚠️ |
| **第三方支持** | ❌ | ✅ |

**实战**：
- 内部微服务 → JWT 自建
- 互联网产品 → OAuth2 + OIDC
- 已有 Keycloak → 用 Keycloak

---

## 8. 一句话总结

> **JWT 自建 SSO = 自签发 + 黑名单撤销 + Refresh Token Rotate + RS256 + HTTPS。简单但需自建登录页 + 用户管理——仅适合微服务内部，互联网首选 OAuth2+OIDC。**

---

← [返回: SSO 总目录](../README.md) · 上一章：[03-spring-security-implementation](03-spring-security-implementation.md) · 下一章：[05-selection-decision-tree](05-selection-decision-tree.md)
