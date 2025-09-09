# TreeMap

**TreeMap 是 Java 中基于红黑树实现的有序映射结构，其核心特性、实现原理、使用场景及与其他 Map 的对比分析如下**：

## 一、核心特性
1. **有序性**
    - **自然排序**：默认按键的自然顺序（如 `Integer` 升序、`String` 字母顺序）排列。
    - **自定义排序**：通过构造函数传入 `Comparator` 实现灵活排序（如降序、复合字段排序）。
    - **遍历顺序**：迭代时按键的顺序输出，无需额外排序操作。

2. **时间复杂度**
    - **插入/删除/查找**：基于红黑树的自平衡特性，所有操作时间复杂度稳定为 **O(log n)**，优于无序场景下的 `HashMap`（O(1) 平均，但最坏情况退化为 O(n)）。

3. **线程安全**
    - **非同步**：`TreeMap` 本身非线程安全，多线程环境下需通过 `Collections.synchronizedSortedMap` 包装或使用 `ConcurrentSkipListMap`（跳表实现，线程安全）。

4. **键值约束**
    - **键不可为 `null`**：若键未实现 `Comparable` 接口且未提供 `Comparator`，或尝试插入 `null` 键，会抛出 `NullPointerException`。
    - **值可为 `null`**：允许值为 `null`。

## 二、实现原理
1. **底层结构**
    - **红黑树**：一种自平衡二叉搜索树，通过以下规则保证平衡：
        - 根节点为黑色。
        - 红色节点的子节点必须为黑色（避免连续红色节点）。
        - 从任意节点到其叶子节点的路径包含相同数量的黑色节点（黑色平衡）。
    - **节点结构**：每个节点包含键、值、颜色、左右子节点及父节点引用。

2. **关键操作**
    - **插入**：按二叉搜索树规则插入新节点，随后通过旋转和变色调整平衡（如左旋、右旋、重新着色）。
    - **删除**：定位目标节点后，通过替换和平衡调整维持红黑树性质。
    - **查找**：从根节点开始，按比较规则（自然顺序或 `Comparator`）递归遍历，时间复杂度 O(log n)。

3. **导航方法**
    - **范围查询**：`subMap(K fromKey, K toKey)` 返回指定键范围内的子映射。
    - **边界查询**：`floorKey(K key)` 返回小于等于给定键的最大键，`ceilingKey(K key)` 返回大于等于给定键的最小键。
    - **极值获取**：`firstKey()` 和 `lastKey()` 分别返回最小和最大键。

## 三、使用场景
1. **需要有序遍历的场景**
    - 生成按字母顺序排列的索引（如字典）、按时间排序的日志条目。
    - 示例：
      ```java
      TreeMap<String, Integer> sortedMap = new TreeMap<>();
      sortedMap.put("apple", 1);
      sortedMap.put("banana", 2);
      System.out.println(sortedMap); // 输出: {apple=1, banana=2}
      ```

2. **范围查询需求**
    - 快速获取某个区间内的键值对（如时间区间查询、成绩分段统计）。
    - 示例：
      ```java
      TreeMap<Integer, String> treeMap = new TreeMap<>();
      treeMap.put(1, "One");
      treeMap.put(3, "Three");
      treeMap.put(5, "Five");
      SortedMap<Integer, String> subMap = treeMap.subMap(3, 5); // 包含 3，不包含 5
      System.out.println(subMap); // 输出: {3=Three}
      ```

3. **自定义排序逻辑**
    - 通过 `Comparator` 实现复杂排序规则（如多字段排序、降序排序）。
    - 示例（按学生年龄降序，年龄相同按姓名升序）：
      ```java
      TreeMap<Student, Integer> studentMap = new TreeMap<>((s1, s2) -> {
          if (s1.getAge() == s2.getAge()) {
              return s1.getName().compareTo(s2.getName());
          }
          return s2.getAge() - s1.getAge();
      });
      ```

4. **实时排序监控**
    - 维护动态数据的有序状态（如实时排行榜、监控指标排序）。

## 四、与其他 Map 的对比
| **特性**    | **TreeMap**  | **HashMap**           | **LinkedHashMap** | **ConcurrentSkipListMap** |
|-----------|--------------|-----------------------|-------------------|---------------------------|
| **底层结构**  | 红黑树          | 哈希表 + 链表/红黑树（Java 8+） | 哈希表 + 双向链表        | 跳表                        |
| **排序性**   | 支持自然排序/自定义排序 | 无序                    | 保持插入顺序或访问顺序       | 支持自然排序/自定义排序（线程安全）        |
| **时间复杂度** | O(log n)     | O(1) 平均，O(n) 最坏       | O(1) 平均           | O(log n)                  |
| **线程安全**  | 非线程安全        | 非线程安全                 | 非线程安全             | 线程安全                      |
| **适用场景**  | 需要有序遍历或范围查询  | 快速存取，无序场景             | 需要保持插入/访问顺序       | 高并发有序场景                   |

## 五、代码示例
1. **基础用法**
   ```java
   TreeMap<Integer, String> treeMap = new TreeMap<>();
   treeMap.put(3, "Three");
   treeMap.put(1, "One");
   treeMap.put(2, "Two");
   System.out.println(treeMap); // 输出: {1=One, 2=Two, 3=Three}
   ```

2. **自定义排序**
   ```java
   TreeMap<Integer, String> descendingMap = new TreeMap<>(Comparator.reverseOrder());
   descendingMap.put(1, "One");
   descendingMap.put(2, "Two");
   System.out.println(descendingMap); // 输出: {2=Two, 1=One}
   ```

3. **范围查询**
   ```java
   TreeMap<Integer, String> treeMap = new TreeMap<>();
   treeMap.put(10, "Ten");
   treeMap.put(20, "Twenty");
   treeMap.put(30, "Thirty");
   SortedMap<Integer, String> headMap = treeMap.headMap(20); // 严格小于 20
   System.out.println(headMap); // 输出: {10=Ten}
   ```