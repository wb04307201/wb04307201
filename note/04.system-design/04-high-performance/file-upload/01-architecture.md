<!--
module:
  parent: system-design/file-upload
  slug: system-design/04-high-performance/file-upload/01-architecture
  type: topic
  category: 系统架构
  summary: 大文件上传 3 阶段架构演进（单机直传→分片+OSS→分布式+CDN）+ 5 大组件
-->

# 大文件上传系统架构 · 3 阶段演进

> **一句话**：大文件上传架构 = **API 层 + 分片调度 + 对象存储 + 元数据 + 缓存**，从单机直传的 100MB 上限到分布式的 100GB+ 无上限。

← [返回: file-upload 总目录](README.md)

---

## 1. 阶段 1：单机直传（< 100MB 文件）

```
┌──────────┐     ┌──────────────┐
│  浏览器    │────→│ Spring MVC    │
│ <form>   │     │ MultipartFile │
└──────────┘     └──────┬───────┘
                        │ 写磁盘
                   ┌────▼────┐
                   │ 本地磁盘  │
                   └─────────┘
```

**实现**：
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    file.transferTo(new File("/data/uploads/" + file.getOriginalFilename()));
    return "success";
}
```

**瓶颈**：
- 文件大小受 JVM 内存限制（默认 max-file-size=10MB）
- 不支持断点续传（断网 = 从头开始）
- 不支持秒传（每次都完整传输）
- 单机磁盘容量有限

---

## 2. 阶段 2：分片 + 对象存储（100MB ~ 10GB）

```
┌──────────┐   ┌──────────────┐   ┌────────────────┐
│  浏览器    │──→│ Upload API   │──→│ 对象存储（OSS/S3）│
│ 前端分片   │   │ (Spring Boot)│   │ /chunks/{uid}/ │
└──────────┘   └──────┬───────┘   └────────┬───────┘
                      │                    │
                 ┌────▼──────┐        ┌────▼───────┐
                 │  MySQL     │        │  合并后文件  │
                 │  元数据    │        │ /objects/   │
                 └───────────┘        └────────────┘
```

**5 大组件**：

| 组件 | 职责 | 技术选型 |
|------|------|---------|
| **Upload API** | 接收分片 + 管理上传会话 | Spring Boot + MultipartFile |
| **对象存储** | 存储分片 + 合并后文件 | 阿里云 OSS / AWS S3 / MinIO |
| **元数据 DB** | 文件信息 + 分片状态 | MySQL / PostgreSQL |
| **Redis 缓存** | uploadId 状态 + 已上传分片列表 | Redis（TTL 24h） |
| **任务队列** | 异步合并 + 内容审核 | RocketMQ / Kafka |

**数据模型**：

```sql
-- 上传会话
CREATE TABLE upload_session (
    upload_id    VARCHAR(64) PRIMARY KEY,
    user_id      BIGINT NOT NULL,
    filename     VARCHAR(255),
    file_size    BIGINT,
    md5          VARCHAR(32),
    total_chunks INT,
    status       ENUM('uploading', 'merging', 'done', 'failed'),
    created_at   DATETIME,
    updated_at   DATETIME
);

-- 分片记录
CREATE TABLE upload_chunk (
    upload_id    VARCHAR(64),
    chunk_index  INT,
    chunk_size   INT,
    chunk_md5    VARCHAR(32),
    storage_path VARCHAR(512),
    uploaded_at  DATETIME,
    PRIMARY KEY (upload_id, chunk_index)
);

-- 文件记录（秒传去重）
CREATE TABLE file_record (
    file_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT NOT NULL,
    filename     VARCHAR(255),
    md5          VARCHAR(32) NOT NULL,
    file_size    BIGINT,
    object_key   VARCHAR(512),  -- 对象存储路径（内容寻址）
    ref_count    INT DEFAULT 1, -- 引用计数
    created_at   DATETIME,
    INDEX idx_md5 (md5)
);
```

---

## 3. 阶段 3：分布式 + CDN + 安全（10GB+ / 高并发）

```
┌──────────┐   ┌───────────┐   ┌──────────────────────┐
│  浏览器    │──→│ CDN 边缘   │──→│ Upload Service（集群） │
│ 前端分片   │   │ 上传加速   │   │ ┌──────────────────┐│
└──────────┘   └───────────┘   │ │ Redis: uploadId   ││
                                │ │ 状态 + 分片索引    ││
                                │ └────────┬─────────┘│
                                └──────────┼──────────┘
                                           │
                    ┌──────────────────────┼──────────────────┐
                    │                      │                  │
              ┌─────▼─────┐   ┌──────────▼──────┐   ┌─────▼──────┐
              │ OSS（多区域）│   │ MQ: 异步合并     │   │ MySQL 集群  │
              │ 分片存储    │   │ + 内容审核       │   │ 元数据      │
              │ + 合并文件  │   │ + 缩略图生成     │   │ + 分片记录  │
              └───────────┘   └─────────────────┘   └────────────┘
```

**分片调度策略**：

| 策略 | 说明 | 优点 |
|------|------|------|
| **顺序上传** | 按 chunkIndex 顺序 | 简单，适合小文件 |
| **并发上传** | 3-6 片同时上传 | 充分利用带宽 |
| **动态并发** | 根据网速自动调整并发数 | 最优体验 |

**安全措施**：

| 安全层 | 措施 |
|--------|------|
| **文件类型** | 白名单校验（后缀 + Magic Number） |
| **大小限制** | 单文件 ≤ 100GB，单分片 ≤ 100MB |
| **病毒扫描** | ClamAV 异步扫描（上传后触发） |
| **内容审核** | 图片/视频走 AI 审核（敏感内容拦截） |
| **防盗链** | OSS Referer 白名单 + 签名 URL（有效期 1h） |

---

## 4. 系列导航

| 文章 | 核心内容 |
|------|---------|
| [总目录](README.md) | 需求分析 + 架构概览 + 面试话术 |
| **本文** | 3 阶段架构演进 + 5 大组件 |
| [分片与断点续传](02-chunked-and-resumable.md) | 分片协议 + 断点续传实现 + 并发控制 |
| [秒传与存储](03-instant-upload-and-storage.md) | MD5 去重 + 对象存储 + 引用计数 |

← [返回: file-upload 总目录](README.md)
