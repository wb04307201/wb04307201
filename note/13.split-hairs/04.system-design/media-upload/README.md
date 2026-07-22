<!--
question:
  id: 04.system-design-media-upload
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [04.system-design, 媒体上传, 图片转码, WebP, AVIF, HLS, CDN, 高可用, DRM]
-->

# 媒体上传面试深挖 —— 图片转码 / 视频 HLS / CDN 边缘 / 高可用容灾

> ⬅️ [返回系统设计咬文嚼字](../README.md) | [主模块深度专题](../../../04.system-design/04-high-performance/media-upload-storage/README.md)

> 一句话定位：**4 大核心图片视频上传面试深挖**（大厂系统设计高频）：图片转码 / 视频 HLS / CDN 边缘优化 / 高可用 4 层防线。

> **系列定位**：高频系统设计题（社招/架构师岗必考）。配套兄弟题：[文件上传](../file-upload/README.md)、[商品搜索](../product-search/README.md)、[缓存一致性](../cache-consistency/README.md)、[限流](../rate-limiting/README.md)。

---

⭐⭐⭐⭐⭐ 深度级别（架构师级）
📚 前置知识：FFmpeg / HLS / WebP/AVIF / CDN 基础 / 对象存储生命周期

---

## 引子：面试经典开场

面试官："设计一个支持商品图 + 短视频 + 长视频混合上传的媒体系统，要求 5 种图片尺寸 + 4K 视频 + 100GB 大文件 + 多 CDN 容灾。"

大多数人答："原图传 OSS + CDN 分发。"

面试官追问：
1. "5 种尺寸全在上传时预生成，CPU 撑得住吗？懒加载怎么设计？"
2. "100GB 视频怎么切片？HLS 分片大小为什么是 6 秒而不是 10 秒？"
3. "CDN 只做静态缓存吗？HTTP/3 真的比 HTTP/2 快 30% 吗？"
4. "跨区域容灾怎么做？同步双写会拖慢主写，怎么权衡？"

大多数人卡在追问上。**这道题考察的不是"会传文件"，而是"转码策略 + 流媒体协议 + 边缘优化 + 容灾架构"四维深度。**

---

## Q1：电商商品图，5 种尺寸 + WebP/AVIF 双格式，怎么设计后端转码？

**陷阱**：
- ❌ 上传时一次性生成所有尺寸（CPU 高峰）
- ❌ 全用 WebP（Safari 16+ 之前不兼容 AVIF）
- ❌ 不删除 EXIF（隐私风险）

**30s 话术**：「**预生成 + 懒加载双轨** = 原图 + 5 尺寸（small/medium/large/xl/web）+ WebP/AVIF 双格式，**懒加载尺寸用 on-the-fly serverless 转码**（首次访问时生成 + CDN 缓存），**EXIF 隐私三件套去除**（GPS/设备/拍摄时间）。」

**90s 话术**：「**4 大设计原则**：

- **① 双轨制**：1-3 热门尺寸（small/medium/large）预生成 + 4-5 冷门尺寸（xl/web）懒加载
- **② 双格式输出**：现代浏览器 WebP+AVIF 双格式，老 Safari 回退 JPEG（Accept header 路由）
- **③ EXIF 三件套去除**：GPS（隐私）/ 设备型号（设备指纹风险）/ 拍摄时间（关联分析），但保留版权 Orientation（影响显示）
- **④ on-the-fly 转码**：用 Go `webp.sh` 或 Node `sharp` 库服务端实时转换 + CDN edge cache（如阿里云 DCDN 边缘）

**实战代码示例**：

```typescript
// sharp 转码示例（Node.js）
const sharp = require('sharp');
async function generateVariants(buffer: Buffer) {
  const variants = {};
  for (const size of [320, 640, 1024, 1920, 3840]) {
    for (const format of ['webp', 'avif', 'jpeg']) {
      variants[`${size}.${format}`] = await sharp(buffer)
        .resize({ width: size, withoutEnlargement: true })
        [format]({ quality: format === 'jpeg' ? 85 : 75 })
        .withMetadata({ exif: { IFD0: { remove: true } } })  // 去除 EXIF
        .toBuffer();
    }
  }
  return variants;  // 15 个变体
}
```

**实战数字**：
- ① 单图 5 尺寸 2 格式 = 10 个文件
- ② OSS 路径 `product/{id}/size_{w}x{h}.{ext}`
- ③ 单图存储 2-5MB
- ④ Accept 路由优先级 `image/avif → image/webp → image/*`

