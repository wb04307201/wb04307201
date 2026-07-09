<!--
module:
  parent: java
  slug: java/jvm/tuning
  type: article
  category: 主模块子文章
  summary: JVM 调优实战——根据服务器配置选择合理的 JVM 启动参数。
-->

# JVM 调优 — 根据服务器配置选择参数

> 目标：拿到一台服务器，按本文档的步骤和模板，配出合理的 JVM 启动参数。

---

## 一、调优前的信息采集

在写任何 JVM 参数之前，先搞清楚四件事：

### 1. 服务器配置

```bash
# CPU 核数
nproc              # Linux
sysctl -n hw.ncpu  # macOS

# 总内存
free -h            # Linux
vm_stat            # macOS

# 磁盘 IO（影响 GC 日志写入）
iostat -x 1 5

# 同一台机器上还有哪些进程
top -bn1 | head -20
```

需要记录：
- CPU 核数：决定 GC 线程数
- 总内存：决定堆能分多少
- 是否有其他进程占用内存（Redis、MQ、Nginx 等）

### 2. 应用类型

| 类型 | 特征 | 性能重点 |
|------|------|----------|
| Web 微服务 | 大量短请求，短生命周期对象多 | 低延迟（P99 响应时间） |
| 大数据/批处理 | 大对象多，内存占用高 | 高吞吐 |
| 定时任务 | 周期性尖峰，平时空闲 | 稳定、不 OOM |
| 金融交易 | 毫秒级延迟敏感 | 极低延迟 + 稳定性 |

### 3. 性能目标

- **低延迟优先**：P99 < 200ms → 选 G1/ZGC，目标减少 STW
- **高吞吐优先**：TPS 越高越好 → 选 Parallel GC，允许较长停顿换吞吐
- **稳定优先**：不能 OOM、不能抖动 → 保守配置，留足余量

### 4. JDK 版本

```bash
java -version
```

JDK 版本决定了可用的 GC 收集器和参数格式（GC 日志 JDK 9+ 大改）。

### LTS 版本选择速查

不同 LTS 版本可用的 GC 和核心能力差异很大，选参数前先确认版本：

```
JDK 8（LTS，仍有大量生产环境）
├── 默认 GC：Parallel GC
├── 低延迟选：CMS + ParNew（注意：JDK 14 移除 CMS）
├── GC 日志：旧格式（-Xloggc、-XX:+PrintGCDetails）
├── 偏向锁：默认开启
└── 无 ZGC、无 Shenandoah、无分代 ZGC

JDK 11（LTS）
├── 默认 GC：G1（从 JDK 9 开始）
├── ZGC：实验性，不建议生产使用
├── GC 日志：统一格式（-Xlog）
└── JFR 免费开放

JDK 17（LTS，当前最推荐的长期版本）
├── 默认 GC：G1
├── ZGC：生产可用
├── 偏向锁：默认关闭（JDK 15 废弃）
├── 强封装 JDK 内部 API（需 --add-opens）
└── CMS 已移除

JDK 21（LTS，功能最丰富的当前版本）
├── 默认 GC：G1
├── ZGC：✅ 分代 ZGC（-XX:+ZGenerational），性能飞跃
├── 虚拟线程正式发布
├── 偏向锁已移除
└── 字符串去重默认开启

JDK 25（LTS，最新）
├── 延续 JDK 21~24 的所有特性
├── ZGC 分代为唯一模式（非分代已移除，JEP 490）
├── -XX:+ZGenerational 变为废弃参数（使用 -XX:+UseZGC 即可）
└── 值类型（Valhalla）预览，对内存布局有深远影响
```

> **版本选择建议**：新项目直接 JDK 21；存量 JDK 8 项目优先升 17（最稳），再考虑 21。

---

## 二、堆大小怎么算

### 核心公式

```
最大堆大小 (-Xmx) = 服务器总内存
                    - 操作系统预留（通常 1~2GB 或总内存 10~15%）
                    - 其他进程占用
                    - 堆外内存预留
```

### 堆外内存怎么估算

JVM 不只用堆，还有很多堆外开销：

| 堆外区域 | 估算公式 | 示例 |
|----------|----------|------|
| Metaspace | 按实际加载类数量，通常 200~500MB | Spring Boot 应用约 256MB |
| 线程栈 | 线程数 × `-Xss` | 500 线程 × 512k = 256MB |
| 直接内存 | 按实际使用，NIO/Netty 应用可能很大 | 不用 NIO 约 0~128MB |
| JVM 自身 | Code Cache + 内部结构 | 约 200~400MB |
| GC 开销 | G1/ZGC 的 Remembered Set 等 | 堆的 5~20% |

**粗略估算**：堆外内存 ≈ **1~2GB**（非 NIO 密集型应用）

### 各服务器配置计算示例

#### 4GB 服务器

