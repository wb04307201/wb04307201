# Stream流介绍及使用指南

在Java 8之前，处理集合数据（如`List`,`Set`,`Map`）通常意味着编写冗长的、以操作为中心的代码：创建迭代器、使用`for`或`while`循环遍历元素、在循环体内进行条件判断和操作、收集结果。这种方式虽然有效，但不够简洁、可读性较差，且难以充分利用多核处理器的优势。

Java 8 引入的 Stream API (`java.util.stream`) 彻底改变了这一局面。它提供了一种高效、声明式、函数式处理数据序列（尤其是集合）的强大抽象。Stream 不是数据结构，而是对数据源（如集合、数组、I/O资源）进行复杂计算操作的流水线。它允许你以声明式的方式（描述“做什么”，而不是“怎么做”）来表达数据处理逻辑，极大地提升了代码的简洁性、可读性和潜在的性能（尤其是并行处理）。

## 什么是 Stream
1. 非数据结构：Stream 本身不存储数据。它从数据源（如集合、数组）获取数据，并携带数据流经一系列计算操作。
2. 函数式操作：Stream 的操作（如`filter`,`map`,`reduce`) 通常接受函数式接口（如`Predicate`,`Function`,`Consumer`) 作为参数，这使其天然支持Lambda表达式和方法引用。
3. 流水线：Stream 操作被链接起来形成一个流水线（Pipeline）。一个Stream操作的结果作为下一个操作的输入。
4. 惰性求值：中间操作（Intermediate Operations）是惰性的。它们只是声明了要执行的操作，但不会立即执行。只有终止操作（Terminal Operation）被调用时，整个流水线才会被触发执行。
5. 只能遍历一次：一个Stream实例一旦被终止操作消费，就不能再被使用。你需要从原始数据源重新创建一个新的Stream来执行其他操作。
6. 支持并行：创建并行Stream（`parallelStream()`）非常简单，Stream API内部会自动处理线程和分区的复杂性（尽管使用时仍需注意线程安全）。

## Stream 操作类型
Stream操作主要分为两类：
1. 中间操作：总是返回一个新的Stream，允许操作链式调用
   - `filter(Predicate<T> predicate)`: 过滤元素，保留满足条件的元素。
   - `map(Function<T, R> mapper)`: 将元素转换成另一种形式（类型可以改变）。例如，从Student对象中提取name属性形成新的字符串流。
   - `flatMap(Function<T, Stream<R>> mapper)`: 将每个元素转换成一个Stream，然后把所有生成的Stream“扁平化”连接成一个Stream。常用于处理嵌套集合（如List<List<String>>）。
   - `distinct()`: 去除重复元素（依据equals()）。
   - `sorted()` / `sorted(Comparator<T> comparator)`: 排序。
   - `peek(Consumer<T> action)`: 对每个元素执行一个操作（通常用于调试，如打印），不影响元素本身。注意： 在并行流中慎用，执行顺序不确定。
   - `limit(long maxSize)`: 截取前N个元素。
   - `skip(long n)`: 跳过前N个元素。
