# 反射

反射是 Java 中的一个特性，它允许程序在运行时获取自身的信息，并动态地操作类或对象的属性、方法和构造函数。通过反射，我们可以在事先不知道确切类名的情况下实例化对象、调用方法和设置属性。

反射机制的核心是`Class`对象，它代表一个类。Java 虚拟机（JVM）在加载类时会自动创建这个`Class`对象。

## JVM 如何创建一个类

当我们编写一个类并进行编译时，编译器会将其转换为存储在`.class`文件中的字节码。在类加载过程中，JVM 使用`ClassLoader`读取`.class`文件，将字节码加载到内存中，并根据这些信息创建相应的`Class`对象。由于每个类在 JVM 中只加载一次，所以每个类都对应一个唯一的`Class`对象。

```java
public class User extends People {
    public String name;
    private int age;

    private static int staticFiled = 10;
    private final String sex;
    protected String protectedFiled;

    static {
        System.out.println("静态方法执行");
    }

    public User(String name, String sex) {
        this.name = name;
        this.sex = sex;
    }

    private void privateMethod() {
        System.out.println("我是私有方法");
    }

    public void publicMethod() {
        System.out.println("我是公共方法");
    }
}

public class People {
    public String publicFiled;
    private String privateFiled;
}
```

## 获取Class对象的三种方式
### 第一种方法

通过类名使用`.class`获取类对象。这是在编译时完成的，所以明确指定了类型`User`，不会导致任何错误。使用这种方法获取对象不会触发类初始化；只有在访问类的静态成员或实例时才会进行初始化。

```java
Class<Hero> heroClass = Hero.class;
```

实例化一个对象：
```java
Hero heroInstance = heroClass.getDeclaredConstructor(String.class, String.class).newInstance("蝙蝠侠", "布鲁斯韦恩");
```

### 第二种方法

通过对象的`getClass()`方法获取类对象。这种方法适用于从已实例化的类对象中获取类对象。请注意，类型不`Hero`，而是通配符`?`，因为`Class`对象是从`Hero`的实例中获取的，实例的具体类型只能在运行时确定，而不是在编译时。

```java
Hero hero = new Hero("蝙蝠侠", "布鲁斯韦恩");
Class<?> heroClass = hero.getClass();
```

实例化一个对象：
```java
Constructor<?> constructor = heroClass.getConstructor(String.class, String.class);
Hero heroInstance = (Hero) constructor.newInstance("蝙蝠侠", "布鲁斯韦恩");
```

### 第二三方法

使用静态方法`Class.forName()`通过全路径获取类对象。由于类型只能在运行时知道，所以类型是通配符`?`。通过这种方法获取类对象将立即触发类初始化。

```java
Class<?> heroClass = Class.forName("cn.wubo.entity.Hero");
```

创建一个实例：
```java
Constructor<?> constructor = heroClass.getConstructor(String.class, String.class);
Hero heroInstance = (Hero) constructor.newInstance("蝙蝠侠", "布鲁斯韦恩");
```

## 在 Java 中访问对象字段
### 获取所有公共字段

要获取所有公共字段，包括从父类继承的字段，使用`getFields()`：

```java
Field[] fields = hero.getFields();
for (Field field : fields) {
    System.out.println(field);
}
```

输出：
```shell
public java.lang.String cn.wubo.entity.Hero.name
public java.lang.String cn.wubo.entity.People.publicField
```

### 获取所有声明的字段

要获取类中所有声明的字段，无论其访问级别如何，使用`getDeclaredFields()`。这不包括从超类继承的字段：

```shell
Field[] fields = hero.getDeclaredFields();
for (Field field : fields) {
    System.out.println(field);
}
```

输出：
```shell
public java.lang.String cn.wubo.entity.Hero.name
private java.lang.String cn.wubo.entity.Hero.realName
protected java.lang.String cn.wubo.entity.People.protectedField
```

### 获取超类中的字段

