<!--
question:
  id: 02.computer-basics-greedy-algorithms
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 算法设计 + 面试深挖
  tags: [02.computer-basics, 贪心算法, greedy, 算法设计, Dijkstra, Huffman, 动态规划对比]
-->

# 贪心算法深度剖析：什么时候局部最优等于全局最优？

> 一句话定位：贪心算法是面试算法设计的**核心策略之一**——关键不是"会写贪心"，而是能**证明贪心选择性质**、**区分贪心 vs DP**、**识别贪心失效场景**。完整深度见 [主模块贪心算法](../../../02.computer-basics/02-algorithms/greedy-algorithms/README.md)。

> **系列定位**：经典 CS 面试题（字节 / 阿里 / 美团 / Google / Meta 高频）。考察的不是"贪心怎么写"，而是 **贪心性质证明** + **贪心 vs DP 决策** + **5 大失效反模式** + **工业级应用**。

---

## 引子：面试现场

```text
场景：某大厂算法面——
面试官："给你一个面值数组 coins = [1, 3, 4]，找零金额 6，用贪心怎么找？"
候选人："每次选最大面值 → 4 + 1 + 1 = 3 枚"
面试官："最优解呢？"
候选人："3 + 3 = 2 枚……贪心错了？"
面试官："对。那什么条件下贪心一定正确？"
```

**决策现场**：
1. 普通候选人：能写出贪心代码，但**不知道什么时候会错**
2. 优秀候选人：能用**交换论证**证明贪心选择性质
3. 资深候选人：能从**拟阵理论**解释为什么 MST 贪心正确，背包问题贪心错误

---

## 一、核心原理（贪心的 2 个必要条件）

### 1.1 贪心选择性质（Greedy Choice Property）

- 全局最优解 = 局部最优选择的序列
- 关键：选了就不回头（区别于 DP 的"考虑所有子问题"）
- 证明方法：**交换论证**（Exchange Argument）——假设最优解不以贪心选择开始，交换后不更差

### 1.2 最优子结构（Optimal Substructure）

- 问题最优解包含子问题最优解
- 贪心和 DP 都需要，但贪心还需额外证明"贪心选择性质"
- 反例：最长简单路径无最优子结构（子路径可能共享顶点）

### 1.3 快速判断决策树

```text
贪心适用？
├── 问题有最优子结构？ → 否 → 不适用
├── 局部最优 = 全局最优？（交换论证）→ 否 → 用 DP
└── 贪心后子问题独立？ → 是 → 用贪心
```

---

## 二、经典题目 5 道（面试高频）

### 题目 1：区间调度（LeetCode 435 / 56）

**贪心策略**：按结束时间升序排序，依次选择不重叠区间

```java
Arrays.sort(intervals, (a, b) -> a[1] - b[1]);
int end = Integer.MIN_VALUE, count = 0;
for (int[] iv : intervals) {
    if (iv[0] >= end) { count++; end = iv[1]; }
}
```

- 复杂度：O(n log n)（排序主导）
- ⚠️ 面试陷阱：**别按开始时间排序**——开始早不代表结束早，会挤占后续空间

### 题目 2：跳跃游戏（LeetCode 55）

**贪心策略**：维护当前最远可达位置，逐步扩展

```java
int farthest = 0;
for (int i = 0; i < nums.length; i++) {
    if (i > farthest) return false;
    farthest = Math.max(farthest, i + nums[i]);
}
return true;
```

- 复杂度：O(n)
- ⚠️ 面试陷阱：**别用 DP O(n²)**——贪心一次遍历即可

### 题目 3：分发饼干（LeetCode 455）

**贪心策略**：双指针 + 排序，小饼干优先满足小胃口

```java
Arrays.sort(g); Arrays.sort(s);
int i = 0, j = 0;
while (i < g.length && j < s.length) {
    if (s[j] >= g[i]) i++;
    j++;
}
return i;
```

- 复杂度：O(n log n)
- ⚠️ 面试陷阱：**别用回溯**——贪心 + 排序就是最优

### 题目 4：任务调度器（LeetCode 621）

**贪心策略**：按频次降序，用最多任务"建框架"，其余任务填空

```java
int[] count = new int[26];
for (char c : tasks) count[c - 'A']++;
int maxFreq = Arrays.stream(count).max().getAsInt();
int maxCount = (int) Arrays.stream(count).filter(c -> c == maxFreq).count();
return Math.max(tasks.length, (maxFreq - 1) * (n + 1) + maxCount);
```

- 复杂度：O(n)
- ⚠️ 面试陷阱：**公式推导易错**——要分清"有空闲"和"无空闲（任务填满）"两种情况

### 题目 5：加油站（LeetCode 134）

**贪心策略**：累计油量，若某点累计为负则重置起点

```java
int totalSum = 0, curSum = 0, start = 0;
for (int i = 0; i < gas.length; i++) {
    int diff = gas[i] - cost[i];
    totalSum += diff; curSum += diff;
    if (curSum < 0) { start = i + 1; curSum = 0; }
}
return totalSum >= 0 ? start : -1;
```

