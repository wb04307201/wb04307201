<!--
module:
  parent: algorithms/string-algorithms
  slug: algorithms/string-algorithms/02-kmp
  type: topic
  category: KMP
  summary: KMP 算法 —— next 数组（部分匹配表）+ Java 实现 + strstr
-->

# KMP 算法 · 部分匹配表（LPS）

> **一句话**：KMP = "已匹配信息不浪费"——构造 next 数组（最长前缀后缀 LPS），匹配失败不后退指针，单次扫描 O(n+m)。朴素算法 O(n × m)。

← [返回: string-algorithms 总目录](../README.md)

---

## 1. 朴素算法的问题

```
haystack = "ABABCABAB"
needle   = "ABAB"

朴素：i=4 时发现不匹配，**回退到 i=1 重新比对**
浪费前面 ABAB 已匹配的信息
```

---

## 2. KMP 核心思想

**关键洞察**：匹配失败时，**needle 指针不一定要回到 0**——可以利用**已匹配的部分**跳过不可能匹配的位置。

```
needle = "ABAB"
已匹配 "AB"，剩下的 "AB" 是 needle 的前缀
→ 移动 needle，让前缀对齐到后缀，从 'A' 继续比对
```

这就是 **next 数组**（部分匹配表，LPS / Longest Proper Prefix which is also Suffix）。

---

## 3. next 数组详解

### 3.1 定义

```
next[i] = needle[0..i-1] 的最长前后缀长度

needle = "ABAB"
next[0] = 0
next[1] = 0 (A 的前后缀长度 = 0)
next[2] = 1 (AB 的最长前后缀 = "A")
next[3] = 2 (ABA 的最长前后缀 = "AB")
```

### 3.2 构造 next 数组

```java
public int[] buildNext(String needle) {
    int[] next = new int[needle.length()];
    int j = 0;  // j = 当前最长前后缀长度
    for (int i = 1; i < needle.length(); i++) {
        while (j > 0 && needle.charAt(i) != needle.charAt(j)) {
            j = next[j - 1];  // 回退（递归求 LPS）
        }
        if (needle.charAt(i) == needle.charAt(j)) {
            j++;
        }
        next[i] = j;
    }
    return next;
}
```

**关键**：`j = next[j - 1]` 是 KMP 的精髓——**回退到上一个可能的 LPS**。

---

## 4. KMP 完整实现

```java
public int strStr(String haystack, String needle) {
    if (needle.isEmpty()) return 0;
    int[] next = buildNext(needle);
    int j = 0;
    for (int i = 0; i < haystack.length(); i++) {
        while (j > 0 && haystack.charAt(i) != needle.charAt(j)) {
            j = next[j - 1];
        }
        if (haystack.charAt(i) == needle.charAt(j)) {
            j++;
        }
        if (j == needle.length()) {
            return i - j + 1;  // 找到匹配
        }
    }
    return -1;
}
```

---

## 5. 时间复杂度

| 操作 | 复杂度 |
|------|--------|
| 构建 next 数组 | O(m) |
| 匹配扫描 | O(n) |
| 总 | **O(n + m)** |

朴素算法：O(n × m)

---

## 6. KMP vs 朴素

| 维度 | 朴素 | KMP |
|------|------|-----|
| 时间 | O(n × m) | O(n + m) |
| 空间 | O(1) | O(m) |
| 实现难度 | 简单 | 中等 |
| 适用 | 短文本 / 单次 | 长文本 / 多次 |

---

## 7. Java 标准库

```java
// Java String.indexOf() 内部实现就是 KMP（简化的 Boyer-Moore）
String haystack = "ABABCABAB";
String needle = "ABAB";
int idx = haystack.indexOf(needle);  // = 0
```

---

## 8. 反模式 · 3 个常见错

### ⚠️ 反模式 1：next 数组越界

```java
// 错：j = next[j - 1] 当 j=0 时越界
while (j > 0 && ...);  // 必须先检查 j > 0
```

### ⚠️ 反模式 2：next 数组含义记错

```
next[i] 是 needle[0..i-1] 的最长前后缀长度 —— 注意是 i-1！
不是 needle[0..i] 的最长前后缀长度
```

### ⚠️ 反模式 3：忘记边界（needle 为空）

```java
// Java indexOf("") = 0，KMP 必须显式处理
if (needle.isEmpty()) return 0;
```

---

## 9. 一句话总结

> **KMP = 部分匹配表 next 数组 + 失配不后退指针 = O(n+m)。核心是 `j = next[j - 1]` 递归回退。单 needle 匹配首选；多 needle 用 AC 自动机。**

---

← [返回: string-algorithms 总目录](../README.md) · 上一章：[01-trie-data-structure](01-trie-data-structure.md) · 下一章：[03-ac-automaton](03-ac-automaton.md)
