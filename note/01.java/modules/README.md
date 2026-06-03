# Java 模块系统 (JPMS / Java 9+)

> Java 9 引入的模块系统（JPMS — Java Platform Module System）是 Java 历史上最大的架构变革之一，它从根本上改变了 JAR 的组织方式和类加载器的行为。

---

## 一、为什么需要模块化

### 1.1 JAR Hell 问题

在 Java 9 之前，所有依赖都放在类路径（classpath）上，导致一系列经典问题：

| 问题类型 | 表现 | 根本原因 |
|---------|------|---------|
| **版本冲突** | `NoSuchMethodError`、`ClassNotFoundException` | 同一依赖的多个版本同时出现在 classpath |
| **隐式依赖** | 编译通过但运行时失败 | 间接依赖未声明，运行时才发现缺失 |
| **巨型 JAR** | 应用打包包含大量无用类 | 无法按需裁剪，`rt.jar` 本身就有 60MB+ |
| **封装泄露** | 内部 API 被外部随意使用 | `public` 即暴露，无法控制可见性边界 |
| **启动慢** | 扫描整个 classpath | 启动时需要查找所有可用类 |

### 1.2 经典案例

```
Exception in thread "main" java.lang.NoSuchMethodError:
  com.google.common.collect.ImmutableList.of(Ljava/lang/Object;)Lcom/google/common/collect/ImmutableList;
```

Guava 的两个版本同时存在，编译时用了一个版本，运行时加载了另一个。模块系统通过**可读性约束**在启动时就能检测此类冲突。

### 1.3 模块化带来的收益

- **可靠的配置**：启动时验证模块依赖，失败即退出，而非运行时 NPE
- **强封装**：模块内部实现默认不可见，只有显式 `exports` 的包才可访问
- **按需裁剪**：通过 `jlink` 只打包需要的模块，减小运行时体积
- **更好的可维护性**：模块图清晰，架构边界明确

---

## 二、module-info.java 语法

### 2.1 基本结构

模块声明文件位于源码根目录，命名为 `module-info.java`：

```java
module com.example.mymodule {
    // 声明导出的包
    exports com.example.mymodule.api;
    exports com.example.mymodule.service to com.example.consumer;

    // 声明依赖
    requires java.base;
    requires transitive com.example.common;
    requires static com.example.optional;

    // 开放反射访问
    opens com.example.mymodule.internal;

    // SPI 声明
    uses com.example.mymodule.spi.Plugin;
    provides com.example.mymodule.spi.Plugin
        with com.example.mymodule.impl.DefaultPlugin;
}
```

### 2.2 命名规则

- 模块名使用**反向域名**，与包名风格一致（如 `com.fasterxml.jackson.databind`）
- 模块名与顶层包名建议保持一致，降低认知成本
- 模块名必须是**合法的 Java 标识符**（不能用连字符 `-`，需用点号 `.`）

### 2.3 java.base 模块

所有模块**隐式依赖** `java.base`，无需显式声明。该模块包含 `java.lang`、`java.util`、`java.io` 等核心包。

### 2.4 模块声明关键字速查

| 关键字 | 作用 | 编译时 | 运行时 |
|--------|------|--------|--------|
| `exports` | 导出包（编译 + 运行） | 可访问 | 可反射访问 public 成员 |
| `opens` | 开放包（深度反射） | 不可用 | 可反射访问所有成员（含 private） |
| `requires` | 声明依赖 | 编译可见 | 运行时可读 |
| `requires static` | 可选依赖 | 编译需要 | 运行时可缺失 |
| `requires transitive` | 传递依赖 | 读我即读它 | 传递可见 |
| `uses` | 声明使用的 SPI | 校验服务类型 | 允许 `ServiceLoader` 查找 |
| `provides ... with` | 声明 SPI 实现 | 校验实现关系 | 注册到服务发现 |

---

## 三、exports vs opens（反射访问）

### 3.1 exports：编译时 + 运行时的类型安全访问

```java
// module-info.java
module com.example.api {
    exports com.example.api.dto;
    // exports ... to com.example.consumer; // 限定导出
}
```

- `exports` 使包中的 **public 类型和 public 成员**对其他模块可见
- 支持**限定导出**（qualified exports），仅对指定模块可见
- 反射调用 `setAccessible(true)` 在 exports 的包上**可以访问 public 成员**，但**无法访问 private/protected 成员**