**反模式**：
- 全预生成 10+ 变体（CPU 浪费 50%+）
- 全懒加载（首次访问慢 2s+）
- 删 Orientation（图片旋转错误）

---

## Q2：100GB 视频怎么上传？HLS 分片 + 多分辨率 + DRM 防盗链？

**陷阱**：
- ❌ 原 mp4 直接 CDN 分发（无法 ABR）
- ❌ 单分辨率（弱网必卡顿）
- ❌ URL 静态（无防盗链）

**30s 话术**：「**5 步链路**：① ffmpeg 转码 4-6 档（360p/480p/720p/1080p/4K + audio 128k）② HLS 切片（每段 6 秒 + .m3u8 索引）③ AES-128 加密（key + keyinfo 文件）④ 签名 URL（5-30 分钟短期 expire）⑤ DRM（Widevine/FairPlay/PlayReady）保护。」

**90s 话术**：「**完整 5 步链路详解**：

```bash
# 1. ffmpeg 转码多档 + HLS 切片（4 档 ABR ladder）
ffmpeg -i source.mp4 \
  -map 0:v -map 0:a -c:v libx264 -crf 22 -preset medium \
  -filter_complex "[0:v]split=4[v360][v480][v720][v1080]" \
  -map "[v360]" -s 640x360 -b:v 800k \
  -map "[v480]" -s 854x480 -b:v 1400k \
  -map "[v720]" -s 1280x720 -b:v 2800k \
  -map "[v1080]" -s 1920x1080 -b:v 5000k \
  -hls_time 6 -hls_playlist_type vod \
  -hls_key_info_file keyinfo -hls_enc true \
  -hls_segment_filename "seg_%v/seg_%03d.ts" \
  -master_pl_name master.m3u8 \
  -var_stream_map "v:0,a:0 v:1,a:0 v:2,a:0 v:3,a:0" \
  "stream_%v.m3u8"
```

**5 大要点**：
- **HLS 分片**：6 秒/段（平衡 seek 精度与请求数）
- **AES-128 加密**：key 文件二进制 16 字节 + keyinfo 文件 3 行（URL/本地路径/IV）
- **签名 URL**：阿里云 OSS / AWS S3 SDK 生成 5-30 分钟短期 URL
- **DRM 三件套**：Widevine（Chrome/Android）/ FairPlay（iOS）/ PlayReady（Edge）
- **防盗链 4 件套**：Referer 白名单 + 签名 URL + Token 鉴权 + IP 限速

**反模式**：
- 切片太长（30s+ 影响 seek）
- 没加密（直链盗用）
- 没 DRM（可被转码工具录屏）
- 单一分辨率（弱网必卡）

---

## Q3：CDN 边缘怎么做图片视频优化？为什么 HTTP/3 重要？

**陷阱**：
- ❌ CDN 只做静态缓存（没启用智能压缩）
- ❌ HTTPS/2 足够（HTTP/3 反而更复杂没必要）
- ❌ CDN 节点越多越好（小型 POP 反而拖慢）

**30s 话术**：「**3 大边缘优化**：① **智能压缩**：CDN edge 自动转 WebP/AVIF（Accept 路由）+ Brotli 文本压缩 ② **HTTP/3 + QUIC**：解决队头阻塞，弱网首屏提升 30%+ ③ **边缘程序**：Edge Functions / Lambda@edge 处理动态 + A/B testing。**阿里云 DCDN / AWS CloudFront + Lambda@edge 是 SOTA**。」

**90s 话术**：「**CDN 边缘优化 4 层**：

- **L1 协议层**：HTTP/3 + QUIC（UDP-based）—— 解决 TCP 队头阻塞，移动弱网首屏提升 30-50%
- **L2 压缩层**：Brotli 文本 + WebP/AVIF 图片 + AV1/H.265 视频
- **L3 边缘程序**：Cloudflare Workers / AWS Lambda@Edge / 阿里云边缘函数（10ms 内响应）
- **L4 智能选路**：实时探测回源链路质量，自动选最快节点

**视频额外 3 招**：
- **HTTP/3 server push**：CDN 主动 push .m3u8 主清单 + 前 3 段 .ts（首屏 0 延迟）
- **HLS Low-Latency Mode（LL-HLS）**：分片从 6s 缩到 200ms（直播场景）
- **多 CDN 厂商容灾**：阿里云 + 腾讯云双 CDN（一故障切另一家）

**实战数字**：
- ① HTTP/3 比 HTTP/2 移动首屏 -30-50%
- ② Brotli 比 gzip -15%
- ③ WebP 比 JPEG -25-35%
- ④ AVIF 比 JPEG -50%
- ⑤ 边缘函数 cold start < 50ms

