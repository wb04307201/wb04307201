# 高频面试题

## 一、Java基础
1. **面向对象三大特性**
    - **封装**：隐藏内部实现，通过public方法访问（如`private`字段+getter/setter）。
    - **继承**：子类继承父类属性/方法（Java单继承，接口多实现）。
    - **多态**：父类引用指向子类对象（如`Animal a = new Dog()`），配合重写实现动态绑定。

2. **String与包装类**
    - String不可变（final修饰），`"abc"`存储于常量池；`new String("abc")`在堆中创建新对象。
    - 基本类型与包装类：`Integer`缓存范围[-128,127]，超出则新建对象（如`Integer a=128; Integer b=128;`，`a==b`为`false`）。

3. **集合框架**
    - **ArrayList vs LinkedList**：ArrayList基于数组，随机访问快（O(1)），插入慢（O(n)）；LinkedList基于链表，插入快（O(1)），随机访问慢（O(n)）。
    - **HashMap原理**：数组+链表/红黑树（JDK8后），哈希冲突通过链表法解决，树化阈值（链表长度>8时转为红黑树）。
    - **ConcurrentHashMap**：JDK8采用CAS+synchronized（锁桶/链表头节点），替代JDK7的分段锁，支持高并发读写。

## 二、多线程与并发
1. **线程创建方式**
    - 继承`Thread`、实现`Runnable`/`Callable`（有返回值）、线程池（`Executors`工具类）。

2. **同步机制**
    - **synchronized**：锁升级（无锁→偏向锁→轻量级锁→重量级锁），修饰代码块或方法。
    - **ReentrantLock**：支持公平锁、超时锁，需手动释放（`lock()`/`unlock()`）。
    - **volatile**：保证可见性（直接读写主内存）与有序性（禁止指令重排序），不保证原子性（如`i++`需配合`AtomicInteger`）。

3. **线程池**
    - 核心参数：`corePoolSize`（核心线程数）、`maximumPoolSize`（最大线程数）、`keepAliveTime`（空闲线程存活时间）、`workQueue`（任务队列）、`handler`（拒绝策略）。
    - 拒绝策略：`AbortPolicy`（抛异常）、`CallerRunsPolicy`（主线程执行）等。

## 三、JVM与性能优化
1. **内存区域**
    - 堆（对象实例）、栈（线程私有，存储局部变量）、方法区（类元数据）、程序计数器（当前指令地址）、本地方法栈（Native方法）。

2. **垃圾回收**
    - **算法**：标记-清除（碎片多）、复制（年轻代）、标记-整理（老年代）。
    - **收集器**：G1（分代+Region化，预测停顿）、ZGC（低延迟，<10ms）。
    - **调优参数**：`-Xmx`（最大堆）、`-XX:+UseG1GC`（启用G1）、`-XX:+PrintGCDetails`（打印GC日志）。

3. **类加载过程**
    - 加载→验证→准备→解析→初始化，双亲委派模型（避免重复加载），自定义类加载器需继承`ClassLoader`并重写`findClass()`。

## 四、Spring框架
1. **核心概念**
    - **IOC**：控制反转，通过`@Component`/`@Service`注解声明Bean，由容器管理生命周期。
    - **AOP**：面向切面编程，基于动态代理（JDK/CGLIB），实现日志、事务等横切关注点。

2. **Spring Boot**
    - 自动配置：`@SpringBootApplication`组合`@EnableAutoConfiguration`，通过`META-INF/spring.factories`加载配置。
    - 起步依赖：如`spring-boot-starter-web`包含Tomcat、Jackson等。

3. **事务管理**
    - 传播机制：`REQUIRED`（默认，加入事务）、`REQUIRES_NEW`（新建事务）。
    - 隔离级别：`READ_COMMITTED`（读已提交）、`SERIALIZABLE`（串行化）。

## 五、分布式与微服务
1. **微服务架构**
    - 组件：服务注册（Eureka/Nacos）、配置中心（Spring Cloud Config）、API网关（Zuul/Gateway）、熔断（Hystrix/Sentinel）。
    - 分布式事务：2PC（两阶段提交）、TCC（Try-Confirm-Cancel）、SAGA（长事务）。

2. **消息队列**
    - RabbitMQ（AMQP协议）、Kafka（高吞吐）、RocketMQ（事务消息）。

## 六、算法与数据结构
- **高频手撕代码**：单例模式（双重检查锁）、LRU Cache（LinkedHashMap+哈希表）、二叉树序列化/反序列化、快排、归并排序。
- **时间复杂度优化**：如从O(n²)到O(nlogn)的常见套路（分治、哈希表）。

## 备考建议
- **基础巩固**：JVM原理、集合源码、多线程机制。
- **项目实战**：结合Spring Boot+微服务框架实现高并发场景（如限流、熔断）。
- **模拟面试**：通过LeetCode刷题（重点链表、树、动态规划）、模拟面试系统（如牛客网）。