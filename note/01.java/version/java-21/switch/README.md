# Switch 模式匹配

**Switch 模式匹配**是Java 21中引入的一项重要语言特性，旨在通过扩展`switch`表达式和语句的模式匹配能力，简化代码并提高开发效率。

## 1. 特性背景与演进
- **起源**：模式匹配的`switch`首次在Java SE 17中以预览形式出现，经过多轮迭代（JEP 406、420、427、433），最终在Java 21中成为永久性功能。
- **目标**：解决传统`switch`语句的冗余代码和“fall-through”行为问题，同时支持更复杂的类型匹配和条件逻辑。

## 2. 核心改进
### (1) 模式匹配扩展
- **类型匹配**：允许在`case`标签中直接匹配对象类型，并解构对象属性。例如：
  ```java
  Object obj = ...;
  String result = switch (obj) {
      case String s -> "字符串: " + s;
      case Integer i -> "整数: " + i;
      default -> "未知类型";
  };
  ```
- **记录模式（Record Patterns）**：结合JEP 440，可解构记录类（Record）的字段：
  ```java
  record Point(int x, int y) {}
  Point p = new Point(3, 4);
  String desc = switch (p) {
      case Point(int x, int y) -> "坐标: (" + x + ", " + y + ")";
  };
  ```

### (2) 语法简化
- **箭头语法（`->`）**：替代传统冒号（`:`），自动终止分支，无需`break`语句。
- **多值匹配**：用逗号分隔多个常量，简化多条件判断：
  ```java
  String day = "MONDAY";
  String type = switch (day) {
      case "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY" -> "工作日";
      case "SATURDAY", "SUNDAY" -> "周末";
      default -> "未知";
  };
  ```

### (3) 表达式返回值
- `switch`可作为表达式返回结果，支持直接赋值或方法调用：
  ```java
  int num = 10;
  String size = switch (num) {
      case 1, 2, 3 -> "小";
      case 4, 5, 6 -> "中";
      default -> "大";
  };
  ```

### (4) `yield`关键字
- 在复杂分支中，用`yield`返回值（替代`break`）：
  ```java
  String result = switch (obj) {
      case Integer i when i > 0 -> {
          System.out.println("正数");
          yield "正整数";
      }
      default -> "非正整数";
  };
  ```

## 3. 实际应用场景
- **类型安全的数据处理**：替代冗长的`instanceof`链，提升代码可读性。
- **状态机与事件分发**：简化多状态逻辑，例如游戏角色行为、网络协议处理。
- **JSON/XML解析**：结合记录模式，快速解构嵌套数据结构。
- **错误处理**：统一处理不同异常类型的分支逻辑。

## 4. 代码示例对比
### 传统写法（Java 20及之前）
```java
Object obj = ...;
String result;
if (obj instanceof String) {
    result = "字符串: " + obj;
} else if (obj instanceof Integer) {
    result = "整数: " + obj;
} else {
    result = "未知类型";
}
```

### Java 21模式匹配写法
```java
Object obj = ...;
String result = switch (obj) {
    case String s -> "字符串: " + s;
    case Integer i -> "整数: " + i;
    default -> "未知类型";
};
```

## 5. 优势总结
- **简洁性**：减少样板代码，提升开发效率。
- **安全性**：编译器类型检查，减少运行时错误。
- **可维护性**：逻辑更清晰，易于扩展和修改。
- **性能**：模式匹配在编译时优化，无额外运行时开销。

## 6. 注意事项
- **兼容性**：Java 21中该特性为永久功能，无需启用预览标志。
- **学习曲线**：需熟悉新语法（如`yield`、箭头操作符）。
- **工具支持**：确保IDE（如IntelliJ IDEA、Eclipse）更新至最新版本以获得完整支持。

## 结语
JEP 441通过模式匹配将`switch`升级为更强大的条件控制工具，尤其适合处理复杂类型和多分支逻辑。这一改进显著提升了Java的语言表达能力，是现代Java开发中不可或缺的高效特性。