### 3.2 opens：深度反射访问（框架场景）

```java
module com.example.app {
    opens com.example.app.entity;            // 对所有模块开放
    opens com.example.app.config to org.hibernate, com.fasterxml.jackson.databind;  // 限定开放
}
```

| 特性 | exports | opens |
|------|---------|-------|
| 编译时类型访问 | ✅ | ❌ |
| 运行时反射（public） | ✅ | ✅ |
| 运行时反射（private/protected） | ❌ | ✅ |
| 框架场景（Jackson/Hibernate/Spring） | 不够 | ✅ |
| `setAccessible(true)` | 部分 | 完全 |

### 3.3 open module：全模块开放

```java
open module com.example.app {
    requires spring.context;
    requires com.fasterxml.jackson.databind;
}
```

`open module` 等价于对模块中所有包执行 `opens`，通常用于纯数据层模块（DTO、Entity），但**不推荐用于业务模块**，会破坏封装性。

### 3.4 反射访问决策流程

```
模块A 访问 模块B 的某个类
    |
    ├── 编译时：检查 exports（或 qualified exports）
    │       ├── exports → 编译通过
    │       └── 未 exports → 编译失败
    |
    └── 运行时反射：
            ├── opens → 可访问所有成员（含 private）
            ├── exports → 仅可访问 public 成员
            └── 既未 exports 也未 opens → InaccessibleObjectException
```

---

## 四、requires（依赖声明）

### 4.1 基本用法

```java
module com.example.service {
    requires com.example.dao;
    requires java.sql;
    requires java.logging;
}
```

`requires` 声明**模块间的依赖关系**，编译器据此检查类型可用性。

### 4.2 可读性规则

- 模块 A `requires` 模块 B → A **可读** B
- A 只能访问 B 中 B 显式 `exports` 的包
- A **不能**访问 B 依赖的其他模块（除非使用 `requires transitive`）

### 4.3 常见模块依赖图

```
com.example.web
    ├── requires com.example.service
    └── requires java.servlet

com.example.service
    ├── requires com.example.dao
    └── requires java.persistence

com.example.dao
    ├── requires java.sql
    └── requires java.logging

java.base（隐式依赖，所有模块自动可读）
```

### 4.4 requires static：可选依赖

```java
module com.example.app {
    requires static com.google.gson;  // 编译时需要，运行时可选
}
```

典型场景：
- 可选功能（如 JSON 解析，运行时可能用 Jackson 替代 Gson）
- 注解处理器依赖（编译后不再需要）
- 测试依赖（运行时不需要）

---

## 五、requires transitive（传递依赖）

### 5.1 概念

```java
// 模块A
module module.a {
    exports com.example.a.api;
    requires module.b;
}

// 模块B
module module.b {
    exports com.example.b.api;
    requires transitive module.c;   // 传递依赖！
}

// 模块C
module module.c {
    exports com.example.c.api;
}
```

当模块 X 读取 `module.b` 时，由于 `requires transitive module.c`，X **也自动可读** `module.c`。

### 5.2 传递性规则

| 声明方式 | 读我的模块能否读到目标 |
|----------|----------------------|
| `requires B` | 否 |
| `requires transitive B` | 是 |

### 5.3 典型场景：API 模块暴露依赖类型

```java
// user-api 模块的公共接口返回了 Address 类型
module com.example.user.api {
    exports com.example.user.api;
    requires transitive com.example.common.api;  // Address 在 common.api 中
}
```

如果 `user.api` 的某个导出类在方法签名中使用了 `com.example.common.api.Address`，则必须使用 `requires transitive`，否则消费方无法编译。

### 5.4 过度使用传递依赖的风险

```
❌ 不推荐：
requires transitive guava;           // guava 是内部实现细节
requires transitive spring.context;  // 框架依赖不应传递

✅ 推荐：
requires guava;                      // 内部使用，不暴露
requires spring.context;             // 内部使用，不暴露
```

**原则**：只有当模块的公共 API 暴露了来自依赖模块的类型时，才使用 `requires transitive`。

---

## 六、uses / provides（SPI 支持）

### 6.1 Service Provider Interface 机制

