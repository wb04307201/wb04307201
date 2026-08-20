<!--
module:
  parent: algorithms/string-algorithms
  slug: algorithms/string-algorithms/03-ac-automaton
  type: topic
  category: AC 自动机
  summary: AC 自动机（Aho-Corasick）—— Trie + fail 指针 + 多模式匹配 + Java 完整实现
-->

# AC 自动机（Aho-Corasick）· 多模式匹配

> **一句话**：AC 自动机 = [Trie](01-trie-data-structure.md)（存所有 patterns）+ fail 指针（类似 [KMP](02-kmp-algorithm.md) 的 next），构建完成后只需扫描文本一次，即可找出所有模式串。

← [返回: string-algorithms 总目录](../README.md)

---

## 问题：从多模式匹配到 AC 自动机
### 1.1 朴素方案

```text
patterns = [敏感词 1 万个]
haystack = 用户评论 1000 字

朴素：每个 pattern 用 KMP 跑一次 → O(10000 × 1000) = 1000 万字符比较 → 几百 ms
```

**性能差**——评论场景不能容忍 100ms+ 延迟。

### 1.2 AC 自动机方案

一次扫描找出所有匹配。先定义变量：

- `P = Σ|pattern_i|`：所有模式串的总长度
- `n = |text|`：待匹配文本长度
- `σ`：字符集大小（数组子节点实现中，每个节点预留 `σ` 个槽位）
- `V`：Trie 节点数，最坏 `V ≤ P + 1`
- `z`：输出的匹配结果数量

在本文使用的 `HashMap` 子节点 + fail 链实现中，插入 Trie 访问每个模式字符一次；BFS 构建 fail 指针时，每个节点入队一次，失配跳转的代价按实现与输入分布而定。若使用完整转移表，把每个节点的 `σ` 个转移都预计算出来，则：

| 阶段 | 时间复杂度 | 空间复杂度 | 推导 |
|------|-----------|-----------|------|
| 构建 | **O(P × σ)** | **O(P × σ)** | 最多 `P + 1` 个节点；每个节点初始化/补齐 `σ` 个转移 |
| 匹配 | **O(n + z)** | O(1) 额外游标空间 | 每个文本字符只做一次状态转移；枚举命中结果另需 O(z) |
| 仅判断是否命中 | **O(n)** | O(1) | 找到首个输出即可返回，不枚举全部结果 |

因此，若不计输出结果，常写成“构建 `O(P × σ)`、匹配 `O(n)`、空间 `O(P × σ)`”；若必须返回全部命中，则总时间应写为 **O(P × σ + n + z)**。稀疏 `HashMap` 实现不为不存在的边分配槽位，节点与边主体空间可降为 O(P)，但常数、哈希开销和最坏跳转行为需要单独基准验证。

---

## AC 自动机 3 大核心组件
```text
┌────────────────────────────────────────────────────────┐
│ 组件 1：Trie 树                                            │
│   - 存所有 patterns                                        │
│   - 每个节点多个 child（children）                          │
└────────────────────────────────────────────────────────┘
                    ↓ 构建
┌────────────────────────────────────────────────────────┐
│ 组件 2：fail 指针（失配指针）                               │
│   - 节点 A 的 fail 指针 = A 父节点 fail 链中能匹配的        │
│     最长后缀对应的 child                                    │
│   - 类似 KMP 的 next 数组                                  │
└────────────────────────────────────────────────────────┘
                    ↓ 构建
┌────────────────────────────────────────────────────────┐
│ 组件 3：output 链（输出指针）                              │
│   - 每个节点维护一个 list，记录"该节点代表的字符串是        │
│     哪些 patterns 的后缀"                                   │
│   - 匹配时沿 output 链收集所有命中                          │
└────────────────────────────────────────────────────────┘
```

---

