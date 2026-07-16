<!--
question:
  id: security-filter-chain
  topic: 06.spring
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [Spring Security, 过滤器链, Servlet Filter, 认证, 授权]
-->

# Spring Security 过滤器链 vs Servlet Filter：你的认证逻辑可能被绕过了

> 一句话定位：Spring Security 本质上是一条"超级过滤器链"，理解它和 Servlet Filter 的执行顺序关系，是写好认证授权逻辑的前提。

> **系列定位**：经典 Spring 面试题（Security、过滤器链、认证授权中频）。考察的不是"怎么配置 Security"，而是 **FilterChainProxy 架构** + **过滤器执行顺序** + **自定义过滤器的正确插入位置**。

---

## 引子：自己写的 JWT 过滤器，被 Spring Security 绕过了

```java
// 开发者写了一个标准 Servlet Filter 做 JWT 认证
@WebFilter(urlPatterns = "/api/*")
public class JwtAuthFilter implements Filter {
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) {
        String token = ((HttpServletRequest) req).getHeader("Authorization");
        if (token == null || !validateToken(token)) {
            ((HttpServletResponse) res).sendError(401, "Unauthorized");
            return;
        }
        chain.doFilter(req, res);
    }
}
```

同时配了 Spring Security 要求 `/api/**` 必须认证。发一个没有 `Authorization` 头的请求 —— 期望返回你写的 401，**结果返回了 403**（Spring Security 的默认拒绝）。

**反直觉**：你的 JwtAuthFilter 根本没执行！Spring Security 的过滤器链 **先于** 你的 Servlet Filter 运行，在 Security 层就直接拒绝了。

问题：**Spring Security 的过滤器链和普通 Servlet Filter 到底是什么关系？执行顺序怎么控制？**

---

> 📚 **前置知识**：[Spring MVC 请求流程](../spring-mvc-flow/README.md) | [AOP 原理](../aop-principle/README.md)

## 一、核心原理

### 1.1 FilterChainProxy：Security 的"总入口"

Spring Security 通过 `DelegatingFilterProxy` 注册为一个名为 `springSecurityFilterChain` 的 Servlet Filter，内部由 `FilterChainProxy` 管理 15+ 个过滤器：

```text
Servlet Container Filter 链
  ├─ 你的 Filter A（@WebFilter）          ← 在 Security 之前
  ├─ springSecurityFilterChain（DelegatingFilterProxy）
  │    └─ FilterChainProxy
  │         ├─ SecurityContextPersistenceFilter（加载 SecurityContext）
  │         ├─ LogoutFilter
  │         ├─ UsernamePasswordAuthenticationFilter（表单登录）
  │         ├─ BasicAuthenticationFilter
  │         ├─ AnonymousAuthenticationFilter
  │         ├─ SessionManagementFilter
  │         ├─ ExceptionTranslationFilter（异常处理）
  │         └─ FilterSecurityInterceptor（授权检查）
  └─ 你的 Filter B（@WebFilter）          ← 在 Security 之后
```

**关键结论**：Servlet Filter 和 Security 内部过滤器不在同一个链条上。`@WebFilter` 无法插入到 Security 过滤器之间。

### 1.2 Spring Security 6.x 的变化

```java
// ❌ 5.x：继承 WebSecurityConfigurerAdapter（已废弃）
// ✅ 6.x：声明 SecurityFilterChain Bean
@Configuration
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/api/**").authenticated()
            )
            .formLogin(Customizer.withDefaults())
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }
}
```

6.x 核心变化：废弃 `WebSecurityConfigurerAdapter`，改为 `SecurityFilterChain` Bean；支持多条链按路径匹配不同安全策略；Lambda DSL 配置风格。

---

## 二、代码示例：正确插入自定义过滤器

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    @Autowired private JwtTokenProvider tokenProvider;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain filterChain) throws ServletException, IOException {
        String token = resolveToken(request);
        if (token != null && tokenProvider.validateToken(token)) {
            SecurityContextHolder.getContext().setAuthentication(
                tokenProvider.getAuthentication(token));
        }
        filterChain.doFilter(request, response);
    }
}

