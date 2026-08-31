<!--
question:
  id: 01.java-cpu-spike-troubleshooting
  topic: 01.java
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 生产 Bug
  tags: [01.java, cpu, spike]
-->

# 线上 CPU 飙升排查全链路

## 引子：凌晨 3 点的告警

```text
🚨 告警：生产服务器 CPU 使用率 98%！
```

半夜被电话叫醒，打开监控一看——CPU 快跑满了。

怎么排查？三步走：

1. **top** → 找到最忙的 Java 进程
2. **jstack** → 找到最忙的线程
3. **分析线程在做什么** → 定位根因

但 CPU 飙升的原因无非三种——**GC 疯狂、死循环、锁竞争**。怎么区分？怎么定位？

---

## 一、核心原理

### 1.1 CPU 飙升的三大元凶

| 元凶 | 典型表现 | 占比 |
|------|----------|------|
| **GC 频繁** | GC 线程占用大量 CPU，GC 日志密集，业务线程几乎停滞 | ⭐⭐⭐⭐⭐ |
| **死循环 / 热点代码** | 个别线程 CPU 持续 100%，代码逻辑存在问题 | ⭐⭐⭐⭐ |
| **锁竞争 / 线程争抢** | 大量线程 BLOCKED/WAITING，上下文切换频繁 | ⭐⭐⭐ |

### 1.2 排查核心思路

```text
监控告警 CPU > 80%
       │
       ▼
  ┌──────────────┐
  │ top 命令确认  │ ── 确认是 Java 进程占用
  └──────┬───────┘
         ▼
  ┌──────────────┐
  │ top -Hp <pid>│ ── 找到 CPU 最高的线程 ID
  └──────┬───────┘
         ▼
  ┌──────────────┐
  │ printf '%x'  │ ── 将线程 ID 转为十六进制
  │ <tid>        │
  └──────┬───────┘
         ▼
  ┌──────────────────┐
  │ jstack <pid>     │ ── 导出线程快照，搜索十六进制线程 ID
  │ grep -A 30       │
  └──────┬───────────┘
         ▼
  ┌──────────────────┐
  │ 分析线程栈顶方法  │ ── 定位代码行 or GC 线程
  └──────┬───────────┘
         ▼
  ┌──────────────────┐
  │ jstat -gcutil    │ ── 确认 GC 频率与耗时
  │ <pid> 1000       │
  └──────────────────┘
```

### 1.3 GC 导致 CPU 飙升的机制

当 `-Xmx` 设置过小时，堆内存不足以容纳正常工作集，JVM 被迫频繁触发 GC：

```text
正常情况：
  应用运行 ████████░░ GC ████████░░ GC    CPU ~20%
                      ↑ 偶尔 GC，间隔长

-Xmx 过小：
  应用运行 ██ GC ██ GC ██ GC ██ GC ██ GC  CPU ~95%
          ↑ 刚分配就满，立即 GC，陷入死循环
```

**恶性循环**：堆越小 → GC 越频繁 → GC 线程占用越多 CPU → 应用线程获得的 CPU 越少 → 响应越慢 → 请求堆积 → 对象创建更快（请求队列积压）→ 堆更快满 → GC 更频繁

---

## 二、实战案例：-Xmx 过小导致 CPU 100%

### 2.1 背景

线上某 Spring Boot 服务，正常运行 CPU 在 15%~25%。某次发布后，CPU 突然飙升到 95%+，接口大面积超时，监控告警。

### 2.2 排查过程

**Step 1：确认进程**

```bash
# 查看 CPU 占用最高的进程
top -bn1 | head -20

# 输出：PID 12345 java，CPU 198%（多核累加）
```

**Step 2：定位高 CPU 线程**

```bash
# 查看该进程内哪些线程 CPU 最高
top -Hp 12345

# 输出：
#   TID    PR   %CPU   COMMAND
#   12360   20   45.2  java    ← GC 线程
#   12361   20   38.7  java    ← GC 线程
#   12362   20   12.1  java    ← GC 线程
#   12400   20    2.3  java    ← 业务线程
```

> 💡 发现 CPU 最高的线程集中在 GC 线程（线程名含 `GC`），而不是业务线程。

**Step 3：确认 GC 状态**

