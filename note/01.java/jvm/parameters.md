# JVM 常用参数速查手册

> 所有参数基于 HotSpot JVM。参数后标注版本状态：`[JDK8]` 仅 JDK 8 可用，`[JDK17+]` 需要 JDK 17 及以上，`[已移除]` 表示在后续版本中被删除。

---

## LTS 版本关键差异速查

Java 的 LTS（长期支持）版本是 **8、11、17、21、25**。跨版本升级时，JVM 参数有实质性变化的集中在以下几个点：

### 参数行为差异一览

| 差异点 | JDK 8 | JDK 11 | JDK 17 | JDK 21 | JDK 25 |
|--------|-------|--------|--------|--------|--------|
| **默认 GC** | Parallel GC | G1 | G1 | G1 | G1 |
| **CMS 收集器** | ✅ 可用 | ⚠️ 已废弃 | ❌ 已移除 | ❌ | ❌ |
| **ZGC** | ❌ | 实验性 | ✅ 生产可用 | ✅ **分代 ZGC** | ✅ 分代为唯一模式（非分代已移除） |
| **Shenandoah** | ❌ | ❌ | ✅ 生产可用 | ✅ | ✅ |
| **GC 日志格式** | `-Xloggc` 旧格式 | `-Xlog` 统一格式 | `-Xlog` | `-Xlog` | `-Xlog` |
| **偏向锁** | 默认开启 | 默认开启 | **默认关闭** | 已移除 | 已移除 |
| **强封装 JDK 内部** | 不封装 | 不封装 | **强封装**（`--add-opens` 必须） | 同 17 | 同 17 |
| **Metaspace** | 刚替换永久代 | 稳定 | 稳定 | 稳定 | 稳定 |
| **Flight Recorder** | 仅 Oracle JDK | ✅ 免费开放 | ✅ | ✅ | ✅ |
| **字符串去重** | 默认关闭 | 默认关闭 | 默认关闭 | **默认开启** | 默认开启 |
| **虚拟线程** | ❌ | ❌ | ❌ | ✅ **正式发布** | ✅ |
| **NMT**（Native Memory Tracking） | 需显式开启 | 需显式开启 | 需显式开启 | 支持 `detail` 级别 | 同 21 |

### 已废弃 / 已移除参数对照

> 升级 JDK 时，启动脚本里的这些参数必须改掉，否则 JVM 会报错或静默忽略。

| 旧参数 | 状态 | 替代方案 |
|------------------|------|----------|
| `-XX:PermSize=N` | JDK ≤ 7 可用；**JDK 8 起忽略（有警告）** | `-XX:MetaspaceSize=N` |
| `-XX:MaxPermSize=N` | JDK ≤ 7 可用；**JDK 8 起忽略（有警告）** | `-XX:MaxMetaspaceSize=N` |
| `-XX:+UseConcMarkSweepGC` | JDK 9 废弃，**JDK 14 移除** | `-XX:+UseG1GC` 或 `-XX:+UseZGC` |
| `-XX:+UseParNewGC` | JDK 9 废弃，**JDK 14 移除** | 由 G1/ZGC 自动处理 |
| `-XX:+CMSIncrementalMode` | JDK 9 废弃，JDK 14 移除 | 无直接替代 |
| `-XX:+UseBiasedLocking` | JDK 15 废弃，**JDK 18+ 默认关闭** | 无需替代，JVM 自动选择锁策略 |
| `-XX:BiasedLockingStartupDelay` | JDK 15 废弃，JDK 18+ 默认关闭 | 无需替代 |
| `-XX:+PrintGCDetails` | JDK 9 废弃 | `-Xlog:gc*` |
| `-XX:+PrintGCDateStamps` | JDK 9 废弃 | `-Xlog:gc*:...time` |
| `-Xloggc:file` | JDK 9 废弃 | `-Xlog:gc*:file=path` |
| `-XX:+PrintTenuringDistribution` | JDK 9 废弃 | `-Xlog:gc+age=trace` |
| `-XX:+PrintReferenceGC` | JDK 9 废弃 | `-Xlog:gc+ref=debug` |
| `-XX:+PrintAdaptiveSizePolicy` | JDK 9 废弃 | `-Xlog:gc+ergo*=trace` |
| `-XX:+PrintHeapAtGC` | JDK 9 废弃 | `-Xlog:gc+heap=debug` |
| `-XX:MaxGCMinorPauseMillis` | JDK 23 废弃 | `-XX:MaxGCPauseMillis` |

