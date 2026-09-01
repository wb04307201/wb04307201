<!--
module:
  parent: algorithms/string-algorithms
  slug: algorithms/string-algorithms/02-kmp
  type: topic
  category: KMP
  summary: KMP 算法 —— next 数组（部分匹配表）+ Java 实现 + strstr
  depth: ⭐⭐⭐⭐
-->

# KMP 算法 · 部分匹配表（LPS）

> **一句话**：KMP 用 LPS 复用已匹配的前后缀；失配时文本指针不回退，预处理 O(m)、匹配 O(n)，总计 O(n+m)。

← [返回: algorithms 总目录](../README.md) · [字符串算法专题](README.md)

---

## 朴素算法的问题
```text
haystack = "ABABABC"
needle   = "ABABC"

候选起点为 0 时，前 4 个字符 "ABAB" 已匹配：
haystack[4] = 'A'
needle[4]   = 'C'  ← 失配

朴素算法：把候选起点从 0 移到 1，重新比较；没有直接复用已知的 "ABAB" 结构。
KMP：保留 i=4，利用 "ABAB" 的最长相等真前后缀 "AB"，只回退模式串指针。
```

朴素算法在每个候选起点最多比较 `m` 次，共有至多 `n-m+1` 个候选起点，最坏时间为 `O((n-m+1)m) = O(nm)`。

---

## KMP 核心思想
**关键洞察**：失配时，`needle` 指针不一定回到 0。已经匹配的部分同时包含某个相等的前缀和后缀，可以把前缀直接对齐到后缀，跳过不可能成为答案的起点。

```text
needle 已匹配部分 = "ABAB"
最长相等真前缀   = "AB"
最长相等真后缀   = "AB"

失配前 j = 4
失配后 j = 2，而 haystack 的 i 保持不变
```

这个“可保留的最长匹配长度”就是 **LPS**（Longest Proper Prefix which is also Suffix），本文使用 `next` 作为数组名。

- 单模式子串查找：使用 KMP。
- 前缀查询：使用 [Trie（字典树）](01-trie-data-structure.md)。
- 多模式匹配：使用 [AC 自动机](03-ac-automaton.md)，其 `fail` 指针可视为 KMP 失配思想在 Trie 上的推广。

---

## next / LPS 数组详解
### 3.1 定义：本文统一采用“长度 + 0 下标”约定

对 0 下标模式串 `needle`，本文定义：

```text
next[i] = needle[0..i] 的最长相等真前缀与真后缀的长度
```

其中 `needle[0..i]` **两端都包含**；“真”表示不能取整个 `needle[0..i]`。更严格地说：

```text
next[i] = max k，满足：
          0 <= k < i + 1
          needle[0..k-1] == needle[i-k+1..i]
```

`k=0` 表示空前后缀，所以 `next[0]=0`。注意：`next[i]` 描述的是 **`needle[0..i]`**，不是 `needle[0..i-1]`。

### 3.2 📌 `ABAB` 的下标与 LPS 对齐图

```text
下标 i        0    1    2    3
字符          A    B    A    B
子串          A    AB   ABA  ABAB
最长相等真前后缀
              ""   ""   A    AB
next[i]       0    0    1    2
```

最后一格的对齐关系：

```text
位置          0    1    2    3
needle        A    B    A    B
真前缀 "AB"  A    B
真后缀 "AB"            A    B

所以 next[3] = 2，而不是 next[4] = 2。
```

当已经匹配 `j` 个字符却发生失配时，已匹配区间是 `needle[0..j-1]`，因此应回退到：

```text
j = next[j - 1]
```

这也解释了为什么本文的代码不是 `j = next[j]`。

### 3.3 🔧 next 数组完整计算：`ABABAC`

为了同时看到“增长”和“连续回退”，取 `needle = "ABABAC"`。进入每轮时，`j` 表示 `needle[0..i-1]` 的当前 LPS 长度，也表示接下来要比较的模式串下标。