```
总内存：4GB
- OS 预留：1GB
- 其他进程：0.5GB（假设有 Nginx）
- 堆外内存：1GB
────────────────
可用堆 = 4 - 1 - 0.5 - 1 = 1.5GB

推荐配置：-Xms1536m -Xmx1536m
```

#### 8GB 服务器

```
总内存：8GB
- OS 预留：1.5GB
- 其他进程：0.5GB
- 堆外内存：1.5GB
────────────────
可用堆 = 8 - 1.5 - 0.5 - 1.5 = 4.5GB

推荐配置：-Xms4g -Xmx4g
```

#### 16GB 服务器

```
总内存：16GB
- OS 预留：2GB
- 其他进程：1GB
- 堆外内存：2GB
────────────────
可用堆 = 16 - 2 - 1 - 2 = 11GB

推荐配置：-Xms10g -Xmx10g（保守）或 -Xms12g -Xmx12g（激进）
```

#### 32GB 服务器

```
总内存：32GB
- OS 预留：3GB
- 其他进程：2GB
- 堆外内存：3GB
────────────────
可用堆 = 32 - 3 - 2 - 3 = 24GB

推荐配置：-Xms20g -Xmx20g（保守）或 -Xms24g -Xmx24g（激进）
```

#### 64GB+ 服务器

```
大内存服务器的原则：
- 不要把所有内存都给堆 → 留给 OS 做文件缓存反而更快
- 堆越大 → Full GC 越慢（G1/ZGC 可以缓解）
- 考虑拆成多个 JVM 实例（容器化），而不是一个巨大 JVM

推荐：单实例堆不超过 32GB（超过 32GB 指针压缩失效，内存利用率反而下降）
```

> **关于 32GB 阈值**：HotSpot 开启了压缩指针（`-XX:+UseCompressedOops`，默认开启），对象指针用 4 字节表示，但只能寻址约 32GB。超过 32GB 后指针变成 8 字节，实际可用内存反而可能更少。所以堆设到 26~30GB 是甜点。

---

## 三、GC 收集器怎么选

```
你的 JDK 版本？
│
├── JDK 8（LTS）
│   ├── 延迟敏感（Web 服务）→ CMS + ParNew
│   │   -XX:+UseConcMarkSweepGC -XX:+UseParNewGC
│   │   ⚠️ CMS 在 JDK 14 移除，升级后必须换 G1
│   │
│   └── 吞吐优先（批处理）→ Parallel GC（默认）
│       -XX:+UseParallelGC
│
├── JDK 11（LTS）
│   └── G1（默认，最优选择）
│       -XX:+UseG1GC
│       ⚠️ ZGC 此时为实验性，不建议生产使用
│
├── JDK 17（LTS，推荐）
│   ├── 通用场景 → G1（默认）
│   │   -XX:+UseG1GC
│   │
│   └── 低延迟（P99 < 50ms）→ ZGC
│       -XX:+UseZGC
│       ⚠️ 此时 ZGC 为非分代，堆大时吞吐不如 G1
│
├── JDK 21（LTS，功能最全）
│   ├── 通用场景 → G1（默认）
│   │   -XX:+UseG1GC
│   │
│   ├── 低延迟 → 分代 ZGC ⭐（强烈推荐）
│   │   -XX:+UseZGC -XX:+ZGenerational
│   │   分代 ZGC 吞吐和延迟都优于非分代版
│   │
│   └── 大堆 + 低延迟 → 分代 ZGC
│       -XX:+UseZGC -XX:+ZGenerational
│
└── JDK 25（LTS，最新）
    └── 延续 JDK 21 路线，分代 ZGC 成为默认模式
```

### 各收集器一句话

| 收集器 | 一句话 | 堆大小建议 | 可用版本 |
|--------|--------|-----------|----------|
| Serial GC | 最简单，单线程，适合小内存 | < 100MB | 所有版本 |
| Parallel GC | 吞吐王，STW 长但总处理量大 | 任意 | 所有版本（JDK 8 默认） |
| CMS | 低延迟但有碎片，**JDK 14 已移除** | 1~8GB | JDK 8（升级后必须换） |
| G1 | 通用首选，停顿可控 | 1~16GB | JDK 7+（JDK 9+ 默认） |
| ZGC | 停顿 < 1ms，堆越大优势越明显 | 4GB ~ 数 TB | JDK 15+ 正式发布，JDK 17+ 生产推荐 |
| ZGC 分代 | 吞吐+延迟双优，**JDK 21 最大亮点** | 4GB ~ 数 TB | JDK 21+（`-XX:+ZGenerational`） |
| Shenandoah | 类似 ZGC，OpenJDK 生态 | 4GB+ | JDK 15+ |

---

## 四、典型场景的完整配置

### 场景 A：8GB 服务器 — Web 微服务（低延迟优先）

**服务器信息**：8GB 内存，4 核 CPU，JDK 17，Spring Boot 微服务