### 从 JDK 8 升级到 JDK 17 的参数改造清单

这是最常见的升级路径，需要改的东西最多：

```diff
  # ═══ 必须改 ═══

  # 1. GC 收集器：CMS 已移除，换 G1 或 ZGC
- -XX:+UseConcMarkSweepGC -XX:+UseParNewGC
+ -XX:+UseG1GC

  # 2. GC 日志：旧格式全部换掉
- -XX:+PrintGCDetails
- -XX:+PrintGCDateStamps
- -Xloggc:/var/log/app/gc.log
+ -Xlog:gc*,gc+age=trace:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=5,filesize=10m

  # 3. 永久代参数：删掉
- -XX:PermSize=256m
- -XX:MaxPermSize=512m
+ -XX:MetaspaceSize=256m
+ -XX:MaxMetaspaceSize=512m

  # 4. 偏向锁：JDK 17 已默认关闭，显式开启反而有警告
- -XX:+UseBiasedLocking
  # ↑ 直接删除此行，不需要替代

  # 5. 强封装：如果用反射访问 JDK 内部类，必须加 --add-opens
+ --add-opens java.base/java.lang=ALL-UNNAMED
+ --add-opens java.base/java.util=ALL-UNNAMED

  # ═══ 建议改 ═══

  # 6. Flight Recorder 现在免费了，可以加上
+ -XX:StartFlightRecording=duration=60s,filename=/tmp/jfr.jfr

  # 7. G1 成为默认 GC，可以不显式指定（但建议还是写上，明确意图）
```

### 从 JDK 17 升级到 JDK 21 的参数改造

相对平滑，主要变化：

```diff
  # ═══ 建议改 ═══

  # 1. 分代 ZGC 大幅提升，低延迟场景强烈推荐
- -XX:+UseZGC
+ -XX:+UseZGC -XX:+ZGenerational

  # 2. 虚拟线程正式发布（不需要 JVM 参数，但需要 JDK 21）
  # 代码层面：使用 Executors.newVirtualThreadPerTaskExecutor()

  # 3. 字符串去重默认开启（减少内存，一般不用管）

  # ═══ 注意 ═══

  # 4. 偏向锁参数已被移除，如果还在用会报错
- -XX:+UseBiasedLocking
  # ↑ 必须删除（JDK 18+ 默认关闭，JDK 19+ 参数已移除）

  # 5. G1 默认 Region 大小算法优化，通常不需要手动设了
  #    如果之前手动设了 G1HeapRegionSize，可以试试去掉让 JVM 自己选
```

---

## 容器环境专属参数（Docker / K8s）

> **这是最容易踩坑的地方**。JVM 在容器里看到的可能不是容器的资源限制，而是宿主机的。

### 容器感知（Container Awareness）

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `-XX:+UseContainerSupport` | 启用容器感知（JVM 读取 cgroup 限制） | JDK 10+ **默认开启** | JDK 8u191+ 才有此参数；**8u191 之前必须手动升级 JDK** |
| `-XX:-UseContainerSupport` | 禁用容器感知 | — | **几乎不要关**，除非你确定容器限制不合理 |
| `-XX:MaxRAMPercentage=N` | 堆占容器可用内存的百分比 | 25%（JDK 8~21）/ **50%（JDK 22+）** | 专用容器设 **75**；共享容器设 **50~60** |
| `-XX:InitialRAMPercentage=N` | 初始堆占容器可用内存的百分比 | 1.5625% | 通常不用设（配合 `-Xms`） |
| `-XX:MinRAMPercentage=N` | 小内存时的最小堆百分比 | 50% | 通常不用改 |

