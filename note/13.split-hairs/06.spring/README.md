# Spring 咬文嚼字

> Spring 高频面试题与细节深挖，对齐主模块 [`06.spring`](../../06.spring/)

---

## 文章清单

### 基础
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [为什么不推荐 @Autowired](not-use-@autowired/) | ⭐⭐⭐ | 字段注入 vs 构造器注入 vs Setter 注入 |
| [各种 O 解释](clarify-various-o/) | ⭐⭐⭐ | POJO / VO / BO / DTO / DO 区别 |

### IoC 与 Bean
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Bean 生命周期详解](bean-lifecycle/) | ⭐⭐⭐⭐ | 实例化 → 注入 → 初始化 → 销毁 12 步 |
| [@Bean vs @Component](bean-vs-component/) | ⭐⭐⭐⭐ | 两种 Bean 注册方式的区别与选择 |
| [Spring Boot 自动配置原理](auto-configuration/) | ⭐⭐⭐⭐⭐ | @EnableAutoConfiguration + spring.factories + 条件注解 |
| [循环依赖三级缓存](circular-dependency/) | ⭐⭐⭐⭐⭐ | DefaultSingletonBeanRegistry 如何解决循环依赖 |

### AOP 与事务
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [@Transactional 失效 8 种场景](transactional-pitfalls/) | ⭐⭐⭐⭐⭐ | 同类调用 / 异常类型 / 多线程 / 传播行为 |
| [@Transactional 传播行为](transactional-propagation/) | ⭐⭐⭐⭐⭐ | 7 种 propagation（REQUIRED / REQUIRES_NEW / NESTED ...） |
| [JDK 动态代理 vs CGLIB](jdk-proxy-vs-cglib/) | ⭐⭐⭐⭐ | 两种代理机制的原理、区别与 Spring 选择策略 |
| [AOP 实现原理](aop-principle/) | ⭐⭐⭐⭐ | 切面、通知、连接点、切入点概念与底层实现 |
| [@Async 失效 4 种场景](async-pitfalls/) | ⭐⭐⭐⭐ | 同类调用 / 非 @Bean / 线程池缺失 / 内部方法调用 |
| [Spring 事件机制](event-mechanism/) | ⭐⭐⭐⭐ | ApplicationEvent / ApplicationListener / @EventListener |

### Spring MVC
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Spring MVC 请求处理流程](spring-mvc-flow/) | ⭐⭐⭐⭐ | DispatcherServlet → HandlerMapping → HandlerAdapter → ViewResolver |

---

## 待补充的高频面试题（强烈建议）

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
2. **进阶**（2 周）：Bean 生命周期 + @Transactional 失效场景 + AOP 原理 + 循环依赖
3. **冲刺面试**：重点看"自动配置原理"、"传播行为"、"JDK 代理 vs CGLIB"、"@Async 失效"

## 交叉引用

- 主模块：[`note/06.spring`](../../06.spring/) — Spring 知识体系
- 相关章节：[`01.java`](../01.java/)（Java 基础）/ [`04.system-design`](../04.system-design/)（系统设计）