```bash
java \
  # === 堆内存 ===
  -Xms4g -Xmx4g \                          # 堆固定 4GB，不动态扩容
  -XX:MetaspaceSize=256m \                  # 元空间初始大小，避免启动期 GC
  -XX:MaxMetaspaceSize=512m \               # 元空间上限，防无限增长
  \
  # === GC 收集器 ===
  -XX:+UseG1GC \                            # G1 收集器，通用首选
  -XX:MaxGCPauseMillis=100 \                # 目标停顿 100ms（Web 服务 SLA）
  -XX:G1HeapRegionSize=4m \                 # Region 4MB（4G 堆适合小 Region）
  -XX:InitiatingHeapOccupancyPercent=45 \   # 堆占用 45% 时开始并发标记
  \
  # === GC 线程 ===
  -XX:ParallelGCThreads=4 \                 # STW 阶段并行线程数 = CPU 核数
  -XX:ConcGCThreads=1 \                     # 并发阶段线程数 = 并行的 1/4
  \
  # === GC 日志 ===
  -Xlog:gc*,gc+age=trace,safepoint:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=5,filesize=10m \
  \
  # === 安全网 ===
  -XX:+HeapDumpOnOutOfMemoryError \         # OOM 时自动 dump
  -XX:HeapDumpPath=/var/log/app/heapdump.hprof \
  -XX:+AlwaysPreTouch \                     # 启动时预分配内存页
  -XX:+DisableExplicitGC \                  # 禁用 System.gc()
  \
  # === 应用 ===
  -jar myapp.jar
```

**为什么这么配**：
- 4G 堆用 G1，Region 设 4MB（堆小不需要大 Region）
- `MaxGCPauseMillis=100`：Web 服务需要快速响应，100ms 停顿用户无感知
- 4 核机器 `ParallelGCThreads=4`，STW 阶段用满所有核
- `ConcGCThreads=1`：并发阶段只用 1 个线程，留 3 个核给应用

---

### 场景 A-JDK8：8GB 服务器 — Web 微服务（JDK 8 版本）

> 与场景 A 同硬件，但跑 JDK 8。对比差异可清楚看到版本带来的参数变化。

**服务器信息**：8GB 内存，4 核 CPU，**JDK 8**，Spring Boot 微服务

```bash
java \
  # === 堆内存 ===
  -Xms4g -Xmx4g \
  -XX:MetaspaceSize=256m \                  # JDK 8 已有元空间
  -XX:MaxMetaspaceSize=512m \
  \
  # === GC 收集器 ===
  # JDK 8 下 CMS 仍可用（JDK 17 已移除！）
  -XX:+UseConcMarkSweepGC \                 # CMS 低延迟
  -XX:+UseParNewGC \                        # CMS 的新生代搭档
  -XX:CMSInitiatingOccupancyFraction=75 \   # 老年代 75% 时开始 CMS
  -XX:+UseCMSInitiatingOccupancyOnly \      # 只在达到阈值时触发，不自动调节
  -XX:+CMSScavengeBeforeRemark \            # Remark 前先 YGC，加速 Remark
  \
  # === GC 线程 ===
  -XX:ParallelGCThreads=4 \
  -XX:ConcGCThreads=2 \
  \
  # === GC 日志（JDK 8 旧格式，JDK 9+ 必须换！）===
  -XX:+PrintGCDetails \
  -XX:+PrintGCDateStamps \
  -XX:+PrintTenuringDistribution \
  -Xloggc:/var/log/app/gc.log \
  \
  # === 安全网 ===
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/app/heapdump.hprof \
  -XX:+AlwaysPreTouch \
  \
  -jar myapp.jar
```

**与 JDK 17 版本的关键差异**：

| 差异点 | JDK 8（本模板） | JDK 17（场景 A） |
|--------|----------------|-----------------|
| GC 收集器 | CMS + ParNew | G1 |
| GC 日志 | `-XX:+PrintGCDetails` | `-Xlog:gc*` |
| 偏向锁 | 默认开启，不用管 | 默认关闭，不需要设 |
| 强封装 | 无此问题 | 需 `--add-opens` |
| 推荐升级路径 | → JDK 17（见升级清单） | — |

> **JDK 8 → 17 升级时**，这个模板应改为场景 A 的配置。具体改造清单见 [parameters.md](parameters.md) 中的"从 JDK 8 升级到 JDK 17"章节。

---

### 场景 B：16GB 服务器 — 大数据/批处理（高吞吐优先）

**服务器信息**：16GB 内存，8 核 CPU，JDK 11，Spark/Flink 类批处理

