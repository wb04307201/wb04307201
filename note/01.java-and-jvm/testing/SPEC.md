
# SPEC for note/01.java-and-jvm/testing/

> **Inherits from**: [../../SPEC.md](../../SPEC.md)
> **Mode**: append + override
> **Updated**: 2026-08-13

---

## 子目录定位

Java 测试技术体系：JUnit 5 + Mockito + JaCoCo 覆盖率 + 测试金字塔 + FIRST 原则，强调「测试金字塔比例 + Mock 边界 + 覆盖率分层标准」三大工程实践。

## 从 L1 继承

- G1-G6 通用 6 维度评分
- A1 源码级深度（带 JDK 版本）
- A3 反例对比（❌/✅）
- A4 参数调优表（覆盖率阈值）

## 本子目录规则（强特异性）

### 评估维度（追加 L1 维度后）

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| T1 | 测试金字塔 | 明确给出 unit/integration/e2e 比例（如 7:2:1） + 适用场景 | 提及金字塔无比例 | 只讲单元测试 |
| T2 | Mock 边界 | 明确「何时 Mock / 何时不 Mock」+ 边界清单 | 有 Mock 用法但无边界 | 全 Mock 或全不 Mock |
| T3 | 覆盖率标准 | 核心 >80% / 一般 >60% + 排除规则（如 getter/setter 不计） | 有阈值无分层 | 只给一个固定数字 |

### 写作要求

- **测试金字塔比例**：每篇测试文章必须给出 unit/integration/e2e 推荐比例（默认 7:2:1）
- **Mock 决策表**：必须给出 Mock vs 不 Mock 的决策清单（外部依赖 Mock / 内部状态不 Mock）
- **覆盖率分层**：核心业务代码 ≥80% / 一般工具类 ≥60% / Controller/Entity 不强求
- **FIRST 原则必备**：Fast / Independent / Repeatable / Self-validating / Timely 五大特性必须解释
- **断言风格**：优先 AssertJ / Hamcrest，不用过时 JUnit 4 assertEquals
- **测试命名规范**：`methodName_condition_expectedResult` 三段式（如 `divide_byZero_throwsException`）
- **Spring Boot 测试注解**：必须区分 `@MockBean`（已 deprecated，Spring 6.2+ 用 `@MockitoBean`）vs `@Mock`

### 互链要求

- 必须互链 `04.spring-backend/` 的 Spring Boot Test 章节
- JUnit 5 文章必须回链「JUnit 4 → 5 迁移指南」
- Mockito 文章必须互链 PowerMock（遗留系统）和 Mockito 5（当前推荐）
- JaCoCo 文章必须互链 SonarQube（覆盖率平台）

### 反模式

- ❌ 单元测试里启动 Spring 上下文（应用 `@SpringBootTest`）
- ❌ 100% 覆盖率追求（牺牲可读性）
- ❌ Mock 所有静态方法（PowerMock 反模式，应重构）
- ❌ 测试间共享状态（违反 Independent）
- ❌ 测试方法名 `test1()` / `test2()`（违反 Self-validating）