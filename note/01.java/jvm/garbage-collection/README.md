# 垃圾回收

JVM（Java虚拟机）的垃圾回收（Garbage Collection, GC）是Java自动内存管理的核心机制，负责自动回收不再被程序使用的对象，释放内存空间，避免内存泄漏和手动内存管理的复杂性。

### **1. 垃圾回收的基本原理**
- **对象存活判定**：
    - **引用计数法**：每个对象有一个引用计数，当引用为0时回收。但无法解决循环引用问题（Java未采用）。
    - **可达性分析（根搜索算法）**：从GC Roots（如静态变量、活跃线程栈、JNI引用等）出发，遍历所有可达对象，不可达对象视为“垃圾”。
- **分代假设**：
    - 对象“朝生夕死”，多数对象很快不可达（年轻代），少数长期存活（老年代）。JVM将堆内存分为：
        - **年轻代（Young Generation）**：存放新创建对象，分为Eden区、Survivor区（From/To）。
        - **老年代（Old Generation）**：存放长期存活的对象。
        - **元空间（Metaspace）**：替代永久代，存放类元数据（JDK8+）。

### **2. 垃圾回收的核心流程**
- **Minor GC（年轻代GC）**：
    - 对象在Eden区分配，当Eden满时触发，将存活对象复制到Survivor区（From），并清空Eden。
    - 经过多次Minor GC后，仍存活的对象晋升到老年代。
- **Major GC / Full GC（老年代GC）**：
    - 清理老年代，通常伴随年轻代回收，速度较慢（可能引发Stop-The-World，STW）。
- **GC算法**：
    - **标记-清除**：标记垃圾后直接清除，易产生内存碎片。
    - **复制算法**：将存活对象复制到另一区域，适合年轻代（如Eden→Survivor）。
    - **标记-整理**：移动存活对象至一端，避免碎片，适合老年代。
    - **分代收集**：结合不同区域特点选择算法（年轻代复制，老年代标记-整理）。

### **3. 常见垃圾回收器**
- **年轻代回收器**：
    - **Serial**：单线程，简单高效（适合客户端应用）。
    - **ParNew**：多线程并行，与CMS配合使用。
    - **Parallel Scavenge**：多线程，注重吞吐量（适合后台任务）。
- **老年代回收器**：
    - **Serial Old**：Serial的老年代版。
    - **Parallel Old**：Parallel Scavenge的老年代版，注重吞吐量。
    - **CMS（Concurrent Mark Sweep）**：以最短停顿为目标，并发标记（但存在碎片、浮动垃圾问题）。
- **低延迟回收器**：
    - **G1（Garbage-First）**：将堆划分为Region，优先回收垃圾多的Region，平衡吞吐与停顿（JDK9+默认）。
    - **ZGC（Z Garbage Collector）**：亚毫秒级停顿，使用染色指针、读屏障实现并发整理（JDK11+实验，JDK15+生产可用）。
    - **Shenandoah**：类似ZGC，通过并发压缩减少停顿（OpenJDK分支）。

### **4. 关键调优参数与策略**
- **堆内存设置**：
    - `-Xms`：初始堆大小，`-Xmx`：最大堆大小（建议设置相同避免动态扩容）。
    - `-Xmn`：年轻代大小（通常占堆1/3~1/2）。
- **回收器选择**：
    - `-XX:+UseSerialGC`：客户端模式。
    - `-XX:+UseParallelGC`（默认，JDK8-）/`-XX:+UseG1GC`（JDK9+默认）。
    - `-XX:+UseZGC`：低延迟场景（需JDK11+）。
- **GC日志分析**：
    - 启用日志：`-Xloggc:gc.log -XX:+PrintGCDetails`。
    - 工具：GCViewer、GCEasy、JDK自带的`jstat`/`jmap`/`jconsole`。
- **避免内存泄漏**：
    - 减少静态集合、非静态内部类（隐式持有外部类引用）、监听器未注销等。
    - 使用弱引用（WeakReference）、软引用（SoftReference）管理缓存。

### **5. 常见问题与优化方向**
- **Stop-The-World（STW）**：GC时暂停所有应用线程，影响响应时间。低延迟回收器（ZGC/Shenandoah）通过并发标记/整理减少STW。
- **内存碎片**：老年代使用标记-清除可能导致碎片，可通过`-XX:+UseCompactAtFullGC`（G1）或定期Full GC整理。
- **晋升失败**：年轻代对象在Survivor区放不下，直接晋升到老年代，可能导致老年代频繁GC。可调整Survivor区大小（`-XX:SurvivorRatio`）或晋升阈值（`-XX:MaxTenuringThreshold`）。
- **元空间溢出**：`java.lang.OutOfMemoryError: Metaspace`，需调整`-XX:MaxMetaspaceSize`。

### **6. 最佳实践建议**
- **监控优先**：使用`jstat -gcutil`、VisualVM、JProfiler等工具实时监控GC行为。
- **合理选择回收器**：根据应用场景（吞吐量/低延迟）选择回收器，如高并发服务优先ZGC/G1。
- **避免过度调优**：先通过日志定位问题，再针对性调整参数，避免盲目扩大堆内存。
- **代码优化**：减少不必要的对象创建，及时释放资源（如关闭连接、文件流），使用对象池（如`java.util.concurrent.ArrayBlockingQueue`）。

JVM垃圾回收是一个复杂的系统工程，理解其原理和机制是优化应用性能的关键。在实际开发中，应结合具体场景（如CPU、内存、业务类型）选择合适的回收器和参数，并通过监控工具持续优化。