# JVM工具

## 一、JDK内置命令行工具
1. **jps（进程状态工具）**
    - 功能：列出所有Java进程PID及主类名，支持远程监控（需配置jstatd）。
    - 场景：快速定位目标Java进程，如`jps -l`显示完整类名。

2. **jstat（统计监控工具）**
    - 功能：实时监控GC、内存、类加载等状态。
    - 示例：`jstat -gcutil <pid> 1000 10`每秒采样GC状态10次，分析Young GC/Full GC频率。

3. **jmap（内存映像工具）**
    - 功能：生成堆转储快照（Heap Dump），分析内存分布。
    - 场景：内存泄漏排查，如`jmap -dump:format=b,file=heap.hprof <pid>`导出堆文件，配合MAT分析。

4. **jstack（线程堆栈工具）**
    - 功能：获取线程快照，定位死锁、高CPU问题。
    - 场景：线上服务卡顿，通过`jstack -l <pid>`分析线程状态，识别死锁或阻塞线程。

5. **jinfo（配置信息工具）**
    - 功能：查看/修改JVM参数（如堆大小），支持动态调整。
    - 示例：`jinfo -flag MaxHeapSize=2048m <pid>`临时调整堆大小。

6. **jcmd（多功能诊断工具）**
    - 功能：集成jmap、jstack等功能，支持GC、线程、内存诊断。
    - 场景：生产环境快速诊断，如`jcmd <pid> Thread.print`输出线程堆栈。

## 二、图形化监控工具
1. **JConsole**
    - 特点：JDK自带轻量级图形工具，监控内存、线程、类加载，支持执行GC操作。

2. **VisualVM**
    - 功能：扩展性强，支持插件（如Visual GC），进行堆转储分析、CPU/内存采样、线程监控。
    - 场景：开发/测试环境性能分析，可连接本地或远程JVM。

3. **JMC（Java Mission Control）**
    - 优势：商业级低开销监控，集成Flight Recorder（需启用`-XX:+FlightRecorder`），记录运行时事件（如GC、线程活动），适合生产环境性能诊断。

## 三、高级分析工具
1. **MAT（Memory Analyzer Tool）**
    - 功能：分析堆转储文件，识别内存泄漏、大对象（如Dominator Tree），支持对象引用链追踪。

2. **Async Profiler**
    - 特点：低开销CPU/内存分析，生成火焰图直观显示热点方法，避免Safepoint偏差。

3. **Arthas**
    - 场景：生产环境在线诊断，支持方法调用追踪（如`watch com.example.Service login`）、线程死锁检测、反编译代码。

4. **GC日志分析工具**
    - 工具：GCViewer、gceasy.io（在线平台），通过JVM参数（如`-Xlog:gc*:file=gc.log`）记录GC日志，分析GC频率和耗时。

## 四、日志与追踪工具
- **ELK Stack**：集中化日志管理（Elasticsearch+Logstash+Kibana），适合生产环境日志监控。
- **BTrace**：动态监控工具，实时插入脚本追踪方法调用、字段访问，适用于动态监控需求。

## 五、工具选择建议
- **开发环境**：优先使用JConsole、VisualVM进行实时监控和调优。
- **生产环境**：推荐低开销工具（如JMC、Arthas），结合日志分析（如GC日志、ELK）。
- **深度分析**：使用MAT、Async Profiler进行内存泄漏和CPU热点分析，配合堆转储文件深入诊断。

## 六、典型故障处理流程
1. **内存泄漏**：通过`jmap -dump`生成堆转储，用MAT分析Dominator Tree，定位大对象或未释放资源。
2. **线程死锁**：使用`jstack -l`获取线程堆栈，分析死锁线程的锁竞争关系。
3. **高CPU使用**：结合`jstack`和Async Profiler生成火焰图，识别CPU热点方法。
4. **GC问题**：通过`jstat -gcutil`监控GC活动，调整JVM参数（如堆大小、GC算法）。
