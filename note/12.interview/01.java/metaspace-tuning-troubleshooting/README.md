<!--
question:
  id: 01.java-metaspace-tuning-troubleshooting
  topic: 01.java
  difficulty: ⭐⭐⭐⭐
  frequency: 中高频（JVM 调优是 Java 面试 Top 3）
  scenario_type: 生产 Bug
  tags: [01.java, JVM, metaspace, container, tuning, docker, gc]
-->

# JVM Metaspace 调优踩坑：只设 MaxMetaspaceSize 不设 MetaspaceSize

> 一句话定位：默认 JVM 在 2G 容器下 `Xmx` 自动被压缩到 512m，加上 Metaspace 动态扩容触发频繁 GC ——"Xmx=1024m + MaxMetaspaceSize=256m" 看似到位，实则把 CPU 推到了 90%+。

> **系列定位**：经典 JVM 调优面试题（容器部署 / Metaspace 治理 / GC 传导 CPU 高频）。考察的不是"加大堆就行"，而是 **容器感知下 Xmx 压缩机制** + **Metaspace 双参数的本质区别** + **GC 频繁 → CPU 升高的传导链** + **预分配 vs 动态扩容**。

---

## 引子：用户拒绝加资源，要求先调优

```text
🛠️ 业务背景：2G 内存后端服务器，默认 JVM 配置
🚨 现象：某天突然收到内存告警 > 90%，CPU > 90%
🔍 查看堆栈和日志：业务正常，无异常
👔 运维姿态：拒绝加资源，先调优
```

某团队部署了一个 Spring Boot 后端服务，服务器只有 **2G 内存**（典型 2 核 4G 容器配置），运行时**完全没有设置任何 JVM 参数**，用了 JVM 默认配置。某天突然收到告警：服务器内存使用率 > 90%，CPU 也飙到了 90%+。

排查堆栈和业务日志后没有任何异常，业务请求也都正常返回，**但 GC 日志却在疯狂刷 Full GC**。

用户的诉求很明确：**拒绝加资源**（没钱加机器），**要求先调优**。这就引出了两个反直觉问题：

1. 2G 内存的容器，默认 JVM 配置下 `Xmx` 到底是多少？（反直觉 1：**默认 Xmx=512m**，不是 2G）
2. 只设 `MaxMetaspaceSize=256m`，Metaspace 就能乖乖不超 256m 吗？（反直觉 2：**不会**，会因为没设 `MetaspaceSize` 而动态扩容，每次扩容触发 Full GC）

接下来看怎么排查、怎么两次调优、怎么避坑。

---

## 一、核心原理

### 1.1 容器感知下"隐藏陷阱"：MaxRAMPercentage=25%

JVM 在 JDK 10+ 引入了**容器感知**（cgroup awareness），会自动读取容器的内存限制。但默认参数是：

```text
-XX:+UseContainerSupport           # JDK 10+ 默认开
-XX:InitialRAMPercentage=???       # 不设，默认为 0（按需分配）
-XX:MaxRAMPercentage=25%           # ⭐ 默认是 25%
-XX:MinRAMPercentage=0              # 0
```

**陷阱**：
- `MaxRAMPercentage=25%` 意思是 **`Xmx` = 容器内存 × 25%**
- 2G 容器下 `Xmx = 2048m × 25% = 512m`
- 即便物理机有 2G 内存，**JVM 也不会自动给你 2G 堆**

```text
2G 容器下默认 Xmx 计算：

容器内存限制 = 2048 MB
Xmx = 2048 × 25% = 512 MB          ← 默认

这意味着：
- 你的堆只有 512m
- 工作集超过 512m 就会触发频繁 GC
- 应用启动快，但运行一段时间就拖慢
```

### 1.2 Metaspace 的双参数机制

Metaspace 治理有两个看似相似、本质不同的参数：

| 参数 | 作用 | 默认值 | 不设的后果 |
|------|------|--------|-----------|
| **`-XX:MetaspaceSize`** | **初始预分配大小**（首次达到时触发 Full GC） | ~20MB | 从默认值动态扩容到 `MaxMetaspaceSize` |
| **`-XX:MaxMetaspaceSize`** | **上限**（防无限增长） | 无上限（受物理内存限制） | OOM 时进程挂掉 |

**核心反直觉**：