```bash
java \
  # === 堆内存 ===
  -Xms10g -Xmx10g \                         # 堆固定 10GB
  -XX:MetaspaceSize=256m \
  -XX:MaxMetaspaceSize=512m \
  \
  # === GC 收集器 ===
  -XX:+UseG1GC \                            # G1（JDK 11 稳定选择）
  -XX:MaxGCPauseMillis=500 \                # 允许较长停顿，换取吞吐
  -XX:G1HeapRegionSize=8m \                 # Region 8MB（大堆适合大 Region）
  -XX:InitiatingHeapOccupancyPercent=40 \   # 提前开始标记，避免 Full GC
  \
  # === GC 线程 ===
  -XX:ParallelGCThreads=8 \                 # STW 阶段 8 线程
  -XX:ConcGCThreads=2 \                     # 并发 2 线程
  \
  # === 性能 ===
  -XX:+AlwaysPreTouch \                     # 预分配
  -XX:-UseBiasedLocking \                   # 关闭偏向锁（高并发下撤销开销大）⚠️ JDK 18+ 默认关闭此参数
  -XX:+ParallelRefProcEnabled \             # 并行处理引用（加速 Full GC）
  \
  # === GC 日志 ===
  -Xlog:gc*:file=/var/log/app/gc.log:time,uptime:filecount=5,filesize=20m \
  \
  # === 安全网 ===
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/app/heapdump.hprof \
  \
  -jar myapp.jar
```

**为什么这么配**：
- `MaxGCPauseMillis=500`：批处理不在乎单次停顿长，吞吐优先
- `InitiatingHeapOccupancyPercent=40`：大堆 Full GC 代价极大，提前标记
- 关闭偏向锁：批处理通常高并发，偏向锁的撤销开销反而更大（⚠️ JDK 18+ 默认关闭此参数，升级后可直接删除此行）

---

### 场景 C：32GB 服务器 — 金融交易（极低延迟）

**服务器信息**：32GB 内存，16 核 CPU，JDK 21，交易系统

```bash
java \
  # === 堆内存 ===
  -Xms20g -Xmx20g \                         # 堆固定 20GB（不超过 32GB 阈值）
  -XX:MetaspaceSize=512m \                  # 交易系统类多，元空间给大一点
  -XX:MaxMetaspaceSize=1g \
  \
  # === GC 收集器 ===
  -XX:+UseZGC \                             # ZGC：亚毫秒级停顿
  -XX:SoftMaxHeapSize=20g \                 # 告诉 ZGC 尽量不超 20GB
  \
  # === ZGC 优化 ===
  -XX:+ZGenerational \                      # JDK 21 分代 ZGC（生产特性，JEP 439，大幅减少停顿）
  \
  # === GC 线程 ===
  -XX:ParallelGCThreads=8 \                 # ZGC 的 STW 很短，不需要太多线程
  -XX:ConcGCThreads=4 \                     # 并发线程给足，保证及时回收
  \
  # === 性能极致 ===
  -XX:+AlwaysPreTouch \
  # 注意：-XX:-UseBiasedLocking 在 JDK 18+ 已默认关闭，JDK 21 不需要也无法设此参数
  -XX:+UseLargePages \                      # 大页内存（需 OS 配置支持）
  # 注意：-XX:+UseNUMA 仅对 Parallel GC 有效，ZGC 通过内部机制自动感知 NUMA，无需此参数
  -XX:ReservedCodeCacheSize=512m \          # JIT 缓存加大
  \
  # === GC 日志 ===
  -Xlog:gc*:file=/var/log/app/gc.log:time,uptime:filecount=10,filesize=20m \
  \
  # === 诊断 ===
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/app/heapdump.hprof \
  -XX:NativeMemoryTracking=summary \        # 跟踪本地内存（ZGC 堆外开销大）
  \
  -jar myapp.jar
```

**为什么这么配**：
- ZGC 是低延迟场景的不二选择，停顿 < 1ms
- JDK 21 的分代 ZGC（`-XX:+ZGenerational`）比非分代版吞吐高很多 — 这是 JDK 17 → 21 升级的最大 GC 收益
- `-XX:+UseLargePages`：大堆用 2MB 大页替代 4KB 小页，TLB miss 减少
- `-XX:NativeMemoryTracking=summary`：ZGC 自身开销在堆外，需要监控
- 偏向锁在 JDK 18 已移除，JDK 21 无需也无法配置

> **大页内存前提**：需要 OS 开启 HugePages
> ```bash
> # Linux 配置 2MB 大页（需要 20GB / 2MB = 10240 页）
> echo 10240 > /proc/sys/vm/nr_hugepages
> # 验证
> grep Huge /proc/meminfo
> ```

---

### 场景 D：4GB 服务器 — 后台任务（资源受限）

**服务器信息**：4GB 内存，2 核 CPU，JDK 17，定时任务/消息消费者

