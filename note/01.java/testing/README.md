<!--
module:
  parent: java
  slug: java/testing
  type: article
  category: 主模块子文章
  summary: 涵盖 JUnit 5、Mockito、JaCoCo 及测试最佳实践
-->

# Java 测试技术笔记

> 涵盖 JUnit 5、Mockito、JaCoCo 及测试最佳实践

---
## 引言：反直觉代码
Java 测试技术笔记 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 目录

- [一、单元测试 vs 集成测试](#一单元测试-vs-集成测试)
- [二、JUnit 5 体系](#二junit-5-体系)
- [三、Mockito 模拟框架](#三mockito-模拟框架)
- [四、测试覆盖率 JaCoCo](#四测试覆盖率-jacoco)
- [五、最佳实践 FIRST 原则](#五最佳实践-first-原则)

---

## 一、单元测试 vs 集成测试

### 1.1 概念对比

| 维度 | 单元测试 (Unit Test) | 集成测试 (Integration Test) |
|------|----------------------|---------------------------|
| 目标 | 验证单个类/方法逻辑正确性 | 验证多个组件协作正确性 |
| 范围 | 隔离的、最小的可测试单元 | 跨模块、跨层、甚至跨服务 |
| 外部依赖 | 必须 Mock/Stub 掉 | 使用真实依赖（数据库、网络等） |
| 执行速度 | 极快（毫秒级） | 较慢（秒级甚至分钟级） |
| 维护成本 | 低 | 较高 |
| 典型注解 | `@Test` | `@SpringBootTest`, `@IntegrationTest` |

### 1.2 测试金字塔

```
         /\
        /  \        E2E 测试 (少量)
       /────\
      /      \      集成测试 (适量)
     /────────\
    /          \    单元测试 (大量)
   /────────────\
```

- **单元测试**占 70% 以上，构成金字塔底座
- **集成测试**占 20% 左右，覆盖关键路径
- **端到端测试**占 10% 以下，验证用户场景

### 1.3 选择策略

- 纯业务逻辑、算法、工具类 --> 写**单元测试**
- 涉及数据库、消息队列、外部 API --> 写**集成测试**
- 对外暴露的 REST 接口 --> 写**集成测试**（`@WebMvcTest` / `@SpringBootTest`）

---

## 二、JUnit 5 体系

### 2.1 模块架构

JUnit 5 由三个子项目组成：

| 模块 | 说明 |
|------|------|
| JUnit Platform | 测试发现与执行的基础平台，定义 `TestEngine` SPI |
| JUnit Jupiter | 新的编程模型和扩展模型，即 Jupiter API |
| JUnit Vintage | 兼容 JUnit 3/4 的运行引擎 |

**Maven 依赖：**

```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.11.4</version>
    <scope>test</scope>
</dependency>
```

### 2.2 生命周期注解

| 注解 | 作用域 | 执行时机 | 方法签名要求 |
|------|--------|----------|-------------|
| `@BeforeAll` | 类级别 | 所有测试方法之前执行一次 | `static void` |
| `@BeforeEach` | 实例级别 | 每个测试方法之前执行 | `void` |
| `@Test` | 实例级别 | 标记测试方法 | `void` |
| `@AfterEach` | 实例级别 | 每个测试方法之后执行 | `void` |
| `@AfterAll` | 类级别 | 所有测试方法之后执行一次 | `static void` |

```java
import org.junit.jupiter.api.*;

class LifecycleTest {

    @BeforeAll
    static void beforeAll() {
        System.out.println("==> 在所有测试之前执行一次（只执行一次）");
    }

    @BeforeEach
    void beforeEach() {
        System.out.println("--> 在每个测试方法之前执行");
    }

    @Test
    void testOne() {
        Assertions.assertEquals(4, 2 + 2);
    }

    @Test
    void testTwo() {
        Assertions.assertTrue("hello".startsWith("he"));
    }

    @AfterEach
    void afterEach() {
        System.out.println("<-- 在每个测试方法之后执行");
    }

    @AfterAll
    static void afterAll() {
        System.out.println("<== 在所有测试之后执行一次（只执行一次）");
    }
}
```

执行顺序：

```
@BeforeAll
@BeforeEach --> @Test (testOne) --> @AfterEach
@BeforeEach --> @Test (testTwo) --> @AfterEach
@AfterAll
```

### 2.3 @DisplayName 显示名称

自定义测试类和方法在报告中的展示名称，支持特殊字符和 Emoji：

```java
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("用户服务测试类")
class UserServiceTest {

    @Test
    @DisplayName("正常登录应返回 Token")
    void loginSuccess() {
        // ...
    }

    @Test
    @DisplayName("密码错误应抛出 AuthenticationException")
    void loginFail() {
        // ...
    }
}
```

### 2.4 @ParameterizedTest 参数化测试

参数化测试允许用不同参数多次运行同一个测试方法，减少重复代码。

**常用参数源注解：**

| 注解 | 说明 |
|------|------|
| `@ValueSource` | 提供字面量值（字符串、数字等） |
| `@EnumSource` | 提供枚举常量 |
| `@CsvSource` | 提供 CSV 格式的参数对 |
| `@CsvFileSource` | 从 CSV 文件读取参数 |
| `@MethodSource` | 从工厂方法获取参数 |
| `@NullSource` / `@EmptySource` | 提供 null / 空值 |

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;
import static org.junit.jupiter.api.Assertions.*;

class ParameterizedTestDemo {

    @ParameterizedTest
    @ValueSource(strings = {"racecar", "radar", "level"})
    @DisplayName("回文判断测试")
    void isPalindrome(String word) {
        assertTrue(StringUtils.isPalindrome(word));
    }

    @ParameterizedTest
    @CsvSource({
        "1, 2, 3",
        "0, 0, 0",
        "-1, 1, 0",
        "100, 200, 300"
    })
    void addTest(int a, int b, int expected) {
        assertEquals(expected, Calculator.add(a, b));
    }

    @ParameterizedTest
    @EnumSource(TimeUnit.class)
    void enumSourceTest(TimeUnit unit) {
        assertNotNull(unit);
    }

    @ParameterizedTest
    @MethodSource("provideStringsForIsBlank")
    void isBlankTest(String input, boolean expected) {
        assertEquals(expected, StringUtils.isBlank(input));
    }

    static Stream<Arguments> provideStringsForIsBlank() {
        return Stream.of(
            Arguments.of(null, true),
            Arguments.of("", true),
            Arguments.of("  ", true),
            Arguments.of("hello", false)
        );
    }
}
```

### 2.5 Assertions 断言

JUnit 5 提供丰富的断言方法，支持 Lambda 延迟求值消息：

```java
import static org.junit.jupiter.api.Assertions.*;

class AssertionsDemo {

    @Test
    void standardAssertions() {
        // 相等断言
        assertEquals(4, 2 + 2, "两个数相加应等于 4");
        assertEquals("hello", "hello");

        // 布尔断言
        assertTrue(5 > 3);
        assertFalse("world".isEmpty());

        // 空值断言
        assertNull(null);
        assertNotNull(new Object());

        // 同一性断言
        assertSame("相同引用", "相同引用");
        assertNotSame(new Object(), new Object());
    }

    @Test
    void exceptionAssertion() {
        // 验证异常类型及消息
        ArithmeticException exception = assertThrows(
            ArithmeticException.class,
            () -> {
                int result = 1 / 0;
            }
        );
        assertEquals("/ by zero", exception.getMessage());
    }

    @Test
    void timeoutAssertion() {
        // 验证方法在指定时间内完成
        assertTimeout(
            Duration.ofMillis(100),
            () -> Thread.sleep(50)
        );

        // 预执行超时断言（方法会先执行，再判断时间）
        assertTimeoutPreemptively(
            Duration.ofSeconds(1),
            () -> someLongRunningTask()
        );
    }

    @Test
    void assertAllGroupedAssertions() {
        // 分组断言：全部执行完毕后再报告失败
        assertAll("用户属性校验",
            () -> assertEquals("张三", user.getName()),
            () -> assertEquals(25, user.getAge()),
            () -> assertTrue(user.isActive())
        );
    }

    @Test
    void lazyMessageEvaluation() {
        // Lambda 延迟求值，仅在断言失败时拼接消息
        assertEquals(4, 2 + 2,
            () -> "计算结果不正确: " + "额外调试信息");
    }
}
```

**常用断言方法一览：**

| 方法 | 说明 |
|------|------|
| `assertEquals(expected, actual)` | 值相等 |
| `assertNotEquals(unexpected, actual)` | 值不等 |
| `assertTrue(condition)` | 条件为真 |
| `assertFalse(condition)` | 条件为假 |
| `assertNull(value)` | 值为 null |
| `assertNotNull(value)` | 值非 null |
| `assertSame(expected, actual)` | 引用相同 |
| `assertNotSame(expected, actual)` | 引用不同 |
| `assertThrows(type, executable)` | 抛出指定异常 |
| `assertDoesNotThrow(executable)` | 不抛出异常 |
| `assertTimeout(duration, executable)` | 在规定时间内完成 |
| `assertAll(executables...)` | 分组断言，全部校验 |
| `assertIterableEquals(expected, actual)` | 迭代器元素逐一相等 |
| `assertArrayEquals(expected, actual)` | 数组元素逐一相等 |

### 2.6 Assumptions 假设

假设用于条件性执行测试。当假设不成立时，测试被**跳过**（而非失败）：

```java
import static org.junit.jupiter.api.Assumptions.*;

class AssumptionsDemo {

    @Test
    void assumeTrueTest() {
        // 假设当前 OS 为 Linux，否则跳过
        assumeTrue(System.getProperty("os.name").contains("Linux"));
        // 仅在 Linux 上执行
        assertEquals(0, runLinuxSpecificCommand());
    }

    @Test
    void assumingThatTest() {
        // 假设成立时执行 lambda，否则跳过 lambda 继续执行后续代码
        assumingThat(
            "CI".equals(System.getenv("ENV")),
            () -> assertEquals(42, runCiOnlyCheck())
        );
        // 这段代码无论假设是否成立都会执行
        assertTrue(true);
    }

    @Test
    void assumeFalseTest() {
        // 假设不是 Windows 环境
        assumeFalse(System.getProperty("os.name").startsWith("Windows"));
        assertTrue(runUnixOnlyTest());
    }
}
```

**Assumptions vs Assertions 区别：**

| 对比项 | Assumptions（假设） | Assertions（断言） |
|--------|---------------------|--------------------|
| 不成立时 | 测试跳过 (SKIPPED) | 测试失败 (FAILED) |
| 用途 | 前置条件检查 | 结果验证 |
| 典型场景 | 环境依赖、外部资源可用性 | 业务逻辑正确性 |

---

## 三、Mockito 模拟框架

### 3.1 核心注解

| 注解 | 说明 |
|------|------|
| `@Mock` | 创建一个模拟对象，所有方法默认返回 null/0/false |
| `@InjectMocks` | 创建实例并自动注入 `@Mock` 标注的依赖 |
| `@Spy` | 创建一个部分模拟对象，真实方法会被调用除非被 stub |
| `@Captor` | 创建 ArgumentCaptor 用于捕获方法参数 |
| `@ExtendWith(MockitoExtension.class)` | 启用 Mockito 注解处理 |

### 3.2 @Mock 与 @InjectMocks

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private PaymentService paymentService;

    @InjectMocks
    private OrderService orderService;

    @Test
    @DisplayName("创建订单应调用 Repository 和 Payment")
    void createOrder_shouldCallRepositoryAndPayment() {
        // Given: 准备测试数据
        Order order = new Order("ORD-001", 100.0);
        when(orderRepository.save(any(Order.class))).thenReturn(order);
        when(paymentService.process(anyString(), anyDouble())).thenReturn(true);

        // When: 执行被测方法
        Order result = orderService.createOrder("ORD-001", 100.0);

        // Then: 验证结果和行为
        assertNotNull(result);
        assertEquals("ORD-001", result.getOrderNo());
        verify(orderRepository).save(any(Order.class));
        verify(paymentService).process("ORD-001", 100.0);
    }
}
```

**注入策略说明：**

| 策略 | 触发条件 | 优先级 |
|------|----------|--------|
| 构造器注入 | 存在单个构造器 | 最高 |
| Setter 注入 | 存在 setter 方法 | 中等 |
| 字段注入 | 直接赋值字段 | 最低 |

### 3.3 Stubbing: when().thenReturn()

```java
@Test
void stubbingDemo() {
    List<String> mockList = mock(List.class);

    // 基本 stub
    when(mockList.get(0)).thenReturn("first");
    assertEquals("first", mockList.get(0));

    // 链式返回值
    when(mockList.size()).thenReturn(1).thenReturn(2).thenReturn(3);
    assertEquals(1, mockList.size());
    assertEquals(2, mockList.size());
    assertEquals(3, mockList.size());

    // 参数匹配器
    when(mockList.contains(anyString())).thenReturn(true);
    assertTrue(mockList.contains("anything"));

    // 抛出异常
    when(mockList.get(-1)).thenThrow(IndexOutOfBoundsException.class);
    assertThrows(IndexOutOfBoundsException.class, () -> mockList.get(-1));

    // doThrow / doReturn（用于 void 方法）
    List<String> spyList = spy(new ArrayList<>());
    doThrow(new RuntimeException("不可添加"))
        .when(spyList).add(anyString());
    assertThrows(RuntimeException.class, () -> spyList.add("item"));
}
```

**常用参数匹配器：**

| 匹配器 | 说明 |
|--------|------|
| `any()` | 匹配任意对象 |
| `any(Class<T>)` | 匹配指定类型 |
| `anyString()` | 匹配任意字符串 |
| `anyInt()` | 匹配任意 int |
| `anyList()` | 匹配任意 List |
| `eq(value)` | 匹配精确值 |
| `isNull()` | 匹配 null |
| `isNotNull()` / `notNull()` | 匹配非 null |
| `startsWith(prefix)` | 字符串前缀匹配 |
| `contains(substring)` | 字符串包含匹配 |

### 3.4 verify() 验证

```java
@Test
void verifyDemo() {
    List<String> mockList = mock(List.class);

    mockList.add("one");
    mockList.add("two");
    mockList.add("three");
    mockList.get(0);

    // 验证方法被调用
    verify(mockList).add("one");

    // 验证调用次数
    verify(mockList, times(3)).add(anyString());
    verify(mockList, atLeastOnce()).add(anyString());
    verify(mockList, atLeast(2)).add(anyString());
    verify(mockList, atMost(5)).add(anyString());
    verify(mockList, never()).clear();

    // 验证调用顺序
    InOrder inOrder = inOrder(mockList);
    inOrder.verify(mockList).add("one");
    inOrder.verify(mockList).add("two");
    inOrder.verify(mockList).add("three");

    // 验证无其他交互
    verifyNoMoreInteractions(mockList);

    // 验证零交互
    List<String> unusedMock = mock(List.class);
    verifyNoInteractions(unusedMock);
}
```

### 3.5 ArgumentCaptor 参数捕获

用于捕获传递给 Mock 方法的参数，进行更精细的断言：

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class ArgumentCaptorDemo {

    @Mock
    private EventPublisher eventPublisher;

    @Captor
    private ArgumentCaptor<OrderEvent> eventCaptor;

    @Test
    void captorWithAnnotation() {
        OrderService service = new OrderService(eventPublisher);
        service.placeOrder("ORD-100", 500.0);

        // 捕获传递的参数
        verify(eventPublisher).publish(eventCaptor.capture());

        OrderEvent captured = eventCaptor.getValue();
        assertEquals("ORD-100", captured.getOrderNo());
        assertEquals(500.0, captured.getAmount());
        assertEquals("CREATED", captured.getStatus());
    }

    @Test
    void captorMultipleValues() {
        // 多次调用时捕获所有值
        eventPublisher.publish(new OrderEvent("A"));
        eventPublisher.publish(new OrderEvent("B"));
        eventPublisher.publish(new OrderEvent("C"));

        verify(eventPublisher, times(3)).publish(eventCaptor.capture());

        List<OrderEvent> allEvents = eventCaptor.getAllValues();
        assertEquals(3, allEvents.size());
        assertEquals("A", allEvents.get(0).getOrderNo());
    }
}
```

### 3.6 @Spy 部分模拟

```java
@Test
void spyDemo() {
    // Spy 包装真实对象，默认调用真实方法
    List<String> spyList = spy(new ArrayList<>());

    spyList.add("real");
    assertEquals(1, spyList.size()); // 真实方法被执行

    // 可以覆盖特定方法
    when(spyList.size()).thenReturn(100);
    assertEquals(100, spyList.size());

    // 注意：spy 必须用 when().thenReturn() 而非 doReturn()
    // 错误写法: when(spyList.get(0)) 会调用真实方法导致异常
    doReturn("mocked").when(spyList).get(0);
    assertEquals("mocked", spyList.get(0));
}
```

### 3.7 静态方法 Mock (MockedStatic)

JUnit 5 + Mockito 3.4+ 支持静态方法模拟：

```java
@Test
void staticMethodMocking() {
    try (MockedStatic<TimeUtil> mocked = mockStatic(TimeUtil.class)) {
        mocked.when(TimeUtil::now).thenReturn(
            LocalDateTime.of(2025, 1, 1, 0, 0)
        );

        assertEquals(
            LocalDateTime.of(2025, 1, 1, 0, 0),
            TimeUtil.now()
        );
    }
    // try-with-resources 结束后静态 mock 自动关闭
    assertNotEquals(
        LocalDateTime.of(2025, 1, 1, 0, 0),
        TimeUtil.now()
    );
}
```

---

## 四、测试覆盖率 JaCoCo

### 4.1 什么是 JaCoCo

JaCoCo (Java Code Coverage) 是 Java 生态中最流行的代码覆盖率工具，支持多种覆盖率指标：

| 覆盖率类型 | 英文 | 说明 |
|-----------|------|------|
| 行覆盖率 | Line Coverage | 被执行的代码行占总行数比例 |
| 分支覆盖率 | Branch Coverage | 被执行的分支（if/else 等）比例 |
| 方法覆盖率 | Method Coverage | 被调用的方法占总方法比例 |
| 类覆盖率 | Class Coverage | 被加载的类占总类比例 |
| 指令覆盖率 | Instruction Coverage | 被执行的字节码指令比例 |
| 复杂度覆盖率 | Complexity Coverage | 基于 cyclomatic complexity 的覆盖率 |

### 4.2 Maven 配置

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <version>0.8.12</version>
            <executions>
                <!-- 准备代理 -->
                <execution>
                    <id>prepare-agent</id>
                    <goals>
                        <goal>prepare-agent</goal>
                    </goals>
                </execution>
                <!-- 生成报告 -->
                <execution>
                    <id>report</id>
                    <phase>test</phase>
                    <goals>
                        <goal>report</goal>
                    </goals>
                </execution>
                <!-- 覆盖率检查 -->
                <execution>
                    <id>check</id>
                    <goals>
                        <goal>check</goal>
                    </goals>
                    <configuration>
                        <rules>
                            <rule>
                                <element>BUNDLE</element>
                                <limits>
                                    <limit>
                                        <counter>LINE</counter>
                                        <value>COVEREDRATIO</value>
                                        <minimum>0.80</minimum>
                                    </limit>
                                    <limit>
                                        <counter>BRANCH</counter>
                                        <value>COVEREDRATIO</value>
                                        <minimum>0.70</minimum>
                                    </limit>
                                </limits>
                            </rule>
                        </rules>
                    </configuration>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

### 4.3 排除规则

```xml
<configuration>
    <excludes>
        <!-- 排除 DTO/VO/Entity 等简单数据类 -->
        <exclude>**/dto/**</exclude>
        <exclude>**/vo/**</exclude>
        <exclude>**/entity/**</exclude>
        <!-- 排除配置类 -->
        <exclude>**/config/**</exclude>
        <!-- 排除启动类 -->
        <exclude>**/Application.*</exclude>
        <!-- 排除异常类 -->
        <exclude>**/exception/**</exclude>
    </excludes>
</configuration>
```

### 4.4 执行命令与报告

```bash
# 运行测试并生成覆盖率报告
mvn clean test jacoco:report

# 运行测试并执行覆盖率检查
mvn clean verify

# 查看报告
# 报告位置: target/site/jacoco/index.html
```

### 4.5 Gradle 配置

```groovy
plugins {
    id 'jacoco'
}

jacoco {
    toolVersion = "0.8.12"
}

jacocoTestReport {
    dependsOn test
    reports {
        xml.required = true
        html.required = true
        html.outputLocation = layout.buildDirectory.dir('jacocoHtml')
    }
    afterEvaluate {
        classDirectories.setFrom(files(classDirectories.files.collect {
            fileTree(dir: it, exclude: [
                '**/dto/**',
                '**/vo/**',
                '**/config/**',
                '**/Application.*'
            ])
        }))
    }
}

