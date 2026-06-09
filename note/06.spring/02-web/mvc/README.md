# Spring MVC

**Spring MVC** 是 **Spring Framework** 中用于构建 **Web 应用程序** 和 **RESTful Web 服务** 的核心模块。它基于经典的 **MVC（Model-View-Controller）架构模式** 设计，将应用程序的不同关注点（业务逻辑、数据展示、用户交互）分离，使代码更清晰、可维护、可测试。

## 核心思想：MVC 架构
*   **Model (模型):** 代表应用程序的数据和业务逻辑（如 Java 对象、数据库操作）。它**不依赖**于 Web 层。
*   **View (视图):** 负责数据的**呈现**（如 JSP, Thymeleaf, FreeMarker 模板，或 JSON/XML 响应）。它从 Model 获取数据并渲染给用户。
*   **Controller (控制器):** 是**核心枢纽**。它接收用户的 HTTP 请求，调用 Model 处理业务逻辑，选择合适的 View 渲染结果，或直接返回数据（如 REST API）。

## 为什么需要 Spring MVC？
*   **解决传统 Servlet/JSP 开发痛点：** 避免在 Servlet 中混杂业务逻辑、数据访问和视图渲染代码，导致代码臃肿、难以维护和测试。
*   **提供强大的基础设施：** 封装了底层 Servlet API 的复杂性（如请求/响应处理、会话管理），开发者只需关注业务逻辑。
*   **高度可配置和可扩展：** 通过配置（XML 或 Java Config）和丰富的接口/抽象类，可以灵活定制几乎任何环节（如参数解析、数据绑定、验证、视图解析、异常处理）。
*   **无缝集成 Spring 生态：** 与 Spring 的核心特性（IoC 容器、AOP、事务管理、数据访问、安全性等）深度集成，享受一致的编程模型和强大的企业级能力。
*   **强大的 REST 支持：** 是构建现代 RESTful Web 服务的首选框架之一（配合 `@RestController`）。

## 核心组件与工作流程
Spring MVC 的核心是一个 **前端控制器 (Front Controller)** 模式实现：

1.  **`DispatcherServlet` (核心引擎):**
  *   本质上是**一个 Servlet**（通常映射到 `/`）。
  *   作为**所有请求的单一入口点**。
  *   负责协调整个请求处理流程。

2.  **请求处理流程:**
  1.  用户发起 HTTP 请求 (e.g., `GET /users/123`)。
  2.  请求被 Servlet 容器（如 Tomcat）接收，并转发给 `DispatcherServlet`。
  3.  **`HandlerMapping`:** `DispatcherServlet` 询问一组 `HandlerMapping` 接口实现，找到能处理此请求的 **Controller** (具体是 Controller 中的某个方法，即 **Handler**)。
  4.  **`HandlerAdapter`:** `DispatcherServlet` 调用 `HandlerAdapter`，它负责**真正执行**找到的 Controller 方法。
    *   **参数解析：** `HandlerAdapter` 利用各种 `HandlerMethodArgumentResolver` 将 HTTP 请求数据（路径变量、查询参数、表单数据、请求体 JSON/XML、Header 等）**自动绑定**到 Controller 方法的参数上。
    *   **数据验证：** 可选地对绑定后的参数进行验证（如 JSR-303 `@Valid`）。
    *   **执行方法：** 调用 Controller 方法，执行业务逻辑，返回一个 **`ModelAndView`** 对象（包含 Model 数据和 View 名称）或直接返回数据（`@ResponseBody`）。
  5.  **处理结果：**
    *   **视图渲染 (传统 Web):** 如果返回 `ModelAndView`，`DispatcherServlet` 通过 **`ViewResolver`** 将逻辑视图名称（如 `"userProfile"`）解析为具体的物理视图对象（如 `ThymeleafView`）。视图对象使用 Model 中的数据进行渲染，生成最终的 HTML 响应。
    *   **直接响应 (REST API):** 如果 Controller 方法标记了 `@ResponseBody` (或类标记了 `@RestController`)，返回值会被 **`HttpMessageConverter`** (如 `MappingJackson2HttpMessageConverter` for JSON) 直接序列化为 HTTP 响应体（如 JSON/XML），无需视图解析。
  6.  **异常处理：** 整个流程中发生的异常，可由 **`HandlerExceptionResolver`** 链统一捕获和处理（如返回自定义错误页面或 JSON 错误信息）。
  7.  `DispatcherServlet` 将最终生成的响应返回给客户端。

## 关键特点与优势
*   **注解驱动开发 (`@Controller`, `@RequestMapping` 等):** 极大简化配置，使代码更简洁、意图更清晰。这是现代 Spring MVC 开发的主流方式。
*   **松耦合：** 各组件（Controller, Service, Repository）通过接口和 Spring IoC 容器管理依赖，易于单元测试和模块替换。
*   **强大的数据绑定与验证：** 自动将请求参数映射到 Java 对象，并支持 JSR-303 Bean Validation 规范。
*   **灵活的视图技术：** 无缝支持 JSP, Thymeleaf, FreeMarker, Velocity, JSON, XML 等各种视图技术，易于切换。
*   **一流的 REST 支持：** 通过 `@RestController`, `@PathVariable`, `@RequestBody`, `@ResponseBody`, `HttpMessageConverter` 等，轻松构建符合 REST 原则的 Web 服务。
*   **国际化 (i18n) 与主题 (Themes) 支持：** 内置对多语言和主题切换的支持。
*   **文件上传/下载：** 提供简单易用的 API 处理文件上传和下载。
*   **与 Spring Boot 深度集成：** **Spring Boot** 极大简化了 Spring MVC 应用的**配置和部署**。通过 `spring-boot-starter-web` 依赖，自动配置 `DispatcherServlet`、常用视图解析器、JSON 转换器等，开发者几乎可以做到“开箱即用”，专注于业务代码。**如今，绝大多数新项目都采用 Spring Boot + Spring MVC (或 Spring WebFlux) 的组合。**

## Spring MVC vs. Spring Boot
*   **Spring MVC:** 是 Spring Framework 中**专门处理 Web 层**的一个**模块/技术**。它定义了 Web 应用的架构和核心组件。
*   **Spring Boot:** 是一个**快速开发框架/平台**，它**包含并自动配置**了 Spring MVC（以及其他 Spring 模块和第三方库）。Spring Boot 的目标是消除繁琐的 XML 配置，提供生产级特性（监控、健康检查、外部化配置等），简化应用的创建、部署和运维。
*   **关系：** 你可以只用 Spring MVC（需要手动配置大量 XML/Java Config），但**强烈推荐**在 Spring Boot 的基础上使用 Spring MVC。Spring Boot 是构建 Spring MVC 应用的**最佳实践和事实标准**。

## 总结
**Spring MVC 是一个强大、灵活、基于 MVC 模式的 Java Web 框架，是 Spring Framework 的核心 Web 模块。** 它通过 `DispatcherServlet` 作为前端控制器，利用注解驱动的方式，将请求分发给 Controller 处理业务逻辑，协调 Model 和 View，最终生成响应。它解决了传统 Web 开发的痛点，提供了企业级应用所需的基础设施，并与 Spring 生态无缝集成。**在现代 Java 开发中，它通常与 Spring Boot 结合使用，以实现极高的开发效率和生产力。** 理解 Spring MVC 的核心概念（尤其是请求处理流程和关键组件）对于成为合格的 Java Web 开发者至关重要。