```bash
# 每秒输出一次 GC 统计
jstat -gcutil 12345 1000

# 输出：
#  S0     S1     E      O      M     CCS    YGC   YGCT    FGC   FGCT    GCT
#  0.00  98.12  12.50  99.87  95.23 92.10  8542  125.34  4271  89.12  214.46
#  0.00  98.12  15.00  99.91  95.23 92.10  8543  125.48  4272  89.25  214.73
#        ↑           ↑            ↑
#   Young GC 每秒 1+ 次  老年代 99.87%   Full GC 也在频繁发生
```

> 🔴 关键发现：Young GC 每秒 1~2 次，老年代几乎满（99.87%），Full GC 也在频繁发生。这是典型的堆内存严重不足的表现。

**Step 4：检查 JVM 参数**

```bash
jinfo -flags 12345

# 输出：
# -Xms256m -Xmx256m     ← 最大堆只有 256MB！
# -XX:+UseG1GC
```

> 🔴 根因确认：`-Xmx` 只有 256MB，而该服务正常工作至少需要 1~2GB 堆内存。本次发布增加了新功能，内存需求上升，256MB 完全不够用。

**Step 5：修复**

```bash
# 将堆内存调整为合理值
-Xms2g -Xmx2g

# 重启后 CPU 恢复正常：15%~25%
```

### 2.2.5 火焰图定位热点（async-profiler）

当 `jstack` 定位到的线程是**业务线程**时（不是 GC 线程），还需要进一步看**具体在跑哪个方法**。`jstack` 的栈快照只能反映一个瞬时状态，**火焰图**通过高频采样画出"方法调用时间占比"，是定位 CPU 热点的终极武器。

**async-profiler 安装与使用**：

```bash
# 下载（最新 release 在 GitHub releases）
wget https://github.com/async-profiler/async-profiler/releases/download/v3.0/async-profiler-3.0-linux-x64.tar.gz
tar -xzf async-profiler-3.0-linux-x64.tar.gz
cd async-profiler-3.0-linux-x64

# 启动采样（60 秒，CPU 模式，生成火焰图 HTML）
./profiler.sh -e cpu -d 60 -f /tmp/flame.html <pid>
# 或 JVM 模式（看线程在做什么，含 native + JVM 内部）
./profiler.sh -e itimer -d 60 -f /tmp/flame.html <pid>
```

**火焰图怎么看**：

```text
       ┌─────────────────────────────────────────────┐
       │              com.example.Service            │  ← 顶层是 JVM 包
       │   ┌──────────────────────────────────┐     │
       │   │  com.example.OrderService.calc() │     │  ← 热点方法：calc()
       │   │   ┌───────────────┐             │     │  ← calc 里的 hot path
       │   │   │  BigDecimal.* │  ← 60%      │     │     BigDecimal 运算占 60%
       │   │   └───────────────┘             │     │
       │   └──────────────────────────────────┘     │
       └─────────────────────────────────────────────┘
       宽度 = 该方法及其子方法在采样中出现的时间占比（越宽越热点）
       颜色 = 同一栈的不同函数（无业务含义）
```

**实战对照**：

| 工具 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| `jstack` | 找线程 + 看瞬时栈 | 内置，快 | 只能看 1 瞬时，高频问题易漏 |
| `top -Hp` | 看 CPU 占用最高的线程 | 内置，最快 | 不知道在跑什么 |
| **火焰图** | 找 CPU 热点方法 | 直观，全局视图 | 需额外工具，几分钟采样 |
| Arthas `trace` | 单方法调用链追踪 | 实时，无需重启 | 路径深时输出冗长 |

**生产环境火焰图采样原则**：
- **持续 30~60 秒**（太短采样不足，太长干扰业务）
- **CPU 高峰期采样**（低谷期看不到热点）
- **attach 模式优于启动注入**（`./profiler.sh <pid>` 即可，进程无侵入）
- **生成的 HTML 直接在浏览器打开**（无需后端，绿色软件）

### 2.3 根因分析

```text
发布前：-Xmx512m，堆勉强够用，GC 频率尚可接受
发布后：新增功能导致对象创建量增加，512MB → 256MB（运维误改配置）
         ↓
   堆不足 → 频繁 Minor GC → 对象加速晋升老年代 → 老年代满
         ↓
   频繁 Full GC → GC 线程吃掉所有 CPU → 业务线程饿死
         ↓
   CPU 95%+，接口超时，服务不可用
```

---

## 三、常见陷阱

