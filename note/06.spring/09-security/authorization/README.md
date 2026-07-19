<!--
module:
  parent: spring
  slug: spring/09-security/authorization
  type: article
  category: 主模块子文章
  summary: 授权机制解决"你能干什么"的问题，通过 URL 级（requestMatchers）+ 方法级（@PreAuthorize）+ 数据级（ACL）三层防护模型从粗到细控制资源访问。
-->

# 授权机制

> ⬅️ [返回 Spring Security](../README.md)

**授权（Authorization）** 解决的是"你能干什么"的问题——在认证通过后，根据用户的角色和权限决定其是否有权访问特定资源。Spring Security 提供了 URL 级、方法级、数据级三层授权模型。

---

## 🎯 一句话定位

**授权 = URL 级（requestMatchers）+ 方法级（@PreAuthorize）+ 数据级（ACL）**——三层防护从粗到细控制"谁能访问什么"。

---

## 一、授权架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                   授权三层模型                                 │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  第 1 层：URL 级授权（requestMatchers）               │     │
│  │  粒度：接口路径                                       │     │
│  │  场景：/admin/** → hasRole('ADMIN')                  │     │
│  └─────────────────────────────────────────────────────┘     │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  第 2 层：方法级授权（@PreAuthorize）                  │     │
│  │  粒度：Service/Controller 方法                       │     │
│  │  场景：@PreAuthorize("hasRole('ADMIN')")             │     │
│  └─────────────────────────────────────────────────────┘     │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  第 3 层：数据级授权（ACL / @PostFilter）              │     │
│  │  粒度：单个数据对象                                   │     │
│  │  场景：用户只能编辑自己创建的订单                     │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、URL 级安全（requestMatchers）

### 2.1 基本用法

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            // 公开端点（不需要认证）
            .requestMatchers("/public/**", "/health", "/api-docs/**").permitAll()
            
            // 角色控制
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .requestMatchers("/manager/**").hasAnyRole("ADMIN", "MANAGER")
            
            // 权限控制
            .requestMatchers("/api/users/delete").hasAuthority("user:delete")
            .requestMatchers("/api/reports/**").hasAnyAuthority("report:read", "report:admin")
            
            // HTTP 方法级控制
            .requestMatchers(HttpMethod.GET, "/api/users").hasRole("USER")
            .requestMatchers(HttpMethod.POST, "/api/users").hasRole("ADMIN")
            .requestMatchers(HttpMethod.DELETE, "/api/users/**").hasRole("ADMIN")
            
            // SpEL 表达式
            .requestMatchers("/api/tenant/{tenantId}/**")
            .access("@tenantSecurity.isCurrentTenant(#tenantId)")
            
            // 兜底规则（必须放最后）
            .anyRequest().authenticated()
        );
    
    return http.build();
}
```

### 2.2 路径匹配模式

| 匹配器 | 语法 | 示例 | 说明 |
|:-------|:-----|:-----|:-----|
| **精确匹配** | 无通配符 | `/api/users` | 只匹配精确路径 |
| **Ant 风格** | `*`, `**`, `?` | `/api/*/list`, `/api/**` | Spring Security 默认 |
| **MVC 风格** | `{var}` | `/api/users/{id}` | 支持路径变量 |
| **正则** | `regex()` | `regex("/api/v[0-9]+/.*")` | 复杂匹配 |

### 2.3 授权规则优先级

```java
// ⚠️ 规则按声明顺序匹配，先匹配先生效
.authorizeHttpRequests(auth -> auth
    .requestMatchers("/api/users/admin").hasRole("ADMIN")    // 1. 先匹配
    .requestMatchers("/api/users/**").hasRole("USER")         // 2. 后匹配
    // /api/users/admin 被第 1 条匹配到，要求 ADMIN 角色
    // /api/users/list  被第 2 条匹配到，要求 USER 角色
)
```

> ⚠️ **常见陷阱**：规则是**按声明顺序**匹配的，不是按"最精确"匹配。如果把 `/api/users/**` 放在 `/api/users/admin` 前面，后者永远不会生效。

---

## 三、方法级安全（@PreAuthorize / @Secured）

### 3.1 启用方法安全

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity  // 启用方法级安全注解（Spring Security 6.x）
// @EnableGlobalMethodSecurity(prePostEnabled = true)  // 5.x 旧写法
public class SecurityConfig {
    // ...
}
```

### 3.2 注解对比

| 注解 | 来源 | 表达式支持 | 推荐 |
|:-----|:-----|:-----------|:-----|
| **`@PreAuthorize`** | Spring Security | SpEL 表达式 | ⭐ **推荐** |
| **`@PostAuthorize`** | Spring Security | SpEL + `returnObject` | 方法执行后鉴权 |
| `@Secured` | Spring Security 旧 | 仅角色名 | 不推荐（功能弱） |
| `@RolesAllowed` | JSR-250 | 仅角色名 | 兼容旧代码 |

### 3.3 @PreAuthorize 详解

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    // 1. 角色检查
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/admin-only")
    public List<User> adminOnly() { /* ... */ }

    // 2. 多角色检查
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    @GetMapping("/management")
    public Dashboard getDashboard() { /* ... */ }

    // 3. 权限检查
    @PreAuthorize("hasAuthority('user:read')")
    @GetMapping
    public List<User> listUsers() { /* ... */ }

    // 4. 组合条件
    @PreAuthorize("hasRole('ADMIN') and hasAuthority('user:delete')")
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) { /* ... */ }

    // 5. 参数级检查（访问方法参数）
    @PreAuthorize("#userId == authentication.principal.userId")
    @GetMapping("/{userId}/profile")
    public UserProfile getProfile(@PathVariable Long userId) { /* ... */ }

    // 6. 调用 Bean 方法
    @PreAuthorize("@permissionService.canAccess(#documentId, authentication)")
    @GetMapping("/documents/{documentId}")
    public Document getDocument(@PathVariable Long documentId) { /* ... */ }

    // 7. 数据所有者检查
    @PreAuthorize("#user.id == authentication.principal.userId or hasRole('ADMIN')")
    @PutMapping("/{id}")
    public User updateUser(@RequestBody User user) { /* ... */ }
}
```

### 3.4 @PostAuthorize 与 @PostFilter

```java
@Service
public class OrderService {