JPMS 内置了对 SPI 的支持，通过 `uses` 和 `provides` 关键字替代传统的 `META-INF/services/` 配置。

### 6.2 uses：声明服务使用方

```java
module com.example.app {
    uses com.example.plugin.spi.Plugin;
}
```

`uses` 声明模块将使用 `ServiceLoader` 查找 `Plugin` 接口的实现。

### 6.3 provides ... with：声明服务提供方

```java
module com.example.plugin.impl {
    requires com.example.plugin.spi;

    provides com.example.plugin.spi.Plugin
        with com.example.plugin.impl.DefaultPlugin,
             com.example.plugin.impl.AdvancedPlugin;
}
```

### 6.4 SPI 完整示例

```java
// ===== SPI 模块 =====
// module-info.java
module com.example.spi {
    exports com.example.spi;
}

// 接口定义
package com.example.spi;
public interface MessageSender {
    void send(String message);
}

// ===== 提供方模块 =====
// module-info.java
module com.example.sender.email {
    requires com.example.spi;
    provides com.example.spi.MessageSender
        with com.example.sender.email.EmailSender;
}

// ===== 使用方模块 =====
// module-info.java
module com.example.app {
    requires com.example.spi;
    uses com.example.spi.MessageSender;
}

// 使用 ServiceLoader 查找实现
ServiceLoader<MessageSender> loader =
    ServiceLoader.load(MessageSender.class);
for (MessageSender sender : loader) {
    sender.send("Hello JPMS!");
}
```

### 6.5 与旧版 SPI 对比

| 特性 | 旧版 (META-INF/services) | JPMS (uses/provides) |
|------|-------------------------|---------------------|
| 配置方式 | 手动创建文本文件 | module-info.java 声明 |
| 编译时校验 | ❌ 无 | ✅ 类型安全校验 |
| 模块图可见性 | ❌ 不可见 | ✅ 可见 |
| 类路径兼容 | ✅ | ✅（兼容模式） |
| 限定服务可见性 | ❌ | ✅（模块级） |

---

## 七、模块化 vs 类路径

### 7.1 两条路径的共存

| 维度 | 类路径 (Classpath) | 模块路径 (Modulepath) |
|------|-------------------|----------------------|
| 可见性 | 所有 JAR 互相可见 | 需显式 exports/requires |
| 封装性 | 无（public 即暴露） | 强封装 |
| 依赖校验 | 运行时才发现 | 启动时校验 |
| 启动速度 | 扫描整个 classpath | 基于模块图 |
| 向后兼容 | N/A | 非模块化 JAR 作为**无名模块** |

### 7.2 无名模块 (Unnamed Module)

当非模块化 JAR 放在模块路径上时，它成为一个**无名模块**：
- 可以读取所有模块
- 所有包都被导出
- 无法声明依赖关系

### 7.3 自动模块 (Automatic Module)

将普通 JAR 放在模块路径上且没有 `module-info.java` 时，Java 会为其创建一个**自动模块**：
- 模块名从 JAR 文件名推导（如 `guava-31.1.jar` → `guava`）
- **导出所有包**（等同于 `open module`）
- **可以读取所有模块**
- 可以读取其他自动模块和具名模块

### 7.4 启动参数控制

```bash
# 强制打开某模块的包（绕过封装，临时兼容方案）
java --add-opens java.base/java.lang=ALL-UNNAMED

# 添加导出（编译时绕过）
javac --add-exports java.base/jdk.internal.misc=my.module

# 添加模块路径
javac --module-path mods -d out $(find src -name "*.java")

# 运行模块应用
java --module-path mods --module com.example.app/com.example.app.Main

# 查看模块图
java --module-path mods --show-module-resolution --module com.example.app
```

### 7.5 迁移阶段对照

| 阶段 | 状态 | 说明 |
|------|------|------|
| 阶段一 | 全类路径 | 传统方式，无任何模块特性 |
| 阶段二 | 类路径 + 部分模块路径 | 核心依赖模块化，部分旧库仍在 classpath |
| 阶段三 | 全模块路径 | 所有依赖模块化 |
| 阶段四 | 完全模块化 | 所有代码有 module-info.java |

---

## 八、jlink（自定义运行时镜像）

### 8.1 基本概念

