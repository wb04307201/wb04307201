# Spring Boot 3 + GraalVM Native Image 简介

> 最后更新: 2026-06-14
> ⬅️ [返回 04 Spring Boot](README.md) | [内嵌服务器](embedded-server.md) | [启动流程](startup-flow.md)

GraalVM Native Image 让 Spring Boot 应用**编译为本地可执行文件**——跳过 JVM 启动，直接以机器码运行，启动时间从秒级降到**毫秒级**，内存占用降低 5-10 倍。

---

## 🎯 一句话定位

**GraalVM Native Image = "提前编译（AOT）+ 封闭世界假设"**——Spring Boot 3 的 AOT 引擎在构建期扫描代码生成反射 / 资源 / 代理 / JNI 提示，GraalVM 据此把应用编译成独立二进制，启动从 2-3 秒降到 **50-200 毫秒**，适合 Serverless / 容器快速弹性场景。

---

## 一、为什么需要 GraalVM Native？

传统 JVM 模式的问题：

| 痛点 | 数据 |
|------|------|
| 启动慢 | Spring Boot 大型应用 2-10 秒 |
| 内存占用高 | 100-500 MB（仅堆） |
| 启动预热 | JIT 编译需要时间达到峰值性能 |
| 容器化资源浪费 | K8s 中 HPA 扩容响应延迟 |

Native Image 的收益：

| 指标 | JVM 模式 | Native 模式 |
|------|---------|-----------|
| 启动时间 | 2-3 s | **50-200 ms** |
| 内存占用 | 200 MB | **30-60 MB** |
| 冷启动 | 慢 | **极快** |
| 峰值性能 | 启动后逐步达到 | 立即达到 |

---

## 二、Spring Boot 3 的 AOT 引擎

Spring Boot 3 引入 **Spring AOT Engine**，在 `process-aot` 阶段提前执行所有"运行期反射 / 代理 / Bean 解析"工作，把结果写进 `target/spring-aot/main/` 目录。

```
┌────────────────────────────────────────┐
│  Maven/Gradle process-aot              │
│  ├── AOT 引擎扫描所有 @Configuration   │
│  ├── 解析 BeanDefinition（静态化）     │
│  ├── 收集 RuntimeHints（反射/资源）    │
│  └── 生成 *.class + reflect-config    │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│  GraalVM native-image                  │
│  ├── closed-world 静态分析             │
│  ├── 编译字节码 → 机器码               │
│  └── 输出可执行二进制                  │
└────────────────────────────────────────┘
```

---

## 三、`spring-boot:process-aot` Maven/Gradle Goal

### Maven

```bash
# 1. 生成 AOT artifacts
mvn -Pnative spring-boot:process-aot

# 2. 调用 native-image 编译
mvn -Pnative native:compile
```

或者使用 Spring Boot 提供的 `native-maven-plugin`：

```xml
<plugin>
    <groupId>org.graalvm.buildtools</groupId>
    <artifactId>native-maven-plugin</artifactId>
    <configuration>
        <buildArgs>
            <buildArg>--no-fallback</buildArg>
        </buildArgs>
    </configuration>
</plugin>
```

### Gradle

```groovy
plugins {
    id 'org.springframework.boot' version '3.2.0'
    id 'io.spring.dependency-management' version '1.1.4'
    id 'org.graalvm.buildtools.native' version '0.10.2'
}

graalvmNative {
    binaries {
        main {
            buildArgs.add('--no-fallback')
        }
    }
}
```

```bash
./gradlew nativeCompile
```

### 前置条件

1. 安装 GraalVM JDK（`sdk install java 21-graal` 或下载 standalone）。
2. 安装 `native-image` 工具：`gu install native-image`（GraalVM 22+ 已内置）。

---

## 四、`RuntimeHints` / `RuntimeHintsRegistrar`

Native Image 编译期**不知道运行时会用到哪些反射 / 资源**。需要通过 `RuntimeHints` 显式声明：

```java
// 1. 注解方式
@RegisterReflectionForBinding(MyDto.class)
@RestController
public class MyController {
    @PostMapping("/dto")
    public String echo(@RequestBody MyDto dto) { return dto.toString(); }
}

// 2. 编程方式（更灵活）
public class MyRuntimeHints implements RuntimeHintsRegistrar {

    @Override
    public void registerHints(RuntimeHints hints, ClassLoader classLoader) {
        // 反射
        hints.reflection().registerType(MyDto.class,
            MemberCategory.INVOKE_DECLARED_CONSTRUCTORS,
            MemberCategory.INVOKE_DECLARED_METHODS,
            MemberCategory.DECLARE_FIELDS);

        // 资源
        hints.resources().registerPattern("db/migration/*.sql");

        // 代理
        hints.proxies().registerJdkProxy(MyService.class);

        // JNI
        hints.jni().registerType(MyNativeClass.class);
    }
}
```

