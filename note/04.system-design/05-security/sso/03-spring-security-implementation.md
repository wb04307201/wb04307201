<!--
module:
  parent: 04.system-design/05-security/sso
  slug: system-design/05-security/sso/03-spring-security
  type: topic
  category: Spring Security 实战
  summary: Spring Authorization Server 配置 OAuth2 + OIDC IdP + Spring Security 资源服务器 + JWT 验签
-->

# Spring Security SSO 实战 · OAuth2 + OIDC 配置

> **一句话**：Java 后端 SSO 首选 **Spring Authorization Server** + **Spring Security 资源服务器** 组合——IdP 用 Spring Authorization Server，业务系统用 Spring Security 验证 JWT。

← [返回: SSO 总目录](../README.md)

---

## 1. 整体架构

```
┌──────────────────────────────────────────────────────────┐
│  Spring Authorization Server (IdP)                       │
│  - 颁发 Access Token + ID Token (JWT)                     │
│  - UserDetails / OAuth2 User                              │
│  - /oauth2/authorize, /token, /userinfo, /.well-known/..  │
│  - 默认数据库用户（可对接 LDAP / 第三方）                  │
└──────────────────────────────────────────────────────────┘
                          ↑
        JWT 签名 / 验签 ↓
┌──────────────────────────────────────────────────────────┐
│  业务系统（Spring Security OAuth2 Resource Server）         │
│  - 验证 JWT 签名 + scope + 角色                            │
│  - @PreAuthorize / SecurityFilterChain                    │
└──────────────────────────────────────────────────────────┘
```

---

## 2. IdP：Spring Authorization Server 配置

### 2.1 添加依赖

```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-oauth2-authorization-server</artifactId>
    <version>1.2.0</version>
</dependency>
```

### 2.2 Authorization Server 配置

```java
@Configuration
@EnableAuthorizationServer
public class AuthorizationServerConfig {

    @Bean
    public RegisteredClientRepository registeredClientRepository() {
        // 注册客户端（业务系统）
        RegisteredClient appA = RegisteredClient.withId(UUID.randomUUID().toString())
            .clientId("app-a")
            .clientSecret("{noop}app-a-secret")  // 生产用 BCrypt
            .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_BASIC)
            .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
            .authorizationGrantType(AuthorizationGrantType.REFRESH_TOKEN)
            .redirectUri("https://app-a.com/callback")
            .postLogoutRedirectUri("https://app-a.com/")
            .scope("openid")     // OIDC 关键
            .scope("profile")
            .scope("email")
            .scope("read")
            .scope("write")
            .tokenSettings(TokenSettings.builder()
                .accessTokenFormat(OAuth2TokenFormat.SELF_CONTAINED)  // JWT
                .accessTokenTimeToLive(Duration.ofHours(1))
                .refreshTokenTimeToLive(Duration.ofDays(7))
                .build())
            .clientSettings(ClientSettings.builder()
                .requireProofKey(true)  // 强制 PKCE
                .build())
            .build();
        
        return new InMemoryRegisteredClientRepository(appA);
    }
    
    @Bean
    public JWKSource<SecurityContext> jwkSource() {
        // RSA 密钥对（生产用 KeyStore）
        KeyPair keyPair = generateRsaKey();
        RSAPublicKey publicKey = (RSAPublicKey) keyPair.getPublic();
        RSAPrivateKey privateKey = (RSAPrivateKey) keyPair.getPrivate();
        RSAKey rsaKey = new RSAKey.Builder(publicKey)
            .privateKey(privateKey)
            .keyID(UUID.randomUUID().toString())
            .build();
        JWKSet jwkSet = new JWKSet(rsaKey);
        return new ImmutableJWKSet<>(jwkSet);
    }
    
    @Bean
    public AuthorizationServerSettings authorizationServerSettings() {
        return AuthorizationServerSettings.builder()
            .issuer("https://idp.example.com")
            .authorizationEndpoint("/oauth2/authorize")
            .tokenEndpoint("/oauth2/token")
            .jwkSetEndpoint("/oauth2/jwks")
            .userinfoEndpoint("/userinfo")
            .build();
    }
}
```

### 2.3 UserDetails / 认证配置

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {
    
    @Override
    public UserDetails loadUserByUsername(String username) {
        // 实际从 DB / LDAP / 飞书 / 钉钉 加载
        return User.withUsername("zhangsan")
            .password("{noop}password123")
            .roles("USER", "ADMIN")
            .build();
    }
}
```

### 2.4 启动类

```java
@SpringBootApplication
@EnableAuthorizationServer
public class IdpApplication {
    public static void main(String[] args) {
        SpringApplication.run(IdpApplication.class, args);
    }
}
```

---

## 3. 资源服务器（业务系统）：Spring Security 配置

### 3.1 添加依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
</dependency>
```

### 3.2 application.yml

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          # IdP 的 issuer URI（Spring 自动发现 /.well-known/openid-configuration）
          issuer-uri: https://idp.example.com
          # 或手动指定 JWK 端点
          # jwk-set-uri: https://idp.example.com/oauth2/jwks
```

### 3.3 SecurityFilterChain 配置

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class ResourceServerConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/admin/**").hasAuthority("SCOPE_admin")
                .requestMatchers("/api/**").authenticated()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt
                    .jwtAuthenticationConverter(jwtAuthConverter())
                )
            )
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS));
        return http.build();
    }
    
    private JwtAuthenticationConverter jwtAuthConverter() {
        // 默认转换器：scope → SCOPE_xxx 权限
        JwtGrantedAuthoritiesConverter scopes = new JwtGrantedAuthoritiesConverter();
        scopes.setAuthorityPrefix("SCOPE_");
        scopes.setAuthoritiesClaimName("scope");
        
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(scopes);
        return converter;
    }
}
```

