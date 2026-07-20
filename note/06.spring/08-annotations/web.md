# Web 注解（Spring MVC）

> ⬅️ [返回注解速查](../README.md) | [AOP 注解](aop.md) | [Bean 注解](bean-and-ioc.md)

本节介绍 Spring MVC 中用于 Web 层的核心注解，包括控制器声明、路由映射、参数绑定、响应处理等。

---

## 🎯 一句话定位

**Web 注解 = 路由 + 参数绑定 + 响应处理三件套**——`@RequestMapping` 家族负责"哪个 URL 走哪个方法"，`@RequestBody`/`@PathVariable`/`@RequestParam` 负责"如何把 HTTP 数据注入到方法参数"，`@ResponseBody`/`@RestController` 负责"如何把返回值写回 HTTP 响应"。

---

## 控制器声明

### @Controller

> 用于修饰 `controller` 层的组件，由控制器负责将用户发来的 URL 请求转发到对应的服务接口，通常配合 `@RequestMapping` 使用。

### @RestController

> 和 `@Controller` 一样标注控制层组件，但它是 `@ResponseBody` 和 `@Controller` 的合集——类上加了 `@RestController`，**类内所有方法默认返回 JSON**（无需每个方法加 `@ResponseBody`）。

```java
@RestController
@RequestMapping("api")
public class LoginController {
    @RequestMapping(value = "login", method = RequestMethod.POST)
    public ResponseEntity login(@RequestBody UserLoginDTO request){
        //...业务处理
        return new ResponseEntity(HttpStatus.OK);
    }
}
```

### @Controller vs @RestController

| 特性 | @Controller | @RestController |
|------|-------------|-----------------|
| **视图渲染** | ✅ 默认返回视图名（走 ViewResolver） | ❌ 直接返回数据（JSON/XML） |
| **HTTP 响应体** | 需配合 `@ResponseBody` | 默认就是 |
| **典型场景** | 传统 MVC 页面 | RESTful API |

> 📌 现代 Spring 项目几乎都用 `@RestController` + 前后端分离架构。

---

## 路由映射

### @RequestMapping

> 提供路由信息，负责 URL 到 Controller 中具体函数的映射，支持指定请求协议（GET/POST/PUT/DELETE 等）。

```java
@RequestMapping(value = "login", method = RequestMethod.POST)
@ResponseBody
public ResponseEntity login(@RequestBody UserLoginDTO request){
    //...业务处理
    return new ResponseEntity(HttpStatus.OK);
}
```

### @GetMapping / @PostMapping / @PutMapping / @DeleteMapping

> `@GetMapping` 等价于 `@RequestMapping(value="/get", method=RequestMethod.GET)`，更简洁。

```java
@GetMapping("get")     // GET /get
@PostMapping("post")   // POST /post
@PutMapping("put")     // PUT /put
@DeleteMapping("delete") // DELETE /delete
```

### 4 个注解的对比

| 注解 | 等价的 RequestMapping | HTTP 方法 | 典型用途 |
|------|----------------------|----------|----------|
| `@GetMapping` | `@RequestMapping(method = GET)` | GET | 查询 |
| `@PostMapping` | `@RequestMapping(method = POST)` | POST | 创建 |
| `@PutMapping` | `@RequestMapping(method = PUT)` | PUT | 完整更新 |
| `@DeleteMapping` | `@RequestMapping(method = DELETE)` | DELETE | 删除 |
| `@PatchMapping` | `@RequestMapping(method = PATCH)` | PATCH | 部分更新 |

---

## 参数绑定

### @RequestBody

> 表示请求体的 `Content-Type` 必须为 `application/json`，接收后自动绑定到 Java 对象。

```java
@PostMapping("login")
public ResponseEntity login(@RequestBody UserLoginDTO request) {
    //...业务处理
    return new ResponseEntity(HttpStatus.OK);
}
```

### @RequestParam

> 用于接收请求参数为**表单类型**（`application/x-www-form-urlencoded`）的数据，通常用在方法参数前。

```java
@PostMapping("login")
@ResponseBody
public ResponseEntity login(@RequestParam(value = "userName", required = true) String userName,
                            @RequestParam(value = "userPwd", required = true) String userPwd){
    //...业务处理
    return new ResponseEntity(HttpStatus.OK);
}
```

### @PathVariable

> 用于获取请求路径中的参数，通常用于 **RESTful 风格** 的 API。

```java
@PostMapping("queryProduct/{id}")
@ResponseBody
public ResponseEntity queryProduct(@PathVariable("id") String id){
    //...业务处理
    return new ResponseEntity(HttpStatus.OK);
}
```

### 3 种参数绑定方式对比

| 注解 | 数据来源 | Content-Type | 典型场景 |
|------|---------|--------------|----------|
| `@RequestBody` | 请求体 | `application/json` | 复杂对象、嵌套结构 |
| `@RequestParam` | URL 查询参数 / 表单 | `application/x-www-form-urlencoded` | 简单参数（id、page、size） |
| `@PathVariable` | URL 路径 | 任意 | RESTful 资源标识（`/users/{id}`） |

> 📌 `@RequestParam` 和 `@PathVariable` 都能接收简单类型（String、Long、Integer），复杂对象必须用 `@RequestBody`。

---

## 响应处理

### @ResponseBody

> 表示该方法的返回结果直接写入 HTTP response body，返回数据格式为 `application/json`。

```java
@Controller
@RequestMapping("api")
public class LoginController {
    @RequestMapping(value = "login", method = RequestMethod.POST)
    @ResponseBody
    public ResponseEntity login(@RequestBody UserLoginDTO request){
        //...业务处理
        return new ResponseEntity(HttpStatus.OK);
    }
}
```