| 步骤 | `i` | 当前字符 | 进入时 `j` | 比较与动作 | `next[i]` | 当前 next |
|------|----:|----------|-----------:|------------|----------:|-----------|
| 初始化 | 0 | `A` | 0 | 单字符没有非空真前后缀 | 0 | `[0]` |
| 1 | 1 | `B` | 0 | `B != needle[0](A)`，不能再退 | 0 | `[0, 0]` |
| 2 | 2 | `A` | 0 | `A == needle[0](A)`，`j++` | 1 | `[0, 0, 1]` |
| 3 | 3 | `B` | 1 | `B == needle[1](B)`，`j++` | 2 | `[0, 0, 1, 2]` |
| 4 | 4 | `A` | 2 | `A == needle[2](A)`，`j++` | 3 | `[0, 0, 1, 2, 3]` |
| 5 | 5 | `C` | 3 | `C != needle[3](B)` → `j=next[2]=1`；仍不等 → `j=next[0]=0`；`C != needle[0](A)` | 0 | `[0, 0, 1, 2, 3, 0]` |

最终对齐：

```text
下标 i   0  1  2  3  4  5
needle   A  B  A  B  A  C
next     0  0  1  2  3  0
```

第 5 步虽然连续回退了两次，但 `i` 没有倒退；只是依次尝试当前已匹配串的次长 LPS。

### 3.4 Java 构造实现

```java
public int[] buildNext(String needle) {
    int[] next = new int[needle.length()];
    int j = 0; // needle[0..i-1] 的当前 LPS 长度

    // next[0] 默认为 0；从 i=1 开始扩展前缀
    for (int i = 1; i < needle.length(); i++) {
        // 当前候选不成立：尝试已匹配部分的次长 LPS
        while (j > 0 && needle.charAt(i) != needle.charAt(j)) {
            j = next[j - 1];
        }

        // 当前字符可接在长度为 j 的前缀后面
        if (needle.charAt(i) == needle.charAt(j)) {
            j++;
        }
        next[i] = j;
    }
    return next;
}
```

循环结束时始终满足：`next[i]` 是 `needle[0..i]` 的 LPS 长度。`j = next[j-1]` 不是从头猜测，而是沿“最长 → 次长 → 更短”的合法前后缀链回退。

---

## KMP 完整匹配
### 4.1 📌 一次完整失配与 LPS 回退

仍取：

```text
haystack = "ABABABC"
needle   = "ABABC"
next     = [0, 0, 1, 2, 0]
```

候选起点为 0，前 4 个字符匹配，随后在 `i=4, j=4` 失配：

```text
index       0  1  2  3  4  5  6
haystack    A  B  A  B  A  B  C
needle@0    A  B  A  B  C
             ✓  ✓  ✓  ✓  ✗
                         ↑ haystack[4]='A' != needle[4]='C'
```

已匹配串 `ABAB` 的 LPS 是 `AB`，所以执行 `j = next[3] = 2`。文本下标 `i=4` 不变，把模式串前缀 `AB` 对齐到刚才已匹配串的后缀 `AB`：

```text
index       0  1  2  3  4  5  6
haystack    A  B  A  B  A  B  C
needle@2          A  B  A  B  C
                   ╰复用╯  ↑
                           仍比较 haystack[4] 与 needle[2]
```

接下来 `haystack[4]='A' == needle[2]='A'`，然后继续匹配 `B`、`C`：

```text
index       0  1  2  3  4  5  6
haystack    A  B  A  B  A  B  C
needle@2          A  B  A  B  C
                   ✓  ✓  ✓  ✓  ✓

匹配起点 = i - j + 1 = 6 - 5 + 1 = 2
```

整个过程中，主串指针从未回到已经扫描过的位置。

### 4.2 Java 实现

```java
public int strStr(String haystack, String needle) {
    // 与 String.indexOf("") 的语义一致
    if (needle.isEmpty()) return 0;
    if (haystack.isEmpty() || needle.length() > haystack.length()) return -1;

    int[] next = buildNext(needle);
    int j = 0; // 已匹配的 needle 前缀长度

    for (int i = 0; i < haystack.length(); i++) {
        // 只回退模式串 j；同一个 haystack[i] 继续参与比较
        while (j > 0 && haystack.charAt(i) != needle.charAt(j)) {
            j = next[j - 1];
        }
        if (haystack.charAt(i) == needle.charAt(j)) {
            j++;
        }
        if (j == needle.length()) {
            return i - j + 1;
        }
    }
    return -1;
}
```