注册 `RuntimeHintsRegistrar`（`META-INF/spring/aot.factories` 或 `@ImportRuntimeHints`）：

```java
@SpringBootApplication
@ImportRuntimeHints(MyRuntimeHints.class)
public class MyApp { ... }
```

---

## 五、反射 / 资源 / 代理 / JNI 提示详解

| 类别 | API | 典型场景 |
|------|-----|---------|
| **反射** | `hints.reflection().registerType(...)` | Jackson 序列化 DTO、JPA Entity |
| **资源** | `hints.resources().registerPattern(...)` | `db/migration/*.sql`、`META-INF/services/*` |
| **代理** | `hints.proxies().registerJdkProxy(...)` | `@Transactional` AOP 代理 |
| **JNI** | `hints.jni().registerType(...)` | 调用本地 .so / .dll |
| **序列化** | `hints.serialization().registerType(...)` | Java 序列化（少见） |

> 📌 **Spring Boot 3 的智能之处**：内置的 Jackson / JPA / Logback 等模块**自动注册了常用 hints**——你只需要为自己的业务 DTO 显式声明。

---

## 六、Buildpacks 构建镜像

Spring Boot 3 默认支持 Cloud Native Buildpacks，无需本地安装 Docker：

```bash
# Maven
mvn -Pnative spring-boot:build-image -Dspring-boot.build-image.imageName=myorg/myapp:native

# Gradle
./gradlew bootBuildImage --imageName=myorg/myapp:native
```

构建产物是一个**包含 Native 二进制的 OCI 镜像**，可直接 push 到镜像仓库：

```bash
docker push myorg/myapp:native

# K8s 部署
kubectl run myapp --image=myorg/myapp:native --port=8080
```

镜像特点：

- 基于 `paketobuildpacks/run`（Paketo 默认）或其他 distroless 镜像
- 无 JVM、无 OS 包管理器
- 体积通常 50-80 MB（vs 普通 JVM 镜像 200+ MB）

---

## 七、性能对比

官方 `spring-petclinic` 应用的实测数据（参考）：

| 指标 | JVM | Native | 提升 |
|------|-----|--------|------|
| 启动到首个请求 | 2.1 s | **80 ms** | 26× |
| 常驻内存 | 180 MB | **40 MB** | 4.5× |
| 镜像体积 | 230 MB | **75 MB** | 3× |
| 峰值吞吐 | 12k req/s | 11k req/s | -8% |
| 冷启动（K8s） | 3-5 s | **< 500 ms** | 10× |

> ⚠️ **吞吐略降**是 Native 模式的已知代价——失去 JIT 即时优化的红利。对于**短任务 / 高弹性**场景收益巨大；对**长跑稳定高吞吐**场景，JVM 仍是首选。

---

## 八、常见陷阱与不兼容点

1. **JDK 动态代理** — `@Transactional` / `@Async` / Spring AOP 在 Native 下**正常工作**（Spring 3 已自动注册代理 hints）。
2. **CGLIB 代理** — 部分第三方库（如旧版 Hibernate）仍需手动配置 hints。
3. **运行时类生成** — CGLIB / Javassist 在 Native 下**受限**。
4. **反射扫描** — 必须显式 `registerType`，否则 `ClassNotFoundException`。
5. **资源文件** — 用 `getResourceAsStream()` 加载的非 .class 资源必须 `registerPattern`。
6. **延迟初始化** — Native 编译期已确定所有 Bean，lazy-init 效果与 JVM 不同。

---

## 🤔 思考

1. **Native Image 适合什么场景？** Serverless（FaaS）、K8s HPA 快速扩容、CLI 工具、内存敏感型微服务。
2. **为什么不所有应用都上 Native？** 编译时间长（5-15 分钟）、生态成熟度仍在演进、运行时反射受限。
3. **Spring Boot 3 Native 最大的改进是什么？** AOT 引擎 + 自动 RuntimeHints 注册——开发者**不需要写一行 native 配置**就能跑通绝大多数 Web / Data 场景。
4. **Native 镜像能跑 Tomcat 吗？** 可以，但**不再需要 Servlet 容器**（直接编译期织入）；实测推荐改用 `spring-boot-starter-webflux` + Undertow 以减小镜像。

---

## 相关章节

- ⬅️ [返回 04 Spring Boot](README.md)
- [内嵌服务器](embedded-server.md) — Native 模式下选择 Undertow 减小体积
- [启动流程](startup-flow.md) — Native 模式跳过 refresh()，启动时间从秒级降到毫秒级

---

