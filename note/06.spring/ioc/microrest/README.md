# MicroRest - 轻量级 Spring MVC 框架实现

## 项目概述

MicroRest 是一个使用 Servlet 技术模拟 Spring IoC 和 MVC 功能的轻量级框架。该项目通过自定义注解、依赖注入、请求映射等功能，实现了类似 Spring Boot 的基础功能。

## 核心功能

### 1. IoC 容器管理
- **Bean 扫描与注册**：基于 [@Service](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\Service.java#L4-L9) 和 [@RestController](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\RestController.java#L4-L9) 注解自动扫描和注册组件
- **依赖注入**：通过 [@Autowired](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\Autowired.java#L4-L9) 实现字段级别的依赖注入
- **配置加载**：从 [application.yml](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\resources\application.yml) 文件读取扫描路径等配置信息

### 2. MVC 架构支持
- **控制器映射**：[@RestController](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\RestController.java#L4-L9) 和 [@GetMapping](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\GetMapping.java#L4-L9) 注解实现 RESTful 接口
- **参数绑定**：[@RequestParam](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\RequestParam.java#L4-L9) 注解支持请求参数绑定
- **请求分发**：[DispatcherServlet](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\DispatcherServlet.java#L15-L72) 负责路由请求到对应处理方法

## 项目结构

```
src/main/java/cn/wubo/micro/rest/
├── core/                     # 框架核心组件
│   ├── annotation/           # 自定义注解
│   ├── handler/              # 请求处理器
│   ├── util/                 # 工具类
│   ├── DefaultConfig.java    # 默认配置类
│   ├── DispatcherServlet.java # 请求分发器
│   └── StartServlet.java     # 启动初始化器
└── demo/                     # 示例代码
    ├── HelloController.java  # 示例控制器
    └── HelloService.java     # 示例服务
```


## 核心组件说明

### 注解系统
- [@Service](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\Service.java#L4-L9): 标记服务层组件
- [@RestController](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\RestController.java#L4-L9): 标记控制器组件
- [@Autowired](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\Autowired.java#L4-L9): 实现依赖注入
- [@GetMapping](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\GetMapping.java#L4-L9): 映射 GET 请求
- [@RequestParam](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\RequestParam.java#L4-L9): 绑定请求参数

### 启动流程 ([StartServlet](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\StartServlet.java#L21-L216))
1. **配置加载**: 读取 [application.yml](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\resources\application.yml) 配置文件
2. **包扫描**: 根据配置的扫描路径查找所有类
3. **Bean 初始化**: 创建带注解类的实例并存入 IoC 容器
4. **依赖注入**: 解析 [@Autowired](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\annotation\Autowired.java#L4-L9) 注解并注入依赖
5. **处理器映射**: 建立 URL 与方法的映射关系

### 请求处理流程 ([DispatcherServlet](file://D:\developer\IdeaProjects\wb04307201\note\06.spring\ioc\microrest\src\main\java\cn\wubo\micro\rest\core\DispatcherServlet.java#L15-L72))
1. **请求接收**: 拦截所有请求
2. **路径匹配**: 根据请求 URL 查找对应的处理器
3. **参数解析**: 解析请求参数并转换为方法参数
4. **方法调用**: 通过反射执行目标方法
5. **响应返回**: 输出处理结果

## 技术栈

- **Servlet API**: Jakarta Servlet 6.1.0
- **构建工具**: Maven Wrapper
- **日志框架**: Logback
- **辅助库**: Commons Lang3、Lombok
- **服务器**: Jetty (端口 6633)

## 使用方法

1. **启动服务**:
   ```bash
   mvn jetty:run
   ```


2. **访问示例接口**:
   - `GET /hello?name=World` → 返回 "Hello World!"
   - `GET /hello1?name=John&name1=Jane` → 返回 "Hello John and Jane!"

## 设计特点

- **轻量化**: 仅实现 Spring 的核心功能，代码简洁易懂
- **可扩展**: 模块化设计，易于添加新功能
- **教学价值**: 适合学习 Spring 框架的设计原理
- **注解驱动**: 使用自定义注解简化开发流程

## 限制与待完善

- 仅支持 GET 请求（可通过扩展支持其他 HTTP 方法）
- 参数处理仅支持基本类型和特定对象（HttpServletRequest/HttpServletResponse）
- 缺少 AOP、事务管理等高级特性
- 错误处理机制相对简单

该项目适合用于学习 Spring 框架内部实现原理，了解 IoC 容器和 MVC 模式的运作机制。