2. 终止操作：消费Stream并产生一个结果（如一个值、一个集合、`void`）或副作用。
   - `forEach(Consumer<T> action)`: 对每个元素执行操作。
   -  `toArray() `: 将元素收集到数组中。
   - `reduce(...)`: 将元素反复结合，得到一个汇总值（如求和、求最大值）。有多个重载形式（带初始值、不带初始值、BinaryOperator）。
   - `min(Comparator<T> comparator)` / `max(Comparator<T> comparator)`: 返回最小/最大元素（基于比较器）。
   - `count()`: 返回元素数量。
   - `anyMatch(Predicate<T> predicate)` / `allMatch(Predicate<T> predicate)` / `noneMatch(Predicate<T> predicate)`: 检查是否存在任意/所有/没有元素匹配给定条件。这些是短路操作（找到结果即停止）。
   - `findFirst()` / `findAny()`: 返回第一个/任意一个元素（Optional<T>）。findAny()在并行流中效率更高。也是短路操作。
   - `collect(Collector<T, A, R> collector): 使用`Collectors`工具类提供的方法（如`toList()`, `toSet()`, `toMap()`, `joining()`, `groupingBy()`, `partitioningBy()`, `summingInt()`, `averagingDouble()`等）将元素汇总成各种形式的结果（集合、字符串、数值统计等）。

## 核心优势
1. 声明式编程： 代码更清晰、更接近问题描述。你关注的是“过滤出大于10的数”、“提取名称字段”、“按年龄分组”这样的逻辑，而不是循环索引和临时变量。
2. 简洁性： 显著减少样板代码（如循环、迭代器、临时集合）。
3. 可读性： 链式调用和Lambda表达式使数据处理逻辑一目了然。
4. 易于并行化： 只需将stream()替换为parallelStream()（或在现有流上调用parallel()），即可尝试利用多核处理器加速计算。Stream API 内部处理了复杂的线程、同步和数据分区问题。（注意：并行不一定总是更快，需要评估数据量和操作复杂度）
5. 函数式风格： 鼓励使用无副作用的纯函数，有利于编写更健壮、可测试的代码。
6. 组合性： 中间操作可以灵活组合，构建复杂的数据处理流水线

## 示例代码
 ```java
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
public class StreamDemo {
    public static void main(String[] args) {
        List<String> names = Arrays.asList("abc", "java", "python", "David", "Anna", "Edward");        
        // 示例1：过滤以"A"开头的名字，转换成大写，收集到List        
        List<String> aNamesUpper = names.stream() // 1. 创建流
                .filter(name -> name.startsWith("A")) // 2. 中间操作：过滤                
                .map(String::toUpperCase) // 3. 中间操作：转换 (方法引用)
                .collect(Collectors.toList()); // 4. 终止操作：收集         
        
        // 示例2：计算所有名字长度的总和 (使用mapToInt避免自动拆箱装箱)        
        int totalLength = names.stream()                
                .mapToInt(String::length) // 转换成IntStream (原始类型流)
                .sum(); // IntStream的终止操作：求和
        System.out.println("Total Length: " + totalLength);        
        
        // 示例3：按名字长度分组       
        Map<Integer, List<String>> namesByLength = names.stream()                
                .collect(Collectors.groupingBy(String::length));
        System.out.println(namesByLength);        
        
        // 示例4：并行流 - 查找任意一个长度大于5的名字 (顺序无关紧要时)        
        names.parallelStream()                
                .filter(name -> name.length() > 5)                
                .findAny()                
                .ifPresent(System.out::println);     
    }
}
```

## 注意事项

1. 一次消费： Stream 只能被终止操作消费一次。之后再次使用会抛出`IllegalStateException`。需要从原始数据源重新创建。
2. 避免有状态的Lambda： 在中间操作的Lambda表达式（特别是并行流中）应避免修改外部状态（如外部变量），否则可能导致线程安全问题或不可预测的结果。尽量使用无状态操作和纯函数。
3. 并行流谨慎使用：
   - 开销： 并行化本身（线程创建、任务调度、结果合并）有开销。数据量小或操作简单时，串行流可能更快。
   - 线程安全： 确保数据源、共享状态、传递给操作的Lambda都是线程安全的。避免修改源集合（使用并发集合或确保只读）。
   - 顺序依赖性： 如果操作结果依赖于元素顺序（如`findFirst()`, `limit()`, `sorted()`在并行流中可能更慢），或者操作本身有状态（如`skip()`），并行可能无益甚至有害。
   - 副作用： 在forEach或peek中进行有副作用的操作（如修改共享集合）在并行流中极易出错。优先使用无副作用的collect进行汇总。
4. peek用于调试： `peek`主要用于调试观察流水线中间状态，不应依赖它执行关键业务逻辑，尤其在并行流中其执行顺序不确定。
5. 原始类型流： 为避免频繁的自动装箱（`int` -> `Integer`）带来的性能损耗，提供了`IntStream`, `LongStream`, `DoubleStream`。使用`mapToInt`, `mapToLong`, `mapToDouble`等方法转换，并使用其专用的方法（如`sum()`, `average()`, `range()`）。

## 变更历史

| 版本      | 描述                                                    |
|---------|-------------------------------------------------------|
| java8   | JEP 107: Stream API：Java 8 新特性—Stream API 对元素流进行函数式操作 |
| java9   | Stream API 增强：Java 9 新特性—Stream API的增强                |
| java10  | Stream API 增强                                         |
| javava2 | JEP 461：流收集器（预览）这个改进使得 Stream API 可以支持自定义中间操作。        |
| java23  | JEP 473:流收集器(第二次预览)                                   |