// 插入到 Security 链的正确位置
http.addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
```

**常用插入位置**：

| 插入位置 | 适用场景 |
|---------|---------|
| `UsernamePasswordAuthenticationFilter` 之前 | JWT、OAuth2 Token 解析 |
| `ExceptionTranslationFilter` 之后 | 自定义异常处理 |
| `FilterSecurityInterceptor` 之前 | 自定义授权检查 |

**多条 SecurityFilterChain 按路径隔离**：

```java
@Bean @Order(1)
public SecurityFilterChain apiChain(HttpSecurity http) throws Exception {
    http.securityMatcher("/api/**")
        .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
        .csrf(csrf -> csrf.disable());  // API 不需要 CSRF
    return http.build();
}

@Bean @Order(2)
public SecurityFilterChain webChain(HttpSecurity http) throws Exception {
    http.securityMatcher("/**").formLogin(Customizer.withDefaults());  // Web 用表单登录
    return http.build();
}
```

---

## 三、常见陷阱

### 陷阱 1：过滤器顺序搞反
- **真相**：Servlet Filter 的执行顺序由 Servlet 容器控制（`@Order` / `FilterRegistrationBean.setOrder()`）。认证逻辑应该放在 SecurityFilterChain 内部，而不是 `@WebFilter`。

### 陷阱 2：忘记注册到 SecurityFilterChain
- **真相**：`@Component` 只是注册到 Spring 容器，不会自动加入 Security 链。必须显式调用 `addFilterBefore/addFilterAfter`。

### 陷阱 3：CORS 预检请求被拦截
- **真相**：`OPTIONS` 请求不带认证信息，被 Security 拒绝。必须显式放行：
```java
http.cors(Customizer.withDefaults())
    .authorizeHttpRequests(auth -> auth
        .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
        .anyRequest().authenticated());
```

---

## 四、最佳实践

- **认证过滤器放在 Security 链内**，不用 Servlet Filter。Security 链内可访问 `SecurityContext`、`Authentication` 等对象，且顺序可控。
- **理解默认过滤器顺序**：`SecurityContext` 加载 → 认证过滤器（表单/Basic/JWT）→ 匿名认证 → 会话管理 → 异常处理 → 授权检查。
- **API 和 Web 用不同的 SecurityFilterChain**，按 `securityMatcher` 路径隔离，`@Order` 控制优先级。

---

## 五、面试话术（90 秒版本）

> "Spring Security 本质是一条由 **FilterChainProxy** 管理的过滤器链，对外通过 `DelegatingFilterProxy` 注册为一个 Servlet Filter。内部 15+ 过滤器按固定顺序执行：从 `SecurityContextPersistenceFilter` 加载上下文，到各种认证过滤器，最后由 `FilterSecurityInterceptor` 做授权检查。
>
> **和 Servlet Filter 的关键区别**：Servlet Filter 在 Security 链外面，顺序由容器控制。如果在 `@WebFilter` 里写认证逻辑，可能被 Security 抢先拦截。正确做法是写成 `OncePerRequestFilter`，用 `addFilterBefore` 插入到 Security 链内部，比如 JWT 过滤器放在 `UsernamePasswordAuthenticationFilter` 之前。
>
> 6.x 废弃了 `WebSecurityConfigurerAdapter`，改为声明 `SecurityFilterChain` Bean，支持多条链按路径匹配。最常见的坑是 **CORS 预检请求被拦截**，需在 Security 配置中显式放行 OPTIONS 请求。"

---

## 六、相关章节

- 同栏目：[`Bean 生命周期`](../bean-lifecycle/README.md) — Spring Bean 的创建顺序与生命周期钩子
- 同栏目：[`自动配置原理`](../auto-configuration/README.md) — Spring Boot 自动配置如何注册 SecurityFilterChain
- 同栏目：[`Spring MVC 请求流程`](../spring-mvc-flow/README.md) — 请求从 DispatcherServlet 到 Controller 的完整链路
- 主模块：[`安全架构`](../../04.system-design/05-security/README.md) — 认证授权原理

← [返回 Spring 咬文嚼字](../README.md)