    /**
     * 方法执行后检查——只有订单的拥有者或管理员才能查看
     * returnObject 是方法返回值
     */
    @PostAuthorize("returnObject.ownerId == authentication.principal.userId " +
                   "or hasRole('ADMIN')")
    public Order getOrder(Long orderId) {
        return orderRepository.findById(orderId)
            .orElseThrow(() -> new NotFoundException("Order not found"));
    }

    /**
     * 过滤返回值——只返回当前用户有权限查看的订单
     */
    @PostFilter("filterObject.ownerId == authentication.principal.userId " +
                "or hasRole('ADMIN')")
    public List<Order> getAllOrders() {
        return orderRepository.findAll();
    }

    /**
     * 过滤入参——只处理当前用户有权限的 ID
     */
    @PreFilter("filterObject == authentication.principal.userId or hasRole('ADMIN')")
    public void batchProcess(@RequestBody List<Long> userIds) {
        // userIds 已经被过滤，只包含有权限的 ID
    }
}
```

### 3.5 SpEL 表达式速查

| 表达式 | 说明 | 示例 |
|:-------|:-----|:-----|
| `hasRole('X')` | 有角色 X（自动加 `ROLE_` 前缀） | `hasRole('ADMIN')` |
| `hasAuthority('X')` | 有权限 X（不加前缀） | `hasAuthority('user:read')` |
| `hasAnyRole('X','Y')` | 有任一角色 | `hasAnyRole('ADMIN','MGR')` |
| `isAuthenticated()` | 已认证 | `isAuthenticated()` |
| `isAnonymous()` | 匿名用户 | `isAnonymous()` |
| `#paramName` | 方法参数 | `#userId` |
| `authentication` | 当前认证对象 | `authentication.principal` |
| `returnObject` | 方法返回值（@Post 专用） | `returnObject.ownerId` |
| `@beanName` | 调用 Spring Bean | `@permSvc.canAccess(#id)` |

---

## 四、角色 vs 权限（Role vs Authority）

这是面试高频考点，很多开发者混淆：

```
┌─────────────────────────────────────────────────────────┐
│              Role vs Authority 关系                       │
│                                                           │
│   Role（角色）           Authority（权限）                 │
│   ─────────            ─────────────                     │
│   ROLE_ADMIN    →      user:read, user:write,            │
│                        user:delete, report:view           │
│                                                           │
│   ROLE_USER     →      user:read, profile:edit           │
│                                                           │
│   ROLE_MANAGER  →      user:read, user:write,            │
│                        report:view, team:manage           │
│                                                           │
│   关系：Role 是 Authority 的集合                          │
│   实现：Role = "ROLE_" + Authority 名（Spring 约定）      │
└─────────────────────────────────────────────────────────┘
```

### 核心区别

