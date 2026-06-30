<!--
question:
  id: 01.java-create-object
  topic: 01.java
  difficulty: 未标
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [01.java, create, object]
-->

# 创建对象

## 引子：你知道几种创建对象的方式？

```java
// 方式 1：最常见
Person p1 = new Person("Alice");

// 方式 2：反射
Person p2 = Person.class.getDeclaredConstructor().newInstance();

// 方式 3：Clone
Person p3 = p1.clone();

// 方式 4：反序列化
ObjectInputStream ois = new ObjectInputStream(new FileInputStream("person.ser"));
Person p4 = (Person) ois.readObject();

// 方式 5：Unsafe（黑科技）
sun.misc.Unsafe unsafe = getUnsafe();
Person p5 = (Person) unsafe.allocateInstance(Person.class);  // 不调构造器！
```

5 种方式，从常规到黑科技，每种方式的底层机制完全不同。你都知道吗？

---

> 📚 **前置知识**：[Object](../../../01.java/concepts/object/README.md)

## 1. 使用`new`关键字（最常见）
通过调用类的构造函数创建对象。
```java
// 定义类
class Person {
    String name;
    public Person(String name) {
        this.name = name;
    }
}

// 创建对象
Person person = new Person("Alice");
```

## 2. 使用反射（Reflection）
通过`Class`类或`Constructor`类动态创建对象，常用于框架设计。
```java
import java.lang.reflect.Constructor;

class Car {
    public Car() {}
}

// 反射创建对象
try {
Class<?> clazz = Class.forName("Car");
Object car = clazz.getDeclaredConstructor().newInstance();
} catch (Exception e) {
        e.printStackTrace();
}
```

## 3. 克隆（Clone）
通过实现`Cloneable`接口并重写`clone()`方法创建对象的副本。
```java
class Animal implements Cloneable {
    int age;
    @Override
    public Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}

Animal animal = new Animal();
Animal animalClone = (Animal) animal.clone();
```

## 4. 对象序列化与反序列化
通过序列化（`ObjectOutputStream`）和反序列化（`ObjectInputStream`）创建对象。
```java
import java.io.*;

class Dog implements Serializable {
    String breed;
}

// 序列化
Dog dog = new Dog();
try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("dog.ser"))) {
        oos.writeObject(dog);
}

// 反序列化
        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream("dog.ser"))) {
Dog dogCopy = (Dog) ois.readObject();
}
```

## 5. 工厂模式（Factory Pattern）
通过工厂类封装对象创建逻辑，提高代码灵活性。
```java
interface Shape {
    void draw();
}

class Circle implements Shape {
    @Override
    public void draw() {
        System.out.println("Drawing Circle");
    }
}

class ShapeFactory {
    public Shape getShape(String type) {
        return switch (type) {
            case "Circle" -> new Circle();
            default -> null;
        };
    }
}

// 使用工厂创建对象
ShapeFactory factory = new ShapeFactory();
Shape shape = factory.getShape("Circle");
```

## 6. 匿名内部类（Anonymous Inner Class）
在创建对象时直接定义类实现。
```java
interface Greeting {
    void sayHello();
}

// 匿名内部类创建对象
Greeting greeting = new Greeting() {
    @Override
    public void sayHello() {
        System.out.println("Hello!");
    }
};
```

## 7. 使用`Object.clone()`的变体
结合`Copyable`接口（非标准，需自定义）实现浅/深拷贝。
```java
class CustomCopy {
    public CustomCopy copy() {
        CustomCopy copy = new CustomCopy();
        // 复制属性逻辑
        return copy;
    }
}

CustomCopy original = new CustomCopy();
CustomCopy copy = original.copy();
```

## 8. 依赖注入（DI）框架
如Spring框架通过`@Autowired`、构造函数注入等方式管理对象创建。
```java
// Spring示例（需配置Spring容器）
@Component
public class Engine {
    // ...
}

@Component
public class Car {
    private final Engine engine;

    @Autowired
    public Car(Engine engine) {
        this.engine = engine;
    }
}
```

## 9. 使用`java.util.function.Supplier`
通过函数式接口延迟创建对象。
```java
import java.util.function.Supplier;

Supplier<String> stringSupplier = () -> "Hello";
String str = stringSupplier.get(); // 创建对象
```

## 10. 使用`Arrays.copyOf`或`System.arraycopy`（数组对象）
专门用于数组对象的创建和复制。
```java
int[] source = {1, 2, 3};
int[] target = Arrays.copyOf(source, source.length);
```

## 总结
- **基础方法**：`new`关键字是最直接的方式。
- **高级场景**：反射、克隆、序列化用于特殊需求（如框架开发、对象复制）。
- **设计模式**：工厂模式、建造者模式（如`StringBuilder`）提升代码可维护性。
- **框架支持**：Spring等框架通过依赖注入简化对象管理。

根据具体场景选择合适的方法，例如：
- 普通对象：优先用`new`。
- 动态加载类：用反射。
- 对象池或复杂构造：用工厂模式或建造者模式。## 相关章节

- 深度阅读：[`01.java/核心概念`](../../../01.java/concepts/README.md) — 反射、序列化、SPI
- 相关：[`13.split-hairs/singleton-pattern`](../singleton-pattern/README.md) — 单例的 5 种实现
- 相关：[`06.spring/01-core/Bean 生命周期`](../../../06.spring/01-core/ioc/bean-lifecycle.md) — Spring 如何管理 Bean 创建
