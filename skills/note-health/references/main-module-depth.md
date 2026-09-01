# 主模块 depth 校准（PoC 方案 + 自动化工具）

> **背景**：12.interview difficulty 校准流程成熟后，扩展到主模块（01-11）需要新方案
> **来源**：`note/.health-tmp/main-module-calibration-design.md` 设计稿 + `01.java-and-jvm` 92 篇 PoC 验证
> **状态**：PoC 完成（commit `b996d1c3`），可推广到 02-11

## 1. depth 字段定义（5 档）

| 档位 | 星标 | 含义 | 典型特征 |
|------|------|------|----------|
| **L1 入门** | ⭐ | 概念 + 简单示例 | < 100 行；无源码；1-2 联动 |
| **L2 进阶** | ⭐⭐ | 原理 + 多语言示例 | 100-200 行；含原理图；2-3 联动 |
| **L3 高级** | ⭐⭐⭐ | 源码级深度 + 版本演进 | 200-400 行；含字节码 / JVM；3-5 联动 |
| **L4 引擎级** | ⭐⭐⭐⭐ | 跨模块 + 性能优化 | 400-800 行；含 OpenJDK 源码；5+ 联动 |
| **L5 大师级** | ⭐⭐⭐⭐⭐ | 系统性深度 + 实战案例 | > 800 行；含引擎级源码；7+ 联动 |

## 2. adapted 5-dim 评分标准（主模块专用）

| 维度 | 2 分 | 1 分 | 0 分 |
|------|------|------|------|
| **D1 源码深度** | OpenJDK / 引擎源码 + 字节码 | 原理 + 设计模式 | 概念 + API 用法 |
| **D2 跨模块联动** | 5+ 主模块联动 | 2-4 联动 | 单模块 |
| **D3 系统性** | 含演进史 + 设计哲学 | 含优缺点对比 | 单一视角 |
| **D4 追问空间** | 可追 5+ 层（架构 → 源码 → 性能 → 演进）| 可追 2-3 层 | 一句话答完 |
| **D5 实战价值** | 3+ 生产案例 / 性能数据 | 1-2 案例 | 纯理论 |

总分 0-10 → depth 映射：
- 9-10 → L5 ⭐⭐⭐⭐⭐
- 7-8 → L4 ⭐⭐⭐⭐
- 5-6 → L3 ⭐⭐⭐⭐⭐
- 3-4 → L2 ⭐⭐
- 0-2 → L1 ⭐

## 3. frontmatter 模板

```yaml
<!--
module:
  parent: java
  slug: java/collection/concurrent-hashmap
  type: article
  category: 主模块子文章
  summary: ConcurrentHashMap JDK7 分段锁 vs JDK8 CAS+synchronized 实现。
  depth: ⭐⭐⭐⭐⭐
-->
```

**关键字段**：
- `depth:` 1-5 星（必填，主模块专用）
- 与 12.interview `difficulty:` 区分（后者是面试准备信号）

## 4. 自动化工具：apply-depth.py

> 脚本位置：`skills/note-health/references/main-module-depth.md` 附录 / `note/.health-tmp/apply-depth.py`

### 4.1 工作流程

```
1. 抽样：每模块随机抽 3-5 篇（用 sample-files-v2.py 类似脚本生成清单）
2. 5-dim 评分：dispatch 并行 subagent 评估（每 agent 处理 20-30 篇）
3. 收集：合并各 agent 结果到 depth-values.json
4. 应用：apply-depth.py 批量修改 frontmatter
5. 验证：git diff 检查 + 重跑评分脚本
6. commit：一条 commit 全部搞定
```

### 4.2 depth-values.json 格式

```json
{
  "01-language/polymorphism": "L5",
  "01-language/syntax": "L1",
  "collection/ConcurrentHashMap": "L5",
  "version/class-file-api": "L5"
}
```

### 4.3 apply-depth.py 用法

```bash
# 默认应用 note/.health-tmp/depth-values.json
python note/.health-tmp/apply-depth.py

# 输出：应用 N / 跳过 M / 失败 K
```

