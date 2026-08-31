<!--
question:
  id: 01.java-excel-export-oom
  topic: 01.java
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 生产实战
  tags: [01.java, Excel, OOM, 多线程, 流式写入, 分批查询, 内存优化]
-->

# 把几十万数据导出到 Excel 直接 OOM 了，怎么利用多线程来导出百万数据到 Excel？为什么多线程可以改善内存占用？

> **一句话定位**：大数据量 Excel 导出 OOM 的经典陷阱 —— 根因是 **POI 全量加载 + 一次性查询 + 对象未释放**，多线程改善内存的核心是 **分片查询 + 独立写入 + 及时 GC**。

---

## 引子：百万数据导出，OOM 告警凌晨 2 点

```text
告警时间：2024-03-15 02:17
现象：运营触发"全量订单导出"，后台 JVM 直接 OOM: Java heap space
堆转储：XSSFWorkbook 对象占堆 1.8 GB，而 JVM 最大堆仅 2 GB
损失：导出任务失败 + 运营投诉 + 凌晨 oncall 被叫醒
```

直觉上"加多线程能提速"，但面试官追问"为什么多线程能降低内存？"——很多人卡住。
根因不是"写得慢"，而是 **POI 全量加载 + 一次性查询 + 对象未释放** 三重叠加。多线程真正的作用不是加速写入，而是让每个线程只持有**一片数据**，独立 GC，避免百万行对象同时驻留堆中。

---

## 🎯 面试高频拷问

```text
Q1：把几十万数据导出到 Excel 直接 OOM 了，怎么解决？
Q2：怎么利用多线程来导出百万数据到 Excel？
Q3：为什么多线程可以改善内存占用？
```

**回答框架（3 大根因 + 4 大方案 + 多线程原理）**：

1. **OOM 根因**：POI 全量加载 + 一次性查询 + 对象未释放
2. **解决方案**：流式写入（EasyExcel）+ 分批查询 + 多线程分片 + 内存优化
3. **多线程改善内存的原理**：分片查询 + 独立 Sheet/文件 + 及时 GC

---

## ⚠️ OOM 根因分析（3 大原因）

### 根因 1：POI 全量加载（XSSFWorkbook）

**问题**：Apache POI 的 `XSSFWorkbook` 会把整个 Excel 文件加载到内存。

```java
// ❌ 错误示例：几十万数据全部加载到内存
XSSFWorkbook workbook = new XSSFWorkbook();
XSSFSheet sheet = workbook.createSheet();

for (int i = 0; i < 1000000; i++) {
    XSSFRow row = sheet.createRow(i);  // 100 万行全部在内存
    row.createCell(0).setCellValue("data");
}

workbook.write(new FileOutputStream("output.xlsx"));
// OOM: Java heap space
```

**内存占用估算**：
- 每行 ~1 KB（含 Cell 对象、样式、公式）
- 100 万行 ≈ **1 GB**
- 加上 JVM 堆限制（默认 256MB~1GB）→ OOM

### 根因 2：一次性查询所有数据

**问题**：数据库一次性查询所有数据到内存。

```java
// ❌ 错误示例：一次性查询 100 万条
List<User> users = userMapper.selectAll();  // 100 万条全部加载到 JVM

for (User user : users) {
    // 写入 Excel
}
```

**内存占用**：
- 每个 User 对象 ~500 字节
- 100 万条 ≈ **500 MB**
- 加上 Excel 对象 → 翻倍 → OOM

### 根因 3：对象未及时释放

**问题**：大对象未及时 GC，导致内存泄漏。

```java
// ❌ 错误示例：对象堆积
List<User> batch1 = queryBatch1();  // 10 万条
List<User> batch2 = queryBatch2();  // 10 万条
// ... 持续查询，所有 batch 都在内存

// 没有及时释放 batch1、batch2...
```

---

## ✅ 解决方案（4 大方案）

### 方案 1：流式写入（EasyExcel / SXSSF）

**原理**：边写边刷盘，不在内存中保留所有行。

```java
// ✅ 正确示例：EasyExcel 流式写入
EasyExcel.write("output.xlsx", User.class)
    .sheet("用户列表")
    .doWrite(() -> {
        // 流式查询，分批写入
        return userMapper.selectStream();  // 返回 Stream<User>
    });
```

**EasyExcel 优势**：
- 底层使用 SAX 模式解析，内存占用极低
- 100 万行写入仅需 **~50 MB** 内存
- 自动管理临时文件

**POI SXSSF 方案**：
```java
// POI 流式写入
SXSSFWorkbook workbook = new SXSSFWorkbook(100);  // 只保留 100 行在内存
SXSSFSheet sheet = workbook.createSheet();

for (int i = 0; i < 1000000; i++) {
    SXSSFRow row = sheet.createRow(i);
    row.createCell(0).setCellValue("data");

    // 每 1000 行刷盘一次
    if (i % 1000 == 0) {
        workbook.dispose();  // 清理临时文件
    }
}
```

### 方案 2：分批查询（游标查询 / 分页查询）

**原理**：不一次性加载所有数据，分批查询 + 分批写入。

```java
// ✅ 正确示例：分批查询 + 分批写入
int batchSize = 10000;
int offset = 0;

while (true) {
    List<User> batch = userMapper.selectPage(offset, batchSize);

    if (batch.isEmpty()) {
        break;  // 查询完毕
    }

    // 写入当前批次
    writeBatchToExcel(batch, sheet);

    // 及时释放
    batch.clear();
    System.gc();  // 提示 GC（可选）

    offset += batchSize;
}
```

**MyBatis 游标查询**：
```java
// MyBatis Cursor 流式查询
try (Cursor<User> cursor = userMapper.selectCursor()) {
    cursor.forEach(user -> {
        // 逐行处理，不加载全部
        writeRowToExcel(user, sheet);
    });
}
```

