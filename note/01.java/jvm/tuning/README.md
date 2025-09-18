# JVM调优

## 一、JVM调优核心参数体系
1. **堆内存管理**
    - **基础参数**：`-Xms`（初始堆）与`-Xmx`（最大堆）建议设为相同值，避免动态扩容开销（如`-Xms4g -Xmx4g`）。
    - **代际划分**：
        - 新生代：`-Xmn`控制大小，`-XX:SurvivorRatio=8`（Eden:Survivor=8:1:1）。
        - 老年代比例：`-XX:NewRatio=2`（老年代:新生代=2:1）。
        - 元空间：`-XX:MetaspaceSize=256m`，避免动态扩容。
    - **GC触发阈值**：`-XX:InitiatingHeapOccupancyPercent=45`（G1触发标记阈值）。

2. **垃圾回收器选择**
    - **高吞吐场景**：Parallel GC（`-XX:+UseParallelGC`），适合批处理/科学计算，通过`-XX:ParallelGCThreads`并行线程数匹配CPU核数。
    - **低延迟场景**：G1 GC（`-XX:+UseG1GC`）或ZGC（`-XX:+UseZGC`），设置`-XX:MaxGCPauseMillis=150`控制暂停时间。
    - **内存敏感场景**：Serial GC（单线程，适合嵌入式系统）。

3. **线程与锁优化**
    - 线程栈大小：`-Xss256k`减少栈内存占用。
    - 锁策略：使用`ReentrantLock`替代`synchronized`，启用自旋锁（`-XX:+UseSpinLock`）减少上下文切换。

## 二、业务场景化调优策略
1. **高并发Web服务**
    - **场景特征**：短生命周期对象多，请求频繁，需低延迟响应。
    - **调优方案**：
        - 回收器：G1 GC + `-XX:MaxGCPauseMillis=150`。
        - 堆设置：`-Xms4g -Xmx4g -Xmn2g`，新生代占比50%减少晋升。
        - 监控：启用GC日志（`-Xloggc:gc.log`）与JFR飞行记录分析。

2. **大数据分析平台**
    - **场景特征**：大对象多，内存占用高，需高吞吐量。
    - **调优方案**：
        - 回收器：Parallel GC + `-XX:GCTimeRatio=19`（95%吞吐量目标）。
        - 堆设置：`-Xms16g -Xmx16g`，老年代占比60%以上。
        - 内存分配：启用`-XX:+AlwaysPreTouch`预分配内存减少碎片。

3. **金融交易系统**
    - **场景特征**：零容忍延迟，需极短STW（Stop-The-World）。
    - **调优方案**：
        - 回收器：ZGC（`-XX:+UseZGC -XX:MaxGCPauseMillis=10`）。
        - 内存管理：`-XX:G1HeapRegionSize=8m`优化Region大小，减少碎片。
        - 诊断：配合`jstat -gcutil`实时监控堆使用率。

4. **内存受限嵌入式系统**
    - **场景特征**：资源稀缺，需最小化内存占用。
    - **调优方案**：
        - 回收器：Serial GC + `-XX:MaxHeapFreeRatio=50`（避免过度扩容）。
        - 线程栈：`-Xss128k`，减少线程内存开销。
        - 对象管理：启用`-XX:+DisableExplicitGC`禁止显式GC调用。

## 三、诊断工具与调优流程
1. **监控工具**：
    - **实时监控**：JVisualVM、JConsole、Arthas（线程/内存快照）。
    - **日志分析**：GC日志（`-XX:+PrintGCDetails`）配合GCEasy在线分析。
    - **内存泄漏检测**：MAT（Memory Analyzer Tool）分析堆转储（`jmap -dump:format=b,file=heap.hprof`）。

2. **调优步骤**：
    - **基准测试**：使用JMH进行微服务性能压测。
    - **参数调整**：每次仅修改1-2个参数（如堆大小/回收器），避免叠加效应。
    - **验证测试**：在测试环境模拟生产负载，验证GC频率与暂停时间。

## 四、常见问题与解决方案
- **频繁Full GC**：增大堆内存（`-Xmx`），调整`-XX:NewRatio`减少晋升，或切换至G1/ZGC。
- **内存泄漏**：使用`jmap -histo`检查对象分布，配合MAT定位泄漏点（如未释放的缓存/连接）。
- **CPU飙升**：通过`jstack`分析线程堆栈，定位高CPU线程（如`RUNNABLE`状态线程）。
- **元空间溢出**：设置`-XX:MaxMetaspaceSize=512m`，检查动态类加载（如热部署工具）。

**总结**：JVM调优需结合业务场景（吞吐量/延迟优先级）、硬件资源（CPU/内存）及监控数据（GC日志/内存快照）动态调整。推荐采用“监控-分析-调优-验证”的闭环流程，持续优化参数以匹配实际负载需求。
