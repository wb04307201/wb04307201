# 快速给Map排序

## 1. TreeMap自然排序（按键排序）
- **自然顺序**：键需实现`Comparable`接口（如String、Integer），TreeMap自动按升序排列。
  ```java
  Map<String, Integer> map = new HashMap<>();
  map.put("Banana", 20);
  map.put("Apple", 15);
  Map<String, Integer> sortedMap = new TreeMap<>(map);
  // 输出：{Apple=15, Banana=20}
  ```
- **自定义顺序**：通过`Comparator`指定排序规则（如降序、按长度）。
  ```java
  Map<String, Integer> sortedMap = new TreeMap<>(
      Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder())
  );
  // 先按字符串长度排序，长度相同按字母顺序
  ```

## 2. Stream API排序（按值或键排序）
- **按值排序**（升序/降序）：
  ```java
  Map<String, Integer> sortedMap = map.entrySet().stream()
      .sorted(Map.Entry.comparingByValue()) // 升序
      // .sorted(Map.Entry.comparingByValue(Comparator.reverseOrder())) // 降序
      .collect(Collectors.toMap(
          Map.Entry::getKey,
          Map.Entry::getValue,
          (oldVal, newVal) -> oldVal, // 键冲突时保留旧值
          LinkedHashMap::new // 保持排序顺序
      ));
  ```
- **按键排序**（自定义逻辑）：
  ```java
  Map<String, Integer> sortedMap = map.entrySet().stream()
      .sorted(Map.Entry.comparingByKey(Comparator.reverseOrder()))
      .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, (e1, e2) -> e1, LinkedHashMap::new));
  ```

## 3. 手动转换+排序（兼容旧版Java）
- 将`Map`转为`List`，排序后存入`LinkedHashMap`（保持插入顺序）：
  ```java
  List<Map.Entry<String, Integer>> list = new ArrayList<>(map.entrySet());
  Collections.sort(list, Map.Entry.comparingByValue()); // 按值升序
  Map<String, Integer> sortedMap = new LinkedHashMap<>();
  for (Map.Entry<String, Integer> entry : list) {
      sortedMap.put(entry.getKey(), entry.getValue());
  }
  ```

## 4. 特殊场景处理
- **线程安全**：使用`Collections.synchronizedSortedMap`或`ConcurrentSkipListMap`。
  ```java
  SortedMap<String, Integer> safeMap = Collections.synchronizedSortedMap(new TreeMap<>(map));
  ```
- **复杂排序**：组合多个`Comparator`（如先按值后按键）。
  ```java
  Comparator<Map.Entry<String, Integer>> comp = 
      Comparator.comparingInt(Map.Entry::getValue)
                .thenComparing(Map.Entry::getKey);
  ```

## 性能与选择建议
- **按键排序**：优先`TreeMap`（时间复杂度O(log n)），适合频繁查询。
- **按值排序**：推荐`Stream API`（简洁高效），大数据量时注意内存消耗。
- **保持顺序**：用`LinkedHashMap`存储结果，避免`HashMap`无序问题。