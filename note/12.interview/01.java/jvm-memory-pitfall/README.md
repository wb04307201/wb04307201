<!--
question:
  id: 01.java-jvm-memory-pitfall
  topic: 01.java
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 生产 Bug
  tags: [01.java, JVM, jvm]
-->

# JVM 内存配置踩坑：-Xmx 超过系统可用内存

> **一句话定位**：JVM 总内存 ≈ 堆 × 1.3~1.5 —— 含 Metaspace/线程栈/直接内存，容器内必须显式设 MaxRAMPercentage。

## 引子：一个"启动就卡死"的惨案

```bash
# 4 核 8G 的服务器
java -Xmx10g -jar app.jar

# 预期：启动失败，报 OOM
# 实际：进程"卡住了"，不报错，不退出，SSH 都卡了
```

你以为 `-Xmx` 设大了 JVM 会报错？不一定！

JVM 总内存 ≠ `-Xmx`。堆内存只是冰山一角——还有元空间、线程栈、直接内存、Code Cache……当总内存超过物理内存，**操作系统开始疯狂 swap**，整台机器卡死。

---

> 📚 **前置知识**：[JVM](../../../01.java-and-jvm/02-jvm/README.md)

## 一、核心原理

### 1.1 JVM 内存全景：堆只是冰山一角

很多开发者误以为 `-Xmx` 就是 JVM 占用的全部内存，实际上 JVM 的内存占用远不止堆：

```text
┌─────────────────────────────────────────┐
│           JVM 总内存占用                 │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │ 堆内存（Heap）                  │    │
│  │ • -Xmx 控制                     │    │
│  │ • 年轻代 + 老年代               │    │
│  │ • 典型值：1g ~ 8g               │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │ 元空间（Metaspace）             │    │
│  │ • -XX:MaxMetaspaceSize          │    │
│  │ • 存储类元数据                  │    │
│  │ • 典型值：256m ~ 512m           │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │ 线程栈（Thread Stack）          │    │
│  │ • -Xss × 线程数                 │    │
│  │ • 默认 -Xss = 1m                │    │
│  │ • 200 线程 = 200m               │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │ 直接内存（Direct Memory）       │    │
│  │ • -XX:MaxDirectMemorySize       │    │
│  │ • NIO ByteBuffer.allocateDirect │    │
│  │ • 典型值：等于 -Xmx 或独立设置  │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │ JVM 自身开销（Native）          │    │
│  │ • Code Cache（JIT 编译代码）    │    │
│  │ • GC 数据结构                   │    │
│  │ • 符号表、字符串表              │    │
│  │ • 典型值：100m ~ 300m           │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘

JVM 总内存 ≈ -Xmx + Metaspace + (线程数 × -Xss) + DirectMemory + Native
```

### 1.2 内存计算公式

```text
JVM 总内存 ≈ -Xmx 
           + MaxMetaspaceSize（或默认无上限）
           + (线程数 × -Xss)
           + MaxDirectMemorySize
           + Native（Code Cache + GC + 其他，约 100~300MB）
```

**示例**：一个典型的 Spring Boot 微服务

```text
-Xmx2g
-MetaspaceSize 256m（实际可能用到 300m+）
-200 个线程 × 1m = 200m
-DirectMemorySize 1g（如果使用了大量 NIO）
-Native 200m

总计 ≈ 2g + 300m + 200m + 1g + 200m ≈ 3.7g
```

> ⚠️ 如果系统只有 4g 内存，设置 `-Xmx2g` 看似合理，但 JVM 实际需要 3.7g+，可能不够！

### 1.3 为什么不会立即报错？

Linux 的内存分配策略：**Overcommit**