要获取超类中的字段，使用`getSuperclass()`：

```java
Field[] fields = hero.getSuperclass().getDeclaredFields();
for (Field field : fields) {
    System.out.println(field);
}
```

输出：
```shell
public java.lang.String cn.wubo.entity.People.publicField
private java.lang.String cn.wubo.entity.People.privateField
```

### 获取特定字段

要通过名称获取特定公共字段，使用`getField(String name)`。对于任何特定字段，无论其访问级别如何，使用`getDeclaredField(String name)`。

### 处理不存在的字段

尝试访问不存在的字段不会产生编译时错误，但会在运行时抛出异常：

```java
try {
    Field nonExistentField = hero.getDeclaredField("nonExistentField");
} catch (NoSuchFieldException e) {
    e.printStackTrace();
}
```

输出：
```shell
java.lang.NoSuchFieldException: nonExistentField
```

### 设置字段值

要设置私有静态字段的值，首先使其可访问：

```java
Class<?> heroClass = Class.forName("cn.wubo.entity.Hero");
Field staticField = userClass.getDeclaredField("staticField");
staticField.setAccessible(true);
System.out.println(staticField.get(null));
```

如果字段是final的，仍然可以修改它：
```java
Field field = userClass.getDeclaredField("sex");
field.setAccessible(true);
field.set(obj, "女");
System.out.println(field.get(obj));
```

输出：
```shell
女
```

## 访问方法
访问方法与访问字段类似：
- getMethods()检索类及其超类中的所有公共方法。
- getDeclaredMethods()检索类中所有声明的方法，无论访问级别如何。
- getMethod(String name, Class<?>... parameterTypes)按名称和参数类型检索特定公共方法。
- getDeclaredMethod(String name, Class<?>... parameterTypes)按名称和参数类型检索特定声明的方法，无论访问级别如何。

## 关键应用场景
- **框架与库**：Spring的依赖注入（通过反射解析Bean）、Hibernate的ORM映射、JUnit的动态测试方法加载。
- **动态代理**：JDK动态代理通过`InvocationHandler`和`Proxy`类实现，底层依赖反射调用方法。
- **注解处理**：运行时通过反射解析自定义注解（如`@Autowired`），实现配置化逻辑。
- **调试与工具**：IDE的智能提示、调试器查看对象状态、Java自带的`jstack`/`jmap`工具分析JVM状态。
- **跨语言通信**：RPC框架（如Dubbo）通过反射序列化/反序列化对象。

## 优点与局限性
- **优点**：
    - **灵活性**：突破编译期限制，实现动态加载类、调用方法、修改字段（如热更新、插件化架构）。
    - **解耦**：框架无需硬编码业务类，提升代码复用性和扩展性。
    - **自省能力**：运行时获取类结构信息，支持元编程（如代码生成、动态代理）。
- **局限性**：
    - **性能开销**：反射操作（如方法调用、字段访问）比直接调用慢（涉及JVM的动态分派和安全检查）。
    - **破坏封装**：访问私有成员可能绕过设计约束，增加代码脆弱性。
    - **安全风险**：需注意`setAccessible(true)`可能引发安全问题，需谨慎使用。
    - **代码可读性**：过度使用反射会使代码逻辑隐蔽，增加维护成本。

## 最佳实践与注意事项
- **性能优化**：对高频反射操作（如循环中调用方法），可缓存`Method`/`Field`对象，避免重复解析。
- **异常处理**：反射方法可能抛出`NoSuchMethodException`、`IllegalAccessException`等，需妥善处理。
- **替代方案**：优先考虑接口、抽象类、工厂模式等设计模式；在性能敏感场景（如高频交易）避免反射。
- **兼容性**：Java 9+引入模块系统（JPMS），反射访问需在`module-info.java`中声明`opens`权限。
- **工具支持**：使用Lombok、MapStruct等工具减少样板代码，减少手动反射需求。