- 复杂度：O(n)，一遍遍历
- ⚠️ 面试陷阱：**两遍遍历 vs 一遍**——一遍就够了，totalSum 判断可行性 + curSum 找起点

---

## 三、常见陷阱（5 大反模式）

### 陷阱 1：0-1 背包用贪心

- **反例**：items=[(v=60,w=10),(v=100,w=20),(v=120,w=30)] capacity=50
- 贪心按单位价值：选 60/10 + 100/20 → 价值 160，重量 30，剩余 20 装不下 w=30
- 最优：100 + 120 = 220（w=50）
- **真相**：0-1 背包无贪心选择性质 → **DP 才是正解**（O(nW)）

### 陷阱 2：特定面值找零

- **反例**：coins=[1,3,4] amount=6
- 贪心：4+1+1=3 枚
- 最优：3+3=2 枚
- **真相**：只有"规范面值系统"（如 1/5/10/25）贪心才正确 → 一般情况用 **DP**

### 陷阱 3：TSP 最近邻

- 贪心：每次去最近的未访问城市 → 最后被迫走很远的回程
- 可能与最优解差距达 O(n!) 倍
- **真相**：TSP 是 NP-hard → 精确解用 DP（Held-Karp O(n²2ⁿ)），大规模用近似算法

### 陷阱 4：混淆"贪心正确"和"贪心直觉上对"

- 区间着色：按开始时间排 vs 按结束时间排 → 只有后者正确
- Dijkstra 不能有负权边 → 直觉"最短边优先"在负权下失效
- **真相**：贪心必须**严格证明**（交换论证 / 拟阵），不能凭直觉

### 陷阱 5：忽略排序的稳定性

- 多个相同结束时间的区间 → 排序不稳定可能导致漏选
- 同频次任务 → 调度顺序影响最终结果
- **真相**：面试中要主动提"排序相同时的二级排序策略"

---

## 四、贪心 vs DP 速查表

| 维度 | 贪心 | DP |
|------|------|----|
| 选择方式 | 局部最优，不回头 | 枚举子问题，记忆化 / 递推 |
| 正确性证明 | 需证明贪心选择性质（交换论证） | 自动（状态转移方程保证） |
| 时间复杂度 | 通常 O(n log n)（排序主导） | O(n²) 或更高 |
| 空间复杂度 | O(1) 或 O(n)（排序空间） | O(n²) 常见 |
| 经典适用 | 区间调度 / Huffman / Dijkstra / MST | 0-1 背包 / LCS / 编辑距离 |
| 面试考点 | "为什么贪心正确？能举个反例吗？" | "状态转移方程是什么？" |
| 代码量 | 通常 5-15 行 | 通常 15-40 行 |

---

## 五、面试话术（90 秒版本）

> "贪心算法的核心思想是：每一步都做局部最优选择，期望最终结果是全局最优。但它不是万能的——要使用贪心，问题必须同时满足两个条件：**最优子结构**（全局最优解包含子问题最优解）和**贪心选择性质**（局部最优选择能导向全局最优）。
>
> 证明贪心正确性最常用的方法是**交换论证**：假设存在一个最优解不以贪心选择开始，我们把它的第一个选择替换成贪心选择，证明新解不会比原解更差。比如区间调度问题，按结束时间排序后选第一个结束的区间，交换论证可以证明这不会减少可选区间数。
>
> 经典贪心问题包括区间调度、Dijkstra 最短路径、Huffman 编码和 Kruskal MST。而 0-1 背包和 TSP 是典型的贪心失效场景——前者因为物品不可分割，贪心按单位价值选会漏掉组合更优的方案；后者因为最后一步的回程代价无法被局部决策覆盖。
>
> 面试中遇到一个新问题，我会先判断：能不能用交换论证证明贪心正确？如果能，贪心通常比 DP 更高效——时间从 O(n²) 降到 O(n log n)。如果不能，就退回 DP。"

---

## 六、相关章节

- 主模块深度：[`02-algorithms/greedy-algorithms`](../../../02.computer-basics/02-algorithms/greedy-algorithms/README.md) —— 完整原理 + 6 大经典问题 + 拟阵理论
- 字符串算法：[`string-algorithms`](../../../02.computer-basics/02-algorithms/string-algorithms/README.md) —— Trie / KMP / AC 自动机
- 复杂度分析：[`complexity`](../../../02.computer-basics/02-algorithms/complexity/README.md) —— 时间 / 空间复杂度
- 同栏目：[`sensitive-word-filter`](../sensitive-word-filter/README.md) —— AC 自动机面试题
- 返回：[`02.computer-basics`](../README.md) —— 计算机基础面试题目录

---

> 📅 2026-07-14 · 咬文嚼字 · 贪心算法 · ⭐⭐⭐⭐

← [返回计算机基础面试题](../README.md)
