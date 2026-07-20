<!--
module:
  parent: system-design/file-upload
  slug: system-design/04-high-performance/file-upload/03-storage
  type: topic
  category: 秒传与存储
  summary: 秒传原理（MD5 去重 + 内容寻址）+ 对象存储选型（OSS/S3/MinIO）+ 引用计数 + GC
-->

# 秒传与存储 · 内容寻址去重 + 对象存储

> **一句话**：秒传 = **上传前查 MD5，已存在则创建引用不传数据**；内容寻址 = **相同 MD5 只存一份物理文件，多个用户共享引用**。

← [返回: file-upload 总目录](README.md)

---

## 1. 秒传原理

### 1.1 流程

```sql
用户上传文件
    │
    ▼ 前端计算 MD5（WebWorker 不阻塞 UI）
MD5 = "abc123def456"
    │
    ▼ POST /api/upload/init {md5: "abc123def456"}
后端查询 DB: SELECT * FROM file_record WHERE md5 = ?
    │
    ├─ 找到 → 秒传成功
    │   INSERT INTO file_record (user_id, md5, object_key, ref_count)
    │   VALUES (new_user, 'abc123def456', existing.object_key, existing.ref_count + 1)
    │   → 返回 {instant: true, fileUrl: existing.fileUrl}
    │
    └─ 没找到 → 正常上传
        → 返回 {instant: false, uploadId: "xxx"}
```

### 1.2 MD5 计算策略

| 策略 | 耗时（1GB） | 内存 | 适用 |
|------|-----------|------|------|
| **全量计算** | ~3 秒 | 低（流式） | 默认方案 |
| **抽样 + 全量** | ~1 秒（快路径） | 低 | 大文件快速判断 |
| **前端 WebWorker** | ~5 秒 | 不阻塞 UI | 生产首选 |

**抽样策略**（快速判断文件是否可能已存在）：

```javascript
// 快速抽样 MD5：取文件头 1MB + 尾 1MB + 中间 1MB
async function quickMD5(file) {
    const head = file.slice(0, 1024 * 1024);
    const tail = file.slice(file.size - 1024 * 1024);
    const mid = file.slice(file.size / 2 - 512 * 1024, file.size / 2 + 512 * 1024);

    const sampleBlob = new Blob([head, tail, mid]);
    const sampleMD5 = await calculateMD5(sampleBlob);

    // 先用抽样 MD5 查询（可能有误判）
    const result = await checkBySampleMD5(sampleMD5, file.size);
    if (result.confirmed) return result;  // 精确匹配（大小 + 抽样 MD5 都一致）

    // 不确定 → 全量 MD5
    return await calculateFullMD5(file);
}
```

### 1.3 MD5 碰撞问题

**Q：MD5 碰撞了怎么办？两个不同文件 MD5 相同？**

**答**：
- **概率极低**：MD5 碰撞概率约 2^-128，10 亿文件也只有 ~10^-20 的概率碰撞
- **双重校验**：MD5 + 文件大小（两个维度同时碰撞的概率趋近于 0）
- **生产加固**：用 SHA-256 替代 MD5（更安全但计算略慢）

```java
// 双重校验
FileRecord existing = fileRecordRepo.findByMd5AndSize(md5, fileSize);
if (existing != null) {
    // 秒传
}
```

---

## 2. 内容寻址与引用计数

### 2.1 存储模型

```text
物理存储（OSS）：
/objects/abc123def456    ← 只存一份物理文件

逻辑记录（MySQL）：
file_record:
┌──────────┬─────────┬──────────────────────────┬───────────┐
│ file_id  │ user_id │ object_key               │ ref_count │
├──────────┼─────────┼──────────────────────────┼───────────┤
│ 1        │ 1001    │ /objects/abc123def456    │ 3         │
│ 2        │ 1002    │ /objects/abc123def456    │ (引用同1) │
│ 3        │ 1003    │ /objects/abc123def456    │ (引用同1) │
└──────────┴─────────┴──────────────────────────┴───────────┘
```

### 2.2 引用计数与 GC

```java
// 用户删除文件时
public void deleteFile(long fileId, long userId) {
    FileRecord record = fileRecordRepo.findById(fileId);

    // 减少引用计数
    int newRefCount = fileRecordRepo.decrementRefCount(record.getMd5());

    if (newRefCount == 0) {
        // 无人引用 → 删除物理文件
        ossClient.deleteObject(record.getObjectKey());
    }
    // 删除逻辑记录
    fileRecordRepo.delete(fileId);
}
```

**定时 GC（防止引用计数不一致）**：

```java
@Scheduled(cron = "0 0 4 * * ?")  // 每天凌晨 4 点
public void gcOrphanObjects() {
    // 扫描 OSS 中所有 object
    // 对比 DB 中的 object_key
    // 无引用的 object → 删除
}
```

---

## 3. 对象存储选型

### 3.1 对比

| 特性 | 阿里云 OSS | AWS S3 | MinIO（自建） |
|------|-----------|--------|-------------|
| **部署** | 托管 | 托管 | 自建 |
| **成本** | 按量计费 | 按量计费 | 硬件 + 运维 |
| **分片上传** | ✅ Multipart Upload | ✅ Multipart Upload | ✅ |
| **CDN 集成** | ✅ 阿里云 CDN | ✅ CloudFront | ❌ 需自建 |
| **跨域** | CORS 配置 | CORS 配置 | 配置 |
| **适用** | 中小规模 | 海外业务 | 私有化部署 |

### 3.2 分片存储路径设计

```text
chunks/{uploadId}/{chunkIndex}     ← 临时分片（合并后删除）
objects/{md5}                       ← 合并后的完整文件（内容寻址）
thumbnails/{md5}/                   ← 缩略图 / 预览
  ├── small.jpg (200x200)
  ├── medium.jpg (800x800)
  └── original.webp
```

### 3.3 上传加速

| 方案 | 原理 | 加速比 |
|------|------|--------|
| **CDN 上传加速** | 就近边缘节点接收 → 回源 OSS | 2-5x |
| **预签名 URL** | 前端直传 OSS（不经后端） | 3-10x |
| **分片并发** | 3-6 片同时上传 | 2-3x |

**预签名 URL 直传**（推荐）：

```java
// 后端生成预签名 URL
@GetMapping("/api/upload/presign")
public String presign(@RequestParam String uploadId, @RequestParam int chunkIndex) {
    String objectKey = "chunks/" + uploadId + "/" + chunkIndex;
    URL url = ossClient.generatePresignedUrl(
        objectKey, HttpMethod.PUT,
        Date.from(Instant.now().plus(Duration.ofMinutes(30)))
    );
    return url.toString();
}

// 前端直传 OSS
const presignedUrl = await fetch(`/api/upload/presign?uploadId=${id}&chunkIndex=${i}`);
await fetch(presignedUrl, { method: 'PUT', body: chunk });
// 不经过后端，直接上传到 OSS → 减少后端带宽压力
```

---

## 4. 系列导航

| 文章 | 核心内容 |
|------|---------|
| [总目录](README.md) | 需求分析 + 架构概览 + 面试话术 |
| [架构演进](01-architecture.md) | 3 阶段架构 + 5 大组件 |
| [分片与断点续传](02-chunked-and-resumable.md) | 分片协议 + 断点续传 + 并发控制 |
| **本文** | MD5 去重 + 对象存储 + 引用计数 |

← [返回: file-upload 总目录](README.md)