## fail 指针构建（BFS）
```java
// BFS 构建 fail 指针
Queue<TrieNode> queue = new LinkedList<>();

// 根节点的 fail = 根
TrieNode root = new TrieNode();
root.fail = root;

// 第一层 child 的 fail = root
for (TrieNode child : root.children.values()) {
    child.fail = root;
    queue.offer(child);
}

// BFS
while (!queue.isEmpty()) {
    TrieNode parent = queue.poll();
    for (Map.Entry<Character, TrieNode> e : parent.children.entrySet()) {
        char c = e.getKey();
        TrieNode child = e.getValue();
        // 沿 parent.fail 链向上查找，找到能匹配 c 的节点
        TrieNode failNode = parent.fail;
        while (failNode != root && !failNode.children.containsKey(c)) {
            failNode = failNode.fail;
        }
        if (failNode.children.containsKey(c)) {
            child.fail = failNode.children.get(c);
        } else {
            child.fail = root;
        }
        // output 链：合并 fail 节点的 output
        child.output.addAll(child.fail.output);
        queue.offer(child);
    }
}
```

---

## AC 自动机匹配
```java
public List<String> match(String text) {
    List<String> matches = new ArrayList<>();
    TrieNode node = root;
    
    for (int i = 0; i < text.length(); i++) {
        char c = text.charAt(i);
        // 沿 fail 链向上，直到能找到 c 的 child
        while (node != root && !node.children.containsKey(c)) {
            node = node.fail;
        }
        if (node.children.containsKey(c)) {
            node = node.children.get(c);
        }
        // 收集匹配（沿 output 链）
        for (String pattern : node.output) {
            matches.add(pattern);
        }
    }
    return matches;
}
```

---

## AC 自动机完整实现
```java
public class AhoCorasick {
    private final TrieNode root = new TrieNode();
    
    /** 插入敏感词 */
    public void insert(String pattern) {
        TrieNode node = root;
        for (char c : pattern.toCharArray()) {
            node.children.putIfAbsent(c, new TrieNode());
            node = node.children.get(c);
        }
        node.isEnd = true;
        node.output.add(pattern);  // 记录 pattern
    }
    
    /** 构建 fail 指针（构建完成后才能匹配） */
    public void build() {
        root.fail = root;
        Queue<TrieNode> queue = new LinkedList<>();
        for (TrieNode child : root.children.values()) {
            child.fail = root;
            queue.offer(child);
        }
        while (!queue.isEmpty()) {
            TrieNode parent = queue.poll();
            for (Map.Entry<Character, TrieNode> e : parent.children.entrySet()) {
                char c = e.getKey();
                TrieNode child = e.getValue();
                TrieNode failNode = parent.fail;
                while (failNode != root && !failNode.children.containsKey(c)) {
                    failNode = failNode.fail;
                }
                if (failNode.children.containsKey(c)) {
                    child.fail = failNode.children.get(c);
                } else {
                    child.fail = root;
                }
                // 合并 output
                child.output.addAll(child.fail.output);
                queue.offer(child);
            }
        }
    }
    
    /** 匹配（找出所有命中的 patterns）*/
    public List<String> match(String text) {
        List<String> matches = new ArrayList<>();
        TrieNode node = root;
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            while (node != root && !node.children.containsKey(c)) {
                node = node.fail;
            }
            if (node.children.containsKey(c)) {
                node = node.children.get(c);
            }
            matches.addAll(node.output);
        }
        return matches;
    }
    
    static class TrieNode {
        Map<Character, TrieNode> children = new HashMap<>();
        boolean isEnd = false;
        TrieNode fail;                    // fail 指针
        List<String> output = new ArrayList<>();  // output 链
    }
}
```

---

## 性能基准（保守口径）
AC 自动机适合“百万级文本 + 千级模式串”的批量多模式匹配场景。此类场景中，**实测匹配时间常见于 5-50 ms**，但该区间只用于量级判断，不能当作跨环境承诺；结果取决于 CPU、内存、JVM 版本与 GC、字符集实现、词典前缀共享度、模式长度分布、文本命中率以及输出数量。

可复现基准应至少记录：

- 硬件：CPU 型号、核心数、内存容量
- 运行时：JDK/JVM 版本、堆大小、GC 参数
- 数据集：文本字符数、模式串数量、`P`、长度分布、字符分布与命中率
- 方法：预热次数、正式迭代次数、吞吐量，以及 P50/P95/P99 延迟
- 边界：构建耗时与匹配耗时分开统计，避免把词典加载混入单次查询

