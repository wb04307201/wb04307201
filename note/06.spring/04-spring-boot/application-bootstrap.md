# Spring Boot启动后执行

## 1. **使用 `@PostConstruct` 注解**
在Bean初始化完成后执行（依赖注入完成后，但在服务启动前）。
```java
import javax.annotation.PostConstruct;
import org.springframework.stereotype.Component;

@Component
public class InitializerBean {
    
    @PostConstruct
    public void init() {
        // 初始化逻辑
        System.out.println("执行初始化任务...");
    }
}
```

**特点**：
- 适用于单个Bean的初始化。
- 在依赖注入完成后立即执行。

## 2. **实现 `ApplicationRunner` 或 `CommandLineRunner` 接口**
在Spring Boot启动完成后执行（所有Bean初始化之后，但在应用就绪前）。

### **方式一：`ApplicationRunner`**
```java
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
public class AppStartupRunner implements ApplicationRunner {
    
    @Override
    public void run(ApplicationArguments args) throws Exception {
        // 初始化逻辑
        System.out.println("应用启动后执行: " + args.getOptionNames());
    }
}
```

### **方式二：`CommandLineRunner`**
```java
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class CmdStartupRunner implements CommandLineRunner {
    
    @Override
    public void run(String... args) throws Exception {
        // 初始化逻辑
        System.out.println("命令行参数: " + Arrays.toString(args));
    }
}
```

**特点**：
- 可以访问命令行参数（`ApplicationRunner` 解析更友好）。
- 支持多个Runner，通过 `@Order` 注解控制顺序：
  ```java
  @Order(1)
  @Component
  public class FirstRunner implements ApplicationRunner { ... }
  ```

## 3. **监听应用事件（`ApplicationReadyEvent`）**
通过监听Spring事件，在应用完全就绪后执行。

```java
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Component
public class AppReadyListener {
    
    @EventListener(ApplicationReadyEvent.class)
    public void onApplicationReady() {
        // 应用启动完成后的逻辑
        System.out.println("应用已完全启动并准备就绪！");
    }
}
```

**特点**：
- 确保所有处理（包括内嵌服务器启动）已完成。
- 适合需要等待应用完全就绪的任务（如发送通知）。

## 4. **使用 `InitializingBean` 接口**
在Bean属性设置完成后执行（类似 `@PostConstruct`，但通过接口实现）。

```java
import org.springframework.beans.factory.InitializingBean;
import org.springframework.stereotype.Component;

@Component
public class InitBean implements InitializingBean {
    
    @Override
    public void afterPropertiesSet() throws Exception {
        // 初始化逻辑
        System.out.println("InitializingBean: 属性设置完成");
    }
}
```

**注意**：不推荐优先使用，`@PostConstruct` 更简洁。

## 5. **通过 `SmartInitializingSingleton` 接口**
在所有单例Bean初始化完成后执行（适合需要所有Bean就绪的场景）。

```java
import org.springframework.context.SmartInitializingSingleton;
import org.springframework.stereotype.Component;

@Component
public class SmartInit implements SmartInitializingSingleton {
    
    @Override
    public void afterSingletonsInstantiated() {
        // 所有单例Bean初始化完成后的逻辑
        System.out.println("所有单例Bean已初始化");
    }
}
```

## 如何选择？

| 方法                           | 执行时机             | 适用场景        |
|------------------------------|------------------|-------------|
| `@PostConstruct`             | Bean依赖注入后        | 单个Bean的初始化  |
| `ApplicationRunner`          | 应用启动完成（命令行参数可用）  | 需要访问启动参数的任务 |
| `ApplicationReadyEvent`      | 应用完全就绪（内嵌服务器已启动） | 需要确保服务可用的任务 |
| `SmartInitializingSingleton` | 所有单例Bean初始化后     | 跨Bean的复杂初始化 |


## 示例：结合异步初始化
如果初始化任务耗时较长，可以结合 `@Async` 避免阻塞启动：
```java
@Component
public class AsyncInitializer implements ApplicationRunner {
    
    @Async
    @Override
    public void run(ApplicationArguments args) {
        // 异步执行初始化
    }
}
```
**注意**：需在主类启用 `@EnableAsync`。
