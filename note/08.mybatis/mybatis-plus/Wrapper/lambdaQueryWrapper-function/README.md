# LambdaQueryWrapper 中的序列化函数式接口 SFunction

在 **LambdaQueryWrapper** 中使用序列化的函数式接口（如 **SFunction**）的核心目的是 **通过 Lambda 表达式的序列化能力，在运行时动态解析实体类属性对应的数据库字段名，同时保证查询条件的线程安全性和可重用性**。

## 1. Lambda 表达式与字段名的动态解析
- **问题背景**：在传统 MyBatis 或 JPA 中，构建查询条件时通常需要直接使用数据库字段名（如 `"username"`），这会导致硬编码问题，字段名变更时需修改多处代码。
- **SFunction 的作用**：  
  SFunction 是 MyBatis-Plus 对 Lambda 表达式的封装，通过方法引用（如 `User::getName`）指定实体类属性。框架在运行时通过 **序列化 Lambda 表达式**，解析出属性的实际数据库字段名（如 `name` → `user_name`，若数据库有下划线转换规则）。
- **示例**：
  ```java
  LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
  wrapper.eq(User::getName, "Alice"); // 自动解析为 WHERE user_name = 'Alice'
  ```
  这里 `User::getName` 是 SFunction 实例，框架通过序列化解析其指向的字段名。

## 2. 序列化的必要性
- **为什么需要序列化**：  
  Lambda 表达式在编译后会生成一个匿名类（如 `LambdaQueryWrapper$$Lambda$1`），但默认情况下这些类无法直接序列化。MyBatis-Plus 需要将 Lambda 表达式转换为可序列化的形式（如 `SerializedLambda`），以便：
    - **跨网络传输**：在分布式环境中，查询条件可能需要序列化后传输到其他节点执行。
    - **持久化存储**：将查询条件保存到缓存或数据库时，需序列化。
    - **反射解析字段名**：通过序列化后的 `SerializedLambda` 对象，框架可以获取 Lambda 表达式的方法签名，进而解析出字段名。
- **实现原理**：  
  MyBatis-Plus 通过 `LambdaUtils.resolve(SFunction)` 方法将 Lambda 表达式转换为 `SerializedLambda`，再从中提取字段信息（如 `implMethod` 字段包含方法名，通过字符串处理得到字段名）。

## 3. 线程安全与可重用性
- **线程安全**：  
  SFunction 是无状态的函数式接口，其序列化后的 `SerializedLambda` 也是线程安全的，因此可以安全地在多线程环境中共享。
- **可重用性**：  
  同一个 SFunction 实例（如 `User::getName`）可以在多个查询条件中复用，避免重复创建 Lambda 表达式，提升性能。

## 4. 对比非序列化方案
- **非序列化方案的问题**：  
  若直接使用非序列化的 Lambda 表达式，框架无法在运行时解析字段名，只能依赖硬编码的字符串字段名，失去 Lambda 表达式的类型安全优势。
- **序列化方案的优势**：  
  通过序列化，框架可以动态解析字段名，同时保持代码的类型安全性和可维护性。例如，字段名变更时，只需修改实体类属性，无需修改查询条件代码。

## 5. 实际应用场景
- **动态查询构建**：  
  在需要根据用户输入动态构建查询条件的场景中，SFunction 的序列化能力使得框架可以安全地传递和解析查询条件。
- **分布式查询**：  
  在微服务架构中，查询条件可能需要序列化后通过网络传输到其他服务执行，SFunction 的序列化支持使得这一过程透明化。
- **缓存查询条件**：  
  将查询条件缓存时，序列化后的 SFunction 可以确保缓存的查询条件在反序列化后仍能正确解析字段名。

## 总结
MyBatis-Plus 在 **LambdaQueryWrapper** 中使用序列化的函数式接口（SFunction），是为了 **通过 Lambda 表达式的序列化能力，在运行时动态解析实体类属性对应的数据库字段名，同时保证查询条件的线程安全性和可重用性**。这一设计使得开发者可以以类型安全的方式构建查询条件，避免硬编码字段名，提升代码的可维护性和灵活性。