jacocoTestCoverageVerification {
    violationRules {
        rule {
            limit {
                minimum = 0.80
            }
        }
    }
}
```

---

## 五、最佳实践 FIRST 原则

### 5.1 FIRST 原则概述

| 原则 | 英文 | 含义 |
|------|------|------|
| **F** | Fast（快速） | 测试应快速执行，单元测试应在毫秒级完成 |
| **I** | Independent（独立） | 测试之间不应有依赖关系，可任意顺序执行 |
| **R** | Repeatable（可重复） | 在任何环境下运行结果一致，不依赖外部状态 |
| **S** | Self-Validating（自验证） | 测试应有明确通过/失败结果，无需人工判断 |
| **T** | Timely（及时） | 测试应在生产代码之前或同时编写（TDD 理念） |

### 5.2 测试命名规范

```
应测试的方法_场景或条件_期望结果
```

示例：

```java
@Test
void createUser_withValidData_shouldReturnCreatedUser() { }

@Test
void createUser_withDuplicateEmail_shouldThrowDuplicateKeyException() { }

@Test
void calculateDiscount_withVipMember_shouldApply20PercentOff() { }

@Test
void processPayment_whenGatewayTimeout_shouldRetry3Times() { }
```

### 5.3 Given-When-Then 结构

```java
@Test
@DisplayName("订单金额超过 100 应免运费")
void orderOver100_shouldHaveFreeShipping() {
    // Given: 准备测试数据和前置条件
    OrderService orderService = new OrderService();
    OrderItem item = new OrderItem("商品A", 50.0, 3);

    // When: 执行被测行为
    Order order = orderService.createOrder(List.of(item));

    // Then: 验证结果符合预期
    assertEquals(150.0, order.getTotalAmount());
    assertTrue(order.isFreeShipping());
    assertEquals(0.0, order.getShippingFee());
}
```

### 5.4 常见反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| 测试依赖执行顺序 | 违反 Independent 原则 | 每个测试自包含完整 setup |
| 在测试中 sleep | 违反 Fast 原则 | 用 Mock 或 CountDownLatch |
| 测试访问私有成员 | 脆弱、重构困难 | 只通过公共接口测试 |
| 一个测试覆盖多个场景 | 失败原因不明确 | 一个测试只验证一个行为 |
| 测试连接真实数据库 | 违反 Fast/Repeatable | 用 H2 内存库或 Testcontainers |
| 测试逻辑复杂 | 难以维护 | 保持测试简单直接 |

### 5.5 分层测试注解建议

```java
// ========== 纯单元测试 ==========
// 无需 Spring 容器，直接使用 Mockito
@ExtendWith(MockitoExtension.class)
class PureUnitTest { }

