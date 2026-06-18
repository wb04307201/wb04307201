# Spring 咬文嚼字

> Spring 高频面试题与细节深挖，对齐主模块 [`06.spring`](../../06.spring/)

---

## 文章清单

### 基础
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [为什么不推荐 @Autowired](not-use-@autowired/) | ⭐⭐⭐ | 字段注入 vs 构造器注入 vs Setter 注入 |
| [各种 O 解释](clarify-various-o/) | ⭐⭐⭐ | POJO / VO / BO / DTO / DO 区别 |

### IoC 与生命周期
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Bean 生命周期详解](bean-lifecycle/) | ⭐⭐⭐⭐ | 实例化 → 注入 → 初始化 → 销毁 12 步 |

### AOP 与事务
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [@Transactional 失效 8 种场景](transactional-pitfalls/) | ⭐⭐⭐⭐⭐ | 同类调用 / 异常类型 / 多线程 / 传播行为 |

---

## 待补充的高频面试题（强烈建议）

### IoC 与 Bean（必考）
- **Bean 生命周期详解**（实例化 → 属性注入 → 初始化 → 销毁）
- **循环依赖三级缓存解决**（DefaultSingletonBeanRegistry）
- **@Bean 与 @Component 区别**
- **Spring 中的代理对象**（什么时候用 JDK 动态代理 vs CGLIB）
- **@Scope 作用域**（singleton / prototype / request / session）

### AOP（高频）
- **AOP 实现原理**（JDK 动态代理 vs CGLIB）
- **@Transactional 失效的 8 种场景**（同类调用、异常类型、propagation 配置...）
- **@Transactional 传播行为**（7 种 propagation）
- **@Async 失效问题**（同类调用、线程池配置）

### Spring MVC（高频）
- **Spring MVC 请求处理流程**（DispatcherServlet → HandlerMapping → HandlerAdapter → ViewResolver）
- **@RestController vs @Controller**
- **拦截器 vs 过滤器 vs AOP**
- **全局异常处理**（@ControllerAdvice + @ExceptionHandler）

### Spring Boot（高频）
- **Spring Boot 自动配置原理**（@EnableAutoConfiguration + spring.factories）
- **Starter 机制**
- **条件注解**（@ConditionalOnClass / @ConditionalOnMissingBean）
- **配置文件加载顺序**

### Spring Security（中频）
- **过滤器链执行顺序**
- **认证 vs 授权流程**
- **JWT vs Session 方案对比**
- **CSRF 防护**

### Spring Cloud（中频）
- **服务注册与发现**（Nacos / Eureka / Consul）
- **负载均衡**（Ribbon / LoadBalancer）
- **熔断降级**（Sentinel / Resilience4j）
- **配置中心**（Nacos Config / Spring Cloud Config）

---

## 学习路径

1. **入门**（3 天）：@Autowired 推荐用法 + POJO/VO/DTO 区别
2. **进阶**（2 周）：Bean 生命周期 + @Transactional 失效场景 + AOP 原理
3. **冲刺面试**：重点看"循环依赖三级缓存"、"AOP 实现原理"、"自动配置原理"（待补）

## 交叉引用

- 主模块：[`note/06.spring`](../../06.spring/) — Spring 知识体系
- 相关章节：[`01.java`](../01.java/)（Java 基础）/ [`04.system-design`](../04.system-design/)（系统设计）
