<!--
module:
  parent: system-design/file-upload
  slug: system-design/04-high-performance/file-upload/02-chunked
  type: topic
  category: 分片与断点续传
  summary: 分片上传协议设计 + 断点续传实现 + 并发控制 + 前端进度条 + 后端合并
-->

# 分片上传与断点续传 · 大文件上传的核心协议

> **一句话**：分片上传 = **前端 slice 切片（5MB）+ 并发 PUT + 后端记录分片状态**；断点续传 = **重连后查询已上传分片 + 从断点继续**。

← [返回: file-upload 总目录](README.md)

---

## 1. 分片上传协议

### 1.1 API 设计

```text
POST /api/upload/init
Body: {filename, fileSize, md5, totalChunks}
Response: {uploadId, uploadedChunks: []}  // 秒传检查 + 初始化

PUT /api/upload/chunk
Headers: {X-Upload-Id, X-Chunk-Index, X-Chunk-MD5}
Body: <binary chunk data>
Response: {chunkIndex, status: "ok"}

POST /api/upload/merge
Body: {uploadId}
Response: {fileId, fileUrl, status: "merging"}

GET /api/upload/status/{uploadId}
Response: {uploadId, status, uploadedChunks: [0,1,2,...,99], totalChunks: 200}
```

### 1.2 前端实现

```javascript
class ChunkedUploader {
    constructor(file, chunkSize = 5 * 1024 * 1024) {
        this.file = file;
        this.chunkSize = chunkSize;
        this.totalChunks = Math.ceil(file.size / chunkSize);
        this.uploadId = null;
        this.uploadedChunks = new Set();
        this.concurrency = 3;  // 并发数
    }

    async start() {
        // 1. 初始化（含秒传检查）
        const md5 = await this.calculateMD5(this.file);
        const init = await fetch('/api/upload/init', {
            method: 'POST',
            body: JSON.stringify({
                filename: this.file.name,
                fileSize: this.file.size,
                md5: md5,
                totalChunks: this.totalChunks
            })
        }).then(r => r.json());

        if (init.instant) return;  // 秒传成功
        this.uploadId = init.uploadId;
        this.uploadedChunks = new Set(init.uploadedChunks || []);

        // 2. 并发上传分片
        await this.uploadChunks();

        // 3. 合并
        await fetch('/api/upload/merge', {
            method: 'POST',
            body: JSON.stringify({ uploadId: this.uploadId })
        });
    }

    async uploadChunks() {
        const pending = [];
        for (let i = 0; i < this.totalChunks; i++) {
            if (!this.uploadedChunks.has(i)) pending.push(i);
        }

        // 并发控制：最多同时 N 片
        const pool = [];
        for (const idx of pending) {
            const task = this.uploadOneChunk(idx).then(() => {
                this.uploadedChunks.add(idx);
                this.onProgress(this.uploadedChunks.size / this.totalChunks);
            });
            pool.push(task);
            if (pool.length >= this.concurrency) {
                await Promise.race(pool);
                pool.splice(pool.findIndex(p => p.resolved), 1);
            }
        }
        await Promise.all(pool);
    }

    async uploadOneChunk(index) {
        const start = index * this.chunkSize;
        const end = Math.min(start + this.chunkSize, this.file.size);
        const chunk = this.file.slice(start, end);

        await fetch('/api/upload/chunk', {
            method: 'PUT',
            headers: {
                'X-Upload-Id': this.uploadId,
                'X-Chunk-Index': index,
                'X-Chunk-MD5': await this.calculateMD5(chunk)
            },
            body: chunk
        });
    }
}
```

### 1.3 后端实现（Spring Boot）

