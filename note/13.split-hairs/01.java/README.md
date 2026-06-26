# Java 咬文嚼字

> Java 高频面试题与细节深挖，对齐主模块 [`01.java`](../../01.java/)

---

## 文章清单

### 集合与数据结构
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [ArrayList 去重](arrayList-distinct/) | ⭐⭐ | ArrayList 如何去重？LinkedHashSet vs Stream |
| [HashSet 替代 LinkedList 查找](replace-linkedlist-with-hashset/) | ⭐⭐ | 什么时候该换数据结构？ |
| [HashMap 扩容](hashmap-resizing/) | ⭐⭐⭐⭐ | 1GB 的 HashMap 扩容会发生什么？ |
| [快速插入大量数据到 HashMap](large-data-into-hashmap/) | ⭐⭐⭐ | 初始化容量 + 负载因子的权衡 |
| [快速给 Map 排序](sort-map/) | ⭐⭐ | TreeMap vs LinkedHashMap 选型 |

### 并发与线程
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [ConcurrentHashMap 原理](concurrent-hashmap/) | ⭐⭐⭐⭐⭐ | ConcurrentHashMap 原理（JDK 7 vs 8） |
| [ThreadLocal 原理](threadlocal/) | ⭐⭐⭐⭐⭐ | ThreadLocal 原理与内存泄漏 |
| [synchronized 锁升级](synchronized-lock-upgrade/) | ⭐⭐⭐⭐⭐ | synchronized 锁升级过程 |
| [volatile 内存语义](volatile/) | ⭐⭐⭐⭐⭐ | volatile 可见性、有序性、原子性 |
| [AQS 框架原理](aqs/) | ⭐⭐⭐⭐⭐ | AbstractQueuedSynchronizer 实现机制 |
| [线程池 7 大参数](thread-pool/) | ⭐⭐⭐⭐⭐ | ThreadPoolExecutor 核心参数详解 |
| [Atomic 替代 synchronized](replace-synchronized-with-atomic/) | ⭐⭐⭐ | CAS 无锁编程 |

### JVM 与类加载
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [JVM 内存区域](jvm-memory/) | ⭐⭐⭐⭐⭐ | JVM 内存模型 + 对象创建流程 |
| [GC 算法与收集器](gc-algorithms/) | ⭐⭐⭐⭐⭐ | GC 算法 + 垃圾收集器对比 |
| [类加载机制](class-loading/) | ⭐⭐⭐⭐⭐ | 双亲委派模型 + 自定义类加载器 |
| [CPU 飙升排查](cpu-spike-troubleshooting/) | ⭐⭐⭐⭐ | 线上 CPU 100% 排查全流程（-Xmx 过小） |
| [JVM 内存配置踩坑](jvm-memory-pitfall/) | ⭐⭐⭐⭐ | -Xmx 超过系统可用内存导致启动失败 |

### 语言基础
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [CompletableFuture 编排](completable-future/) | ⭐⭐⭐⭐ | CompletableFuture 异步任务编排 |
| [== / equals / hashCode](equals-hashcode/) | ⭐⭐⭐⭐ | 相等性判断契约与陷阱 |
| [泛型擦除与 PECS](generics-erasure/) | ⭐⭐⭐⭐ | 类型擦除 + Producer Extends Consumer Super |
| [反射原理与性能](reflection/) | ⭐⭐⭐⭐ | Reflection API 使用与性能开销 |
| [String/Builder/Buffer](string-builder-buffer/) | ⭐⭐⭐ | 字符串拼接选型指南 |
| [StringBuilder 重用](reuse-of-stringbuilder/) | ⭐⭐ | 循环中字符串拼接优化 |
| [final/finally/finalize](final-finally-finalize/) | ⭐⭐⭐ | 三个关键字的区别与用法 |
| [SPI 机制](spi/) | ⭐⭐⭐⭐ | Service Provider Interface 扩展机制 |

### 对象与类型
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [创建对象](create-object/) | ⭐⭐ | Java 创建对象的 5 种方式 |
| [基础类型封装为对象](object/) | ⭐⭐ | 为什么需要 Integer / Double 包装类？ |
| [Integer 缓存](integer-cache/) | ⭐⭐⭐ | -128 到 127 的复用机制与陷阱 |
| [new String("123") 创建几个对象](new-string/) | ⭐⭐⭐⭐ | 字符串常量池 vs 堆 |
| [Record 与泛型](record-t/) | ⭐⭐⭐ | Java 14+ Record 可以用泛型吗？ |

### 设计模式与技巧
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [单例模式](singleton-pattern/) | ⭐⭐⭐ | 5 种实现方式 + 反射 / 序列化破坏 |
| [switch 前用 if 优化](if-before-switch/) | ⭐⭐⭐ | 热点状态的快速路径优化 |

### 综合
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [高频面试题合集](questions/) | ⭐⭐⭐ | Java 综合高频问题速查 |

---

## 学习路径

1. **入门**（1 周）：集合去重 + 对象创建 + Integer 缓存 + String 相关
2. **进阶**（2 周）：HashMap 扩容 + 并发线程 + JVM 内存 + 设计模式
3. **冲刺面试**（1 周）：AQS + 锁升级 + GC 算法 + 类加载 + 高频面试题合集

## 相关章节

- 主模块：[`note/01.java`](../../01.java/) — Java 知识体系
- 相关章节：[`03.database`](../03.database/)（SQL 相关）/ [`06.spring`](../06.spring/)（框架相关）