```bash
java \
  # === 堆内存 ===
  -Xms1536m -Xmx1536m \                     # 堆 1.5GB
  -Xss256k \                                # 栈减小，节省内存
  -XX:MetaspaceSize=128m \
  -XX:MaxMetaspaceSize=256m \
  -XX:MaxDirectMemorySize=128m \            # 限制直接内存
  \
  # === GC 收集器 ===
  -XX:+UseG1GC \                            # JDK 17 下 G1 仍是最优
  -XX:MaxGCPauseMillis=200 \                # 后台任务允许稍长停顿
  -XX:G1HeapRegionSize=2m \                 # 小堆用小 Region
  \
  # === GC 线程 ===
  -XX:ParallelGCThreads=2 \                 # 2 核机器
  -XX:ConcGCThreads=1 \
  \
  # === 节省内存 ===
  -XX:-TieredCompilation \                  # 关闭分层编译，省 Code Cache
  -XX:ReservedCodeCacheSize=64m \           # 减小 JIT 缓存
  -XX:MaxMetaspaceSize=256m \               # 限制元空间
  \
  # === GC 日志 ===
  -Xlog:gc*:file=/var/log/app/gc.log:time,uptime:filecount=3,filesize=5m \
  \
  # === 安全网 ===
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/app/heapdump.hprof \
  \
  -jar myapp.jar
```

**为什么这么配**：
- 内存紧张，从各处省：栈 256k、直接内存 128m、Code Cache 64m
- 关闭分层编译省内存，后台任务不需要极致的执行速度
- G1 仍优于 Serial GC — 即使是小堆，G1 的并发标记也能减少 Full GC

---

### 场景 E：容器环境 — Docker/K8s 微服务

> **生产环境最常见的部署方式**。容器环境下 JVM 参数有专门的注意事项。

**服务器信息**：K8s Pod，内存 limit 4GB，CPU limit 2 核，JDK 21

```bash
java \
  # === 容器感知 ===
  -XX:+UseContainerSupport \                # 读取 cgroup 限制（JDK 10+ 默认开）
  -XX:MaxRAMPercentage=75 \                 # 堆占容器内存的 75%（4G × 75% = 3G）
  -XX:InitialRAMPercentage=75 \             # 初始堆同上，避免扩容
  # -XX:ActiveProcessorCount=2 \            # JDK 10+ 自动识别 cgroup CPU，通常不需要手动设
  \
  # === GC 收集器 ===
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=100 \
  \
  # === 安全网 ===
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/tmp/heapdump.hprof \    # 容器里通常 dump 到 /tmp
  -XX:+ExitOnOutOfMemoryError \             # OOM 时退出进程，让 K8s 重启 Pod
  \
  # === GC 日志（写到 stdout，由 K8s 收集）===
  -Xlog:gc*:file=/var/log/app/gc.log:time,uptime:filecount=3,filesize=5m \
  \
  -jar myapp.jar
```

**与裸机部署的关键差异**：

| 差异点 | 裸机 | 容器 |
|--------|------|------|
| 堆大小计算 | 用 `-Xms`/`-Xmx` 精确设置 | 用 `-XX:MaxRAMPercentage` 按比例 |
| CPU 核数 | 自动识别 | JDK 10+ 自动；JDK 8 需 `ActiveProcessorCount` |
| OOM 处理 | heapdump + 告警脚本 | `ExitOnOutOfMemoryError` + K8s 自动重启 |
| 内存上限 | 物理内存 | cgroup limit（必须确认 JVM 能识别） |

#### 配套 Dockerfile

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app
COPY target/myapp.jar app.jar

# 关键：设置容器的内存和 CPU 限制
# JVM 参数通过 ENV 传入，方便不同环境覆盖
ENV JAVA_OPTS="\
  -XX:+UseContainerSupport \
  -XX:MaxRAMPercentage=75 \
  -XX:InitialRAMPercentage=75 \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=100 \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/tmp/heapdump.hprof \
  -XX:+ExitOnOutOfMemoryError \
  -Xlog:gc*:file=/var/log/app/gc.log:time,uptime:filecount=3,filesize=5m"

EXPOSE 8080

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

#### 配套 K8s Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        resources:
          requests:
            memory: "4Gi"        # ← JVM 看到的是这个值
            cpu: "2"             # ← JVM 看到的是 2 核
          limits:
            memory: "4Gi"        # ← 超过就被 OOM Killed
            cpu: "2"
        env:
        - name: JAVA_OPTS
          value: >-
            -XX:+UseContainerSupport
            -XX:MaxRAMPercentage=75
            -XX:InitialRAMPercentage=75
            -XX:+UseG1GC
            -XX:MaxGCPauseMillis=100
            -XX:+HeapDumpOnOutOfMemoryError
            -XX:HeapDumpPath=/tmp/heapdump.hprof
            -XX:+ExitOnOutOfMemoryError
            -Xlog:gc*:file=/var/log/app/gc.log:time,uptime:filecount=3,filesize=5m
