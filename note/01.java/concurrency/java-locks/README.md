# Java锁

## 1. 按锁的粒度分类
### (1) 对象锁（Instance Lock）
- **作用对象**：实例方法或同步代码块（`synchronized`修饰）。
- **特点**：
    - 锁是当前对象实例（`this`）。
    - 不同实例的锁互不干扰。
- **示例**：
  ```java
  public synchronized void method() { ... } // 锁是当前对象实例
  public void method() {
      synchronized(this) { ... } // 显式使用对象锁
  }
  ```

### (2) 类锁（Class Lock）
- **作用对象**：静态方法或同步代码块（`synchronized`修饰静态方法或`Class`对象）。
- **特点**：
    - 锁是类的`Class`对象（如`MyClass.class`）。
    - 所有实例共享同一把锁。
- **示例**：
  ```java
  public static synchronized void staticMethod() { ... } // 锁是MyClass.class
  public void method() {
      synchronized(MyClass.class) { ... } // 显式使用类锁
  }
  ```

---

## 2. 按锁的实现方式分类
### (1) 同步锁（`synchronized`）
- **内置锁**：Java语言级别的关键字，基于JVM实现。
- **特点**：
    - 可重入（同一线程可多次获取）。
    - 不可中断（除非抛出异常或等待超时）。
    - 公平性由JVM控制（默认非公平）。
- **分类**：
    - **偏向锁**：无竞争时偏向第一个获取锁的线程，减少CAS操作。
    - **轻量级锁**：竞争不激烈时使用自旋等待（CAS操作）。
    - **重量级锁**：竞争激烈时退化为操作系统互斥锁（`mutex`）。

### (2) 显式锁（`java.util.concurrent.locks`）
- **`ReentrantLock`**：
    - 可重入锁，支持公平/非公平模式。
    - 可中断（`lockInterruptibly()`）、可超时（`tryLock(long, TimeUnit)`）。
    - 需手动释放锁（`unlock()`）。
- **`ReadWriteLock`（`ReentrantReadWriteLock`）**：
    - 读写分离锁，读锁共享，写锁独占。
    - 适合读多写少的场景。
- **`StampedLock`**：
    - 支持乐观读，进一步优化读性能。
    - 提供三种模式：写锁、悲观读锁、乐观读。

---

## 3. 按锁的公平性分类
### (1) 公平锁
- **特点**：按照线程请求锁的顺序分配锁，避免线程饥饿。
- **缺点**：性能较低（需维护队列）。
- **示例**：
  ```java
  ReentrantLock fairLock = new ReentrantLock(true); // 公平锁
  ```

### (2) 非公平锁
- **特点**：不保证顺序，可能插队，但性能更高。
- **默认行为**：`synchronized`和`ReentrantLock`默认非公平。
- **示例**：
  ```java
  ReentrantLock nonFairLock = new ReentrantLock(false); // 非公平锁（默认）
  ```

---

## 4. 按锁的乐观/悲观策略分类
### (1) 悲观锁
- **特点**：假设并发冲突频繁，每次操作都加锁。
- **实现**：`synchronized`、`ReentrantLock`。
- **适用场景**：写多读少或高竞争环境。

### (2) 乐观锁
- **特点**：假设并发冲突少，通过版本号或CAS（Compare-And-Swap）实现无锁操作。
- **实现**：
    - `Atomic`类（如`AtomicInteger`）。
    - `StampedLock`的乐观读模式。
- **适用场景**：读多写少或低竞争环境。

---

## 5. 其他特殊锁
### (1) 分布式锁
- **特点**：跨JVM的锁机制，通常基于Redis、ZooKeeper等中间件。
- **实现**：Redisson、Curator。

### (2) 分段锁（Segment Lock）
- **特点**：将数据分段，每段独立加锁（如`ConcurrentHashMap`的早期实现）。
- **目的**：减少锁竞争，提高并发性能。

### (3) 自旋锁（Spin Lock）
- **特点**：线程循环检查锁状态，避免线程切换开销。
- **实现**：`ReentrantLock`的轻量级锁阶段。

---

## 总结对比表
| **锁类型**       | **实现方式**          | **公平性** | **可中断** | **适用场景**               |
|------------------|----------------------|------------|------------|---------------------------|
| `synchronized`   | JVM内置               | 非公平     | 否         | 简单同步需求               |
| `ReentrantLock`  | AQS框架              | 可配置     | 是         | 需要灵活控制的场景         |
| `ReadWriteLock`  | AQS框架              | 可配置     | 是         | 读多写少                  |
| `StampedLock`    | 自定义实现            | 非公平     | 否         | 乐观读优化                |
| 乐观锁（CAS）    | `Atomic`类           | 无锁       | -          | 低竞争、读多写少          |

---

## 选择建议
- **简单场景**：优先使用`synchronized`（JVM优化更成熟）。
- **复杂需求**：如可中断、超时、公平性，选择`ReentrantLock`。
- **读多写少**：使用`ReadWriteLock`或`StampedLock`。
- **高并发无锁**：考虑`Atomic`类或乐观读。

理解锁的分类和特性有助于在并发编程中做出更优的选择，平衡性能和正确性。