```text
┌──────────────────────────────────────────────────────────┐
│                    Linux 内存分配策略                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  虚拟内存（Virtual Memory）                              │
│  ┌────────────────────────────────────────────────┐     │
│  │  进程申请的内存（如 -Xmx2g）                    │     │
│  │  → 内核立即分配虚拟地址空间                     │     │
│  │  → 但不立即分配物理内存                         │     │
│  │  → 实际使用时才「按需分配」                     │     │
│  └────────────────────────────────────────────────┘     │
│                         ↓                               │
│  物理内存（Physical Memory）                            │
│  ┌────────────────────────────────────────────────┐     │
│  │  当进程真正写入内存时，才分配物理页              │     │
│  │  → 如果物理内存不足：                           │     │
│  │    1. 使用 Swap（极慢）                         │     │
│  │    2. 触发 OOM Killer（杀进程）                 │     │
│  │    3. 分配失败（返回错误）                      │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  Overcommit 模式（vm.overcommit_memory）：               │
│  • 0 = 启发式策略（默认，允许一定程度的 overcommit）     │
│  • 1 = 始终允许（直到物理内存+Swap 耗尽）               │
│  • 2 = 严格模式（不允许超过 CommitLimit）               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**结果**：JVM 启动时成功分配了虚拟内存，但实际使用时物理内存不足，导致系统开始频繁 Swap 或直接卡死，而不是立即报 `OutOfMemoryError`。

### 1.4 容器环境的内存隔离：cgroup v1 vs v2

> **这是云原生时代的内存关键**。Docker / K8s 的内存限制由 cgroup 控制，JVM 的 overcommit 行为在容器里会**有额外麻烦**。

**cgroup v1（Docker 默认，至 K8s 1.25 之前）**：

```text
/sys/fs/cgroup/memory/memory.limit_in_bytes   ← 内存硬上限
/sys/fs/cgroup/memory/memory.usage_in_bytes   ← 当前使用量
/sys/fs/cgroup/memory/memory.failcnt          ← OOM 次数
```

- JVM 8u191~JDK 21：自动读 `memory.limit_in_bytes`（`-XX:+UseContainerSupport`）
- `MaxRAMPercentage` 默认 25%，4G 容器下 Xmx=1G

**cgroup v2（K8s 1.25+ 逐步启用）**：

```text
/sys/fs/cgroup/memory.max                     ← 内存硬上限（统一接口）
/sys/fs/cgroup/memory.current                 ← 当前使用量
/sys/fs/cgroup/memory.events                  ← OOM 事件（含 low/high/max）
/sys/fs/cgroup/memory.high                    ← 软上限（触发回收）
/sys/fs/cgroup/memory.swap.max                ← swap 上限
```

- **JDK 21+ 默认支持** cgroup v2 完整接口（含 `memory.high` 软上限）
- **JDK 16+** 引入 cgroup v2 感知
- **JDK 8u372+** 才支持 cgroup v2（之前只能看 v1 路径）

**关键差异：容器内 Swap 行为**：

| cgroup 版本 | Swap 默认 | JVM 看到的 Swap | 影响 |
|------------|----------|-----------------|------|
| v1 | 关闭（K8s 默认） | 无 swap 可用 | JVM 内存不足 → 立即 OOM Kill |
| v2 | 关闭（K8s 默认） | 显式 `swap.max=0` | 同 v1 |

**生产建议**：

```bash
# 1. 确认 cgroup 版本
stat -fc %T /sys/fs/cgroup/   # 0xcgroup2 → v2；0x1 → v1

# 2. 显式设 MaxRAMPercentage，避免默认 25% 太小
-XX:+UseContainerSupport
-XX:MaxRAMPercentage=70       # 留 30% 给堆外 + native
-XX:InitialRAMPercentage=70  # 避免启动扩容

# 3. 配套 ExitOnOutOfMemoryError，让 K8s 重启 Pod
-XX:+ExitOnOutOfMemoryError