| 对比项 | Role（角色） | Authority（权限） |
|:-------|:-------------|:------------------|
| **粒度** | 粗粒度（一组权限的集合） | 细粒度（单个操作权限） |
| **前缀** | `ROLE_`（Spring Security 约定） | 无前缀 |
| **判断方法** | `hasRole('ADMIN')` 等价于 `hasAuthority('ROLE_ADMIN')` | `hasAuthority('user:delete')` |
| **使用场景** | URL 级粗控制 | 方法级细控制 |
| **数据库设计** | `user_role` 表 | `role_permission` 表 |

### 代码示例

```java
// hasRole('ADMIN') 内部转换为 hasAuthority('ROLE_ADMIN')
@PreAuthorize("hasRole('ADMIN')")     // 检查 ROLE_ADMIN
@PreAuthorize("hasAuthority('ROLE_ADMIN')")  // 等价写法

// hasAuthority 不添加前缀，精确匹配
@PreAuthorize("hasAuthority('user:delete')") // 检查 user:delete（不是 ROLE_user:delete）
```

### 数据库 RBAC 模型

```
┌──────────┐     ┌──────────────┐     ┌──────────┐     ┌────────────────┐
│   User   │────→│  user_role   │←────│   Role   │────→│role_permission │
│          │     │              │     │          │     │                │
│ id       │     │ user_id      │     │ id       │     │ role_id        │
│ username │     │ role_id      │     │ name     │     │ permission_id  │
│ password │     └──────────────┘     └──────────┘     └────────────────┘
└──────────┘                                                  │
                                                              ↓
                                                        ┌──────────────┐
                                                        │  Permission  │
                                                        │              │
                                                        │ id           │
                                                        │ code         │
                                                        │ name         │
                                                        └──────────────┘
```

---

## 五、ACL（Access Control List）

ACL 提供数据对象级别的权限控制，适用于"用户 A 只能编辑自己创建的文档"这类场景。

### 5.1 适用场景

| 场景 | 是否需要 ACL |
|:-----|:------------|
| 管理员能管理所有用户 | 不需要（Role 就够） |
| 用户只能编辑自己创建的文档 | ✅ 需要 ACL |
| 用户 A 授权用户 B 查看某篇文档 | ✅ 需要 ACL |
| 不同租户看到不同数据 | 可考虑 ACL 或多租户过滤 |

### 5.2 Spring Security ACL 配置

```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-acl</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-context-support</artifactId>
</dependency>
```

```java
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class AclConfig {

    @Bean
    public AclService aclService(DataSource dataSource) {
        JdbcMutableAclService aclService = new JdbcMutableAclService(
            dataSource, lookupStrategy(), aclCache());
        return aclService;
    }

    @Bean
    public AclAuthorizationStrategy aclAuthorizationStrategy() {
        return new AclAuthorizationStrategyImpl(
            new SimpleGrantedAuthority("ROLE_ADMIN"));
    }

    @Bean
    public LookupStrategy lookupStrategy() {
        return new BasicLookupStrategy(
            dataSource, aclCache(), 
            aclAuthorizationStrategy(), 
            new ConsoleAuditLogger());
    }

    @Bean
    public AclCache aclCache() {
        return new SpringCacheBasedAclCache(
            caffeineCacheManager.getCache("acl"),
            permissionGrantingStrategy(),
            aclAuthorizationStrategy());
    }
}
```

### 5.3 ACL 使用示例

```java
@Service
public class DocumentService {

    private final MutableAclService aclService;

    /**
     * 创建文档时自动设置 ACL
     */
    @PostAuthorize("hasPermission(returnObject, 'ADMINISTRATION')")
    public Document createDocument(String title, String content) {
        Document doc = documentRepository.save(new Document(title, content));
        
        // 为创建者设置 ACL 权限
        ObjectIdentity oid = new ObjectIdentityImpl(Document.class, doc.getId());
        Sid sid = new PrincipalSid(SecurityContextHolder.getContext()
            .getAuthentication().getName());
        
        MutableAcl acl = aclService.createAcl(oid);
        acl.insertAce(acl.getEntries().size(), BasePermission.READ, sid, true);
        acl.insertAce(acl.getEntries().size(), BasePermission.WRITE, sid, true);
        acl.insertAce(acl.getEntries().size(), BasePermission.ADMINISTRATION, sid, true);
        aclService.updateAcl(acl);
        
        return doc;
    }

    /**
     * 只有有 READ 权限的用户才能查看文档
     */
    @PreAuthorize("hasPermission(#id, 'com.example.Document', 'READ')")
    public Document getDocument(@PathVariable Long id) {
        return documentRepository.findById(id)
            .orElseThrow(() -> new NotFoundException("Document not found"));
    }
}
```

