# Lombok

是一款通过注解简化Java代码的工具，在编译期自动生成模板代码（如getter、setter、构造器等）。

### **基础功能注解**
1. **@Data**  
   组合注解，等价于同时使用`@Getter`、`@Setter`、`@ToString`、`@EqualsAndHashCode`和`@RequiredArgsConstructor`。生成无参构造需配合`@NoArgsConstructor`，适用于POJO类。

2. **@Getter/@Setter**  
   为类或属性生成getter/setter方法。可指定访问级别（如`AccessLevel.PRIVATE`），final属性不生成setter。

3. **@ToString**  
   生成`toString()`方法，默认包含所有非静态字段。支持`exclude`排除字段、`callSuper`包含父类信息、`includeFieldNames`控制字段名显示。

4. **@EqualsAndHashCode**  
   生成`equals()`和`hashCode()`方法。通过`callSuper=true`可包含父类字段，`exclude`可排除指定字段。

5. **构造器相关**
    - `@NoArgsConstructor`：无参构造器。
    - `@RequiredArgsConstructor`：为`@NonNull`或final字段生成构造器。
    - `@AllArgsConstructor`：全参数构造器。

### **高级功能注解**
6. **@Builder**  
   实现建造者模式，支持链式调用（如`User.builder().name("test").age(20).build()`）。可配合`@SuperBuilder`支持父类字段。

7. **日志注解**  
   `@Slf4j`、`@Log`、`@Log4j`等，自动生成日志记录器（如`private static final Logger log = ...`）。

8. **资源管理**
    - `@Cleanup`：自动关闭资源（如文件流、数据库连接），确保`close()`被调用。
    - `@SneakyThrows`：将检查异常转为运行时异常，无需显式捕获。

9. **非空校验**  
   `@NonNull`用于字段或参数，若值为null则抛出`NullPointerException`。

10. **同步控制**  
    `@Synchronized`：将方法体包裹在`synchronized`块中，可指定锁对象。

11. **不可变类**  
    `@Value`：生成不可变类（字段final，无setter，全参构造器），类似`@Data`但更严格。

12. **类型推断**  
    `val`/`var`：局部变量类型推断（`val`为final，`var`不可变），需配合Java 10+。

### **特殊场景注解**
13. **懒加载**  
    `@Getter(lazy=true)`：字段首次访问时初始化，线程安全。

14. **委托模式**  
    `@Delegate`：将方法调用转发到另一个对象（如`@Delegate(types=List.class)`实现List接口）。

15. **工具类**  
    `@UtilityClass`：生成不可实例化的工具类，自动添加`private`构造器和`static`方法。

16. **字段默认值**  
    `@FieldDefaults(makeFinal=true, level=AccessLevel.PRIVATE)`：设置字段默认访问级别和final属性。

### **注意事项**
- **依赖配置**：需在Maven/Gradle中添加Lombok依赖，并在IDE安装插件（如IntelliJ的Lombok插件）。
- **代码可读性**：过度使用可能降低代码可读性，建议仅用于POJO类或简单工具类。
- **构造器冲突**：Lombok不支持多种构造器重载，需通过注解组合实现。
- **父类字段**：`@EqualsAndHashCode`和`@ToString`需通过`callSuper=true`显式包含父类字段。

Lombok通过编译期注解处理器（JSR 269）修改抽象语法树（AST）生成代码，不改变运行时行为。官方文档建议结合具体场景选择注解，避免过度简化影响代码维护性。