# 4. 监控容器真实内存（不要只看 JVM 堆）
kubectl top pod <name> --containers
# 或
cat /sys/fs/cgroup/memory.current  # 容器视角的真实使用量
```

**反面教材**：某团队在 K8s 上跑了 2 个 JVM 实例（每个 `-Xmx4g`），容器 limit 也是 4g。**`-Xmx4g` ≠ JVM 实际只用 4g**，加上 Metaspace + 线程栈 + 直接内存 + Code Cache ≈ 5g+，**两个实例直接 OOM Killed**。解决方案：要么调小 `-Xmx`，要么用 `MaxRAMPercentage=40` 让 JVM 自己算。

---

## 二、实战案例：-Xmx 超过系统内存导致启动超时

### 2.1 背景

线上某 Spring Boot 服务，部署在 4 核 8g 的服务器上。某次配置调整后，应用启动时卡住，6000 秒（100 分钟）后报数据库连接超时，启动失败。

### 2.2 排查过程

**Step 1：现象观察**

```text
启动日志：
[2024-01-15 10:00:00] Starting Application...
[2024-01-15 10:00:05] Initializing Spring context...
[2024-01-15 10:00:10] Connecting to database...
... （日志停止）...
[2024-01-15 11:40:10] HikariPool - Connection is not available, request timed out after 6000ms.
[2024-01-15 11:40:10] Application startup failed
```

> 💡 关键现象：不是立即报错，而是卡了 100 分钟后才超时。说明进程还在，但系统响应极慢。

**Step 2：检查系统内存**

```bash
# 查看系统内存状态
free -h

# 输出：
              total        used        free      shared  buff/cache   available
Mem:          7.8G        7.5G         50M         10M       200M       100M
Swap:         4.0G        4.0G          0M           ← Swap 已用满！
```

> 🔴 关键发现：物理内存几乎耗尽（available 只有 100M），Swap 也已用满。系统处于严重的内存压力状态。

**Step 3：检查 JVM 参数**

```bash
# 查看启动参数
ps aux | grep java

# 输出：
java -Xms6g -Xmx6g -jar app.jar
      ↑
   -Xmx 设置为 6g，但系统只有 8g！
```

> 🔴 根因：`-Xmx6g` 看似小于系统总内存 8g，但 JVM 实际需要 6g（堆）+ 300m（Metaspace）+ 200m（线程栈）+ ... ≈ 6.5g+。加上操作系统和其他进程，内存完全不够。

**Step 4：为什么卡了 6000 秒？**

```text
启动过程：
1. JVM 启动，申请 6g 虚拟内存 → 成功（Overcommit）
2. 初始化 Spring 上下文，开始使用内存 → 物理内存逐渐耗尽
3. 创建数据库连接池，需要分配连接缓冲区
   → 物理内存不足，系统开始使用 Swap（极慢）
   → 数据库连接操作原本需要几毫秒，现在需要几秒甚至几十秒
4. 连接超时时间设置为 6000 秒（可能是配置错误或默认值）
   → 在 Swap 中挣扎了 100 分钟
   → 最终超时失败
```

**Step 5：检查 OOM Killer**

```bash
# 查看系统日志，是否有进程被杀
dmesg | grep -i "out of memory"

# 输出：
# [12345.678] Out of memory: Kill process 12345 (java) score 900 or sacrifice child
# 但这次 JVM 没有被杀，因为 Swap 还在，只是系统变得极慢
```

**Step 6：修复**

```bash
# 调整 -Xmx 为合理值
-Xms4g -Xmx4g

# JVM 总内存 ≈ 4g + 300m + 200m + ... ≈ 4.5g
# 系统 8g，留 3.5g 给操作系统和其他进程，安全

# 重启后正常启动，耗时 30 秒
```

### 2.3 根因分析

```text
配置错误链：

运维看到服务器是 8g 内存
      ↓
认为「内存充足，给 JVM 多分配点」
      ↓
设置 -Xmx6g（占系统内存 75%）
      ↓
