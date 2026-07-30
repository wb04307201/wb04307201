<!--
question:
  id: 01.java-full-gc-troubleshooting
  topic: 01.java
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 线上故障
  tags: [01.java, JVM, gc, troubleshooting]
-->

# 线上频繁 Full GC 排查全链路

## 引子：深夜告警

```text
[2026-07-30T02:15:32.451+0800] 4271.234: [Full GC (Ergonomics) 3.8G->3.6G:4.0G, 4.523 secs]
[2026-07-30T02:15:38.102+0800] 4276.885: [Full GC (Allocation Failure) 3.9G->3.7G:4.0G, 5.102 secs]
[2026-07-30T02:15:44.320+0800] 4283.103: [Full GC (Ergonomics) 3.9G->3.7G:4.0G, 4.891 secs]
[2026-07-30T02:15:50.512+0800] 4289.295: [Full GC (Allocation Failure) 3.9G->3.8G:4.0G, 5.234 secs]
```

Full GC 每 6 秒一次，每次停顿 4~5 秒——用户请求大面积超时，接口 504。

**怎么排查？**

---

## 一、核心原理

### 1.1 Full GC 的 4 大触发条件

| 触发条件 | 说明 | 常见场景 |
|----------|------|----------|
| **老年代空间不足** | 老年代可用空间低于阈值，无法容纳晋升对象 | -Xmx 过小 / 内存泄漏 / 大对象直接晋升 |
| **Metaspace 不足** | 元空间满了，触发 Full GC 尝试释放 | 动态代理/CGLIB/Groovy 脚本大量生成类 |
| **System.gc() 显式调用** | 代码或第三方库显式触发 Full GC | RMI / NIO DirectBuffer / JMX 定期调用 |
| **CMS promotion failed** | 并发清除期间老年代被填满，晋升失败 | CMS 收集器，老年代预留空间不足 |

### 1.2 Full GC 为什么停顿长？

Full GC 需要扫描整个堆（新生代 + 老年代 + Metaspace），标记所有存活对象，执行清理或整理。堆越大，耗时越长。

```text
Minor GC：只扫新生代（通常几十 MB）→ 停顿 10~50ms
Full GC  ：扫全堆（几 GB）           → 停顿 500ms~数秒
```

---

## 二、排查工具箱

| 工具 | 用途 | 常用命令 |
|------|------|----------|
| `jstat` | 实时监控 GC 频率和堆占用 | `jstat -gcutil <pid> 1000` |
| `jmap -histo` | 查看堆内对象分布 | `jmap -histo <pid> \| head -30` |
| `jmap -dump` | 导出堆快照 | `jmap -dump:format=b,file=heap.hprof <pid>` |
| `jcmd` | 综合性诊断 | `jcmd <pid> GC.class_histogram` |
| `MAT` | 离线分析堆转储 | Eclipse Memory Analyzer Tool |
| GC 日志 | 分析 GC 历史 | `-Xlog:gc*:file=gc.log:time,uptime,level,tags` |

---

## 三、排查五步法

**Step 1：确认 GC 频率**

```bash
jstat -gcutil <pid> 1000

# 输出示例：
#  S0     S1     E      O      M     CCS    YGC   YGCT    FGC   FGCT    GCT
#  0.00  95.23  88.12  98.76  92.34 88.12  12543  89.12  6271  234.56  323.68
#  0.00  95.23  92.45  99.12  92.34 88.12  12544  89.25  6272  234.89  324.14
#                        ↑              ↑            ↑
#                   老年代 98.76%    Full GC 已 6271 次  平均每次 37ms+
```

关键指标：**O%（老年代占用）> 90%、FGC（Full GC 次数）持续增长**，说明问题确凿。

**Step 2：看大对象**

```bash
jmap -histo <pid> | head -30

# 输出示例：
#  num     #instances         #bytes  class name
# ----------------------------------------------
#    1:     12500000     1200000000  java.util.HashMap$Node
#    2:      8500000      680000000  byte[]
#    3:      5200000      416000000  java.lang.String
#    4:      3100000      248000000  java.util.ArrayList
```

如果 `HashMap$Node` 或 `byte[]` 占据榜首，说明可能存在**内存泄漏**或**大对象**。

**Step 3：导出堆快照**

```bash
jmap -dump:format=b,file=/tmp/heap.hprof <pid>
```

生产环境建议配置自动 dump：
```bash
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/data/logs/
```

