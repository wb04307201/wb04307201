# Java锁机制

Java中的锁机制是并发编程的核心，用于协调多线程对共享资源的访问，避免数据竞争和不一致问题。

## 1. 内置锁：synchronized
- **基本用法**：
    - 修饰代码块：`synchronized(锁对象) { ... }`，锁对象可以是任意对象（如`this`、私有对象）。
    - 修饰方法：`public synchronized void method() { ... }`，锁对象为当前实例（实例方法）或类对象（静态方法）。
- **核心特性**：
    - **可重入性**：同一线程可重复获取同一把锁，避免自身死锁。
    - **非公平性**：线程竞争锁时无固定顺序（JVM优化，减少上下文切换）。
    - **自动释放**：代码块/方法执行结束或异常抛出时自动释放锁，无需手动操作。
- **优化机制（JVM层面）**：
    - **偏向锁**：无竞争时，将对象头标记为偏向当前线程，避免CAS操作。
    - **轻量级锁**：少量竞争时，通过CAS尝试获取锁，避免线程阻塞。
    - **重量级锁**：高竞争时，线程阻塞等待，依赖OS调度。
- **适用场景**：简单同步需求，如单方法级线程安全。

## 2. 显式锁：Lock接口（java.util.concurrent.locks）
- **核心实现类**：`ReentrantLock`（可重入锁）、`ReadWriteLock`（读写锁，含`ReentrantReadWriteLock`）。
- **核心特性**：
    - **可中断等待**：`lockInterruptibly()`允许线程被中断时放弃等待。
    - **超时机制**：`tryLock(long timeout, TimeUnit unit)`在指定时间内尝试获取锁。
    - **公平锁选项**：构造时可指定`fair=true`，按等待顺序分配锁（性能略低，避免线程饥饿）。
    - **条件变量**：`Condition`对象（通过`newCondition()`创建），支持多条件队列（如生产者-消费者模式）。
- **ReentrantLock示例**：
  ```java
  Lock lock = new ReentrantLock();
  try {
      lock.lock(); // 获取锁
      // 临界区代码
  } finally {
      lock.unlock(); // 确保释放锁
  }
  ```
- **ReadWriteLock示例**：
  ```java
  ReadWriteLock rwLock = new ReentrantReadWriteLock();
  Lock readLock = rwLock.readLock();  // 读锁（共享）
  Lock writeLock = rwLock.writeLock(); // 写锁（排他）
  
  // 读操作
  readLock.lock();
  try { /* 读取数据 */ }
  finally { readLock.unlock(); }
  
  // 写操作
  writeLock.lock();
  try { /* 修改数据 */ }
  finally { writeLock.unlock(); }
  ```
- **适用场景**：需要灵活控制锁行为（如超时、条件等待）或高并发读多写少场景（读写锁）。

## 3. 其他锁工具与高级特性
- **StampedLock（Java 8+）**：
    - 支持三种模式：写锁（独占）、读锁（共享）、乐观读（无锁验证）。
    - 乐观读：先无锁读取数据，后通过`validate()`验证数据未被修改，适用于读多写少且对一致性要求适中的场景。
- **Atomic原子类（java.util.concurrent.atomic）**：
    - 基于CAS（Compare-And-Swap）实现无锁更新，如`AtomicInteger`、`AtomicReference`。
    - 适用于简单计数器、标志位等场景，避免锁开销。
- **volatile关键字**：
    - 保证变量的可见性（所有线程立即看到修改），但不保证原子性。
    - 常用于状态标志、单次写入多次读取的场景。
- **锁消除与锁粗化（JVM优化）**：
    - 锁消除：JVM检测到某些对象不可能被共享时，直接去除同步操作（如局部对象）。
    - 锁粗化：将连续的同步操作合并为一次，减少锁开销（如循环内的同步操作外提）。

## 关键对比与选择建议
| **锁类型**       | 优点              | 缺点             | 适用场景           |
|---------------|-----------------|----------------|----------------|
| synchronized  | 简单易用、自动释放、JVM优化 | 无法中断等待、无法设置超时  | 简单同步、低竞争场景     |
| ReentrantLock | 可中断、超时、公平锁、条件队列 | 需手动释放、代码稍复杂    | 复杂同步逻辑、高竞争场景   |
| ReadWriteLock | 读读不阻塞、读写互斥、写写互斥 | 写操作可能饥饿（需调整策略） | 读多写少场景（如配置缓存）  |
| StampedLock   | 乐观读无锁、性能更高      | 使用复杂、需验证数据一致性  | 读多写少且对性能敏感的场景  |
| Atomic原子类     | 无锁、高并发性能好       | 仅支持简单操作        | 计数器、标志位等简单数据更新 |

## 死锁与避免策略
- **死锁成因**：多线程互相持有对方所需锁，且互不释放。
- **避免策略**：
    - 固定锁的获取顺序（如按对象地址排序）。
    - 使用超时机制（如`tryLock(timeout)`）。
    - 使用`java.util.concurrent`中的工具类（如`CountDownLatch`、`CyclicBarrier`）。
    - 避免嵌套锁（减少锁的交叉依赖）。

**总结**：Java的锁机制从内置的synchronized到显式的Lock接口，再到无锁的CAS操作，形成了丰富的并发控制工具链。选择时需结合具体场景（如竞争程度、性能需求、代码复杂度）权衡，优先使用高层次工具（如`ConcurrentHashMap`）而非手动实现锁逻辑，以降低开发成本与出错概率。