忽略 JVM 还有其他内存开销（Metaspace、线程栈、Native）
      ↓
启动时虚拟内存分配成功，但物理内存不足
      ↓
系统开始使用 Swap，性能急剧下降
      ↓
数据库连接操作超时（6000s）
      ↓
启动失败
```

---

## 三、常见陷阱

### 3.1 ❌ 认为 -Xmx = JVM 总内存

**误区**：系统 8g，设置 `-Xmx6g` 应该没问题。

**现实**：JVM 总内存 ≈ -Xmx + Metaspace + 线程栈 + 直接内存 + Native，实际可能占用 -Xmx 的 1.3~1.5 倍。

```text
-Xmx6g 的实际占用：
  堆内存：        6.0g
+ Metaspace：     300m
+ 线程栈(200线程)：200m
+ 直接内存：      1.0g（如果用了 NIO）
+ Native：        200m
─────────────────────
  总计：          ≈ 7.7g  ← 几乎占满 8g 系统！
```

### 3.2 ❌ 容器环境只关注 -Xmx

**现象**：Docker 容器限制内存 4g，设置 `-Xmx3g`，认为留了 1g 给系统。

**问题**：
- JVM 实际需要 3g × 1.3 ≈ 3.9g
- 容器 OOM Killer 直接杀进程
- 或者容器内 Swap 被禁用，立即 OOM

```bash
# Docker 容器内检查内存限制
cat /sys/fs/cgroup/memory/memory.limit_in_bytes

# 设置 -Xmx 的推荐公式（容器环境）：
# -Xmx ≤ 容器内存限制 × 60%
# 例：容器 4g → -Xmx ≤ 2.4g，推荐 -Xmx2g
```

### 3.3 ❌ 忽略线程栈内存

**现象**：-Xmx 设置合理，但线程数很多（如 500 个），线程栈占用 500m+。

```bash
# 查看线程数
jstack <pid> | grep "java.lang.Thread.State" | wc -l

# 如果线程数过多，可以调整线程栈大小
-Xss512k  # 默认是 1m，可以减半
```

> ⚠️ 注意：-Xss 不要设太小，否则可能 StackOverflowError（特别是递归较深的代码）。

### 3.4 ❌ 数据库连接超时时间过长

**现象**：应用启动卡住很久才失败，排查时浪费时间。

**建议**：
- 启动阶段数据库连接超时设置为 30~60 秒即可
- 不要设置成 6000 秒（可能是误配置）
- 快速失败，快速发现问题

```yaml
# application.yml
spring:
  datasource:
    hikari:
      connection-timeout: 30000  # 30 秒，而非 6000 秒
```

---

## 四、最佳实践

### 4.1 -Xmx 安全值计算

```text
服务器环境：
-Xmx ≤ (系统总内存 - 操作系统预留) × 60%

操作系统预留：
  • Linux 基础：1g
  • 其他进程：每个 200~500m
  • 文件缓存：建议保留 1~2g（提升 I/O 性能）

示例：
  系统 8g：
    操作系统预留：2g
    可用内存：6g
    -Xmx ≤ 6g × 60% = 3.6g
    推荐：-Xmx2g ~ 3g

  系统 16g：
    操作系统预留：3g
    可用内存：13g
    -Xmx ≤ 13g × 60% = 7.8g
    推荐：-Xmx4g ~ 6g
```

### 4.2 容器环境配置模板

```bash
#!/bin/bash
# 容器启动脚本，自动计算 -Xmx

# 读取容器内存限制（单位：字节）
CONTAINER_MEMORY=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes)

# 转换为 MB
CONTAINER_MEMORY_MB=$((CONTAINER_MEMORY / 1024 / 1024))

# 计算 -Xmx（容器内存的 60%）
XMX_MB=$((CONTAINER_MEMORY_MB * 60 / 100))

# 对齐到整百
XMX_MB=$(( (XMX_MB / 100) * 100 ))

