
# SPEC for note/01.java-and-jvm/04-patterns/

> **Inherits from**: [../../SPEC.md](../../SPEC.md)
> **Mode**: append + override
> **Updated**: 2026-08-13

---

## 子目录定位

GoF 23 种设计模式的 Java 实战指南：创建型 / 结构型 / 行为型三大类，按 GoF 分类拆分，强调「何时用 vs 何时不用 + 现代语言特性替换」。

## 从 L1 继承

- G1-G6 通用 6 维度评分
- A1 源码级深度（带 JDK 版本）
- A3 反例对比（❌/✅）
- A2 版本演进对比（Java 8 Lambda/Stream 前后）

## 本子目录规则（强特异性）

### 评估维度（追加 L1 维度后）

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| P1 | 23 种 GoF 适用场景 | 每个模式给出「适用场景 + 不适用场景」对比 | 只有适用场景 | 只有定义和 UML |
| P2 | 反模式识别 | 有 ❌ 滥用案例 + 触发条件 | 有反模式但未说明触发 | 无反模式 |
| P3 | 现代语言特性替换 | 注明 Lambda / Stream / record / sealed 是否能替代 | 提及但无对比 | 完全忽略现代特性 |

### 写作要求

- **UML/结构图必备**：每个模式至少有 1 张类图（PlantUML 或 Mermaid）
- **JDK 版本演进**：注明模式适用的 JDK 版本（如 Observer 在 Java 9+ 已 deprecated）
- **相似模式对比**：高频二选一必须并列对比（Factory Method vs Abstract Factory / Decorator vs Proxy / Strategy vs State）
- **现代替换清单**：能用 Lambda / Stream 替代的模式必须标注「Java 8+ 优先用 Lambda」
- **代码可直接运行**：示例代码必须有 main 方法或可独立编译运行
- **GoF 三分类严格分离**：创建型 / 结构型 / 行为型必须各自成目录，不混淆

### 互链要求

- `creation/README.md`、`structural/README.md`、`behavioral/README.md` 必须互链
- 每个 split-hairs 迁出的模式（如 `creation/singleton.md`）必须回链本目录 README
- 单例模式必须互链「Java 5+ 枚举实现」（split-hairs 视角）
- 装饰器 / 代理模式必须互链 Spring AOP（`04.spring-backend/`）

### 反模式

- ❌ 罗列 23 种模式但不分场景
- ❌ 不区分 Java 7 vs Java 8+ 实现差异
- ❌ 把 Builder 模式写成链式 setter 而不说清「为什么需要 Director」
- ❌ 推荐单例 + 静态变量（已被 Spring 单例 Bean 替代）