这里的 `i` 始终单调递增；`j` 表示“截至当前文本位置，能与模式串前缀匹配的最长后缀长度”。

---

## 时间与空间复杂度：为什么是 O(n+m)
设文本长度为 `n`，模式串长度为 `m`。

### 5.1 构建 next：O(m)

- 外层 `i` 从 1 增长到 `m-1`，共 `m-1` 轮。
- 每次字符匹配成功，`j` 最多增加 1；整个构建过程中，`j++` 至多发生 `m-1` 次。
- `while` 每执行一次，`j = next[j-1] < j`，至少下降 1。由于 `j` 从 0 开始且不会为负，累计回退次数不会超过此前累计增长次数，因此也是 O(m)。

所以，即使某一轮出现多次回退，所有轮次的回退总数仍是 O(m)，构建不是 O(m²)。

### 5.2 扫描文本：O(n)

- 主串指针 `i` 只从 0 走到 `n-1`，不会回退，共 n 轮。
- 每个文本字符至多让 `j` 增加 1，因此 `j++` 总次数不超过 n。
- 每次失配回退都会严格减小 `j`；累计回退次数受此前 `j` 的累计增长次数约束，也是 O(n)。

因此匹配阶段是 O(n)，总时间为：

```text
构建 next + 扫描文本 = O(m) + O(n) = O(n+m)
```

| 操作 | 时间复杂度 | 额外空间 |
|------|------------|----------|
| 构建 next 数组 | O(m) | O(m) |
| 匹配扫描 | O(n) | O(1)（不计 next） |
| 总计 | **O(n+m)** | **O(m)** |

---

## KMP vs 朴素匹配
| 维度 | 朴素匹配 | KMP |
|------|----------|-----|
| 最坏时间 | O(nm) | O(n+m) |
| 额外空间 | O(1) | O(m) |
| 文本指针失配后 | 回到下一候选起点 | 不回退 |
| 实现难度 | 简单 | 中等，必须统一 next 约定 |
| 适用 | 短文本、一次性查询 | 长文本、重复前缀明显、要求最坏线性时间 |

---

## 🛠️ 边界用例
本文实现约定输入对象非 `null`；空模式串遵循 Java `String.indexOf("") == 0` 的语义。

| 类别 | `haystack` | `needle` | 期望结果 | 要验证的点 |
|------|------------|----------|----------:|------------|
| 空文本 | `""` | `"A"` | -1 | 主循环不执行 |
| 空文本 + 空模式 | `""` | `""` | 0 | 必须先处理空模式，不能直接返回 -1 |
| 单字符 | `"A"` | `"A"` / `"B"` | 0 / -1 | `next=[0]`，命中与失配都不越界 |
| 重复字符 | `"AAAAA"` | `"AAA"` | 0 | 模式串 next 为 `[0,1,2]` |
| 极端重复前缀 | `"A" × 100000` | `"A" × 49999 + "B"` | -1 | 在模式尾部反复失配，仍保持 O(n+m) |

JUnit 风格的回归用例：

```java
assertEquals(-1, strStr("", "A"));
assertEquals(0, strStr("", ""));
assertEquals(0, strStr("A", "A"));
assertEquals(-1, strStr("A", "B"));
assertEquals(0, strStr("AAAAA", "AAA"));
assertArrayEquals(new int[]{0, 1, 2}, buildNext("AAA"));

// String.repeat 从 JDK 11 开始提供
String longText = "A".repeat(100_000);
String longNeedle = "A".repeat(49_999) + "B";
assertEquals(-1, strStr(longText, longNeedle));
```

极端用例中，朴素匹配会在大量候选起点接近模式尾部时才失败；KMP 用 LPS 链复用这些重复的 `A`，不会重新扫描主串。

---

## Java 标准库
```java
// Java String.indexOf() 使用朴素暴力匹配（双循环），不是 KMP 也不是 Boyer-Moore
// KMP 在长文本 + 有重复前缀场景更优，但 Java 标准库未采用
String haystack = "ABABCABAB";
String needle = "ABAB";
int idx = haystack.indexOf(needle); // 0
```