echo "Container memory: ${CONTAINER_MEMORY_MB}MB"
echo "Calculated -Xmx: ${XMX_MB}MB"

# 启动 JVM
exec java -Xms${XMX_MB}m -Xmx${XMX_MB}m \
     -XX:MetaspaceSize=256m \          # 补充：避免启动时频繁触发 GC 扩容（详见 metaspace-tuning-troubleshooting）
     -XX:MaxMetaspaceSize=512m \       # 原值 256m → 512m（与 metaspace-tuning-troubleshooting 最终配置对齐）
     -XX:+UseG1GC \
     -jar app.jar
```

### 4.3 启动前内存检查脚本

```bash
#!/bin/bash
# pre-check-memory.sh - 启动前检查内存配置是否合理

SYSTEM_MEMORY_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
SYSTEM_MEMORY_MB=$((SYSTEM_MEMORY_KB / 1024))

# 解析 -Xmx 参数
XMX=$(java -XshowSettings:memory -version 2>&1 | grep "Max heap size" | awk '{print $4}')
# 简化处理：从启动参数提取
XMX_PARAM=$(echo "$@" | grep -oP '\-Xmx\K[0-9]+[gGmM]')

if [[ $XMX_PARAM =~ ^([0-9]+)[gG]$ ]]; then
    XMX_MB=$((${BASH_REMATCH[1]} * 1024))
elif [[ $XMX_PARAM =~ ^([0-9]+)[mM]$ ]]; then
    XMX_MB=${BASH_REMATCH[1]}
else
    echo "Warning: Could not parse -Xmx parameter"
    exit 1
fi

# 计算安全阈值（系统内存的 60%）
SAFE_THRESHOLD_MB=$((SYSTEM_MEMORY_MB * 60 / 100))

echo "System memory: ${SYSTEM_MEMORY_MB}MB"
echo "-Xmx: ${XMX_MB}MB"
echo "Safe threshold (60%): ${SAFE_THRESHOLD_MB}MB"

if [ $XMX_MB -gt $SAFE_THRESHOLD_MB ]; then
    echo "❌ ERROR: -Xmx (${XMX_MB}MB) exceeds safe threshold (${SAFE_THRESHOLD_MB}MB)"
    echo "   JVM total memory will exceed system capacity!"
    echo "   Recommended: -Xmx${SAFE_THRESHOLD_MB}m or less"
    exit 1
else
    echo "✅ Memory configuration looks safe"