### 为什么这很重要 — 不设置的后果

```text
场景：Docker 容器限制 4GB 内存，宿主机 64GB

JDK 8u190（无容器感知）：
  JVM 看到 64GB → -Xmx 默认 16GB → 容器被 OOM Killed 💀

JDK 8u191+（有容器感知）：
  JVM 看到 4GB → -Xmx 默认 1GB（25%）→ 正常运行但堆太小

正确配置：
  -XX:+UseContainerSupport -XX:MaxRAMPercentage=75
  → JVM 看到 4GB → -Xmx 约 3GB → 合理 ✅
```

### 容器里的 CPU 核数

```text
场景：容器限制 2 核，宿主机 32 核

JDK 默认行为：
  Runtime.getRuntime().availableProcessors() → 32（宿主机核数）
  ParallelGCThreads → 32 → 创建 32 个 GC 线程 → 浪费内存 + 上下文切换

解决方案：
  1. JDK 10+：自动读取 cgroup CPU 限制 ✅
  2. JDK 8：手动指定 -XX:ParallelGCThreads=2 -XX:ConcGCThreads=1
  3. 或者设置 -XX:ActiveProcessorCount=2（JDK 8u191+）
```

| 参数 | 说明 | 建议 |
|------|------|------|
| `-XX:ActiveProcessorCount=N` | 覆盖 JVM 检测到的 CPU 核数 | 设为容器实际的 CPU limit；JDK 10+ 通常自动正确 |

### 容器环境推荐配置

```bash
# Docker 容器通用模板（JDK 17+）
java \
  -XX:+UseContainerSupport \              # 启用容器感知
  -XX:MaxRAMPercentage=75 \               # 堆占容器内存的 75%
  -XX:InitialRAMPercentage=75 \           # 初始堆也一样（避免扩容）
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=100 \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/tmp/heapdump.hprof \
  -Xlog:gc*:file=/var/log/app/gc.log:time,uptime:filecount=3,filesize=10m \
  -jar myapp.jar
```

> **注意**：`MaxRAMPercentage=75` 意味着堆占 75%，剩下 25% 给堆外内存。容器内存越紧张，这个值越要精确计算。

---

## 一、堆内存参数

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `-Xms` | 初始堆大小 | 物理内存的 1/64 | **设为与 `-Xmx` 相同**，避免运行时动态扩容的开销和 STW |
| `-Xmx` | 最大堆大小 | 物理内存的 1/4 | 根据服务器可用内存计算（见 [tuning.md](tuning.md)） |
| `-Xmn` | 新生代大小 | 堆的约 1/3 | 通常为堆的 1/3~1/2；设太大会挤压老年代 |
| `-Xss` | 每个线程的栈大小 | 1MB (64位) | 256k~512k 通常够用；线程多时减小可节省内存 |

**要点**：
- `-Xms` 和 `-Xmx` 设成一样是最重要的一条规则 — 消除扩容带来的停顿
- `-Xmn` 和 `-XX:NewRatio` 二选一，不要同时设

---

## 二、分代与晋升参数

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `-XX:NewRatio` | 老年代:新生代的比例 | 2（即老年代占 2/3） | 一般不用改；对象创建密集可调为 1 |
| `-XX:SurvivorRatio` | Eden:每个 Survivor 的比例 | 8（即 8:1:1） | Survivor 放不小可调小（如 6），让 Survivor 更大 |
| `-XX:MaxTenuringThreshold` | 对象在 Survivor 中经历 GC 的次数上限 | 15 | 默认 15 通常够用；频繁晋升到老年代可适当调大 |
| `-XX:PretenureSizeThreshold` | 超过此大小的对象直接进老年代 | 0（不启用） | 仅 Serial/ParNew 生效；G1 用 `-XX:G1HeapRegionSize` 间接控制 |
| `-XX:+DisableExplicitGC` | 禁用 `System.gc()` | 不禁用 | **建议加上**，防止代码或第三方库乱调 GC |
| `-XX:+AlwaysPreTouch` | 启动时预分配并触碰所有堆内存页 | 关闭 | 生产环境建议开启，避免运行时分配内存页的延迟 |