脚本逻辑：
- 检查文件 frontmatter 是否已有 `depth:` 字段
- 如有 → 更新；如无 → 在 `module:` 块末尾插入
- 兼容两种 frontmatter 格式（`<!--module:` 和 `<!--\nmodule:`）

## 5. PoC 验证数据（01.java-and-jvm 92 篇）

| Depth | 数量 | 占比 | 代表 |
|-------|------|------|------|
| L5 | 24 | 26% | polymorphism / virtual-threads / ConcurrentHashMap / ArrayList / TreeMap / io/nio / io/zero-copy / jdbc / class-file-api / ffi-api / gc / vector-api |
| L4 | 10 | 11% | java-locks / synchronized / volatile / excel-export-oom / atomic / generics / object / exception |
| L3 | 30 | 33% | concurrency 主流 / patterns 三件套 / LinkedHashSet |
| L2 | 17 | 18% | kotlin 系列 5 篇 / method / variable |
| L1 | 7 | 8% | java-10/12/13/23/26 / record / syntax |

**平均分**：6.1 / 10

**关键洞察**：
1. **JVM/集合/IO/网络** 是 L5 高地（四大金刚）
2. **virtual-threads** 是 Java 21 LTS 标杆（JEP 425/444/491 演进链）
3. **Kotlin 系列** 01-05 严重浅薄，06-engineering 凭 KMP 跨平台拿到 L5
4. **设计模式** 三篇整齐 L3（缺 JDK 源码深度）
5. **13/24 L5 文章**均涉及 OpenJDK 源码 + 实战案例 + 演进史（3 大特征）

## 6. 推广路径

### 6.1 推荐顺序（按 leaf 数量）

| 优先级 | 模块 | leaf 数 | 复杂度 |
|--------|------|---------|--------|
| P1 | 06.distributed-systems | 158 | 高（架构多）|
| P1 | 04.spring-backend | 141 | 高（Spring 源码）|
| P1 | 09.ai-applications | 133 | 中（AI 应用）|
| P2 | 05.frontend | 57 | 中（前端框架）|
| P2 | 07.devops-and-tools | 47 | 低 |
| P2 | 02.cs-foundations | 43 | 中（算法）|
| P3 | 10.business-systems | 38 | 低 |
| P3 | 03.data-stack | 32 | 中（数据库）|
| P3 | 08.ai-foundations | 14 | 低 |
| P3 | 11.product-and-pm | 12 | 低 |

### 6.2 批量执行

- 每模块 5-10 个并行 subagent，每 agent 处理 20-30 篇
- 5-dim 评分 → depth-values.json → apply-depth.py → commit
- 单模块 commit message 格式：`feat(NN.module-name): depth 校准 PoC（X 篇）`

## 7. 与 12.interview difficulty 的关系

| 维度 | 12.interview difficulty | 主模块 depth |
|------|----------------------|---------------|
| 目标读者 | 求职者（面试准备）| 自学者（系统学习）|
| 关键维度 | D3 频次 + D5 陷阱 | D1 源码 + D2 联动 |
| 星数含义 | 面试重要程度 | 内容深度档位 |

**映射参考**（不是强制）：
- 12.interview ⭐⭐⭐⭐⭐（5 星保留档）→ 主模块 depth 4-5 星（引擎级 / 大师级）
- 12.interview ⭐⭐⭐（高频）→ 主模块 depth 3-4 星（高级 / 引擎级）
- 12.interview ⭐（冷门）→ 主模块 depth 2-3 星（进阶 / 高级）

## 8. CI 集成（未来）

在 `.github/workflows/difficulty-calibration.yml` 中扩展：

```yaml
# 检查主模块 depth 字段
- name: Check main module depth
  run: python scripts/check-depth.py
```

check-depth.py 校验：
- 所有 module: frontmatter 必有 depth: 字段
- depth 值合法（L1-L5）
- 与 5-dim 评分（可选）一致
