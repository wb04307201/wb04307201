<!--
question:
  id: 01.java-cpu-spike-troubleshooting
  topic: 01.java
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 生产 Bug
  tags: [01.java, cpu, spike]
-->

# 线上 CPU 飙升排查全链路

## 引子：凌晨 3 点的告警

```
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

```
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

```
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

### 2.3 根因分析

```
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

```
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

```
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

## 六、交叉引用

- 主模块：[`01.java`](../../../01.java/) — Java 知识体系
- [JVM 内存区域](../jvm-memory/) — JVM 运行时数据区详解
- [JVM 内存配置踩坑](../jvm-memory-pitfall/) — -Xmx 超过系统可用内存导致启动失败
- [GC 算法与收集器](../gc-algorithms/) — GC 算法与各类收集器对比
- [类加载机制](../class-loading/) — 类加载过程与双亲委派

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · cpu-spike-troubleshooting](../README.md)