```text
只设 MaxMetaspaceSize=256m 的行为：

  应用启动 → Metaspace 默认值 ~20MB
              ↓
  类加载逐渐增加 → Metaspace 用到 20MB+ → 触发扩容
              ↓
  扩容到 30MB → 触发 Full GC（扩容阈值）
              ↓
  继续扩容到 50MB → 触发 Full GC
              ↓
  ... 一直到 256MB
              ↓
  最后一次 Full GC 后停在 256MB

  后果：每次扩容都触发 Full GC，频繁 GC → CPU 高
```

**正解**：

```text
设置 MetaspaceSize=256m + MaxMetaspaceSize=512m：

  应用启动 → Metaspace 预分配 256MB（不会触发 GC）
              ↓
  类加载增加时直接使用预分配空间，不触发扩容
              ↓
  业务平稳运行，只有真正的 Full GC（不是扩容触发的）

  效果：避免运行时扩容触发的 Full GC
```

### 1.3 GC 频繁 → CPU 升高的传导链

这是理解"为什么只设 MaxMetaspaceSize 会让 CPU 高"的关键：

```text
Metaspace 动态扩容 → 触发 Full GC
                              ↓
                    Full GC 停顿（STW）+ 占用 CPU
                              ↓
                    GC 线程占用大量 CPU 时间
                              ↓
                    业务线程获得的 CPU 减少
                              ↓
                    请求处理变慢 → 请求堆积
                              ↓
                    对象创建更快（队列积压）→ 堆更快满
                              ↓
                    更频繁的 GC → 更多 CPU 被吃
                              ↓
                    CPU 90%+，但根因不是业务代码，是 GC 频繁
```

**反直觉**：CPU 高 ≠ CPU 问题，是**内存问题（Metaspace 扩容）的传导**。

---

## 二、排查方法论

### 2.1 看堆栈和业务日志

```bash
# 看应用是否报错
tail -f app.log
# 期望：业务日志无异常，请求正常返回
```

### 2.2 看 GC 日志（关键）

```bash
# 实时看 GC 频率
jstat -gcutil <pid> 1000

# 输出示例：
#  S0     S1     E      O      M     CCS    YGC   YGCT    FGC   FGCT    GCT
#  0.00  95.23  12.50  99.87  95.23 92.10  8542  125.34  4271  89.12  214.46
#  0.00  95.23  15.00  99.91  95.23 92.10  8543  125.48  4272  89.25  214.73
#        ↑           ↑            ↑
#   Young GC 每秒 1+ 次  老年代 99.87%   Full GC 频繁发生

# M 列（Metaspace）持续上涨 → 元空间在动态扩容
```

### 2.3 反推"内存压力 → CPU 升高"传导链

```bash
# 看 CPU 占用最高的线程
top -Hp <pid>

# 输出：
#   TID    PR   %CPU   COMMAND
#   12360   20   45.2  java    ← GC 线程
#   12361   20   38.7  java    ← GC 线程
#   12362   20   12.1  java    ← GC 线程

# 关键：CPU 最高的线程是 GC 线程，不是业务线程
```

### 2.4 用 jcmd 看 Metaspace 实际使用

```bash
# 查看 native memory 详细分布
jcmd <pid> VM.native_memory

# 输出：
# Total: reserved=2GB, committed=1.7GB
#   - Java Heap:    512MB (reserved=512MB)            ← 默认 Xmx=512m
#   - Class/Meta:   256MB (reserved=256MB, max=256MB)  ← Metaspace 上限
#   - Thread:       150MB (threads=200)
#   - Code Cache:   100MB

# 关键：
#   Java Heap = 512m → 确认默认 Xmx=512m（容器感知 25%）
#   Class/Meta 在涨但没到上限 → Metaspace 动态扩容中
```

---

## 三、根因深挖（3 大反直觉）

### 3.1 反直觉 1：CPU 高 ≠ CPU 问题，是 GC 频繁的传导

| 直觉 | 真相 |
|------|------|
| CPU 高就是业务代码死循环 / 高并发 / 锁竞争 | 90% 的线上 CPU 高，**根因是 GC 频繁** |
| 调优 CPU 就是改代码 | **先看 GC 日志**，如果是 GC 引起，调内存参数 |

### 3.2 反直觉 2：只设 MaxMetaspaceSize ≠ 设了 Metaspace

| 错误配置 | 正确配置 |
|---------|---------|
| `-XX:MaxMetaspaceSize=256m` | `-XX:MetaspaceSize=256m` + `-XX:MaxMetaspaceSize=512m` |