### 3.1 ❌ 不看 GC 日志就直接改代码

**现象**：看到 CPU 高，第一反应是代码有 bug，开始 review 代码找死循环。

**正确做法**：先用 `jstat -gcutil` 看 GC 频率。如果 GC 频率异常高，优先排查内存问题。

```bash
# GC 频率参考
# Young GC 间隔 < 5 秒   → 堆可能偏小
# Full GC 频繁（每分钟 1+ 次） → 堆严重不足或有内存泄漏
```

### 3.2 ❌ -Xmx 设置「越小越好」

**误区**：认为 `-Xmx` 越小，GC 越快，响应越好。

**现实**：`-Xmx` 过小导致 GC 频率暴增，GC 本身消耗 CPU，反而拖垮整个服务。

```text
-Xmx 与性能的关系：

  性能
   ↑      ╭──────╮
   │     ╱        ╲
   │    ╱          ╲
   │   ╱            ╲
   │  ╱              ╲
   │ ╱                ╲
   │╱                  ╲────── 堆太大，GC 单次耗时长
   │                     堆太小，GC 频繁
   └──────────────────────────→ -Xmx
              ↑
           最佳平衡点
```

### 3.3 ❌ -Xms 和 -Xmx 设置不一致

**问题**：`-Xms` 远小于 `-Xmx`，堆需要动态扩容，扩容过程中会触发 Full GC，造成周期性 CPU 尖峰。

**最佳实践**：`-Xms` = `-Xmx`，避免堆动态伸缩带来的性能抖动。

```bash
# ❌ 不推荐
-Xms256m -Xmx2g

# ✅ 推荐：初始堆 = 最大堆
-Xms2g -Xmx2g
```

### 3.4 ❌ 线程栈分析只看线程名不看方法

**现象**：用 `top -Hp` 找到高 CPU 线程后，直接看线程名是 `http-nio-8080-exec-1`，就认为是业务代码问题。

**正确做法**：必须用 `jstack` 导出线程栈，看栈顶方法才能确定线程在做什么。如果栈顶是 `GC task thread`，说明是 GC 问题而非代码问题。

---

## 四、最佳实践

### 4.1 排查工具箱

| 工具 | 用途 | 常用命令 |
|------|------|----------|
| `top` | 定位高 CPU 进程 | `top -bn1 \| head -20` |
| `top -Hp` | 定位高 CPU 线程 | `top -Hp <pid>` |
| `jstack` | 导出线程快照 | `jstack <pid> > thread_dump.txt` |
| `jstat` | 监控 GC 状态 | `jstat -gcutil <pid> 1000` |
| `jmap` | 导出堆快照 | `jmap -dump:format=b,file=heap.hprof <pid>` |
| `arthas` | 在线诊断（阿里开源） | `thread -n 3`（直接看 CPU 最高的 3 个线程） |
| `async-profiler` | 生成火焰图 | `./asprof -d 30 -f flame.html <pid>` |

### 4.2 JVM 参数配置建议

```bash
# 堆内存：初始 = 最大，避免动态伸缩
-Xms2g -Xmx2g

# GC 收集器：JDK 11+ 推荐 G1
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200

# GC 日志：出问题时有据可查
-Xlog:gc*:file=gc.log:time,uptime,level,tags

# 堆转储：OOM 时自动保存现场
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/data/logs/heap.hprof
```

### 4.3 -Xmx 合理值估算

```text
-Xmx ≥ 工作集大小 × 1.5 ~ 2.0

工作集 = 常驻对象 + 请求处理中的临时对象

经验值：
  小型微服务（QPS < 100）：1g ~ 2g
  中型服务（QPS 100~1000）：2g ~ 4g
  大型服务（QPS > 1000）：4g ~ 8g
  内存密集型（大数据/缓存）：8g ~ 16g+
```

> ⚠️ 注意：堆不是越大越好。堆过大会导致 GC 单次停顿时间变长（尤其是非 G1/ZGC 收集器）。建议根据实际监控数据调整。

### 4.4 一键排查脚本