```

> **容器调优 Checklist**：
> - [ ] 确认 JDK 版本 ≥ 8u191（有容器感知）
> - [ ] 确认 `requests.memory == limits.memory`（避免被调度到内存不足的节点）
> - [ ] 确认 `MaxRAMPercentage` 留了足够堆外内存（25% 通常够用）
> - [ ] 设置 `ExitOnOutOfMemoryError`，让 K8s 自动重启
> - [ ] heapdump 路径在容器可写目录（`/tmp` 或挂载卷）

---

## 五、调优五步法

```
第 1 步：默认参数跑基线
    ↓
第 2 步：开 GC 日志，压测观察
    ↓
第 3 步：分析日志，定位瓶颈
    ↓
第 4 步：针对性调参（每次只改 1~2 个）
    ↓
第 5 步：压测验证，对比基线
    ↓
  改善？→ 是 → 记录参数，上线
         → 否 → 回到第 3 步
```

### 第 1 步：基线数据

用默认参数（只设 `-Xms` `-Xmx`）跑一轮压测，记录：
- P50 / P95 / P99 响应时间
- TPS（每秒事务数）
- GC 频率和耗时（从 GC 日志读）

**压测工具推荐**：

| 工具 | 适用场景 | 说明 |
|------|----------|------|
| **wrk** | HTTP 压测 | 轻量高性能，`wrk -t4 -c100 -d60s http://localhost:8080/api` |
| **Gatling** | 复杂场景 | Scala DSL 编写压测脚本，支持阶梯加压 |
| **JMeter** | 通用压测 | 图形化，支持多种协议 |
| **JMH** | 微基准测试 | 验证单个方法/JIT 优化效果，不测整体服务 |

> **压测注意事项**：先跑 5~10 分钟预热（让 JIT 编译完成），再开始记录数据。至少压测 30 分钟才有效。

### 第 2 步：开 GC 日志观察

**实时观察**：
```bash
# 至少跑 30 分钟以上才有意义
jstat -gcutil <pid> 1000    # 每秒打印一次
```

**离线分析 GC 日志文件**（推荐）：

| 工具 | 类型 | 说明 |
|------|------|------|
| **GCEasy**（gceasy.io） | 在线 | 上传 GC 日志自动生成图表和分析报告，最方便 |
| **GCViewer** | 开源本地 | 轻量级 GC 日志可视化，离线可用 |
| **JMC + JFR** | JDK 自带 | JDK Mission Control 配合 Flight Recorder 做深度分析 |
| **grep + awk** | 手动 | `grep "Pause" gc.log \| awk '{print $NF}'` 提取停顿时间 |

```
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT    CGC    CGCT     GCT
  0.00  45.23  78.91   32.45  95.12  93.50    120    2.345     2    0.856     0    0.000   3.201
  ↑      ↑      ↑      ↑      ↑              ↑      ↑       ↑      ↑                        ↑
  S0%   S1%   Eden%  Old%  Meta%           YGC次数 YGC总耗时 FGC次数 FGC总耗时              GC总耗时

健康指标：
- Eden%：GC 后应该接近 0（如果 GC 后还很高 → 新生代太小）
- Old%：GC 后应该明显下降（如果 GC 后还 > 80% → 堆不够或有泄漏）
- YGC 频率：几分钟一次正常（如果几秒一次 → 新生代太小或对象创建太多）
- FGC 次数：越少越好（频繁 FGC = 有大问题）
- GCT 占比：GC 总时间 / 运行时间 < 5% 是健康的
```

### 第 3 步：定位瓶颈

| GC 日志现象 | 诊断 |
|-------------|------|
| Young GC 频繁（几秒一次） | 新生代太小，或短命对象创建太多 |
| Young GC 耗时长（> 100ms） | 新生代太大，或存活对象太多 |
| Full GC 频繁 | 老年代空间不足 / 大对象直接进老年代 / 内存泄漏 |
| Full GC 后老年代使用率不降 | **内存泄漏**（重点排查） |
| Metaspace GC 频繁 | 动态加载类太多，或类加载器泄漏 |
| to-space exhausted | G1 的 Survivor/老年代 Region 不够 |
| Evacuation Failure | G1 回收时找不到空间放存活对象 |
| GC 后堆使用率持续上升 | 内存泄漏 |

### 第 4 步：针对性调参

**原则：每次只改 1~2 个参数**。改多了分不清是哪个参数起了作用。

| 问题 | 调什么 |
|------|--------|
| Young GC 频繁 | 增大 `-Xmn`（新生代） |
| Young GC 耗时长 | 减小 `-Xmn`（新生代不要太大） |
| 频繁 Full GC | 增大 `-Xmx`（总堆）；降低 `-XX:InitiatingHeapOccupancyPercent` |
| 对象过早晋升老年代 | 增大 Survivor（减小 `-XX:SurvivorRatio`）；增大 `-XX:MaxTenuringThreshold` |
| 大对象直接进老年代 | G1：增大 `-XX:G1HeapRegionSize` |
| GC 停顿超时 | 降低 `-XX:MaxGCPauseMillis`；切换更低延迟的收集器 |
| 吞吐量不够 | 提高 `-XX:GCTimeRatio`；切换到 Parallel GC |