// ========== Web 层测试 ==========
// 只加载 MVC 相关 Bean，速度快
@WebMvcTest(UserController.class)
class WebLayerTest { }

// ========== 数据层测试 ==========
// 加载 JPA/MyBatis 相关 Bean
@DataJpaTest
class DataLayerTest { }

// ========== 完整集成测试 ==========
// 加载完整 Spring 上下文
@SpringBootTest
@AutoConfigureMockMvc
class FullIntegrationTest { }

// ========== 使用真实数据库 ==========
@Testcontainers
@SpringBootTest
class TestcontainersIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16");
}
```

### 5.6 测试类结构模板

```java
package com.example.service;

import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * {@link OrderService} 的单元测试
 */
@DisplayName("订单服务单元测试")
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private InventoryService inventoryService;

    @InjectMocks
    private OrderService orderService;

    @BeforeEach
    void setUp() {
        // 每个测试的公共准备逻辑
    }

    @Nested
    @DisplayName("创建订单")
    class CreateOrder {

        @Test
        @DisplayName("库存充足时应成功创建订单")
        void withSufficientInventory_shouldCreateOrder() {
            // Given
            when(inventoryService.checkStock("ITEM-001", 2))
                .thenReturn(true);
            when(orderRepository.save(any(Order.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

            // When
            Order result = orderService.createOrder("ITEM-001", 2);

            // Then
            assertNotNull(result);
            assertEquals("ITEM-001", result.getItems().get(0).getItemCode());
            verify(orderRepository).save(any(Order.class));
        }

        @Test
        @DisplayName("库存不足时应抛出 BusinessException")
        void withInsufficientInventory_shouldThrowException() {
            // Given
            when(inventoryService.checkStock("ITEM-001", 100))
                .thenReturn(false);

            // When & Then
            assertThrows(BusinessException.class,
                () -> orderService.createOrder("ITEM-001", 100));

            verify(orderRepository, never()).save(any());
        }
    }

    @Nested
    @DisplayName("取消订单")
    class CancelOrder {

        @Test
        @DisplayName("已发货的订单不应允许取消")
        void shippedOrder_shouldNotAllowCancellation() {
            // Given
            Order shippedOrder = new Order();
            shippedOrder.setStatus("SHIPPED");
            when(orderRepository.findById("ORD-001"))
                .thenReturn(Optional.of(shippedOrder));

            // When & Then
            assertThrows(IllegalStateException.class,
                () -> orderService.cancelOrder("ORD-001"));
        }
    }
}
```

### 5.7 关键指标参考

| 指标 | 建议阈值 | 说明 |
|------|----------|------|
| 行覆盖率 | >= 80% | 核心业务逻辑建议 >= 90% |
| 分支覆盖率 | >= 70% | 比行覆盖率更难达标 |
| 单元测试执行时间 | < 1s / 个 | 整体单元测试套件 < 1 分钟 |
| 集成测试执行时间 | < 10s / 个 | 整体集成测试 < 5 分钟 |
| 测试/生产代码比例 | 1:1 ~ 2:1 | 高质量项目测试代码多于生产代码 |

---

> **总结：** 好的测试不是追求 100% 覆盖率，而是对核心业务逻辑做到充分覆盖。遵循 FIRST 原则，保持测试快速、独立、可重复、自验证、及时编写，才能构建可持续维护的测试体系。

---

## 📊 本节统计

| 统计维度 | 数值 | 口径 |
|----------|------|------|
| 分类主题数 | 1 | 测试（单元 / 集成 / JUnit 5 / Mockito / JaCoCo / FIRST 原则 5 节） |
| 子 README 数 | 0 | 无子 README |
| 含 frontmatter 的 README | 1 / 1 | 100% 覆盖（2026-07-01） |

> **统计时间戳**：2026-07-01

---

← [返回 01.java 主模块](../README.md)