### 方案 3：多线程分片（每个线程处理一个 Sheet 或文件）

**原理**：将数据分片，每个线程独立处理一个 Sheet 或文件，最后合并。

```java
// ✅ 正确示例：多线程分片导出
int totalRows = 1000000;
int shardSize = 100000;  // 每个线程处理 10 万行
int shardCount = totalRows / shardSize;  // 10 个分片

ExecutorService executor = Executors.newFixedThreadPool(10);
List<Future<File>> futures = new ArrayList<>();

for (int i = 0; i < shardCount; i++) {
    final int shardIndex = i;

    Future<File> future = executor.submit(() -> {
        // 每个线程独立查询 + 写入
        int offset = shardIndex * shardSize;
        List<User> batch = userMapper.selectPage(offset, shardSize);

        File tempFile = File.createTempFile("export_" + shardIndex, ".xlsx");
        EasyExcel.write(tempFile, User.class)
            .sheet("Sheet" + shardIndex)
            .doWrite(batch);

        return tempFile;
    });

    futures.add(future);
}

// 等待所有线程完成，合并文件
List<File> tempFiles = futures.stream()
    .map(f -> {
        try { return f.get(); }
        catch (Exception e) { throw new RuntimeException(e); }
    })
    .collect(Collectors.toList());

mergeExcelFiles(tempFiles, "final_output.xlsx");

// 清理临时文件
tempFiles.forEach(File::delete);
executor.shutdown();
```

### 方案 4：内存优化（对象复用 + 及时 GC）

**技巧**：
1. **对象复用**：避免重复创建大对象
2. **及时 GC**：批次处理完后调用 `System.gc()`
3. **弱引用**：大对象使用 `WeakReference`

```java
// ✅ 内存优化示例
public void exportExcel() {
    // 1. 复用 Workbook 对象
    try (ExcelWriter writer = EasyExcel.write("output.xlsx").build()) {
        WriteSheet sheet = EasyExcel.writerSheet("用户列表").build();

        // 2. 分批查询 + 写入
        int batchSize = 10000;
        int offset = 0;

        while (true) {
            List<User> batch = userMapper.selectPage(offset, batchSize);

            if (batch.isEmpty()) break;

            writer.write(batch, sheet);

            // 3. 及时释放
            batch.clear();

            // 4. 每 10 批次提示 GC
            if (offset % (batchSize * 10) == 0) {
                System.gc();
            }

            offset += batchSize;
        }
    }
}
```

---

## 🧠 为什么多线程可以改善内存占用？

### 核心原理：分治 + 隔离

```text
单线程导出（OOM）：
┌─────────────────────────────────────┐
│  查询 100 万条 → 全部在内存 → OOM   │
└─────────────────────────────────────┘

多线程导出（改善）：
┌──────────┐  ┌──────────┐  ┌──────────┐
│ 线程 1   │  │ 线程 2   │  │ 线程 3   │
│ 10 万条  │  │ 10 万条  │  │ 10 万条  │
│ ~50 MB   │  │ ~50 MB   │  │ ~50 MB   │
└──────────┘  └──────────┘  └──────────┘
     ↓              ↓              ↓
  独立写入        独立写入        独立写入
  Sheet 1        Sheet 2        Sheet 3

总内存：10 × 50 MB = 500 MB（可控）
```

### 3 大改善机制

| 机制 | 说明 | 内存改善 |
|------|------|---------|
| **分片查询** | 每个线程只查询自己的分片（如 10 万条） | 避免一次性加载 100 万条 |
| **独立写入** | 每个线程写入独立的 Sheet/文件 | 避免单个 Workbook 过大 |
| **及时 GC** | 线程结束后，其内存可被 GC 回收 | 内存峰值降低 |

### 内存对比

| 方案 | 内存占用 | 导出 100 万行 |
|------|---------|--------------|
| 单线程 + POI | ~1 GB | OOM ❌ |
| 单线程 + EasyExcel | ~100 MB | ✅ 可行 |
| 多线程 + EasyExcel（10 线程） | ~500 MB | ✅ 更快 |

---

## 💡 30 秒面试话术

> "大数据量 Excel 导出 OOM 的根因是 **POI 全量加载 + 一次性查询 + 对象未释放**。
>
> 解决方案有 4 个：
>
> **第一**：流式写入。用 EasyExcel 或 POI SXSSF，边写边刷盘，不在内存保留所有行。EasyExcel 100 万行只需 50 MB。
>
> **第二**：分批查询。不要一次性 selectAll，而是分页查询 + 分批写入，每批 1 万条。
>
> **第三**：多线程分片。把 100 万条分成 10 个分片，每个线程处理 10 万条，写入独立的 Sheet 或文件，最后合并。
>
> **第四**：内存优化。对象复用 + 及时 GC，批次处理完后调用 `System.gc()`。
>
> **多线程改善内存的原理**：分治 + 隔离。每个线程只查询自己的分片（10 万条），写入独立的 Sheet，线程结束后内存可被 GC 回收。这样内存峰值从 1 GB 降到 500 MB，避免 OOM。"

---

## 📚 深度阅读

- [主模块深度文章](../../../01.java-and-jvm/03-concurrency/excel-export-oom/README.md) — 完整代码示例 + 性能对比 + 生产环境注意事项
- [线程池 7 大参数](../thread-pool/) — ThreadPoolExecutor 核心参数详解
- [JVM 内存区域](../jvm-memory/) — JVM 内存模型 + GC 算法

---

> 📅 2026-09-01 · 咬文嚼字 · Excel 导出 OOM · ⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回: Java 咬文嚼字](../README.md)