### 第 5 步：验证

- 同样的压测脚本，同样的并发量
- 对比基线数据：P99 是否下降？TPS 是否提升？GC 频率是否改善？
- 至少跑 30 分钟确认稳定（不要只看前 5 分钟）

---

## 六、常见问题速查表

| 现象 | 可能原因 | 排查方法 | 调优方向 |
|------|----------|----------|----------|
| 频繁 Full GC | 老年代不足 / 内存泄漏 | `jstat -gcutil` 看 Old% 变化趋势 | 增大 `-Xmx`；用 MAT 分析 heapdump |
| Young GC 频繁 | 新生代太小 / 对象创建过多 | GC 日志看 YGC 频率 | 增大 `-Xmn`；优化代码减少对象创建 |
| Young GC 耗时长 | 新生代太大 / 引用链过长 | GC 日志看 YGC 耗时 | 减小 `-Xmn`；减少对象间的引用深度 |
| GC 后老年代使用率不降 | 内存泄漏 | `jmap -histo` 找大对象；MAT 分析 | 排查代码泄漏（集合、缓存、连接未关闭） |
| to-space exhausted | G1 Region 不足 | GC 日志看此关键词 | 增大 `-Xmx`；调大 `-XX:G1HeapRegionSize` |
| Metaspace OOM | 动态类太多 / 类加载器泄漏 | `jcmd <pid> VM.classloader_stats` | 增大 `-XX:MaxMetaspaceSize`；排查热部署 |
| Direct buffer OOM | NIO buffer 未释放 | `jmap -histo` 看 DirectByteBuffer | 增大 `-XX:MaxDirectMemorySize`；排查泄漏 |
| CPU 高但吞吐低 | GC 线程过多 / 锁竞争 / JIT 编译 | `top -Hp <pid>` 找高 CPU 线程 → `jstack` | 减少 `ParallelGCThreads`；排查锁竞争 |
| 应用启动慢 | 元空间频繁扩容触发 GC | 启动日志看 GC 频率 | 增大 `-XX:MetaspaceSize` |
| 堆内存不释放 | 正常 — `-Xms = -Xmx` 时不释放 | 确认配置 | 这是预期行为，不影响性能 |

### 6.5 内存泄漏排查完整流程

当 `jstat` 显示 Full GC 后老年代使用率持续不降（或 GC 后 Old% 逐次升高），高度怀疑内存泄漏。按以下步骤排查：

```
第 1 步：确认泄漏
  jstat -gcutil <pid> 1000
  观察 Old% 列 — 如果 Full GC 后仍 > 80% 且逐次升高 → 确认泄漏
  如果 Full GC 后能降下来但很快又涨上去 → 可能是老年代不够大，不一定是泄漏

第 2 步：获取堆转储
  方式 A：OOM 自动 dump（前提：已配置 -XX:+HeapDumpOnOutOfMemoryError）
  方式 B：手动 dump
    jcmd <pid> GC.heap_dump /tmp/heapdump.hprof
    # 或
    jmap -dump:format=b,file=/tmp/heapdump.hprof <pid>
  ⚠️ dump 过程会 STW，生产环境选择低峰期执行

第 3 步：用 MAT 分析（Eclipse Memory Analyzer Tool）
  1. 打开 .hprof 文件
  2. 查看 Leak Suspects Report（MAT 自动分析可疑泄漏）
  3. 查看 Histogram → 按 Retained Size 排序 → 找到最大的对象/类
  4. 查看 Dominator Tree → 找到占用内存最多的对象
  5. 右键 → List Objects → with incoming references → 查看谁在引用它
  6. 右键 → Path To GC Roots → exclude weak/soft references → 找到强引用链

第 4 步：定位代码
  从 GC Root 引用链追溯到具体的类名和字段 → 定位到代码行

第 5 步：常见泄漏模式
```

**常见泄漏模式速查**：

| 泄漏模式 | 特征 | 修复方法 |
|----------|------|----------|
| **集合未清理** | HashMap/ArrayList 持续增长 | 添加清理逻辑或改用有界缓存（如 Caffeine） |
| **缓存无上限** | 自定义缓存只加不删 | 改用 LRU 缓存或设上限 |
| **连接未关闭** | JDBC Connection / HttpClient 泄漏 | 使用 try-with-resources |
| **ThreadLocal 未 remove** | 线程池场景下 ThreadLocal 残留 | 在 finally 中调用 `remove()` |
| **监听器未注销** | 注册了 Listener 但从未注销 | 实现 `AutoCloseable`，确保注销 |
| **类加载器泄漏** | 热部署后旧 ClassLoader 无法回收 | 检查是否有静态引用持有旧类 |
| **大对象被意外持有** | byte[] 或 String 被静态变量引用 | 改为局部变量或弱引用 |