`jlink` 允许你**按需打包** Java 运行时，只包含应用实际使用的模块，大幅缩减 JRE 体积。

### 8.2 基础用法

```bash
# 1. 编译模块
javac --module-path mods -d out $(find src -name "*.java")

# 2. 打包模块
jar --module-version 1.0 --file mods/mymodule.jar -C out .

# 3. 使用 jlink 创建自定义运行时
jlink --module-path $JAVA_HOME/jmods:mods \
      --add-modules com.example.app \
      --output myapp-runtime \
      --launcher myapp=com.example.app/com.example.app.Main \
      --strip-debug \
      --compress=2 \
      --no-header-files \
      --no-man-pages
```

### 8.3 jlink 常用参数

| 参数 | 说明 | 效果 |
|------|------|------|
| `--module-path` | 模块搜索路径 | 指定 jmods 目录和应用模块 |
| `--add-modules` | 包含的模块 | 根模块（自动包含依赖） |
| `--output` | 输出目录 | 生成的运行时镜像位置 |
| `--launcher` | 创建启动脚本 | 格式 `名称=模块/主类` |
| `--strip-debug` | 移除调试信息 | 减小体积 |
| `--compress=<level>` | 压缩级别 (0/1/2) | 2 = 最高压缩 |
| `--no-header-files` | 排除头文件 | 减小体积 |
| `--no-man-pages` | 排除 man 手册 | 减小体积 |
| `--bind-services` | 链接服务提供者 | 将 SPI 实现打包进来 |
| `--limit-modules` | 限制可见模块 | 安全加固 |

### 8.4 体积对比示例

```
完整 JDK (jdk-17)          ~300MB
jlink (java.base + app)    ~30MB    ← 缩减约 90%
jlink + 压缩 + 裁剪        ~20MB    ← 最小化
```

### 8.5 jlink 的限制

- 只能链接**具名模块**，类路径上的 JAR 无法通过 jlink 打包
- 如果应用使用 `ServiceLoader` 动态加载，需用 `--bind-services` 或在运行时通过 `--module-path` 补充
- 使用反射访问的类必须确保模块正确 `opens`

---

## 九、迁移非模块化代码

### 9.1 迁移路径

```
[classpath 应用]
      │
      ▼
┌─────────────────────────┐
│ 步骤1: 识别模块边界      │  分析包结构，确定模块划分
├─────────────────────────┤
│ 步骤2: 创建 module-info  │  为每个模块添加声明文件
├─────────────────────────┤
│ 步骤3: 处理依赖          │  确认所有依赖的模块化状态
├─────────────────────────┤
│ 步骤4: 处理反射/深度访问 │  opens 框架需要的包
├─────────────────────────┤
│ 步骤5: 测试验证          │  运行完整测试套件
├─────────────────────────┤
│ 步骤6: jlink 打包        │  可选，创建最小运行时
└─────────────────────────┘
```

### 9.2 常见问题及解决方案

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `InaccessibleObjectException` | 反射访问未 opens 的包 | 添加 `opens` 或使用 `--add-opens` |
| 编译时找不到类 | 缺少 requires 声明 | 检查 module-info.java 的依赖 |
| 自动模块名冲突 | 多个 JAR 推导同名 | 使用 `Automatic-Module-Name` MANIFEST 条目 |
| SPI 实现未找到 | uses/provides 未声明 | 补充 module-info.java 中的 SPI 声明 |
| 编译通过但运行失败 | 传递依赖未声明 | 使用 `requires transitive` 或补充 `requires` |

### 9.3 渐进式迁移策略

**策略一：自动模块过渡**
```
不急于写 module-info.java，先将依赖 JAR 放到 module-path 上，
Java 会自动为它们创建自动模块。验证兼容性后再逐个添加 module-info.java。
```

**策略二：MANIFEST.MF 声明模块名**
```
为 JAR 添加 MANIFEST.MF 条目：
Automatic-Module-Name: com.example.mymodule

这确保了自动模块名的稳定性，避免 JAR 文件名变化导致模块名变化。
```

**策略三：混合模式运行**
```bash
# 部分模块在 module-path，部分在 classpath
java --module-path mods -cp legacy.jar com.example.app.Main
```

### 9.4 jdeps 分析工具