fi
```

### 4.4 关键配置建议

| 参数 | 建议值 | 说明 |
|------|--------|------|
| `-Xms` | = `-Xmx` | 避免堆动态伸缩 |
| `-Xmx` | ≤ 系统内存 × 60% | 留空间给 JVM 其他开销 + OS |
| `-XX:MaxMetaspaceSize` | 256m ~ 512m | 限制元空间上限 |
| `-Xss` | 512k ~ 1m | 线程栈大小，线程多时可以减半 |
| `-XX:MaxDirectMemorySize` | 按需设置 | 不设置则默认等于 -Xmx |
| 数据库连接超时 | 30s ~ 60s | 快速失败，避免长时间卡住 |

### 4.5 监控与告警

```bash
# 关键监控指标
1. 系统可用内存（available < 500m 告警）
2. Swap 使用率（Swap used > 0 告警）
3. OOM Killer 事件（dmesg 监控）
4. JVM 堆使用率（-Xmx 的 80% 告警）
5. GC 频率（Young GC 间隔 < 5s 告警）
```

---

## 五、面试话术（30 秒版）

> "JVM 总内存不等于 -Xmx，还包括 Metaspace、线程栈、直接内存和 Native 开销，实际可能是 -Xmx 的 1.3~1.5 倍。我遇到过一次线上事故，运维把 -Xmx 设成了 6g，服务器只有 8g 内存，启动时 JVM 实际占用超过 7g，物理内存不足导致系统频繁 Swap，应用卡在数据库连接初始化，等了 6000 秒才超时失败。排查时用 free -h 发现 Swap 已用满，jinfo 看到 -Xmx6g，调整到 4g 后正常启动。之后我建议 -Xmx 不超过系统内存的 60%，并加了启动前内存检查脚本。"

---

## 面试话术（90 秒版）

> 「**JVM 总内存 ≠ `-Xmx`**——这是 JVM 内存最常见的认知误区。`-Xmx` 只控制堆，但 JVM 实际占用还包括 **Metaspace + 线程栈 + 直接内存 + Code Cache + Native 自身开销**，**通常是 `-Xmx` 的 1.3~1.5 倍**。
>
> 具体公式：
>
> ```text
> JVM 总内存 ≈ -Xmx
>            + MaxMetaspaceSize（默认无上限）
>            + (线程数 × -Xss)
>            + MaxDirectMemorySize
>            + Native（Code Cache + GC + 内部结构，约 100~300MB）
> ```
>
> 举个真实案例：线上某 Spring Boot 服务，**4 核 8G 服务器，运维设置 `-Xmx6g`**，认为只占 75% 内存很安全。实际启动时 JVM 总内存 = 6g（堆）+ 300m（Metaspace）+ 200m（200 个线程 × 1m 栈）+ 1g（直接内存）+ 200m（Native）≈ **7.7g**，几乎占满 8G 系统。
>
> 结果是 JVM 启动时**虚拟内存分配成功**（Linux 的 overcommit 机制，vm.overcommit_memory=0 默认允许），但运行时物理内存不够，**系统疯狂 Swap**，数据库连接操作从几毫秒变成几秒，应用卡在初始化 100 分钟才超时失败，SSH 都进不去。**不会立即 OOM 报错**，这是最可怕的——`dmesg` 看也没 OOM Killer 记录。
>
> **3 大踩坑场景**：
>
> 1. **`-Xmx` 过大**——`-Xmx` 不应超过**系统内存的 60%**（留 40% 给 OS + 其他进程 + 文件缓存）。4G 服务器 `-Xmx ≤ 2.4G`、8G 服务器 `-Xmx ≤ 4.8G`。
>
> 2. **容器环境只设 `-Xmx`**——Docker 容器限制 4G 内存，JDK 10+ 通过 `UseContainerSupport` 读 cgroup 限制，但**默认 `MaxRAMPercentage=25%`**（JDK 8u191~21）或 50%（JDK 22+），4G 容器下 Xmx 默认只有 1G（25%）或 2G（50%）。**必须显式设 `MaxRAMPercentage=50~75`**。
>
> 3. **线程数爆炸**——`-Xss` 默认 1MB，500 线程就吃 500MB。生产环境**应设 `-Xss256k~512k`**（除非有深度递归）。
>
> 实践经验：上线前用 **`java -XshowSettings:memory -version`** 看实际堆配置，加**启动前内存检查脚本**对比 `-Xmx` 与系统 `MemTotal`，超阈值就拒绝启动——比线上卡死靠谱。」

---

## 六、交叉引用

- 主模块：[`01.java`](../../../01.java-and-jvm/) — Java 知识体系
- [CPU 飙升排查](../cpu-spike-troubleshooting/) — -Xmx 过小导致 CPU 100%
- [JVM 内存区域](../jvm-memory/) — JVM 运行时数据区详解
- [GC 算法与收集器](../gc-algorithms/) — GC 算法与各类收集器对比
- [JVM Metaspace 调优踩坑](../metaspace-tuning-troubleshooting/) — 只设 MaxMetaspaceSize 不设 MetaspaceSize 触发频繁 GC + 容器默认 Xmx 陷阱

## 相关章节

- 深度阅读：[`01.java-and-jvm`](../../../01.java-and-jvm/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · jvm-memory-pitfall](../README.md)
