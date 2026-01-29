# Spring MVC组件执行顺序与功能分析

## 一、执行顺序

在Spring MVC请求处理流程中，各组件的执行顺序为：

1. **Filter链**（过滤器）
2. **Servlet**（通常是DispatcherServlet）
3. **HandlerInterceptor**的preHandle方法（拦截器）
4. **AOP**切面（前置通知等）
5. **Controller**（控制器处理请求）
6. **AOP**切面（后置通知、返回通知等）
7. **HandlerInterceptor**的postHandle方法
8. **ViewResolver**（视图解析器）
9. 视图渲染
10. **HandlerInterceptor**的afterCompletion方法
11. 响应返回**Filter链**

## 二、各组件详细分析

### 1. Filter（过滤器）
- **作用**：Servlet规范组件，在请求到达Servlet前和响应离开Servlet后进行处理
- **特点**：
    - 基于Servlet规范，不依赖Spring框架
    - 通过web.xml或@ServletComponentScan配置
    - 只能访问ServletRequest和ServletResponse
    - 执行于Web容器级别
- **使用场景**：
    - 字符编码过滤（CharacterEncodingFilter）
    - 跨域请求处理（CORS）
    - 安全防护（XSS、CSRF）
    - 全局请求/响应日志记录

### 2. Servlet / DispatcherServlet
- **作用**：前端控制器，协调各组件处理请求
- **特点**：
    - DispatcherServlet是Spring MVC的核心
    - 初始化WebApplicationContext
    - 加载HandlerMapping、HandlerAdapter、ViewResolver等组件
    - 统一异常处理
- **使用场景**：
    - 任何Spring MVC应用的核心入口
    - 请求分发和协调处理

### 3. HandlerInterceptor（拦截器）
- **作用**：Spring MVC提供的请求拦截机制
- **特点**：
    - 三个核心方法：
        - `preHandle`：Controller方法执行前，可阻止请求
        - `postHandle`：Controller方法执行后，视图渲染前
        - `afterCompletion`：视图渲染完成后
    - 可访问Spring上下文和Handler信息
    - 支持按路径模式配置
- **使用场景**：
    - 登录认证与会话管理
    - 权限验证（ACL）
    - 请求参数校验
    - 性能监控与统计
    - 多语言切换

### 4. AOP（面向切面编程）
- **作用**：提供横切关注点的模块化
- **特点**：
    - 基于代理实现（JDK动态代理或CGLIB）
    - 支持多种通知类型（@Before, @After, @Around等）
    - 可精确控制切点表达式
    - 与业务逻辑高度解耦
- **使用场景**：
    - 事务管理（@Transactional）
    - 业务日志记录
    - 方法执行性能监控
    - 参数校验
    - 异常统一处理
    - 缓存管理

### 5. Controller（控制器）
- **作用**：处理具体业务请求，返回处理结果
- **特点**：
    - 使用@Controller或@RestController注解
    - 通过@RequestMapping系列注解映射请求
    - 可注入Service、Repository等组件
    - 支持参数绑定、数据校验
- **使用场景**：
    - RESTful API开发
    - 传统Web页面控制器
    - 文件上传/下载处理
    - 表单数据处理

### 6. ViewResolver（视图解析器）
- **作用**：将逻辑视图名解析为具体视图对象
- **特点**：
    - 多种实现（InternalResourceViewResolver、ThymeleafViewResolver等）
    - 配置前缀(prefix)和后缀(suffix)简化视图路径
    - 支持内容协商（ContentNegotiatingViewResolver）
    - 可配置视图缓存
- **使用场景**：
    - JSP/Thymeleaf/FreeMarker等模板渲染
    - 视图国际化
    - 多视图技术混合使用
    - REST API与传统Web页面混合架构

## 三、组件对比与选择

### Filter vs HandlerInterceptor
| 特性   | Filter       | HandlerInterceptor  |
|------|--------------|---------------------|
| 规范层级 | Servlet规范    | Spring框架            |
| 依赖关系 | 不依赖Spring    | 依赖Spring上下文         |
| 执行时机 | 更早，在Servlet前 | 在DispatcherServlet内 |
| 访问能力 | 仅能访问请求/响应    | 可访问Handler、Model等   |
| 适用场景 | 全局性、底层处理     | 业务相关的请求处理           |

### HandlerInterceptor vs AOP
| 特性   | HandlerInterceptor          | AOP               |
|------|-----------------------------|-------------------|
| 作用范围 | Web层请求级别                    | 任何Spring Bean方法级别 |
| 访问对象 | HttpServletRequest/Response | 方法参数、返回值          |
| 执行粒度 | 粗粒度（请求级别）                   | 细粒度（方法级别）         |
| 适用场景 | Web层通用处理                    | 业务逻辑横切关注点         |

## 四、实际应用场景示例

在电商系统中：
1. **Filter**：全局设置UTF-8编码，处理跨域请求
2. **HandlerInterceptor**：验证用户登录状态，检查购物车
3. **AOP**：记录商品浏览日志，管理订单事务
4. **Controller**：处理商品查询、下单、支付等业务
5. **ViewResolver**：解析商品列表、详情页等视图