```bash
# 分析 JAR 的依赖
jdeps myapp.jar

# 分析模块依赖
jdeps --module-path mods --module-info com.example.app

# 列出 JDK 内部 API 的使用
jdeps --jdk-internals myapp.jar

# 生成 module-info.java 模板
jdeps --generate-module-info out myapp.jar
```

---

## 十、最佳实践

### 10.1 模块设计原则

| 原则 | 说明 | 反例 |
|------|------|------|
| **单一职责** | 一个模块只做一件事 | 一个模块包含 web + dao + service |
| **最小导出** | 只导出公共 API 包 | `exports com.example.**` 全部导出 |
| **隐藏实现** | 内部包放在 `impl` 包下 | 内部类放在公共包中 |
| **避免循环** | 模块依赖图应无环 | A→B→C→A |
| **稳定接口** | API 模块与 Impl 模块分离 | 实现细节暴露在接口中 |

### 10.2 推荐的模块分层结构

```
┌─────────────────────────────────────────┐
│           com.example.web               │  ← HTTP 层
├─────────────────────────────────────────┤
│           com.example.service.api       │  ← 接口层
│           com.example.service.impl      │  ← 实现层
├─────────────────────────────────────────┤
│           com.example.dao               │  ← 数据访问层
├─────────────────────────────────────────┤
│           com.example.common            │  ← 公共工具层
├─────────────────────────────────────────┤
│           java.base (隐式)              │  ← JDK 核心
└─────────────────────────────────────────┘
```

### 10.3 module-info.java 编写规范

```java
// ✅ 好的实践
module com.example.order.service {
    // 1. 先声明导出的公共 API
    exports com.example.order.service.api;

    // 2. 限定导出（如有需要）
    exports com.example.order.service.internal to com.example.order.web;

    // 3. 声明依赖
    requires com.example.order.dao;
    requires com.example.common;
    requires java.persistence;

    // 4. 框架反射需要的包
    opens com.example.order.service.entity to org.hibernate;

    // 5. SPI 声明
    uses com.example.order.service.spi.OrderValidator;
}
```

### 10.4 命名约定

```
✅ 推荐：
com.example.project.api          # 公共接口模块
com.example.project.impl         # 实现模块（可不导出）
com.example.project.core         # 核心共享模块
com.example.project.web          # Web 层模块

❌ 避免：
com.example.project-all          # 巨型模块
com.example.project.utils        # 过于笼统
com.example-project              # 连字符不合法
```

### 10.5 常见陷阱

1. **忘记 `requires transitive`**：API 模块使用了依赖的类型但未声明传递依赖，导致消费方编译失败
2. **过度 `opens`**：将整个模块 `open`，破坏了封装性优势
3. **SPI 忘记 `uses`**：使用 `ServiceLoader` 但未在 module-info.java 中声明 `uses`
4. **测试模块未配置**：测试代码需要独立的 `module-info.java`（通常放在 `src/test/java`）
5. **IDE 与构建工具不同步**：IDE 识别了模块但 Maven/Gradle 未配置 `maven-compiler-plugin` 的 `--module-path`

### 10.6 Maven 配置示例

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.11.0</version>
    <configuration>
        <release>17</release>
        <source>17</source>
        <target>17</target>
    </configuration>
</plugin>
```

> 注意：Maven 3.9+ 默认支持模块路径，无需额外配置。旧版本需要确认 `maven-compiler-plugin` 版本 >= 3.6。

---

## 附录：JPMS 核心模块速查表

| 模块名 | 包含内容 | 典型场景 |
|--------|---------|---------|
| `java.base` | lang, util, io, net | 所有项目（隐式依赖） |
| `java.sql` | JDBC API | 数据库操作 |
| `java.persistence` | JPA | ORM 框架 |
| `java.logging` | java.util.logging | 日志记录 |
| `java.xml` | DOM, SAX, StAX | XML 处理 |
| `java.desktop` | AWT, Swing | GUI 应用 |
| `java.net.http` | HttpClient (Java 11+) | HTTP 请求 |
| `java.security.jgss` | GSS-API/Kerberos | 安全认证 |
| `jdk.compiler` | javac 编译器 | 代码生成工具 |
| `jdk.jshell` | JShell REPL | 交互式脚本 |