**Survivor 放不下的判断**：
```text
# 观察 GC 日志中是否有：
"Desired survivor size XXX bytes, new threshold N"
# 如果 threshold 被自动调低了（如降到 3），说明 Survivor 太小
# 解决：减小 SurvivorRatio（如从 8 改为 6），增大 Survivor 空间
```

---

## 三、元空间参数

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `-XX:MetaspaceSize` | 元空间初始大小 | 约 20MB | 设为 256m，避免启动时频繁触发 GC 扩容 |
| `-XX:MaxMetaspaceSize` | 元空间最大大小 | 无上限 | 建议设一个上限（如 512m），防止无限增长 |

**什么时候该关注**：
- Spring Boot + 大量 AOP 代理 → 动态生成很多类
- 热部署 / 频繁重新加载 → 类卸载不及时
- OOM: Metaspace → 先排查是否有类加载泄漏，再调大上限

> JDK ≤ 7 用户注意：永久代参数 `-XX:PermSize` / `-XX:MaxPermSize` 从 JDK 8 起已被忽略（启动时会打印警告）。
> 升级到 JDK 8+ 后应替换为上方表格中的 `-XX:MetaspaceSize` / `-XX:MaxMetaspaceSize`。
> 完整的新旧参数对照见 [已废弃 / 已移除参数对照](#已废弃--已移除参数对照)。

---

## 四、GC 收集器选择参数

| 参数 | 收集器 | 适用场景 | JDK 要求 |
|------|--------|----------|----------|
| `-XX:+UseSerialGC` | Serial + Serial Old | 单核 / 嵌入式 / 内存 < 100MB | 所有版本 |
| `-XX:+UseParallelGC` | Parallel Scavenge + Parallel Old | 高吞吐、批处理、不在乎延迟 | 所有版本（JDK 8 默认） |
| `-XX:+UseParNewGC` | ParNew（配合 CMS） | [JDK8] CMS 的新生代搭档 | JDK 8 |
| `-XX:+UseConcMarkSweepGC` | CMS | [JDK8] 低延迟 | JDK 8（JDK 14 移除） |
| `-XX:+UseG1GC` | G1 | **通用首选**，堆 ≤ 16G | JDK 7+（JDK 9+ 默认） |
| `-XX:+UseZGC` | ZGC | 大堆 + 极低延迟 | JDK 15+ 正式发布，JDK 17+ 生产推荐 |
| `-XX:+UseShenandoahGC` | Shenandoah | 低延迟，类似 ZGC | JDK 15+（OpenJDK） |

**选择决策**：

```text
JDK 版本？
├── JDK ≤ 8 → 延迟敏感？
│   ├── 是 → -XX:+UseConcMarkSweepGC（CMS）
│   └── 否 → -XX:+UseParallelGC（默认）
├── JDK 9~14 → -XX:+UseG1GC（默认，通用最优）
└── JDK 15+ → 延迟要求？
    ├── 极低（< 1ms）→ -XX:+UseZGC
    ├── 中等（< 200ms）→ -XX:+UseG1GC（默认）
    └── 不在乎 → -XX:+UseParallelGC
```

---

## 五、GC 行为调优参数

### 通用参数

| 参数 | 说明 | 建议 |
|------|------|------|
| `-XX:ParallelGCThreads=N` | GC 并行线程数（STW 阶段） | 默认 CPU 核数（≤8 时）；8 核以上：`8 + (N-8)*5/8` |
| `-XX:ConcGCThreads=N` | GC 并发线程数（不停顿阶段） | 默认 ParallelGCThreads 的 1/4 |
| `-XX:GCTimeRatio=N` | 吞吐量目标：应用时间 / GC 时间 ≥ N | 默认 99（即 GC 时间 ≤ 1%） |

### G1 专用参数

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `-XX:MaxGCPauseMillis=N` | 目标最大 GC 停顿时间 | 200ms | 根据业务 SLA 设定，如 Web 服务 100~200ms |
| `-XX:G1HeapRegionSize=N` | Region 大小 | 自动（1~32MB） | 堆大时可设为 8m 或 16m |
| `-XX:InitiatingHeapOccupancyPercent=N` | 堆占用率达到多少时触发并发标记 | 45% | 默认 45%；频繁 Full GC 可调低（如 35） |
| `-XX:G1ReservePercent=N` | 保留多少空间防止 to-space exhausted | 10% | 默认 10%；大对象多可调高 |
| `-XX:G1MixedGCCountTarget=N` | Mixed GC 的轮次目标 | 8 | 调大可以分摊每轮的回收量 |
| `-XX:G1HeapWastePercent=N` | 老年代可回收垃圾低于此比例时停止 Mixed GC | 5% | 默认 5%；设低可以继续回收更多垃圾 |

### Parallel GC 专用参数

| 参数 | 说明 | 建议 |
|------|------|------|
| `-XX:MaxGCPauseMillis=N` | 目标最大停顿时间 | Parallel GC 会自适应调整 |
| `-XX:MaxGCMinorPauseMillis=N` | 目标 Minor GC 最大停顿 | 同上 |
| `-XX:GCTimeRatio=N` | 吞吐量比例目标 | 默认 99，批处理可调到 19（GC ≤ 5%） |
| `-XX:+UseAdaptiveSizePolicy` | 自适应调节新生代大小 | **默认开启，建议保持** |

### ZGC 专用参数

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `-XX:MaxGCPauseMillis=N` | 目标停顿时间 | 1ms | ZGC 默认就是亚毫秒，通常不用调 |
| `-XX:SoftMaxHeapSize=N` | 软性堆上限（ZGC 会尽量不超） | 无 | 设成接近 `-Xmx`，帮助 ZGC 更积极地回收 |
| `-XX:ZCollectionInterval=N` | 固定 GC 间隔（秒），0=不固定 | 0 | 需要定期回收可设（如 120） |
| `-XX:+ZGenerational` | 启用分代 ZGC（吞吐+延迟双优） | 关闭（JDK 21）/ **默认开启**（JDK 23+） | **JDK 21 低延迟场景强烈推荐**（JEP 439，生产特性） |

---

## 六、GC 日志参数

### JDK 9+ 统一日志格式（推荐）

```bash
# 基础配置：GC 日志输出到文件，滚动保留 5 个文件，每个 10MB
-Xlog:gc*:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=5,filesize=10m

# 详细配置：包含 GC、堆、元空间信息
-Xlog:gc*,gc+heap=debug:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=5,filesize=20m

# 打印安全点信息（排查 STW 延迟）
-Xlog:gc+safepoint=info:file=/var/log/app/gc.log
```

### JDK 8 格式（旧）

```bash
# 基础配置
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-Xloggc:/var/log/app/gc.log

# 详细配置
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-XX:+PrintTenuringDistribution     # 打印对象晋升年龄分布
-XX:+PrintHeapAtGC                 # GC 前后堆信息
-XX:+PrintReferenceGC              # 引用处理耗时
-Xloggc:/var/log/app/gc.log

# 大堆时打印堆区域变化（G1）
-XX:+PrintAdaptiveSizePolicy
```

### 日志中看什么

```text
# JDK 9+ 格式示例
[2024-01-15T10:30:05.123+0800][12.345s][info][gc] GC(0) Pause Young (Normal) (G1 Evacuation Pause) 209M->45M(2048M) 8.234ms
                                                    ↑        ↑              ↑                     ↑      ↑
                                                    第几次GC  类型           触发原因              前→后   耗时

关键指标：
- 频率：Young GC 几分钟一次正常，Full GC 几小时一次以上就有问题
- 耗时：Young GC < 50ms 正常，Full GC < 200ms 可接受
- 回收后使用率：GC 后仍 > 80% → 堆不够或有泄漏
```

---

## 七、引用类型与 GC 行为

Java 有四种引用类型，GC 对它们的回收策略完全不同。理解这个对写缓存、避免 ThreadLocal 泄漏至关重要。

| 引用类型 | 创建方式 | GC 行为 | 典型用途 |
|----------|----------|---------|----------|
| **强引用** | `Object o = new Object()` | 只要强引用存在，**永远不回收** | 普通变量，绝大多数场景 |
| **软引用** | `SoftReference<Object> sr = new SoftReference<>(obj)` | **内存不足时才回收** | 缓存（内存紧张时自动清理） |
| **弱引用** | `WeakReference<Object> wr = new WeakReference<>(obj)` | **下次 GC 就回收**（不管内存够不够） | `ThreadLocal`、`WeakHashMap` |
| **虚引用** | `PhantomReference<Object> pr = new PhantomReference<>(obj, queue)` | 随时可回收，无法通过引用获取对象 | 跟踪对象被回收的时机（资源清理） |

**GC 回收优先级**：
```text
强引用 → 永不回收（OOM 也不回收）
  ↓ 失去强引用后
软引用 → 内存不足时回收（GC 会尽量保留）
  ↓ 失去软引用后
弱引用 → 下次 GC 立刻回收
  ↓ 失去弱引用后
虚引用 → 入队通知，对象已死
```

**实际影响**：

```java
// 1. 软引用做缓存 — 内存紧张时自动清理
Map<String, SoftReference<byte[]>> cache = new HashMap<>();
cache.put("key", new SoftReference<>(new byte[1024 * 1024]));

// 2. ThreadLocal 用弱引用 — 但 key 弱引用不意味着 value 也弱！
//    ThreadLocalMap 的 key 是弱引用，value 是强引用
//    → 线程不销毁时 value 永远不会被回收 → 内存泄漏！
ThreadLocal<Session> session = ThreadLocal.withInitial(Session::new);
// 必须在使用完后显式 remove()
session.remove();

// 3. WeakHashMap — key 被回收时整个 entry 自动移除
Map<Key, Value> map = new WeakHashMap<>();
```

**GC 调优相关**：
- 大量软引用对象 → Minor GC 时需要额外判断"内存是否充足"，可能拖慢 GC
- `-XX:SoftRefLRUPolicyMSPerMB=N`：控制软引用的存活时间（默认 1000ms/MB 空闲堆），调小可以更积极地回收软引用

---

## 八、JIT 编译参数

| 参数 | 说明 | 建议 |
|------|------|------|
| `-XX:+TieredCompilation` | 启用分层编译（C1 + C2） | **JDK 8+ 默认开启，不要关** |
| `-XX:CompileThreshold=N` | 方法编译阈值（调用多少次触发 JIT） | 默认 10000（分层编译下自动调节，一般不改） |
| `-XX:ReservedCodeCacheSize=N` | JIT 编译后的机器码缓存大小 | 默认 240MB；大型应用可调到 512m |
| `-XX:+PrintCompilation` | 打印 JIT 编译事件 | 排查编译问题时临时开启 |
| `-XX:-UseCompilation` | 禁用 JIT（纯解释执行） | **永远不要在生产环境用**，仅供调试 |

---

## 九、直接内存参数

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `-XX:MaxDirectMemorySize=N` | 直接内存最大大小 | 等于 `-Xmx` | 不用 NIO 可设小（如 256m）；NIO 密集按需调大 |

**什么时候关注**：
- Netty / NIO 应用 → 直接内存用量大
- OOM: Direct buffer memory → 检查是否有 buffer 未释放

---

## 十、诊断与调试参数

### OOM 时自动保存现场

```bash
# 发生 OOM 时自动 dump 堆（必加）
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/heapdump.hprof

# OOM 时直接退出进程（配合 K8s 自动重启，容器环境必加）
-XX:+ExitOnOutOfMemoryError

# OOM 时执行自定义脚本（如发告警）
-XX:OnOutOfMemoryError="/opt/scripts/oom-alert.sh %p"
```

| 参数 | 说明 | 建议 |
|------|------|------|
| `-XX:+HeapDumpOnOutOfMemoryError` | OOM 时自动导出堆转储 | **生产环境必加** |
| `-XX:HeapDumpPath=N` | 堆转储文件路径 | 指向有足够空间的目录 |
| `-XX:+ExitOnOutOfMemoryError` | OOM 时直接退出 JVM | **容器环境必加**，配合 K8s 自动重启 |
| `-XX:OnOutOfMemoryError=cmd` | OOM 时执行自定义命令 | 用于发告警或执行清理脚本 |

### JFR（Java Flight Recorder）

```bash
# JDK 11+ 免费使用（JDK 8 需 Oracle JDK）
-XX:StartFlightRecording=duration=60s,filename=/tmp/recording.jfr
-XX:FlightRecorderOptions=stackdepth=128
```

### 常用诊断开关

| 参数 | 说明 | 场景 |
|------|------|------|
| `-XX:+PrintFlagsFinal` | 启动时打印所有 JVM 参数的最终值 | 确认参数是否生效 |
| `-XX:+PrintVMOptions` | 打印启动时的 JVM 选项 | 排查启动问题 |
| `-verbose:gc` | 每次 GC 打印一行摘要 | 快速观察 GC 行为 |
| `-XX:+UnlockDiagnosticVMOptions` | 解锁诊断参数 | 使用高级诊断参数时需要先加这个 |
| `-XX:+PrintSafepointStatistics` | 打印安全点统计 | 排查 STW 延迟 |
| `-XX:NativeMemoryTracking=summary` | 跟踪 JVM 本地内存使用 | `jcmd <pid> VM.native_memory summary` 查看 |

---

## 十一、常用 JDK 诊断命令速查

| 命令 | 用途 | 示例 |
|------|------|------|
| `jps -l` | 列出 Java 进程 | 找到目标进程 PID |
| `jstat -gcutil <pid> 1000` | 每秒打印 GC 使用率 | 实时观察 GC 状态 |
| `jstat -gc <pid> 1000 10` | 每秒打印 GC 详情，共 10 次 | 详细分析 |
| `jmap -heap <pid>` | 查看堆配置和使用情况 | 快速检查堆状态 |
| `jmap -dump:format=b,file=heap.hprof <pid>` | 导出堆转储 | MAT 分析内存泄漏 |
| `jmap -histo <pid>` | 对象数量和大小的直方图 | 快速找大对象 |
| `jstack <pid>` | 线程堆栈快照 | 排查死锁、CPU 高 |
| `jstack -l <pid>` | 线程堆栈 + 锁信息 | 排查锁竞争 |
| `jinfo -flags <pid>` | 查看 JVM 启动参数 | 确认线上参数 |
| `jcmd <pid> VM.flags` | 查看 JVM 参数 | 同 jinfo |
| `jcmd <pid> GC.heap_dump /tmp/dump.hprof` | 堆转储（推荐替代 jmap） | 对生产影响更小 |
| `jcmd <pid> VM.native_memory summary` | 本地内存概况 | 需开启 NMT |

### Arthas（生产环境推荐）

```bash
# 安装
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar

# 常用命令
dashboard          # 实时仪表盘（线程、内存、GC）
thread -n 3        # CPU 最高的 3 个线程
watch com.example.Service getUser '{params, returnObj, throwExp}' -n 5  # 观察方法调用
trace com.example.Service getUser '#cost > 100'  # 方法耗时追踪
sc -d com.example.Service  # 查看类加载信息
jad com.example.Service    # 反编译（确认线上代码版本）
```
