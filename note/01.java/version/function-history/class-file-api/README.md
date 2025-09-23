# Class-File API

| Java版本  | 新特性/增强内容                                       |
|---------|------------------------------------------------|
| Java 22 | JEP 457: 类文件 API（第一次预览）- 引入标准化的类文件解析、生成和转换 API |
| Java 23 | JEP 466: 类文件 API（第二次预览）- 继续完善类文件 API 功能        |
| Java 24 | JEP 484: 类文件 API（正式版）- 类文件 API 转正为标准特性         |

## 功能详细介绍

### Java 22 - 类文件 API 初始引入 (JEP 457)

Java 22 首次引入了类文件 API 作为预览特性，这是对 Java 平台底层操作能力的重要增强。

#### 核心概念：

1. **标准化 API**：提供了一套标准化的 API 来处理 Java 类文件，替代了过去对第三方库（如 ASM）的依赖
2. **类文件解析**：能够将字节数组解析为结构化的 `ClassModel` 对象
3. **类文件构建**：支持构建新的类文件，可以对现有类文件进行修改和转换

#### 主要目标：

- 提供官方标准的类文件处理 API
- 简化类文件操作的复杂性
- 提高类文件处理的性能和安全性

### Java 23 - 类文件 API 第二次预览 (JEP 466)

Java 23 继续预览并完善类文件 API，在第一版的基础上进行了改进和优化。

#### 改进内容：

1. **API 完善**：根据用户反馈完善了 API 设计
2. **功能增强**：增强了类文件解析和生成的功能
3. **性能优化**：优化了 API 的性能表现

### Java 24 - 类文件 API 转正 (JEP 484)

Java 24 将类文件 API 从预览特性转为标准特性，标志着该功能的成熟和稳定。

#### 基本用法：

```java
// 创建一个 ClassFile 对象，这是操作类文件的入口。
ClassFile cf = ClassFile.of();
// 解析字节数组为 ClassModel
ClassModel classModel = cf.parse(bytes);

// 构建新的类文件，移除以 "debug" 开头的所有方法
byte[] newBytes = cf.build(classModel.thisClass().asSymbol(),
        classBuilder -> {
            // 遍历所有类元素
            for (ClassElement ce : classModel) {
                // 判断是否为方法 且 方法名以 "debug" 开头
                if (!(ce instanceof MethodModel mm
                        && mm.methodName().stringValue().startsWith("debug"))) {
                    // 添加到新的类文件中
                    classBuilder.with(ce);
                }
            }
        });
```


#### 主要优势：

1. **标准化**：提供了官方标准的类文件处理 API，避免了对第三方库的依赖
2. **易用性**：API 设计现代化且易于使用，简化了类文件操作的复杂性
3. **功能强大**：支持完整的类文件解析、生成和转换功能
4. **性能优化**：作为官方 API，有更好的性能优化潜力

类文件 API 的引入为 Java 开发者提供了更强大和标准化的方式来处理类文件，特别是在需要动态生成或修改类文件的场景中，如框架开发、代码生成工具、AOP 实现等领域。