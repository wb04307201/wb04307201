<!--
module:
  parent: computer-basics
  slug: algorithms/search/branch-and-bound
  type: article
  category: 主模块子文章
  summary: 分支界限 Branch and Bound 算法
-->

# 分支界限（Branch and Bound）

> ⬅️ [返回 02 算法](../../README.md) | [返回 02.computer-basics](../../../README.md)

> **一句话定位**：分支界限 = **分支 + 剪枝**的精确求解方法，**用上界/下界剪掉不可能最优的分支**。1960 年 Land 和 Doig 提出，**整数规划 / 旅行商问题（TSP）** 的标准精确解法。

---

## 🎯 一句话理解

```text
1. 分支（Branch）：把问题分成子问题
2. 界限（Bound）：计算子问题的上/下界
3. 剪枝（Bound）：如果界 < 当前最优解，整个分支剪掉
```

**核心**：用"数学下界"提前排除不可能最优的分支，避免穷举。

---

## 📐 旅行商问题（TSP）示例

```text
问题：5 个城市，从 A 出发，经过所有城市一次回到 A，最短路径

暴力：5! / 2 = 60 种
分支界限：通常 < 10 次搜索即可
```

### 流程

```text
1. 从 A 出发，候选分支：A→B, A→C, A→D, A→E
2. 计算每个分支的下界（贪心近似）
3. 选下界最小的先探索
4. 如果某分支下界 > 当前最优解，剪掉
```

---

## 🛠️ Python 实现（TSP）

```python
import numpy as np
from itertools import permutations

def tsp_branch_bound(dist_matrix):
    n = dist_matrix.shape[0]
    best_path = None
    best_cost = float('inf')
    
    def branch(path, visited, current_cost, lower_bound):
        nonlocal best_path, best_cost
        # 剪枝：如果当前下界 > 最优解
        if current_cost + lower_bound >= best_cost:
            return
        
        if len(path) == n:
            # 完成路径
            total = current_cost + dist_matrix[path[-1], path[0]]
            if total < best_cost:
                best_cost = total
                best_path = path
            return
        
        # 分支：尝试每个未访问城市
        for next_city in range(n):
            if next_city not in visited:
                new_path = path + [next_city]
                new_visited = visited | {next_city}
                new_cost = current_cost + dist_matrix[path[-1], next_city]
                # 简化下界：剩余城市的最小生成树
                lb = min(dist_matrix[next_city, j] for j in range(n) if j not in new_visited)
                branch(new_path, new_visited, new_cost, lb)
    
    branch([0], {0}, 0, 0)
    return best_path, best_cost
```

---

## 📊 4 大剪枝策略

| 策略 | 含义 | 效果 |
|------|------|------|
| **上界剪枝** | 分支上界 < 当前最优 | 排除 |
| **下界剪枝** | 分支下界 > 当前最优 | 排除 |
| **可行性剪枝** | 不可行解 | 排除 |
| **最优性剪枝** | 已找到最优 | 停止 |

---

## 🛠️ 4 大应用场景

| 场景 | 含义 | 状态 |
|------|------|------|
| **整数规划** | 0-1 变量 | 主流 |
| **TSP** | 旅行商问题 | 主流 |
| **调度** | 任务调度 | 主流 |
| **装箱** | 0-1 背包 | 主流 |

---

## 🆚 BFS / DFS / A* 对比

| 算法 | 数据结构 | 完备性 | 最优性 | 适用 |
|------|---------|--------|--------|------|
| **BFS** | 队列 | ✅ | ✅（均匀代价）| 最短路径 |
| **DFS** | 栈 | ❌（可能无限）| ❌ | 任意解 |
| **A*** | 优先队列 | ✅ | ✅（启发式）| 启发式搜索 |
| **Branch & Bound** | 优先队列 | ✅ | ✅ | 组合优化 |

**分支界限** = BFS + 智能剪枝。

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 分支界限一定快 | ✅ 最坏情况仍是指数 |
| ❌ 剪枝越多越好 | ✅ 太多剪枝反误判 |
| ❌ 只能解小问题 | ✅ TSP 100+ 城市也能解（小时级）|
| ❌ 下界计算越紧越好 | ✅ 计算成本 vs 紧度需权衡 |

---

## 🔗 兄弟章节

- **本目录**：[A* 搜索](../) / [动态规划](../) / [回溯](../)
- **02 同级**：[K-means](../../clustering/k-means/README.md) / [PCA](../../dimensionality-reduction/pca/README.md)
- **13.split-hairs**：算法面试题

---

← [返回: 搜索算法](../README.md)