**快速排查命令**（不需要 MAT 时的轻量手段）：

```bash
# 1. 查看对象数量直方图（按占用内存排序）
jmap -histo <pid> | head -30

# 2. 只看存活对象（触发一次 GC 后统计，生产慎用）
jmap -histo:live <pid> | head -30

# 3. 对比两次 dump 的差异
jmap -histo <pid> > before.txt
# ... 等待一段时间 ...
jmap -histo <pid> > after.txt
diff before.txt after.txt   # 增长最多的类型就是嫌疑对象
```

---

## 七、参数配置 Checklist

上线前过一遍这个清单：

- [ ] `-Xms` 和 `-Xmx` 设为相同值（或容器环境用 `MaxRAMPercentage` + `InitialRAMPercentage`）
- [ ] `-XX:MetaspaceSize` 已设置（避免启动期 GC）
- [ ] `-XX:MaxMetaspaceSize` 已设置（防止无限增长）
- [ ] GC 收集器已明确选择（不依赖默认值）
- [ ] GC 日志已开启，输出到磁盘文件
- [ ] GC 日志配置了文件滚动（filecount + filesize）
- [ ] `-XX:+HeapDumpOnOutOfMemoryError` 已设置
- [ ] `-XX:HeapDumpPath` 指向有足够空间的目录
- [ ] `-XX:+DisableExplicitGC` 已设置（防 System.gc()）
- [ ] `-XX:ParallelGCThreads` 与 CPU 核数匹配
- [ ] 生产环境没有开启诊断参数（PrintCompilation 等）
- [ ] 已通过压测验证参数效果
- [ ] **容器环境**：`-XX:+UseContainerSupport` 已启用（JDK 10+ 默认）
- [ ] **容器环境**：`MaxRAMPercentage` 留了足够堆外内存（≥ 25%）
- [ ] **容器环境**：`ExitOnOutOfMemoryError` 已设置（配合 K8s 自动重启）

---

## 八、一个真实的调优案例

**问题**：8GB 服务器上的 Web 服务，P99 响应时间偶尔飙到 2 秒

**第 1 步 — 看 GC 日志**：
```
YGC 频率：每 30 秒一次（正常）
YGC 耗时：平均 30ms（正常）
FGC 频率：每小时 2~3 次（不正常！）
FGC 耗时：每次 800ms~1.5s（这就是 P99 飙升的原因）
FGC 后老年代使用率：从 85% 降到 45%（说明不是泄漏，是老年代不够大）
```

**第 2 步 — 分析**：
- Full GC 后老年代能降到 45% → 不是内存泄漏
- 老年代 85% 就触发 Full GC → 老年代空间不够
- 当前配置：`-Xms4g -Xmx4g -Xmn2g` → 老年代只有 2GB

**第 3 步 — 调参**：
```diff
- -Xms4g -Xmx4g -Xmn2g
+ -Xms4g -Xmx4g -Xmn1536m
```
把新生代从 2GB 减到 1.5GB，老年代从 2GB 增到 2.5GB。

**第 4 步 — 验证**：
```
FGC 频率：从每小时 2~3 次 → 每天 1~2 次
P99 响应时间：从偶尔 2 秒 → 稳定在 150ms 以内
YGC 频率：从 30 秒 → 25 秒（新生代小了一点，略频繁，可接受）
```

**结论**：只改了一个参数（`-Xmn`），老年代多出了 512MB，Full GC 频率大幅下降。

---

## 九、最后的忠告

1. **先监控，再调优** — 没有 GC 日志就调优等于盲人摸象
2. **每次只改 1~2 个参数** — 改多了无法归因
3. **不要过度调优** — JVM 默认参数已经很好，大多数应用只需设 `-Xms` `-Xmx` 和 GC 收集器
4. **32GB 是单实例堆的天花板** — 超过就拆实例，别硬堆
5. **代码优化 > JVM 调优** — 一个内存泄漏能打败所有参数调优
6. **生产环境必须有 GC 日志** — 这是你出问题时唯一的证据
7. **JDK 升级 = 免费调优** — 升级比调参有效，具体收益：

| 升级路径 | 你白赚什么 |
|----------|-----------|
| JDK 8 → 17 | G1 默认 GC（比 CMS/Parallel 更智能）、统一 GC 日志、JFR 免费、更强的编译器优化 |
| JDK 11 → 17 | ZGC 生产可用、CMS 被清理（少一个坑）、编译器持续优化 |
| JDK 17 → 21 | **分代 ZGC**（吞吐翻倍 + 停顿更低）、虚拟线程、字符串去重默认开启 |
| JDK 21 → 25 | 值类型预览、ZGC 分代成默认、持续性能改进 |

> **版本选择结论**：新项目选 JDK 21（当前最佳平衡点）。JDK 8 存量项目优先升 17（最稳），有条件直接上 21。JDK 25 等生态稳定后再跟进。