以下 JMH 骨架展示统计口径；具体数字必须以目标机器和真实数据集的结果为准：

```java
@Benchmark
public List<String> matchMillionCharacters(BenchmarkState state) {
    // state.ac 已在 @Setup 中完成词典插入和 build，避免重复计入构建时间
    return state.ac.match(state.text);
}
```

### 6.1 内存评估

内存不能仅由“词典条数”推出：同样是千级模式串，前缀共享度、平均长度、字符集和节点容器实现不同，节点数 `V` 与对象开销会显著变化。评估时应记录实际 `V`，并分别测量数组转移表、`HashMap` 稀疏边和双数组 Trie；生产选型以堆转储或 JOL/JMH 实测为准。

---

## 反模式 · 5 个常见错
### ⚠️ 反模式 1：忘记构建 fail 指针

```java
ac.insert(patterns);
ac.match(text);  // ❌ 输出是空的（没 build）
ac.build();      // ✅ 必须先 build
ac.match(text);
```

### ⚠️ 反模式 2：output 链没合并

```java
// 错：只检查当前节点的 output
// 漏掉 fail 链上的 output（如 "he" 和 "she" 共用 "he"）

// 对：构建 fail 时合并 output
child.output.addAll(child.fail.output);
```

### ⚠️ 反模式 3：未经测量就认定朴素 Trie 内存过高

```java
// 错：仅凭词典条数断言固定内存占用
// 对：统计节点数 V，并在真实词典上比较 HashMap、数组转移表与双数组 Trie
```

### ⚠️ 反模式 4：把分词当作绕过字符的归一化

```java
// 敏感词是 "黄色电影"，文本是 "黄​色 电 影"（零宽空格 + 分隔符）
// 错：中文分词不能保证恢复被拆散的敏感词，分词边界反而可能继续保留拆分
// 对：建树前与匹配前采用同一管线：Unicode NFKC 归一化、同形字符映射、
//     移除业务允许忽略的分隔符（如零宽空格），同时保存原始位置映射供审计
```

NFKC 只能折叠部分兼容字符，**不能自动解决所有跨文字系统同形字符**（如拉丁字母与西里尔字母的视觉混淆），因此同形字符映射必须基于业务风险维护白名单；移除分隔符也要限制范围，避免把正常文本拼接成误报。更完整的对抗策略见[变体绕过对抗](../../../06.distributed-systems/04-high-performance/sensitive-word-filter/05-anti-evasion.md)。

### ⚠️ 反模式 5：忽略大小写 / 简繁

```java
// 错：严格匹配，漏掉 "Fuck" / "FUCK"
ac.insert("fuck");
// 预处理：统一转小写 + 简繁转换
```

---

## 工业级开源库
| 库 | 语言 | 备注 |
|----|------|------|
| **AhoCorasickDoubleArrayTrie** | Java | hanlp 出品，工业首选 ✅ |
| **aho-corasick** | Rust | 高性能 |
| **AC 算法** | C++ | 嵌入式 / 内核 |
| **ahocorasick** | Python | 快速原型 |

**推荐**：`com.hankcs:hanlp:AhoCorasickDoubleArrayTrie`

---

## 一句话总结
> **AC 自动机 = Trie 建树 + fail 指针复用后缀状态 + output 输出命中。**完整转移表的构建与空间上界均为 O(P × σ)，匹配扫描为 O(n)，返回全部结果时还需 O(z)；真实性能必须在目标硬件、JVM 和数据分布上测量。

> 🔗 **工程应用**：AC 自动机在高并发敏感词过滤系统中的完整落地（Bloom + 缓存 + 分布式 + [变体绕过对抗](../../../06.distributed-systems/04-high-performance/sensitive-word-filter/05-anti-evasion.md)）见 [12.interview/04.system-design/sensitive-word-filter 专题](../../../06.distributed-systems/04-high-performance/sensitive-word-filter/README.md)。

---

← [返回: string-algorithms 总目录](../README.md) · 上一章：[KMP 算法](02-kmp-algorithm.md) · 基础：[Trie 数据结构](01-trie-data-structure.md)