**关键认知**：

- **`MetaspaceSize` 是初始预分配**（避免运行时扩容触发 GC）
- **`MaxMetaspaceSize` 是上限**（防无限增长）
- 只设上限不设初始值 → **从默认值动态扩容，每次扩容触发 Full GC**

### 3.3 反直觉 3：2G 容器下默认 Xmx=512m（容器感知 25%）

```bash
# 假设你有 2G 内存的服务器
java -jar app.jar
# 默认 Xmx = 2048m × 25% = 512m      ← 不是 2G！

# 验证
jinfo -flags <pid> | grep MaxRAM
# -XX:MaxRAMPercentage=25.000000

jcmd <pid> VM.native_memory | grep "Java Heap"
# Java Heap: 512MB (reserved=512MB)    ← 实际只有 512m
```

**为什么默认 25%**：

- JVM 在 JDK 10 之前不感知容器，会按物理机内存算
- 容器内可能还有 native 进程、日志收集器等需要内存
- 25% 是 JVM 工程师保守选择的"安全默认值"
- **但 2G 容器下 25% = 512m，对大多数应用偏小**

---

## 四、解决：两次调优对照

### 4.1 第一次失败：Xms=Xmx=1024m + MaxMetaspaceSize=256m

```bash
# 第一次调优（自认为到位）
exec java -Xms1024m -Xmx1024m \
     -XX:MaxMetaspaceSize=256m \
     -XX:+UseG1GC \
     -jar app.jar
```

**结果**：**CPU 仍然 90%+，频繁 GC**。

**问题分析**：

- ✅ `Xms=Xmx=1024m` 显式设置，绕过了 `MaxRAMPercentage=25%` 的坑
- ❌ **没设 `MetaspaceSize`**，Metaspace 还是从默认值动态扩容
- ❌ 每次扩容触发 Full GC → CPU 高

```text
Metaspace 行为：

  默认值 20MB → 扩容到 30MB → Full GC（扩容阈值）
            → 扩容到 50MB → Full GC
            → 扩容到 100MB → Full GC
            → 扩容到 200MB → Full GC
            → 扩容到 256MB → Full GC（达到上限）

  全过程触发 5+ 次 Full GC，每次停顿 0.5~2 秒
  CPU 被 GC 线程吃满
```

### 4.2 第二次成功：增加 MetaspaceSize=256m + MaxMetaspaceSize=512m

```bash
# 第二次调优（最终配置）
exec java -Xms1024m -Xmx1024m \
     -XX:MetaspaceSize=256m \      # ⭐ 关键：预分配，避免运行时扩容
     -XX:MaxMetaspaceSize=512m \   # 上限调整到 512m（业务加载类的需求）
     -XX:MaxDirectMemorySize=512m \
     -XX:ReservedCodeCacheSize=128m \
     -Xss512k \
     -XX:+UseStringDeduplication \
     -Duser.timezone=GMT+08 \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -Xlog:gc*:file=gc.log:time,uptime,level,tags \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/data/logs/ \
     -jar app.jar
```

**关键变化**：

| 参数 | 第一次 | 第二次 | 效果 |
|------|--------|--------|------|
| `MetaspaceSize` | 未设（默认 20m） | **256m** | 预分配，避免运行时扩容 |
| `MaxMetaspaceSize` | 256m | **512m** | 留足空间，避免业务加载类触发 OOM |

**修复效果**：

```text
Metaspace 行为：

  启动时预分配 256MB → 直接占用，不触发 GC
              ↓
  业务加载类时使用预分配空间，不扩容
              ↓
  业务平稳运行，没有扩容触发的 Full GC
              ↓
  CPU 恢复正常（从 90%+ 降到 20%）
```

### 4.3 最终配置要点

```text
✅ -Xms = -Xmx            避免堆动态伸缩
✅ MetaspaceSize 设大     避免运行时扩容触发 GC
✅ MaxMetaspaceSize 留足  避免业务加载类触发 OOM
✅ 显式设 -Xmx            绕开 MaxRAMPercentage=25% 的坑
✅ UseContainerSupport    让 JVM 感知容器（但调整百分比）
✅ UseStringDeduplication 字符串去重，节省堆
✅ HeapDumpOnOutOfMemoryError OOM 自动保留现场
```

---

## 五、验证

### 5.1 看 GC 频率下降