```java
@RestController
@RequestMapping("/api/upload")
public class UploadController {

    @PostMapping("/init")
    public UploadInitResponse init(@RequestBody UploadInitRequest req) {
        // 秒传检查
        FileRecord existing = fileRecordRepo.findByMd5(req.getMd5());
        if (existing != null) {
            fileRecordRepo.createRef(existing.getFileId(), req.getUserId());
            return UploadInitResponse.instant(existing.getFileUrl());
        }

        // 创建上传会话
        String uploadId = UUID.randomUUID().toString();
        uploadSessionRepo.create(uploadId, req);
        redisTemplate.opsForSet().add("upload:" + uploadId + ":chunks");
        redisTemplate.expire("upload:" + uploadId + ":chunks", 24, TimeUnit.HOURS);

        return UploadInitResponse.normal(uploadId);
    }

    @PutMapping("/chunk")
    public void uploadChunk(
            @RequestHeader("X-Upload-Id") String uploadId,
            @RequestHeader("X-Chunk-Index") int chunkIndex,
            @RequestHeader("X-Chunk-MD5") String chunkMd5,
            @RequestBody MultipartFile chunk) throws IOException {

        // 1. 校验分片 MD5
        String actualMd5 = DigestUtils.md5Hex(chunk.getInputStream());
        if (!actualMd5.equals(chunkMd5)) {
            throw new ChunkCorruptException("分片 MD5 不匹配");
        }

        // 2. 写入 OSS 临时路径
        String ossKey = "chunks/" + uploadId + "/" + chunkIndex;
        ossClient.putObject(ossKey, chunk.getInputStream());

        // 3. 记录已上传
        redisTemplate.opsForSet().add("upload:" + uploadId + ":chunks", chunkIndex);
        uploadChunkRepo.save(new UploadChunk(uploadId, chunkIndex, chunk.getSize(), chunkMd5, ossKey));
    }

    @PostMapping("/merge")
    public void merge(@RequestBody MergeRequest req) {
        // 异步合并（MQ 消费）
        mqTemplate.send("file-merge", req.getUploadId());
    }
}
```

---

## 2. 断点续传

### 2.1 原理

```text
第 1 次上传：
  chunk 0 ✅ → chunk 1 ✅ → ... → chunk 99 ✅ → 断网！

第 2 次（续传）：
  POST /api/upload/init（带原 uploadId 或新 uploadId + MD5）
  → 后端返回 uploadedChunks: [0, 1, ..., 99]
  → 前端从 chunk 100 继续
```

### 2.2 Redis 状态管理

```java
// 记录已上传分片（Redis Set）
// Key: upload:{uploadId}:chunks
// Value: Set<Integer> chunkIndex

// 查询已上传分片
Set<Object> uploaded = redisTemplate.opsForSet().members("upload:" + uploadId + ":chunks");

// 续传时跳过已完成的
List<Integer> pending = IntStream.range(0, totalChunks)
    .filter(i -> !uploaded.contains(i))
    .boxed().collect(Collectors.toList());
```

### 2.3 过期清理

```java
@Scheduled(cron = "0 0 3 * * ?")  // 每天凌晨 3 点
public void cleanExpiredUploads() {
    // 查找 24h 未活动的 upload session
    List<String> expired = uploadSessionRepo.findExpired(Duration.ofHours(24));
    for (String uploadId : expired) {
        // 删除 OSS 上的分片
        ossClient.deleteObjects("chunks/" + uploadId + "/");
        // 删除 Redis 状态
        redisTemplate.delete("upload:" + uploadId + ":chunks");
        // 标记 session 为 failed
        uploadSessionRepo.updateStatus(uploadId, "failed");
    }
}
```

---

## 3. 合并与校验

```java
@Component
public class FileMerger {

    public void merge(String uploadId) {
        UploadSession session = uploadSessionRepo.findById(uploadId);
        List<UploadChunk> chunks = uploadChunkRepo.findByUploadIdOrderByIndex(uploadId);

        // 1. 下载所有分片并合并
        String tempPath = "/tmp/merge/" + uploadId;
        try (OutputStream out = new BufferedOutputStream(new FileOutputStream(tempPath))) {
            for (UploadChunk chunk : chunks) {
                InputStream in = ossClient.getObject(chunk.getStoragePath());
                in.transferTo(out);
            }
        }

        // 2. 校验完整文件 MD5
        String actualMd5 = DigestUtils.md5Hex(new FileInputStream(tempPath));
        if (!actualMd5.equals(session.getMd5())) {
            throw new MergeException("合并后 MD5 不匹配");
        }

        // 3. 上传到对象存储（内容寻址）
        String objectKey = "objects/" + actualMd5;
        if (!ossClient.doesObjectExist(objectKey)) {
            ossClient.putObject(objectKey, new FileInputStream(tempPath));
        }

        // 4. 创建文件记录
        fileRecordRepo.create(session.getUserId(), session.getFilename(),
            actualMd5, session.getFileSize(), objectKey);

        // 5. 清理临时分片
        ossClient.deleteObjects("chunks/" + uploadId + "/");
        uploadSessionRepo.updateStatus(uploadId, "done");
    }
}
```

---

## 4. 系列导航

| 文章 | 核心内容 |
|------|---------|
| [总目录](README.md) | 需求分析 + 架构概览 + 面试话术 |
| [架构演进](01-architecture.md) | 3 阶段架构 + 5 大组件 |
| **本文** | 分片协议 + 断点续传 + 并发控制 |
| [秒传与存储](03-instant-upload-and-storage.md) | MD5 去重 + 对象存储 + 引用计数 |

← [返回: file-upload 总目录](README.md)