业务代码通常应优先使用 `String.indexOf()`，不要仅为“使用 KMP”而手写；需要解释最坏复杂度、处理流式字符或算法题明确要求时，再使用可控的 KMP 实现。标准库内部实现属于 JDK / JVM 的实现细节，调用方不应依赖其具体搜索算法。

---

## 🚨 实战陷阱 · 5 类
### ⚠️ 陷阱 1：把 LPS 长度约定与 `-1` 约定混用

KMP 常见两套 `next` 定义，它们都能工作，但数组含义和回退公式不同：

| 约定 | `ABAB` 的一个典型 next | 初值 | 失配回退 |
|------|------------------------|------|----------|
| 本文：LPS 长度 | `[0,0,1,2]` | `next[0]=0` | `j=next[j-1]` |
| 经典 `-1` 失配位置 | `[-1,0,0,1]` | `next[0]=-1` | `j=next[j]` |

```java
// ❌ 错：数组按 LPS 长度构造，却套用 -1 版本的回退公式
j = next[j];

// ✅ 对：本文从头到尾使用“LPS 长度”约定
j = next[j - 1];
```

看到 `next[0]` 时先确认约定：是 0 还是 -1。不要背一份数组、套另一份代码。

### ⚠️ 陷阱 2：混淆主串 `i` 与模式串 `j`

```java
// ❌ 错：失配后回退 i，退化成朴素匹配
// i = i - j + 1;
// j = 0;

// ✅ 对：i 始终向前，只沿模式串的 LPS 链回退 j
while (j > 0 && haystack.charAt(i) != needle.charAt(j)) {
    j = next[j - 1];
}
```

`j == needle.length()` 时，当前字符下标是 `i`，起点应为 `i-j+1`，不是 `i-j`。

### ⚠️ 陷阱 3：把“子串部分匹配”当成“严格匹配”

```java
strStr("concatenate", "cat"); // 3：KMP 找的是连续子串
```

- 要求整个字符串相等：直接用 `haystack.equals(needle)`。
- 要求完整单词匹配：命中后还要检查左右边界或先分词。
- 要求忽略大小写、空格或 Unicode 规范化：先明确并执行预处理；KMP 本身只比较字符序列。

### ⚠️ 陷阱 4：认为字符串哈希可以无条件替代 KMP

| 维度 | KMP | 字符串哈希 / Rabin-Karp |
|------|-----|-------------------------|
| 正确性 | 字符逐一确认，无碰撞 | 哈希相等仍可能碰撞 |
| 时间保证 | 最坏 O(n+m) | 通常 O(n+m)，碰撞并逐窗复核时最坏 O(nm) |
| 额外空间 | O(m) | O(1) 滚动状态，或 O(n) 前缀哈希 |
| 更适合 | 单模式、要求确定性最坏界 | 大量子串相等查询、多个等长模式的哈希筛选 |

需要严格正确且只查一个模式时，KMP 的保证更直接；前缀哈希适合“同一文本上大量区间比较”，但要设计碰撞处理。

### ⚠️ 陷阱 5：rolling hash 只比较哈希值，不复核字符

长度为 `m` 的窗口右移一格时，常见多项式滚动公式是：

```text
H_next = (((H - old × base^(m-1)) mod mod + mod) mod mod
          × base + new) mod mod
```

实战要同时处理三点：

1. Java 用 `long` 保存乘法中间值，避免 `int` 提前溢出。
2. 减去旧字符后先加 `mod` 再取模，避免负余数。
3. 哈希相等后再逐字符确认；双哈希只能降低碰撞概率，不能把概率性结论变成严格证明。

如果不能接受碰撞和最坏 O(nm) 复核成本，直接选 KMP。

---

## 一句话总结
> **KMP = LPS 长度数组 + 主串指针不回退。本文统一 `next[i] = needle[0..i]` 的最长相等真前后缀长度，失配执行 `j = next[j-1]`；构建 O(m)、匹配 O(n)、空间 O(m)。单模式用 KMP，多模式转向 AC 自动机。**

---

← [返回: algorithms 总目录](../README.md) · [字符串算法专题](README.md) · 系列：上一章 [01-trie-data-structure](01-trie-data-structure.md) · 下一章 [03-ac-automaton](03-ac-automaton.md)
