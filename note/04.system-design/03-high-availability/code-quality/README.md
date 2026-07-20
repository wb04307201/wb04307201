<!--
module:
  parent: system-design
  slug: system-design/code-quality
  type: article
  category: 主模块子文章
  summary: Java 代码质量提升 本应该很简单
-->

# Java 代码质量提升

---

提高 Java 代码质量是开发高效、可维护和可扩展软件的关键。以下是一些核心方面和最佳实践：

## 与高可用的关系

代码质量是**高可用（HA）的第一道防线**——很多生产事故的根因都出在"代码可读性差、异常被吞掉、资源没释放"这类基础质量问题上：

- **防御性编程**（`Objects.requireNonNull`、参数校验）能避免 NPE 引起的请求失败，降低 [熔断](../circuit-break/README.md) 误触发的概率。
- **异常处理规范**（不要 catch-and-ignore、try-with-resources）能防止文件句柄、数据库连接、线程池等资源泄漏，避免 [超时](../timeout/README.md) 雪崩。
- **幂等设计**（唯一 ID、状态机）是 [重试](../retry/README.md) 策略的基石：没有幂等性，重试会带来重复扣款、重复下单等业务灾难。
- **可观测性**（结构化日志、Metrics 埋点）让 [服务降级](../service-degradation/README.md) 触发条件可量化、可自动执行。

> 一句话总结：**质量差的代码会让所有 HA 模式形同虚设。** 本章梳理的是基础质量，建议在阅读 [限流](../rate-limiting/README.md)、[熔断](../circuit-break/README.md)、[重试](../retry/README.md)、[超时](../timeout/README.md)、[降级](../service-degradation/README.md) 之前先扫一遍。

## 1. 代码可读性

- **命名规范**：
    - 类名使用大驼峰（UpperCamelCase）
    - 方法名和变量名使用小驼峰（lowerCamelCase）
    - 常量使用全大写加下划线（UPPER_CASE_WITH_UNDERSCORES）
    - 避免缩写，除非是广泛认可的（如`id`、`url`）

- **代码格式**：
    - 一致的缩进（通常4个空格）
    - 合理的行长度（建议不超过120字符）
    - 适当的空行分隔逻辑块

- **注释**：
    - 解释"为什么"而不是"做什么"
    - 使用Javadoc为公共API编写文档
    - 避免冗余注释（代码本身应清晰表达意图）

## 2. 代码结构

- **单一职责原则**：每个类/方法只做一件事
- **小方法**：方法长度建议不超过20行
- **避免深层嵌套**：控制if/for嵌套层级（通常不超过3层）
- **防御性编程**：
  ```java
  public void process(String input) {
      Objects.requireNonNull(input, "Input cannot be null");
      // 处理逻辑
  }
  ```

## 3. 异常处理

- 不要捕获并忽略异常（至少记录日志）
- 避免过于宽泛的异常捕获（如`catch (Exception e)`）
- 自定义异常应继承自`RuntimeException`或`Exception`
- 优先使用特定异常而非通用异常

## 4. 性能考虑

- 优先使用StringBuilder进行字符串拼接（在循环中）
- 合理使用集合框架（ArrayList vs LinkedList, HashMap vs TreeMap）
- 避免在循环中创建对象
- 及时关闭资源（使用try-with-resources）
  ```java
  try (InputStream is = new FileInputStream("file.txt")) {
      // 使用资源
  }
  ```

## 5. 并发编程

- 使用线程安全集合（如`ConcurrentHashMap`）
- 避免共享可变状态
- 使用`volatile`、`synchronized`或`Lock`正确处理同步
- 考虑使用`java.util.concurrent`包中的高级并发工具

## 6. 测试实践

- 编写单元测试（JUnit/TestNG）
- 测试覆盖率目标至少70-80%
- 使用Mockito进行mock测试
- 实践测试驱动开发(TDD)

## 7. 工具支持

- **静态代码分析**：
    - SonarQube
    - Checkstyle
    - PMD
    - FindBugs/SpotBugs

- **IDE插件**：
    - IntelliJ IDEA的代码检查
    - Eclipse的代码分析工具

- **构建工具集成**：
    - Maven/Gradle的代码质量插件

## 8. 设计模式应用

- 适当使用设计模式（如单例、工厂、策略等）
- 避免过度设计
- 理解模式适用场景

## 9. 现代Java特性

- 使用Optional处理null值
- 利用Java 8+特性：
    - Lambda表达式
    - Stream API
    - 方法引用
    - 新日期时间API

## 10. 代码审查

- 定期进行同行代码审查
- 使用Pull Request/Merge Request流程
- 建立代码质量检查清单

## 示例：高质量代码片段

```java
/**
 * 用户服务实现类
 */
public class UserServiceImpl implements UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    /**
     * 构造函数注入依赖
     * @param userRepository 用户存储库
     * @param passwordEncoder 密码编码器
     */
    public UserServiceImpl(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = Objects.requireNonNull(userRepository, "UserRepository cannot be null");
        this.passwordEncoder = Objects.requireNonNull(passwordEncoder, "PasswordEncoder cannot be null");
    }
    
    @Override
    @Transactional
    public UserRegistrationResult registerUser(UserRegistrationRequest request) {
        validateRegistrationRequest(request);
        
        if (userRepository.existsByUsername(request.getUsername())) {
            return UserRegistrationResult.failure("Username already exists");
        }
        
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        // 其他字段设置...
        
        User savedUser = userRepository.save(user);
        return UserRegistrationResult.success(savedUser.getId());
    }
    
    private void validateRegistrationRequest(UserRegistrationRequest request) {
        if (request == null) {
            throw new IllegalArgumentException("Registration request cannot be null");
        }
        if (StringUtils.isBlank(request.getUsername())) {
            throw new IllegalArgumentException("Username cannot be blank");
        }
        // 其他验证...
    }
}
```

通过遵循这些实践，您可以显著提高Java代码的质量，使其更易于维护、扩展和调试。

## 专题导航

- [2 行/8 行原则](2-lines-8-lines/README.md) — **2 行/8 行原则** — 用约 2 行表达 Happy Path，以约 8 行处理鲁棒性与边界情况（功能与鲁棒性约 1:4 投入）

---

← [返回 高可用](../README.md)