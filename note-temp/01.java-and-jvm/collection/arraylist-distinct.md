<!--
module:
  parent: java
  slug: java/collection/arraylist-distinct
  type: article
  category: 主模块子文章
  summary: List 去重方案对比：HashSet / 排序遍历 / 外部排序 / 并行流（split-hairs 迁出）
-->

# List 去重（split-hairs 视角）

> **定位**：List 去重方案对比：HashSet / 排序遍历 / 外部排序 / 并行流 的核心原理、实现与最佳实践。
>
> 本节由 `13.split-hairs/01.java/arrayList-distinct/` 迁出，按数据规模递进：**内存充足 → 内存紧张 → 海量数据**。ArrayList 基础原理见 [ArrayList/README.md](./ArrayList/README.md)。

## 引言：一亿条数据怎么去重？

```java
// 方式 1：Stream distinct（最简洁但未必最快）
List<Integer> result = list.stream().distinct().collect(Collectors.toList());

// 方式 2：HashSet（最快，但内存翻倍）
List<Integer> result = new ArrayList<>(new HashSet<>(list));

// 方式 3：排序后去重（省内存，但改变了顺序）
list.sort(null);
// 然后遍历去重...
```

数据量小时随便写，数据量大时必须考虑 **时间复杂度 + 空间复杂度 + 是否保序** 三个维度。

---

## 方案对比速查表

| 方法 | 时间复杂度 | 空间复杂度 | 是否保序 | 适用场景 |
|------|:---------:|:---------:|:------:|---------|
| HashSet 去重 | O(n) | O(n) | ❌ | 内存充足、追求速度（百万级默认方案） |
| 排序后遍历 | O(n log n) | O(1) | ❌ | 内存紧张、可接受排序开销 |
| 分块+外部排序 | O(n log n) | O(1) | ❌ | 数据量远超内存（十亿级） |
| `parallelStream().distinct()` | O(n) | O(n) | ❌ | 多核 CPU、中等内存 |

---

## 一、内存充足场景：HashSet（最优时间复杂度）

**原理**：利用 `HashSet` 的 O(1) 查找特性，遍历时自动去重。

```java
import java.util.*;

public class Deduplication {
    public static void main(String[] args) {
        List<Integer> list = new ArrayList<>(100_000_000);
        // 填充数据...

        // HashSet 去重：O(n) 时间 + O(n) 空间
        List<Integer> deduplicated = new ArrayList<>(new HashSet<>(list));
    }
}
```

⚠️ **内存占用估算**：1 亿条 Integer ≈ 4GB（对象头 16 字节 + int 4 字节 + 引用 8 字节 + padding）。自定义对象需考虑字段大小。

---

## 二、内存受限场景：排序后遍历（最优空间复杂度）

**原理**：先排序（相同元素聚集），再遍历跳过重复项。

```java
import java.util.*;

public class Deduplication {
    public static void main(String[] args) {
        List<Integer> list = new ArrayList<>(100_000_000);

        // 1. 排序（Java 对 ArrayList 排序优化较好）
        Collections.sort(list);

        // 2. 原地遍历去重（双指针写法）
        int writeIndex = 0;
        for (int i = 1; i < list.size(); i++) {
            if (!list.get(writeIndex).equals(list.get(i))) {
                list.set(++writeIndex, list.get(i));
            }
        }
        // 3. 截断列表至去重后大小
        list.subList(writeIndex + 1, list.size()).clear();
    }
}
```

**复杂度**：时间 O(n log n)（排序）+ 空间 O(1)（原地去重）。

---

## 三、海量数据场景：分块 + 外部排序（突破内存限制）

**原理**：将数据分块写入磁盘，对每块排序后归并去重。

```java
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class ExternalDeduplication {
    static List<File> splitAndSort(List<String> data, int chunkSize) throws IOException {
        List<File> tempFiles = new ArrayList<>();
        for (int i = 0; i < data.size(); i += chunkSize) {
            // 每块独立排序 + 写入磁盘
            List<String> chunk = new ArrayList<>(data.subList(i, Math.min(i + chunkSize, data.size())));
            Collections.sort(chunk);
            File tempFile = Files.createTempFile("chunk", ".txt").toFile();
            Files.write(tempFile.toPath(), chunk);
            tempFiles.add(tempFile);
        }
        return tempFiles;
    }
}
```

**适用**：数据量远超内存容量（如 1 亿条字符串，每条 1KB，总大小约 95GB）。

---

## 四、并行流处理（Java 8+）

```java
List<Integer> deduplicated = list.parallelStream()
                                 .distinct()
                                 .collect(Collectors.toList());
```

⚠️ **底层使用 ForkJoinPool.commonPool()**，默认并行度 = CPU 核数 - 1。共享状态/阻塞 IO 操作需谨慎。

---

## 五、特定数据类型优化

| 数据类型 | 推荐方案 | 优势 |
|---------|---------|------|
| 数值（int/long） | `BitSet` 或 `RoaringBitmap` | 位图压缩，内存极省 |
| 字符串（前缀规律） | `Trie` 树 | 前缀压缩 |
| 自定义对象 | 重写 `hashCode` + `equals` | 减少哈希冲突 |

---

## 选型决策树

```text
数据量多大？
├── < 100 万
│   ├── 要保序 → Stream.distinct()
│   └── 追求极快 → HashSet
├── 100 万 ~ 1 亿
│   ├── 内存足够 → HashSet（首选）
│   └── 内存紧张 → 排序遍历
└── > 1 亿（远超内存）
    └── 分块 + 外部排序（MapReduce 思路）
```

---

## 30 秒面试话术

> "List 去重要看**数据规模**：默认用 `HashSet`（O(n) 时间 + O(n) 空间，最快）；内存紧张用排序 + 双指针原地去重（O(n log n) + O(1)）；数据量超过内存用外部排序（分块 + 归并）。**Stream.distinct() 底层就是 HashSet**，但包装了一层 Stream 开销。如果涉及自定义对象，必须正确重写 `hashCode` 和 `equals` 否则 `HashSet` 会把相同对象当不同对象处理。"

## 关键建议

1. **优先小数据测试**：完整数据集运行前，先用 1 万条数据验证逻辑正确性
2. **监控内存与 GC**：用 VisualVM / JFR 观察内存峰值与 GC 频率
3. **避免对象膨胀**：自定义对象 `hashCode`/`equals` 用 `Objects.hash()` 模板，不要字符串拼接
4. **优先 SQL 方案**：若数据源自数据库，直接 `SELECT DISTINCT` 性能通常远超 JVM 内去重

---

## 相关章节

- [集合框架总览](./README.md) — 集合体系、选型决策树
- [ArrayList 源码分析](./ArrayList/README.md) — 扩容、fail-fast、最佳实践
- [HashMap 大数据插入](./hashmap-performance.md) — 类似的"大数据 + 性能"案例
- [split-hairs/hashmap-resizing](../../../note/13.split-hairs/01.java/hashmap-resizing/README.md) — HashMap 扩容原理

← [返回 集合框架](./README.md)