```bash
# 修复后
jstat -gcutil <pid> 1000

# 期望输出：
#  S0     S1     E      O      M     CCS    YGC   YGCT    FGC   FGCT    GCT
#  0.00   8.23  45.12  35.87  85.23 90.10  125   4.12   0    0.00   4.12    ← FGC=0!
#  0.00  10.23  48.50  36.91  85.23 90.10  126   4.18   0    0.00   4.18
#                              ↑
#                         老年代健康占用（35% 而非 99%）
```

### 5.2 看 CPU 恢复

```bash
top -bn1 | head -10

# 期望：
#   PID  USER   PR  NI  VIRT  RES  SHR  S  %CPU  %MEM   TIME  COMMAND
#  12345 app     20   0  3.2g 1.5g 50m  S  18.5  75.0   2:34.45 java    ← CPU 18% 而非 90%
```

### 5.3 监控告警恢复

```text
✅ 内存告警 < 80%
✅ CPU 告警 < 70%
✅ Full GC 频率 < 1 次/小时（修复前是每分钟 1+ 次）
✅ Young GC 频率 < 1 次/10 秒
```

### 5.4 业务请求 RT 正常

```text
✅ P99 RT < 500ms（修复前 Full GC 停顿时 RT 飙到 5s+）
✅ 接口成功率 > 99.9%
✅ 无超时告警
```

---

## 六、面试话术（90 秒版本）

> "线上 JVM 调优有个反直觉点：**默认 JVM 在 2G 容器下 `Xmx` 只有 512m**。这是因为 JDK 10+ 容器感知默认 `MaxRAMPercentage=25%`，2G × 25% = 512m。即便是物理 2G 内存，JVM 也不会自动给你 2G 堆。
>
> 还有一个反直觉点：**只设 `MaxMetaspaceSize=256m` 不等于设了 Metaspace**。`MetaspaceSize` 是初始预分配大小（避免运行时扩容触发 GC），`MaxMetaspaceSize` 只是上限。如果只设上限，Metaspace 会从默认值 ~20MB 动态扩容到 256MB，**每次扩容都触发 Full GC**。
>
> 我实际遇到过一次：2G 内存服务器，默认 JVM 配置，CPU 突然 90%+。看堆栈和业务日志都正常，但 GC 日志在疯狂刷 Full GC，CPU 最高的线程是 GC 线程。根因是 GC 频繁导致 CPU 高，是内存问题传导到 CPU。
>
> 第一次调优：Xms=Xmx=1024m + MaxMetaspaceSize=256m。结果 CPU 仍然高，因为 Metaspace 还是动态扩容触发 Full GC。
>
> 第二次调优：增加 `MetaspaceSize=256m` + 把 `MaxMetaspaceSize` 调到 512m。Metaspace 启动时预分配 256m，业务加载类时直接用预分配空间，不扩容触 GC。修复后 CPU 从 90%+ 降到 20%。
>
> 关键认知：**CPU 高不一定是 CPU 问题**；**`MetaspaceSize` 和 `MaxMetaspaceSize` 是两个本质不同的参数**；**容器下默认 `MaxRAMPercentage=25%` 是隐藏陷阱**，必须显式设 `-Xmx` 才稳。"

---

## 七、相关章节

### 同栏目兄弟（12.interview/01.java）

- [`jvm-memory-pitfall`](../jvm-memory-pitfall/README.md) — `-Xmx` 超过系统可用内存的踩坑 + 容器内存配置模板（同样涉及容器感知）
- [`cpu-spike-troubleshooting`](../cpu-spike-troubleshooting/README.md) — 线上 CPU 飙升排查全链路（GC 频繁是 CPU 升高的元凶之一）

### 主模块深度版（01.java-and-jvm）

- [`02-jvm/parameters`](../../../01.java-and-jvm/02-jvm/parameters.md) — MetaspaceSize / MaxMetaspaceSize 参数详解 + 容器感知段
- [`02-jvm/tuning`](../../../01.java-and-jvm/02-jvm/tuning.md) — JVM 调优指南（堆 / Metaspace / GC 收集器选择）

---

> 📅 2026-08-28 · 咬文嚼字 · JVM Metaspace 调优踩坑 · ⭐⭐⭐⭐（容器感知 + Metaspace 双参数 + GC→CPU 传导链深度题）

← [返回 12.interview/01.java 目录表](../README.md)