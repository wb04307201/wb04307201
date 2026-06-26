# 手写 Mini Spring

> 通过 200 行 Servlet 模拟 Spring IoC + MVC，理解框架底层运作机制

---

## 导航

| 序号 | 主题 | 核心内容 |
|------|------|---------|
| 1 | [microrest/](microrest/README.md) | MicroRest 轻量实现：Bean 扫描、字段注入、GET 请求分发 |

---

## 知识脉络

```mermaid
graph TB
    A[Mini Spring] --> B[microrest 项目]
    B --> C[IoC 容器]
    B --> D[MVC 分发]

    C --> C1[@Service/@RestController 扫描]
    C --> C2[@Autowired 字段注入]
    C --> C3[StartServlet 启动流程]

    D --> D1[@GetMapping 映射]
    D --> D2[@RequestParam 参数绑定]
    D --> D3[DispatcherServlet 请求分发]
```

---

## 学习价值

本项目是一个**教学型 mini 框架**，用 Servlet 模拟 Spring 核心机制：

- **IoC 容器**：通过类扫描 → 实例化 → 依赖注入，理解 Spring 如何管理 Bean
- **MVC 分发**：通过 URL 映射 → 参数解析 → 反射调用，理解 Spring MVC 请求流转
- **注解驱动**：自定义注解替代 XML 配置，理解 Spring 的注解处理链

## 范围与限制

| 已实现 | 未实现 |
|--------|--------|
| Bean 扫描与注册 | AOP / 动态代理 |
| 字段级 `@Autowired` | `@Qualifier` / `@Primary` |
| GET 请求分发 | POST / PUT / DELETE |
| 基础 `@RequestParam` | 复杂参数绑定 |
| YAML 配置加载 | `@Configuration` / `@Bean` |
| 日志与 Servlet 容器 | Bean 生命周期 / 作用域 |

## 核心流程

```
配置加载 → 包扫描 → Bean 实例化 → 依赖注入 → 处理器映射 → 启动监听
```

---

## 相关章节

- 上游：[`01 核心容器`](../README.md) — IoC 容器 + AOP 框架 + 工具集
- 关联：[`IoC 容器`](../ioc/README.md) — 理解 Spring 原生 Bean 管理
- 关联：[`AOP 总览`](../aop/README.md) — Mini Spring 未覆盖 AOP，需另行学习
- 关联：[`02 Web 层`](../../02-web/README.md) — Spring MVC 完整实现

---

> 建议路径：先读 [IoC 容器](../ioc/README.md) 理解概念 → 再看 MicroRest 代码 → 对照 Spring 源码验证理解