---

## 六、自定义权限评估器

当内置的 SpEL 表达式不够用时，可以自定义 `PermissionEvaluator`：

```java
/**
 * 自定义权限评估器——支持业务级权限判断
 */
@Component
public class CustomPermissionEvaluator implements PermissionEvaluator {

    private final PermissionRepository permissionRepository;

    /**
     * hasPermission(authentication, targetDomainObject, permission)
     * 用于 @PostAuthorize / @PostFilter
     */
    @Override
    public boolean hasPermission(Authentication authentication, 
                                  Object targetDomainObject, 
                                  Object permission) {
        if (authentication == null || targetDomainObject == null) {
            return false;
        }

        CustomUserDetails user = (CustomUserDetails) authentication.getPrincipal();
        String perm = (String) permission;

        // 超级管理员直接通过
        if (user.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_SUPER_ADMIN"))) {
            return true;
        }

        // 业务逻辑：检查用户是否有该对象的操作权限
        return permissionRepository.hasPermission(
            user.getUserId(), 
            targetDomainObject.getClass().getSimpleName(),
            getObjectId(targetDomainObject),
            perm
        );
    }

    /**
     * hasPermission(authentication, targetId, targetType, permission)
     * 用于 @PreAuthorize（方法执行前，只有 ID 没有对象）
     */
    @Override
    public boolean hasPermission(Authentication authentication, 
                                  Serializable targetId, 
                                  String targetType, 
                                  Object permission) {
        CustomUserDetails user = (CustomUserDetails) authentication.getPrincipal();
        
        return permissionRepository.hasPermission(
            user.getUserId(), targetType, (Long) targetId, (String) permission);
    }

    private Long getObjectId(Object obj) {
        // 反射获取 ID 字段
        try {
            Method getId = obj.getClass().getMethod("getId");
            return (Long) getId.invoke(obj);
        } catch (Exception e) {
            throw new RuntimeException("Cannot get object ID", e);
        }
    }
}

// 注册自定义评估器
@Configuration
@EnableMethodSecurity
public class MethodSecurityConfig {

    @Bean
    public MethodSecurityExpressionHandler expressionHandler(
            CustomPermissionEvaluator permissionEvaluator) {
        DefaultMethodSecurityExpressionHandler handler = 
            new DefaultMethodSecurityExpressionHandler();
        handler.setPermissionEvaluator(permissionEvaluator);
        return handler;
    }
}

// 使用
@PreAuthorize("hasPermission(#id, 'Document', 'READ')")
public Document getDocument(Long id) { /* ... */ }
```

---

## 七、权限数据缓存

权限查询通常涉及多表 JOIN，频繁查库会影响性能：

```java
@Service
public class CachedPermissionService {

    private final PermissionRepository permissionRepository;
    
    // 本地缓存：userId → Set<permission>
    private final Cache<Long, Set<String>> permissionCache = 
        Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterWrite(Duration.ofMinutes(5))
            .build();

    public Set<String> getUserPermissions(Long userId) {
        return permissionCache.get(userId, 
            id -> permissionRepository.findPermissionCodesByUserId(id));
    }

    /**
     * 权限变更时清除缓存（通过事件机制）
     */
    @EventListener
    public void onPermissionChanged(PermissionChangedEvent event) {
        permissionCache.invalidate(event.getUserId());
    }
}
```

---

## 八、面试要点

| 问题 | 核心答案 |
|:-----|:---------|
| `hasRole('ADMIN')` 和 `hasAuthority('ROLE_ADMIN')` 的区别？ | 完全等价。`hasRole` 自动加 `ROLE_` 前缀，`hasAuthority` 不加前缀 |
| `@PreAuthorize` 和 `@Secured` 的区别？ | `@PreAuthorize` 支持 SpEL 表达式（可访问参数、Bean），`@Secured` 只支持角色名 |
| `@PreAuthorize` 和 `@PostAuthorize` 的区别？ | `@Pre` 在方法执行前检查，`@Post` 在方法执行后检查（可访问 `returnObject`） |
| 如何实现"用户只能操作自己的数据"？ | 方案 1：`@PreAuthorize("#id == authentication.principal.userId")`；方案 2：ACL；方案 3：`@PostFilter` |
| `requestMatchers` 规则的匹配顺序？ | 按声明顺序匹配，先匹配先生效（不是最精确匹配） |

---

← [返回: Spring Security](../README.md)