### 3.4 业务代码

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping("/me")
    @PreAuthorize("isAuthenticated()")
    public Map<String, Object> me(@AuthenticationPrincipal Jwt jwt) {
        // 直接从 JWT 拿用户信息
        return Map.of(
            "sub", jwt.getSubject(),
            "name", jwt.getClaimAsString("name"),
            "email", jwt.getClaimAsString("email"),
            "roles", jwt.getClaimAsStringList("scope")
        );
    }
    
    @GetMapping("/admin")
    @PreAuthorize("hasAuthority('SCOPE_admin')")
    public List<User> admin() {
        return userService.findAll();
    }
}
```

### 3.5 测试登录流程

```
1. 浏览器访问 https://app-a.com/login
   → 重定向到 https://idp.example.com/oauth2/authorize?response_type=code&...

2. 用户在 IdP 登录
   → 重定向回 https://app-a.com/callback?code=ABC123

3. App-A 用 code 换 Token
   → POST https://idp.example.com/oauth2/token
   → 返回: { access_token: "eyJ...", id_token: "eyJ..." }

4. App-A 设置 Cookie / Session
   → 后续请求带 access_token

5. App-A 请求用户 API
   → GET /api/users/me + Authorization: Bearer eyJ...
   → Spring Security 验证 JWT 签名 → @AuthenticationPrincipal Jwt
```

---

## 4. 4 大关键配置

### 4.1 PKCE（强制）

```yaml
# PKCE 防 code 拦截
.requireProofKey(true)
```

**适用**：所有公网 OAuth2 客户端（SPA / 移动端）

### 4.2 Token 时长

```yaml
accessTokenTimeToLive: 1h     # Access Token 1 小时
refreshTokenTimeToLive: 7d    # Refresh Token 7 天
```

**最佳实践**：
- Access Token 短（1h 内）
- Refresh Token 长（7-30 天）+ Rotate

### 4.3 Scope 设计

```
openid    —— OIDC 必选
profile   —— 用户画像（姓名/头像）
email     —— 邮箱
read:X    —— 读资源 X 的权限
write:X   —— 写资源 X 的权限
admin     —— 管理员
```

### 4.4 HTTPS 强制

```yaml
# application.yml
server:
  port: 8443
  ssl:
    enabled: true
    key-store: classpath:keystore.p12
    key-store-password: changeit
    key-store-type: PKCS12
    key-alias: idp
```

⚠️ OAuth2 **必须 HTTPS**，否则 Token 在网络被截获。

---

## 5. 6 大生产坑

### 坑 1：JWT 默认 HS256 + 单一 secret

**错**：所有子系统共享一个 HS256 secret（密钥泄露风险高）

**正解**：用 RS256（RSA 密钥对），公钥分发，子系统验签不用 secret

### 坑 2：Refresh Token 永远不过期

**错**：Refresh Token 设 30 天有效，但服务器端从不删除

**正解**：
- Refresh Token Rotate（每次刷新换新 Token，旧 Token 立即失效）
- 设备码流（device flow）

### 坑 3：scope 当 role 用

**错**：把 `scope=admin` 当作"用户是管理员"

**正解**：
- scope：API 权限（"能否调 admin API"）
- role：用户角色（"是不是管理员"）—— JWT claims role
- 区分开

### 坑 4：IdP 单点未高可用

**错**：IdP 部署单实例 —— IdP 挂了所有系统登不上

**正解**：
- IdP 多实例集群（Nacos / Eureka 注册）
- 数据库主从 + 哨兵
- Redis Cluster 存 Session

### 坑 5：登出逻辑缺失

**错**：只实现登录，没实现统一登出

**正解**：
- OIDC backchannel logout（IdP 推送登出到 SP）
- SP 本地会话清理 + IdP Cookie 失效
- 用户主动登出时清所有 SP 会话

### 坑 6：CORS 配置错误

**错**：业务 API 跨域调用未配置 CORS

**正解**：
```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.addAllowedOrigin("https://app-a.com");
    config.addAllowedOrigin("https://app-b.com");
    config.addAllowedHeader("*");
    config.addAllowedMethod("*");
    config.setAllowCredentials(true);
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}
```

---

## 6. Spring Authorization Server vs Keycloak 选型

| 维度 | Spring Authorization Server | Keycloak |
|------|------------------------------|----------|
| 类型 | Java 框架 | 完整产品 |
| 集成 | Spring 全家桶 | 多语言 |
| 主题定制 | 完全自定义 | 内置主题 |
| 用户联邦 | 自定义 | 内置 LDAP / SAML / OAuth |
| 学习曲线 | 中（需懂 OAuth2） | 中（产品配置）|
| 适用 | Spring 项目 | 多语言企业 |

**实战选择**：Spring 项目选 **Spring Authorization Server**；多语言 / 已有产品选 **Keycloak**。

---

## 7. 一句话总结

> **Spring Security SSO = Spring Authorization Server（IdP）+ Spring Security OAuth2 Resource Server（SP）+ PKCE + RS256 + HTTPS + Refresh Token Rotate。配置 100-200 行，企业级 SSO 闭环。**

---

← [返回: SSO 总目录](../README.md) · 上一章：[02-six-schemes-comparison](02-six-schemes-comparison.md) · 下一章：[04-jwt-implementation](04-jwt-implementation.md)
