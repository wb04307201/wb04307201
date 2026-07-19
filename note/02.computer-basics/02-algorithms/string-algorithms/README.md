<!--
module:
  parent: algorithms
  slug: algorithms/string-algorithms
  type: deep-dive
  category: 字符串算法
  summary: 字符串算法 3 大深度 —— Trie（字典树）/ KMP / AC 自动机（多模式匹配）+ 实战选型
-->

# 字符串算法 · 3 大深度（Trie / KMP / AC 自动机）

> **一句话答案**：**单模式匹配（找一个串）用 KMP**；**多模式匹配（同时找多个串）用 AC 自动机（基于 Trie + 失配指针）**；**前缀查询（字典/自动补全）用 Trie**。

← [返回: algorithms 总目录](../README.md) · 实战：[sensitive-word-filter](../../../04.system-design/04-high-performance/sensitive-word-filter/README.md)

---

## 0. 3 大算法速览

| 算法 | 适用 | 时间复杂度 | 空间复杂度 | 典型场景 |
|------|------|-----------|-----------|----------|
| **Trie（字典树）** | 前缀查询 | O(n) 插入 / 查询 | O(Σ × n) | 自动补全 / 词频统计 |
| **KMP** | 单模式匹配 | O(n + m) | O(m) | strstr / findInText |
| **AC 自动机（Aho-Corasick）** | 多模式匹配 | O(n + m + z) | O(Σ × m) | 敏感词过滤 / 日志告警 |

**关键洞察**：
- 敏感词过滤是**多模式匹配**场景 → **AC 自动机是工业首选**
- Trie 是 AC 自动机的核心数据结构（fail 指针基于 Trie 构建）
- KMP 处理单模式匹配（一个 needle 在 haystack 中），AC 处理多模式（多个 needle）

---

## 1. Trie（字典树 / 前缀树）

### 1.1 核心思想

```
存储 "apple" / "app" / "apply" / "banana"：

root
├── a
│   └── p
│       └── p (标记 end)
│           ├── l
│           │   └── e (end)
│           │       └── y (end)
│           └── (空)
└── b
    └── a
        └── n
            └── a
                └── n
                    └── a (end)
```

### 1.2 关键性质

- 共享前缀（"app" / "apple" / "apply" 共享 'app'）
- 查找时间 O(len(word))，与字典大小**无关**
- 空间换时间

### 1.3 适用场景

- 自动补全（搜索框 / IDE）
- 词频统计
- IP 路由表最长前缀匹配
- 敏感词 Trie 部分（AC 自动机前置）

详细：[01-trie-data-structure.md](01-trie-data-structure.md)

---

## 2. KMP（单模式匹配）

### 2.1 核心思想

**问题**：`strstr(haystack, needle)`——在 haystack 中找 needle 出现的位置。

朴素算法遇到不匹配时，**回退到头部重新比对**——O(n × m)。

KMP 利用**已匹配信息**——构造 next 数组（部分匹配表 LPS），不匹配时**跳过不可能匹配的位置**——O(n + m)。

### 2.2 时间复杂度

- 预处理 next 数组：O(m)
- 匹配：O(n)
- 总：O(n + m)

### 2.3 适用场景

- 文本编辑器查找（Ctrl+F）
- 日志关键字搜索
- 单 needle 搜索

详细：[02-kmp-algorithm.md](02-kmp-algorithm.md)

---

## 3. AC 自动机（Aho-Corasick）

### 3.1 核心思想

**问题**：同时在 haystack 中找 N 个 patterns（如 1 万个敏感词）？

**朴素**：每个 pattern 用 KMP 跑一次 → O(N × n + Σ m)

**AC 自动机**：构建 Trie + fail 指针，一次扫描找全部 → **O(n + Σ m + z)**（z = 匹配数）

```
构建：build_trie(patterns) + build_fail(trie) → O(Σ m)
匹配：scan(haystack) → 沿 Trie 走，失配时沿 fail 跳转
```

### 3.2 关键概念

- **fail 指针**（失配指针）：节点 A 的 fail 指向 A 父节点的 fail 链中能匹配的最长后缀
- **output 链**：每个节点维护一个链表，记录"该节点代表的字符串是哪些 patterns 的后缀"

### 3.3 适用场景

- **敏感词过滤**（10k+ 词）
- 日志关键字多模式匹配
- DNA 序列多模式匹配
- 入侵检测（Snort / Suricata）

详细：[03-ac-automaton.md](03-ac-automaton.md)

---

## 4. 3 大算法对比

| 维度 | Trie | KMP | AC 自动机 |
|------|------|-----|----------|
| **场景** | 前缀查询 | 单模式匹配 | **多模式匹配** |
| **时间** | O(len) | O(n+m) | O(n + Σ m + z) |
| **空间** | 高（O(Σn)） | 低（O(m)）| 高 |
| **实现复杂度** | 中 | 中 | 高（fail 指针）|
| **Java 实现** | 数组/HashMap | Loop | Trie + BFS 建 fail |

---

## 5. 字符串算法选型决策

```
场景：你在做敏感词过滤系统，怎么选？

Q1：需要过滤多少个敏感词？
├─ < 100 词 → 暴力 KMP（每个词 O(n+m)，总 O(N×(n+m)），100 词够用）
├─ 100 - 1k → KMP 仍可接受
└─ > 1k 词 → AC 自动机 ✅

Q2：需要支持"前缀匹配"（如 "黄" 要匹配 "黄色电影"）？
├─ 是 → Trie + AC
└─ 否（精确匹配）→ KMP / AC 均可

Q3：实时性要求（每条消息 < 10ms 检测）？
├─ 是 → AC 自动机（O(n) 单次扫描）
└─ 否 → 任何方案都够用
```

**实战**：
- 90% 敏感词过滤场景：**AC 自动机**
- 10% 自动补全场景：**Trie**

---

## 6. 子章节导航

| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [Trie 数据结构](01-trie-data-structure.md) | Trie 怎么实现？字典序 / 自动补全 / 路由前缀 |
| 02 | [KMP 算法](02-kmp-algorithm.md) | next 数组怎么算？单模式匹配的最佳实践 |
| 03 | [AC 自动机](03-ac-automaton.md) | fail 指针怎么建？Java 完整实现 + 性能对比 |

---

## 7. 一句话总结

> **3 大算法选型公式：前缀查询 → Trie；单模式 → KMP；多模式 → AC 自动机（敏感词过滤 99% 用这个）。3 算法配合形成 AC 自动机基础——Trie 建树 + fail 指针 = AC 自动机。**

---

## 8. 实战推荐

| 库 | 语言 | 备注 |
|----|------|------|
| **AhoCorasickDoubleArrayTrie** | Java | hanlp 出品，工业级 ✅ |
| **aho-corasick** | C++ / Rust | 高性能 |
| **AC 算法 Java 实现** | 100 行手写 | 面试常考 |

实战案例见 [sensitive-word-filter 高并发设计](../../../04.system-design/04-high-performance/sensitive-word-filter/README.md)

---

← [返回: algorithms 总目录](../README.md)