**反模式**：
- 滥用边缘函数（cold start 100ms+ 反而更慢）
- 小流量用大 CDN（不划算）
- 没启用 HTTP/3（默认 HTTP/2 浪费）

---

## Q4：高可用 4 层防线具体怎么设计？跨区域容灾怎么做？

**陷阱**：
- ❌ 单 LB + 1 个 OSS（无容灾）
- ❌ 跨区域同步写（主备延迟 100ms+ 拖慢主）
- ❌ CDN 故障无 fallback

**30s 话术**：「**4 层防线**：**L1 客户端断点续传 + 重试 → L2 服务端多机房 + 限流熔断 → L3 CDN 多厂商 + 智能选路 → L4 跨区域 OSS 多写异步复制**。**跨区域容灾**：异地多活 + 双写 OSS + S3 Cross-Region Replication（异步）。」

**90s 话术**：「

**L1 客户端**：
- ① 3 次重试 + 指数退避（1s/3s/9s）
- ② 断点续传（uploadId + offset）
- ③ 客户端本地缓存已上传 chunks

**L2 服务端**：
- ① 接入层 LB（Nginx SLB / ALB）
- ② 业务服务 K8s 多 Pod + HPA 弹性
- ③ Sentinel/Resilience4j 限流熔断

**L3 CDN 边缘**：
- ① 多 CDN 厂商（阿里云 + 腾讯云）容灾切换
- ② 智能 DNS（GSLB）
- ③ HTTP/3 + QUIC
- ④ Origin Shield 回源配额

**L4 跨区域复制**：
- **同区域多写**：同城双 OSS bucket 同步（RPO=0）
- **跨区域异步**：CRR（Cross-Region Replication）异步复制（RPO 几秒-分钟级）
- **异地多活**：双 region 接收上传（双写），DNS 切换流量

**实战数字**：
- L1 客户端重试成功率 +25%
- L2 多机房可用性 +1 个 9（99.9% → 99.99%）
- L3 多 CDN 容灾后 CDN 故障 0 宕机
- L4 RTO < 1 小时 / RPO < 5 分钟

**反模式**：
- ① 同步跨区域写（拖慢主 100ms+）
- ② 单机房死扛
- ③ CDN 故障无 fallback

---

## 交叉引用

- **深度实战**：[媒体上传存储系统](../../../04.system-design/04-high-performance/media-upload-storage/README.md) — 图片 WebP/AVIF + 视频 HLS/DASH + 冷热分层 + 高可用 4 层防线 + 防盗链 DRM
- **兄弟面试题**：[文件上传](../file-upload/README.md) — 通用分片上传（断点续传 + 秒传）
- **兄弟面试题**：[商品搜索](../product-search/README.md) — 搜索系统设计案例
- **兄弟面试题**：[缓存一致性](../cache-consistency/README.md) — Redis 状态管理
- **兄弟面试题**：[限流](../rate-limiting/README.md) — 高并发入口防护
- **主模块**：[`04.system-design`](../../../04.system-design/) — 系统设计知识体系

---

## 📊 4 题难度速查表

| 题号 | 主题 | 难度 | 频率 | 核心考点 |
|------|------|------|------|---------|
| Q1 | 图片多尺寸转码 | ⭐⭐⭐⭐ | 高频 | 双轨制 + 双格式 + EXIF + on-the-fly |
| Q2 | 视频 HLS + DRM | ⭐⭐⭐⭐⭐ | 高频 | ffmpeg 转码 + AES-128 + 签名 URL + DRM 三件套 |
| Q3 | CDN 边缘优化 | ⭐⭐⭐⭐ | 中频 | HTTP/3 + Brotli + 边缘函数 + 多 CDN |
| Q4 | 高可用 4 层防线 | ⭐⭐⭐⭐⭐ | 高频 | 客户端重试 + 多机房 + 多 CDN + 跨区域异步 |

---

## 📚 参考来源

- [RFC 8216 — HTTP Live Streaming (HLS)](https://datatracker.ietf.org/doc/html/rfc8216)
- [AWS S3 Storage Classes & Cross-Region Replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html)
- [阿里云 OSS 对象存储 + DCDN 全站加速](https://help.aliyun.com/product/31815.html)
- [FFmpeg 官方文档 — HLS muxer](https://ffmpeg.org/documentation.html)
- [AOMedia AV1 / WebP — 下一代图像压缩标准](https://aomedia.googlesource.com/)

← [返回 AI 咬文嚼字](../../README.md)