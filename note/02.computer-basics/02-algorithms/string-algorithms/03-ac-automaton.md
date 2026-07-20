<!--
module:
  parent: algorithms/string-algorithms
  slug: algorithms/string-algorithms/03-ac-automaton
  type: topic
  category: AC 自动机
  summary: AC 自动机（Aho-Corasick）—— Trie + fail 指针 + 多模式匹配 + Java 完整实现
-->

# AC 自动机（Aho-Corasick）· 多模式匹配

> **一句话**：AC 自动机 = Trie（存所有 patterns）+ fail 指针（类似 KMP 的 next，单次扫描 O(n) 找出所有 patterns）。**敏感词过滤 99% 用这个**——10 万词典也能毫秒级匹配。

← [返回: string-algorithms 总目录](../README.md)

---

## 1. 问题：从多模式匹配到 AC 自动机

### 1.1 朴素方案

```text
patterns = [敏感词 1 万个]
haystack = 用户评论 1000 字

朴素：每个 pattern 用 KMP 跑一次 → O(10000 × 1000) = 1000 万字符比较 → 几百 ms
```

**性能差**——评论场景不能容忍 100ms+ 延迟。

### 1.2 AC 自动机方案

**一次扫描**找出所有匹配 patterns → **O(n + Σ m + z)**（n=haystack 长度，Σ m = patterns 总长，z = 匹配数）

---

## 2. AC 自动机 3 大核心组件

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

## 3. fail 指针构建（BFS）

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

## 4. AC 自动机匹配

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

## 5. AC 自动机完整实现

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

## 6. 性能基准

### 6.1 典型场景

| 场景 | 词典大小 | 文本长度 | AC 耗时 | 朴素耗时 |
|------|---------|---------|---------|----------|
| 评论过滤 | 10k | 500 | **2 ms** | 500 ms |
| 弹幕审核 | 100k | 50 | **0.5 ms** | 200 ms |
| 日志告警 | 1k | 10000 | **10 ms** | 5000 ms |

**性能提升 100-500x**。

### 6.2 内存占用

- 词典 10k：~50 MB（朴素 Trie）
- 词典 100k：~500 MB
- **生产推荐**：用**双数组 Trie**（DoubleArrayTrie）压缩到 1/10

---

## 7. 反模式 · 5 个常见错

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

### ⚠️ 反模式 3：朴素 Trie（不压缩）

```java
// 词典 100k → 500 MB 内存
// 生产必上：DoubleArrayTrie / AhoCorasickDoubleArrayTrie（hanlp）
```

### ⚠️ 反模式 4：忘记中文分词

```java
// 敏感词是 "黄色电影"，文本是 "黄 色 电 影"（带空格）→ 直接匹配失败
// 解：在 Trie 建树前对文本做中文分词（IK Analyzer / HanLP）
```

### ⚠️ 反模式 5：忽略大小写 / 简繁

```java
// 错：严格匹配，漏掉 "Fuck" / "FUCK"
ac.insert("fuck");
// 预处理：统一转小写 + 简繁转换
```

---

## 8. 工业级开源库

| 库 | 语言 | 备注 |
|----|------|------|
| **AhoCorasickDoubleArrayTrie** | Java | hanlp 出品，工业首选 ✅ |
| **aho-corasick** | Rust | 高性能 |
| **AC 算法** | C++ | 嵌入式 / 内核 |
| **ahocorasick** | Python | 快速原型 |

**推荐**：`com.hankcs:hanlp:AhoCorasickDoubleArrayTrie`

---

## 9. 一句话总结

> **AC 自动机 = Trie（建树）+ fail 指针（类似 KMP 的 next）+ output 链（合并匹配）= 多模式匹配 O(n+Σm+z)。敏感词过滤 99% 用 AC，双数组 Trie 实现可压到 1/10 内存。**

> 🔗 **工程应用**：AC 自动机在高并发敏感词过滤系统中的完整落地（Bloom + 缓存 + 分布式 + [变体绕过对抗](../../../04.system-design/04-high-performance/sensitive-word-filter/05-anti-evasion.md)）见 [04.system-design/sensitive-word-filter 专题](../../../04.system-design/04-high-performance/sensitive-word-filter/README.md)。

---

← [返回: string-algorithms 总目录](../README.md) · 上一章：[02-kmp-algorithm](02-kmp-algorithm.md)
