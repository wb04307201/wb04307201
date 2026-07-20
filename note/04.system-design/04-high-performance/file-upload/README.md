<!--
module:
  parent: high-performance
  slug: system-design/04-high-performance/file-upload
  type: deep-dive
  category: 大文件上传系统
  summary: 大文件上传系统设计 —— 分片上传 + 断点续传 + 秒传（MD5 去重）+ 对象存储 + CDN 分发，从单机到分布式完整演进
-->

# 大文件上传系统设计 · 分片 + 断点续传 + 秒传

> **一句话答案**：大文件上传 = **前端分片（5MB/chunk）+ 并发上传 + 后端合并 + MD5 秒传（去重）+ 断点续传（uploadId + offset 续传）**。1GB 文件分 200 片并发上传，断网后只传剩余部分；相同文件秒传（O(1) 返回）。

← [返回: 高性能设计](../README.md) · 面试题：[13.split-hairs/file-upload](../../../13.split-hairs/04.system-design/file-upload/README.md)

---

## 0. 面试高频拷问

```text
Q：设计一个大文件上传系统，支持 10GB 文件、断点续传、秒传？
Q：分片上传的协议怎么设计？断网后怎么续传？
Q：秒传的原理是什么？怎么保证 MD5 不碰撞？
```

**回答框架（4 层递进）**：

1. **需求分析**：大文件（GB 级）+ 断点续传 + 秒传 + 多用户并发
2. **3 大核心机制**：分片上传 + 断点续传协议 + 秒传（内容寻址去重）
3. **架构演进**：单机直传 → 分片 + 对象存储 → 分布式 + CDN
4. **5 反模式**：整文件一次上传 / 分片太大 / 没校验完整性 / 没做秒传 / 没限速

完整面试题见 [13.split-hairs/04.system-design/file-upload](../../../13.split-hairs/04.system-design/file-upload/README.md)。

---

## 1. 需求拆解

### 1.1 功能需求

| 功能 | 说明 | 技术挑战 |
|------|------|---------|
| **大文件上传** | 支持 10GB+ 文件 | 分片 + 并发 + 内存控制 |
| **断点续传** | 网络中断后从断点继续 | uploadId + 已上传分片记录 |
| **秒传** | 相同文件瞬间完成 | MD5/SHA256 去重 + 内容寻址 |
| **进度显示** | 实时上传进度 | 分片完成回调 + WebSocket/SSE |
| **文件管理** | 上传后下载/删除/分享 | 元数据存储 + 权限控制 |

### 1.2 性能需求

| 指标 | 要求 |
|------|------|
| **上传速度** | 充分利用带宽（> 80%） |
| **分片大小** | 5MB（平衡请求数和单次传输量） |
| **并发分片数** | 3-6（避免浏览器连接数限制） |
| **秒传延迟** | < 500ms（一次 MD5 查询） |

---

## 2. 核心流程

### 2.1 完整上传流程

```text
前端                                    后端
 │                                       │
 │  1. 计算文件 MD5                       │
 │  ──────→ 2. POST /api/upload/check    │
 │           {md5, filename, size}        │
 │                                       │
 │  ←────── 3. 检查秒传                   │
 │           已存在? → 秒传成功            │
 │           不存在? → 返回 uploadId       │
 │           + 已上传分片列表              │
 │                                       │
 │  4. 分片（5MB/chunk）                  │
 │  ──────→ 5. PUT /api/upload/chunk     │  (并发 3-6 片)
 │           {uploadId, chunkIndex, data} │
 │                                       │
 │  ←────── 6. 分片确认                   │
 │                                       │
 │  7. 所有分片完成                        │
 │  ──────→ 8. POST /api/upload/merge    │
 │           {uploadId}                   │
 │                                       │
 │  ←────── 9. 合并 + 返回文件 URL        │
```

---

## 3. 核心技术

### 3.1 分片上传

> 📖 **深度阅读**：[02-chunked-and-resumable.md](02-chunked-and-resumable.md) — 分片协议 + 断点续传详解

```javascript
// 前端：文件分片
const CHUNK_SIZE = 5 * 1024 * 1024;  // 5MB
const file = input.files[0];
const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

for (let i = 0; i < totalChunks; i++) {
    const start = i * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const chunk = file.slice(start, end);  // Blob.slice()
    uploadChunk(uploadId, i, chunk);       // 并发上传
}
```

### 3.2 秒传（Instant Upload）

> 📖 **深度阅读**：[03-instant-upload-and-storage.md](03-instant-upload-and-storage.md) — 秒传原理 + 存储后端详解

