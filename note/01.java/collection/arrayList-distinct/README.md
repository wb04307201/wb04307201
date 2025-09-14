# ArrayList去重

## 1. 内存充足场景：哈希集合（最优时间复杂度）
**原理**：利用`HashSet`的O(1)查找特性，遍历时自动去重。  
**时间复杂度**：O(n)  
**空间复杂度**：O(n)（需存储所有不重复元素）  
**适用场景**：内存足够（一亿条数据若为Integer，约需4GB内存；若为自定义对象，需考虑对象大小）。

```java
import java.util.*;

public class Deduplication {
    public static void main(String[] args) {
        // 模拟一亿条数据的ArrayList（实际场景替换为真实数据）
        List<Integer> list = new ArrayList<>(100_000_000);
        // 填充数据（此处省略填充逻辑）

        // 使用HashSet去重
        List<Integer> deduplicated = new ArrayList<>(new HashSet<>(list));
    }
}
```

## 2. 内存受限场景：排序后遍历（最优空间复杂度）
**原理**：先排序（相同元素聚集），再遍历跳过重复项。  
**时间复杂度**：O(n log n)（排序耗时）  
**空间复杂度**：O(1)（原地去重，仅需常数级额外空间）  
**适用场景**：内存不足，但可接受排序开销。

```java
import java.util.*;

public class Deduplication {
    public static void main(String[] args) {
        List<Integer> list = new ArrayList<>(100_000_000);
        // 填充数据

        // 排序（Java排序对ArrayList优化较好）
        Collections.sort(list);

        // 遍历去重
        int writeIndex = 0;
        for (int i = 1; i < list.size(); i++) {
            if (!list.get(writeIndex).equals(list.get(i))) {
                list.set(++writeIndex, list.get(i));
            }
        }
        // 截断列表至去重后大小
        list.subList(writeIndex + 1, list.size()).clear();
    }
}
```

## 3. 海量数据场景：分块+外部排序（突破内存限制）
**原理**：将数据分块写入磁盘文件，对每块排序后归并去重。  
**适用场景**：数据量远超内存容量（如1亿条字符串，每条1KB，总大小约95GB）。  
**工具推荐**：使用`Files`类处理磁盘文件，结合归并排序思想。

```java
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class ExternalDeduplication {
    public static void main(String[] args) throws IOException {
        List<String> bigList = new ArrayList<>(); // 实际为1亿条数据
        // 分块写入临时文件
        List<File> tempFiles = splitAndSort(bigList, 1_000_000); // 每块100万条
        // 归并去重
        List<String> result = mergeAndDeduplicate(tempFiles);
    }

    static List<File> splitAndSort(List<String> data, int chunkSize) throws IOException {
        List<File> tempFiles = new ArrayList<>();
        for (int i = 0; i < data.size(); i += chunkSize) {
            List<String> chunk = new ArrayList<>(data.subList(i, Math.min(i + chunkSize, data.size())));
            Collections.sort(chunk);
            File tempFile = Files.createTempFile("chunk", ".txt").toFile();
            Files.write(tempFile.toPath(), chunk);
            tempFiles.add(tempFile);
        }
        return tempFiles;
    }

    static List<String> mergeAndDeduplicate(List<File> files) throws IOException {
        List<BufferedReader> readers = new ArrayList<>();
        for (File file : files) {
            readers.add(new BufferedReader(new FileReader(file)));
        }
        // 归并逻辑（需实现多路归并算法，此处简化）
        // ...
        return new ArrayList<>(); // 返回归并去重结果
    }
}
```

## 4. 特定数据类型优化
- **数值型数据**：使用`BitSet`（针对整型）或`RoaringBitmap`压缩存储。
- **字符串**：若存在前缀/后缀规律，可用`Trie`树压缩存储。
- **自定义对象**：重写`hashCode()`和`equals()`，确保哈希冲突最小化。

## 5. 并行流处理（Java 8+）
**原理**：利用`parallelStream().distinct()`并行去重。  
**注意**：并行流底层使用`ForkJoinPool`，对CPU多核利用率高，但内存占用增加。

```java
List<Integer> deduplicated = list.parallelStream()
                                 .distinct()
                                 .collect(Collectors.toList());
```

## 性能对比表
| 方法                | 时间复杂度 | 空间复杂度 | 内存需求 | 适用场景               |
|---------------------|-----------|-----------|---------|-----------------------|
| HashSet去重          | O(n)      | O(n)      | 高      | 内存充足，追求速度     |
| 排序后遍历           | O(n log n)| O(1)      | 低      | 内存不足，可接受排序耗时 |
| 分块+外部排序        | O(n log n)| O(1)      | 极低    | 数据量远超内存容量     |
| 并行流去重           | O(n)      | O(n)      | 较高    | 多核CPU，中等内存     |

## **关键建议**
1. **优先测试小数据**：在完整数据集上运行前，先用1万条数据验证逻辑正确性。
2. **监控内存与GC**：使用JVM监控工具（如VisualVM）观察内存占用和垃圾回收情况。
3. **避免对象膨胀**：确保自定义对象的`hashCode()`和`equals()`高效实现，避免字符串拼接等耗时操作。
4. **考虑数据库方案**：若数据源自数据库，直接用SQL的`SELECT DISTINCT`可能更高效。

根据具体场景选择合适方案，通常**内存充足选HashSet，内存紧张选排序遍历**。对于超大数据，需结合磁盘存储和分治思想处理。