### @ResponseBody 工作原理

```text
Java 对象 → HttpMessageConverter (MappingJackson2HttpMessageConverter) → JSON 字符串 → HTTP 响应体
```

---

## 跨域与请求映射细节

> 本节介绍 CORS 跨域与 5 个常被忽略的请求映射注解。

### @CrossOrigin（CORS 跨域）

> 解决浏览器**同源策略**导致的跨域问题。标注在 `@Controller` / `@RequestMapping` 上。

```java
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "https://frontend.example.com", maxAge = 3600)   // 类级别
public class ApiController {

    @CrossOrigin(origins = "*")      // 方法级别覆盖
    @GetMapping("/public")
    public Result publicApi() { ... }
}
```

| 属性 | 默认 | 说明 |
|:-----|:-----|:-----|
| `origins` | `"*"` | 允许的 Origin（`https://x.com`） |
| `methods` | `*` | 允许的 HTTP 方法 |
| `allowedHeaders` | `*` | 允许的请求头 |
| `exposedHeaders` | `""` | 暴露给浏览器的响应头 |
| `allowCredentials` | `false` | 是否允许携带 Cookie |
| `maxAge` | `1800` | 预检（preflight）缓存秒数 |

> 💡 全局配置请使用 `WebMvcConfigurer.addCorsMappings(CorsRegistry)`。详见 [02-web/mvc/cors-and-static](../02-web/mvc/cors-and-static.md)。

### @RequestHeader（获取请求头）

> 把 HTTP 请求头绑定到方法参数。

```java
@GetMapping("/headers")
public String headers(@RequestHeader("User-Agent") String ua,
                      @RequestHeader(value = "X-Token", required = false) String token) { ... }
```

### @CookieValue（获取 Cookie）

> 读取请求中的 Cookie 值。

```java
@GetMapping("/profile")
public User profile(@CookieValue("JSESSIONID") String sessionId,
                    @CookieValue(value = "lang", defaultValue = "zh") String lang) { ... }
```

### @MatrixVariable（矩阵变量）

> 读取 URL 矩阵参数（`;` 分隔）：`/cars;color=red;year=2020`。

```java
// 需开启：WebMvcConfigurer.configurePathMatch().setUseSuffixPatternMatch(false) + URL 不被 UrlPathHelper 去掉分号
@GetMapping("/cars/{id}")
public String car(@PathVariable String id, @MatrixVariable String color) { ... }
```

> ⚠️ Spring MVC 默认**禁用**矩阵变量（UrlPathHelper `removeSemicolonContent=true`），需先在 `WebMvcConfigurer` 中开启。

### @ModelAttribute（绑定表单 / 命令对象）

> 将多个请求参数绑定到一个 POJO（**表单提交场景**），或**提前准备模型数据**。

```java
// 1. 入参：绑定表单
@PostMapping("/users")
public User create(@ModelAttribute CreateUserForm form) { ... }

// 2. 方法级：预先准备模型
@ModelAttribute
public void populateModel(@RequestParam Long id, Model model) {
    model.addAttribute("user", userService.findById(id));
}
```

> 📌 `@RequestBody` 处理 JSON，`@ModelAttribute` 处理 **application/x-www-form-urlencoded** 表单。

### @SessionAttribute（绑定 Session 作用域）

> 把方法参数绑定到 HTTP Session 中的 attribute。

```java
@GetMapping("/me")
public User me(@SessionAttribute("loginUser") User user) { ... }

// 类级别：声明需要 session 中的 attr
@Controller
@SessionAttributes("cart")
public class CartController { ... }
```

### 5 个注解速查对照

| 注解 | 数据来源 | 典型场景 |
|:-----|:---------|:---------|
| `@RequestHeader` | HTTP 请求头 | token、UA、Content-Type |
| `@CookieValue` | Cookie | sessionId、用户偏好 |
| `@MatrixVariable` | URL 矩阵参数 | `/cars;color=red;year=2020` |
| `@ModelAttribute` | 表单参数 | 提交整张表单 |
| `@SessionAttribute` | Session 域 | 跨请求共享数据 |

---

## 🤔 思考

1. **@RestController 还是 @Controller？** 99% 的现代项目用 `@RestController`（前后端分离）。
2. **@RequestParam 和 @RequestBody 能不能同时用？** 能，但不同场景：
   ```java
   @PostMapping("/users")  // 表单 + JSON 混用
   public User create(@RequestParam String type, @RequestBody User user) {...}
   ```
3. **@PathVariable 名称必须和占位符一致？** 默认一致，可显式指定：
   ```java
   @GetMapping("/users/{userId}")
   public User get(@PathVariable("userId") Long id) {...}
   ```
4. **为什么 @RequestMapping 不直接写 method=POST？** 兼容老代码（Spring 4.3 前没有专用注解）。
5. **@CrossOrigin 加类上还是方法上？** 全局规则放类，单接口特殊覆盖放方法。**全局配置推荐**用 `WebMvcConfigurer` 集中管理，避免散落在 N 个 Controller。

---

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [AOP 注解](aop.md) — 切面常用于 Controller 层
- [02 Web 层 MVC](../../README.md) — Spring MVC 工作流程
- [02 Web 层 CORS 与静态资源](../02-web/mvc/cors-and-static.md) — @CrossOrigin 全局配置
- [06 集成组件/Validation](../06-integration/validation/validation-annotations-and-usage.md) — @Valid 用于 @RequestBody 参数校验