```text
用户 A 上传 "movie.mp4"（MD5: abc123）
    → 存储到 OSS: /objects/abc123
    → DB 记录: file_id=1, md5=abc123, path=/objects/abc123

用户 B 上传相同 "movie.mp4"（MD5: abc123）
    → 查询 DB: md5=abc123 → 已存在!
    → 创建新 file_id=2, 引用同一 object path
    → 返回"秒传成功"（实际未传输任何数据）
```

### 3.3 断点续传

```text
用户上传 1GB 文件（200 片），传到第 100 片时断网
    → 重连后 POST /api/upload/check
    → 后端返回: {uploadId: "xxx", uploadedChunks: [0,1,...,99]}
    → 前端从第 100 片继续上传（跳过已完成的 0-99）
```

---

## 4. 架构演进

> 📖 **深度阅读**：[01-architecture.md](01-architecture.md) — 3 阶段架构演进详解

### 4.1 阶段 1：单机直传

```text
浏览器 → Spring MVC MultipartFile → 本地磁盘
```

**问题**：文件大小受限于服务器内存/磁盘、不支持断点续传。

### 4.2 阶段 2：分片 + 对象存储

```text
浏览器 → API Gateway → Upload Service → 分片写入 OSS/S3
                                       → 元数据写入 MySQL
```

### 4.3 阶段 3：分布式 + CDN

```text
浏览器 → CDN（边缘加速）→ Upload Service → 分片写入 OSS（多区域）
                                          → Redis 缓存 uploadId 状态
                                          → 异步合并 + 内容审核
```

---

## 5. 5 大反模式

### 5.1 整文件一次上传

```html
// ❌ 10GB 文件一次 POST → 超时/内存溢出
<form enctype="multipart/form-data">
    <input type="file" name="file"/>
</form>
```

**修复**：前端分片（5MB/chunk），后端逐片接收。

### 5.2 分片太大或太小

| 分片大小 | 问题 |
|----------|------|
| 1MB | 请求数太多（10GB = 10000 请求），HTTP 开销大 |
| 100MB | 单片失败重传代价高，内存占用大 |
| **5MB**（推荐）| 平衡请求数和单次传输量 |

### 5.3 没做完整性校验

```text
// ❌ 分片合并后不校验 → 损坏文件
mergeChunks(uploadId);
return fileUrl;

// ✅ 合并后校验 MD5
mergeChunks(uploadId);
String actualMd5 = calculateMd5(mergedFile);
if (!actualMd5.equals(expectedMd5)) {
    throw new UploadException("文件完整性校验失败");
}
```

### 5.4 没做秒传

```text
// ❌ 每个用户都上传完整文件 → 存储浪费 + 带宽浪费
// ✅ 上传前查 MD5 → 已存在则直接引用
```

### 5.5 没有限速/限流

```text
// ❌ 单用户占满带宽 → 其他用户无法上传
// ✅ 令牌桶限流：每用户最大 10MB/s
```

---

## 6. 面试话术（30 秒版）

> "大文件上传系统核心是三个机制：分片上传、断点续传、秒传。
>
> 分片：前端把文件切成 5MB 的 chunk，3-6 片并发上传到 OSS，后端收到所有分片后合并。
>
> 断点续传：每个上传会话有 uploadId，后端记录已完成的分片索引。断网重连后，前端查询已上传分片，从断点继续。
>
> 秒传：上传前先算文件 MD5 发给后端查询，如果已存在相同 MD5 的文件，直接创建引用记录，不传输任何数据，O(1) 完成。
>
> 存储用对象存储（OSS/S3），元数据用 MySQL，uploadId 状态用 Redis 缓存。安全方面做文件类型白名单 + 病毒扫描 + 内容审核。"

---

## 7. 交叉引用

- 主模块：[`04.system-design`](../../README.md) — 系统设计知识体系
- 同级案例：[商品搜索](../product-search/README.md) — 倒排索引 + 多阶段排序
- 同级案例：[敏感词过滤](../sensitive-word-filter/README.md) — AC 自动机 + 高并发过滤
- CDN 加速：[CDN 加速](../cdn/README.md) — 上传后的文件分发
- 消息队列：[消息队列](../mq/README.md) — 异步合并 + 内容审核
- Spring 上传：[Spring MVC 文件上传](../../../06.spring/02-web/mvc/file-upload.md) — 框架层实现

## 相关章节

- 面试题：[`13.split-hairs/04.system-design`](../../../13.split-hairs/04.system-design/README.md) — 系统设计面试题全集
- 深度阅读：[`04.system-design`](../../README.md) — 系统设计主模块

← [返回: 高性能设计](../README.md)
