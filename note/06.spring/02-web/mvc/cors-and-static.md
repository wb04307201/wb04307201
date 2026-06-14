# CORS 与静态资源

> 最后更新: 2026-06-14
> ⬅️ [返回 MVC 总览](README.md) | [02 Web 层](../README.md)

CORS（跨域资源共享）与静态资源处理是 Web 层两大**横切关注点**：前者解决"浏览器跨域 AJAX 拦截"问题，后者解决"前端打包产物 / WebJars / 上传文件"的访问路径问题。本文系统讲清楚 Spring MVC 的三种 CORS 写法、静态资源处理机制与最佳实践。

---

## 🎯 一句话定位

**CORS = "服务端声明哪些 Origin 可以跨域访问"**；**静态资源 = "把磁盘目录或 classpath 路径映射成 HTTP URL"**。两者都通过 `WebMvcConfigurer` 的 4 个方法配置，简洁、类型安全。

---

## 一、CORS 三种写法

### 1. @CrossOrigin 注解（最简单）

```java
@RestController
@RequestMapping("/api")
public class UserController {

    @CrossOrigin(origins = "https://admin.example.com",
                 allowedHeaders = "*",
                 methods = {RequestMethod.GET, RequestMethod.POST},
                 maxAge = 3600)
    @GetMapping("/users")
    public List<User> list() { /* ... */ }
}
```

> 粒度细，但**每个方法都要写一遍**；生产环境多用全局配置。

### 2. WebMvcConfigurer.addCorsMappings（推荐：全局）

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("https://admin.example.com", "https://m.example.com")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .exposedHeaders("Authorization", "X-Trace-Id")
                .allowCredentials(true)
                .maxAge(3600);
    }
}
```

> 简洁、类型安全、支持路径模式，**最常用**。

### 3. CorsFilter / CorsConfigurationSource（精细控制）

```java
@Bean
public CorsFilter corsFilter() {
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    CorsConfiguration cfg = new CorsConfiguration();
    cfg.addAllowedOriginPattern("https://*.example.com"); // 通配符（Spring 5.3+）
    cfg.addAllowedMethod("*");
    cfg.addAllowedHeader("*");
    cfg.setAllowCredentials(true);
    cfg.setMaxAge(3600L);
    source.registerCorsConfiguration("/**", cfg);
    return new CorsFilter(source);
}
```

> 适合**与 Spring Security 集成**（Security 需 `cors().configurationSource(source)`）。

---

## 二、CORS 关键字段

| 字段 | 含义 | 建议 |
|------|------|------|
| `allowedOrigins` | 允许的 Origin 列表 | 精确白名单，**不要用 `*`**（与 `allowCredentials=true` 冲突） |
| `allowedOriginPatterns` | Origin 模式（支持通配符） | 子域通配用这个 |
| `allowedMethods` | 允许的 HTTP 方法 | 至少包含 `OPTIONS`（预检） |
| `allowedHeaders` | 允许的请求头 | 生产可收紧为 `Authorization, Content-Type` |
| `exposedHeaders` | 暴露给 JS 的响应头 | 自定义头必须显式声明 |
| `allowCredentials` | 是否允许 `Cookie` | 严格场景关闭 |
| `maxAge` | 预检缓存时间（秒） | 3600 即可 |

---

## 三、常见 CORS 陷阱

1. **带 Cookie 跨域用了 `*`**：浏览器拒绝。必须显式列出 Origin。
2. **预检失败 (405/403)**：OPTIONS 请求被 Security/拦截器吃掉；放行 `OPTIONS` 或在 Security 中 `disable()`。
3. **网关层 CORS**：微服务由网关统一加 CORS 响应头，业务服务不加；避免重复。
4. **Spring Security**：默认开启 CORS 支持，但**不会自动放行 OPTIONS**；需 `cors().and().csrf().disable()` 或自定义 `CorsConfigurationSource`。

---

## 四、静态资源处理

### 1. 默认静态资源位置

Spring Boot 默认从以下位置查找静态资源（按顺序）：

```
classpath:/META-INF/resources/
classpath:/resources/
classpath:/static/
classpath:/public/
```

例如 `src/main/resources/static/index.html` → `http://localhost:8080/index.html`。

### 2. 自定义：WebMvcConfigurer.addResourceHandlers

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 1) classpath 静态目录
        registry.addResourceHandler("/static/**")
                .addResourceLocations("classpath:/static/");

        // 2) 磁盘目录（上传文件 / 共享目录）
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations("file:/var/uploads/");

        // 3) WebJars
        registry.addResourceHandler("/webjars/**")
                .addResourceLocations("classpath:/META-INF/resources/webjars/");
    }
}
```

### 3. 缓存策略

```java
registry.addResourceHandler("/static/**")
        .addResourceLocations("classpath:/static/")
        .setCachePeriod(3600)                          // Cache-Control: max-age=3600
        .setCacheControl(CacheControl.maxAge(7, TimeUnit.DAYS).cachePublic())
        .resourceChain(true)
        .addResolver(new VersionResourceResolver()      // /static/main-1.0.0.js
                .addContentVersionPath("/**"));
```

### 4. 欢迎页与 Favicon

- 启动时自动从 `static/`、`public/` 等位置找 `index.html`。
- `favicon.ico` 同样自动识别。

---

## 五、WebJars

> 把前端库（jQuery、Bootstrap、Vue）打包成 Jar，Maven/Gradle 直接引入。

```xml
<dependency>
    <groupId>org.webjars</groupId>
    <artifactId>webjars-locator-core</artifactId>
</dependency>
<dependency>
    <groupId>org.webjars</groupId>
    <artifactId>bootstrap</artifactId>
    <version>5.3.0</version>
</dependency>
```

HTML 引用：

```html
<link rel="stylesheet" href="/webjars/bootstrap/5.3.0/css/bootstrap.min.css">
```

> Spring Boot 已自动配置 WebJars 资源处理器（依赖 `webjars-locator-core` 时支持**版本无关路径** `/webjars/bootstrap/css/bootstrap.min.css`）。

---

## 六、Spring Boot 默认配置一览

```yaml
spring:
  web:
    resources:
      static-locations: classpath:/META-INF/resources/,classpath:/resources/,classpath:/static/,classpath:/public/
      cache:
        cachecontrol:
          max-age: 0
```

| 配置 | 默认 | 说明 |
|------|------|------|
| `spring.web.resources.static-locations` | 4 个默认目录 | 静态资源查找路径 |
| `spring.web.resources.cache.cachecontrol.max-age` | 0 | 生产建议 7d~30d |
| `spring.mvc.static-path-pattern` | `/**` | URL 匹配模式（除 `/api/**` 等显式映射外） |

---

## 七、最佳实践

1. **生产环境静态资源交给 Nginx/CDN**，不要让 Spring 容器直接服务大文件。
2. **缓存 + 文件指纹**：前端构建产物用 `app-1.0.0.js`，通过 `VersionResourceResolver` 关联，长缓存。
3. **CORS 严格白名单**：永远不要 `allowedOrigins(*)`，子域用 `allowedOriginPatterns`。
4. **CORS 放在网关**：微服务架构里由 Spring Cloud Gateway 统一处理，业务服务不重复加。
5. **上传文件回显**：通过 `addResourceHandler("/uploads/**")` 映射本地目录到 URL，**不要**自己写 Controller 下载（性能差）。

---

## 相关章节

- ⬅️ [返回 MVC 总览](README.md)
- [文件上传](file-upload.md) — MultipartFile 落盘
- [异常处理](exception-resolver.md) — 静态资源 404 处理
- [组件对比与场景](components-order.md) — Filter 与静态资源