**Step 4：MAT 分析**

1. 打开 `heap.hprof`
2. **Dominator Tree**：查看占用最大的对象链
3. **Leak Suspects**：自动报告疑似泄漏点
4. **Path to GC Roots**：确认对象为什么没被回收

**Step 5：定位代码 + 修复**

根据 MAT 分析结果定位到具体类和代码行，修改后重启验证。

---

## 四、5 大根因 + 修复方案

| 根因 | 现象 | 排查手段 | 修复方案 |
|------|------|----------|----------|
| **1. 内存泄漏**：集合/缓存/连接未关闭 | Old% 持续上升不降，FGC 频繁，`jmap -histo` 显示某类实例暴增 | MAT 分析 Dominator Tree，找到 GC Roots 路径 | 清理无用引用 / 加 TTL / 连接池复用 / WeakHashMap |
| **2. 大对象直接进老年代**：大数组/大 String | `jmap -histo` 显示 `byte[]` / `String` 单个体积巨大（>1MB） | GC 日志看分配速率，jmap 看对象大小分布 | 分批处理 / 流式读取 / 对象池复用 / 调大新生代 |
| **3. 老年代空间不足**：-Xmx 过小 | Old% 长期 >90%，扩容后 GC 频率骤降 | `jinfo -flags <pid>` 看 -Xmx 值，对比实际工作集 | 调大 -Xmx（Xms=Xmx），监控基线后再定 |
| **4. Metaspace 不足**：动态类太多 | `jstat` 的 M% 接近 100%，`jmap -clstats` 显示类加载器泄漏 | `jcmd <pid> GC.class_histogram` 看类数量 | `-XX:MaxMetaspaceSize=512m`，排查类加载器泄漏 |
| **5. 显式 System.gc()**：RMI/JMX 触发 | GC 日志显示 `System.gc()` 字样，FGC 规律性出现（如每 5 分钟一次） | GC 日志过滤 `System.gc()`，`jcmd <pid> VM.flags` | `-XX:+DisableExplicitGC` 禁用，或用 G1/ZGC 替代 |

---

## 五、调优方向

### 5.1 GC 收集器选择

| 场景 | 推荐收集器 | 理由 |
|------|-----------|------|
| 堆 < 4GB，延迟不敏感 | G1（JDK 9+ 默认） | 自动调优，综合性能好 |
| 堆 > 4GB，停顿要求 < 200ms | G1 | 可预测停顿，Region 化管理 |
| 堆 > 32GB，极低延迟（<10ms） | ZGC | 染色指针+读屏障，停顿与堆大小无关 |

### 5.2 关键 JVM 参数

```bash
# 堆内存：初始 = 最大，避免动态扩容触发 Full GC
-Xms4g -Xmx4g

# G1：提前触发并发标记，避免退化 Full GC
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:InitiatingHeapOccupancyPercent=45

# Metaspace：防止动态类撑爆元空间
-XX:MetaspaceSize=256m
-XX:MaxMetaspaceSize=512m

# GC 日志：出问题时有据可查
-Xlog:gc*:file=gc.log:time,uptime,level,tags

# OOM 自动保留现场
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/data/logs/

# 禁用显式 Full GC（生产环境推荐）
-XX:+DisableExplicitGC
```

---

## 六、面试话术（30 秒版）

> "线上频繁 Full GC 排查分五步：第一步用 `jstat -gcutil` 确认老年代占用和 Full GC 频率；第二步用 `jmap -histo` 看堆内大对象分布；第三步导出堆快照 `jmap -dump`；第四步用 MAT 分析 Dominator Tree 和 Leak Suspects 定位泄漏对象链；第五步定位到具体代码修复。常见根因有 5 种——内存泄漏、大对象直接进老年代、-Xmx 过小、Metaspace 不足和显式 System.gc() 调用，每种对应不同的排查手段和修复方案。"

---

## 七、交叉引用

- 主模块：[`01.java`](../../../01.java/) — Java 知识体系
- [CPU 飙升排查](../cpu-spike-troubleshooting/) — 线上 CPU 100% 排查全流程
- [GC 算法与收集器](../gc-algorithms/) — GC 算法与各类收集器对比
- [JVM 内存区域](../jvm-memory/) — JVM 运行时数据区详解
- [Excel 导出 OOM](../excel-export-oom/) — 大文件导出内存溢出排查

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · full-gc-troubleshooting](../README.md)