```bash
#!/bin/bash
# cpu-spike-check.sh - CPU 飙升快速排查

PID=$(pgrep -f "your-app.jar" | head -1)
if [ -z "$PID" ]; then
    echo "Java process not found"
    exit 1
fi

echo "=== Java Process: $PID ==="

echo -e "\n--- Top 5 CPU Threads ---"
top -Hp "$PID" -bn1 | tail -n +8 | head -5

echo -e "\n--- GC Statistics ---"
jstat -gcutil "$PID" 1000 3

echo -e "\n--- JVM Flags ---"
jinfo -flags "$PID" 2>/dev/null | grep -E "Xmx|Xms|UseG1|UseCMS|UseParallel"

echo -e "\n--- Thread Dump (top 3 CPU threads) ---"
for TID in $(top -Hp "$PID" -bn1 | tail -n +8 | head -3 | awk '{print $1}'); do
    HEX=$(printf '%x' "$TID")
    echo "Thread $TID (0x$HEX):"
    jstack "$PID" 2>/dev/null | grep -A 20 "nid=0x$HEX " | head -20
    echo "---"
done
```

---

## 五、面试话术（30 秒版）

> "线上 CPU 飙升排查分四步：第一步用 `top` 确认是 Java 进程占用；第二步用 `top -Hp` 定位到具体线程，将线程 ID 转为十六进制后在 `jstack` 输出中搜索，看栈顶方法确定线程在做什么；第三步用 `jstat -gcutil` 看 GC 频率和老年代占用，如果 GC 非常频繁就优先考虑内存问题。我实际遇到过一次，是 `-Xmx` 被设成了 256MB，堆太小导致 GC 疯狂运行，CPU 被 GC 线程吃满，最后把堆调到 2G 就恢复正常了。"

---

## 面试话术（90 秒版）

> 「线上 CPU 飙升是高频故障，**90% 不是业务代码问题，是内存/GC 问题传导**。排查必须按四步走，不能乱猜：
>
> **第一步：`top` 看进程**——先确认是 Java 进程还是其他系统进程（有时候是 cron、正则回溯、日志框架）。看到 `java` 进程 CPU 高，再进入 JVM 内部排查。
>
> **第二步：`top -Hp <pid>` 看线程**——Java 是多线程，CPU 高一定是某几个线程在忙。`top -Hp` 能看到进程内每个线程的 CPU 占用，把占用最高的 3 个线程的 TID 记下来。
>
> **第三步：TID 16 进制 + `jstack` 定位方法**——把十进制 TID 转 16 进制（printf '%x'），在 `jstack <pid>` 输出里搜 `nid=0x<hex>`，能看到线程在跑什么方法。这是**定位业务代码还是 GC 线程**的关键——如果是 `GC Thread` 或 `VM Thread`，就是内存问题。
>
> **第四步：`jstat -gcutil` 看 GC 频率**——每秒一次，看 YGC 和 FGC 的频次。如果每秒 1 次以上 Full GC，根因不在 CPU，**在堆**：可能是内存泄漏、大对象直接进老年代、`-Xmx` 太小、或者 Metaspace 动态扩容。
>
> 我实际遇到过一个经典案例：线上 CPU 突然 100%，看 `top -Hp` 最高的 3 个线程全是 `GC Thread`，`jstat` 看老年代 99%，FGC 每秒 2 次。**根因不是 CPU，是内存**：运维把 `-Xmx` 从 2G 改成了 256M，堆太小导致 GC 疯狂，CPU 全被 GC 线程吃光。调到 2G 后 5 分钟内恢复。
>
> 进阶工具：**Arthas**（阿里开源，dashboard 实时看线程和 GC 状态，无需重启）、**async-profiler**（生成火焰图，看 CPU 热点方法，10 秒采样无侵入）。生产环境**推荐**这两个，比 jstack 更直观。」

---

## 六、交叉引用

- 主模块：[`01.java`](../../../01.java-and-jvm/) — Java 知识体系
- [JVM 内存区域](../jvm-memory/) — JVM 运行时数据区详解
- [JVM 内存配置踩坑](../jvm-memory-pitfall/) — -Xmx 超过系统可用内存导致启动失败
- [GC 算法与收集器](../gc-algorithms/) — GC 算法与各类收集器对比
- [类加载机制](../class-loading/) — 类加载过程与双亲委派
- [JVM Metaspace 调优踩坑](../metaspace-tuning-troubleshooting/) — CPU 飙升的元凶之一是 Metaspace 动态扩容触发频繁 GC

## 相关章节

- 深度阅读：[`01.java-and-jvm`](../../../01.java-and-jvm/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · cpu-spike-troubleshooting](../README.md)
