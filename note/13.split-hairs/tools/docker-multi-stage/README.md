<!--
question:
  id: tools-docker-multi-stage
  topic: tools
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 性能对比
  tags: [tools, Docker, 多阶段构建, 镜像优化, Dockerfile, 层缓存]
-->

# Docker 多阶段构建为什么能大幅减小镜像体积？

> 一句话定位：多阶段构建把"编译环境"和"运行环境"拆成两个 stage —— 最终镜像只留下运行产物，体积可缩小 10-50 倍。

> **系列定位**：经典容器化面试题（Docker 高频）。考察的不是"多写几个 FROM"，而是 **镜像分层原理** + **构建缓存策略** + **生产镜像瘦身实践**。

---

## 引子：一个 1.2GB 的 Go 应用镜像

```text
你的 Go 应用编译后二进制文件只有 15MB。
但 docker build 出来的镜像却有 1.2GB ——
因为镜像里包含了整个 Go 编译工具链（500MB+）、
源码目录、中间产物、apt 安装的构建依赖。
```

15MB 的应用拖着 1.2GB 的镜像上生产，每次部署拉取浪费带宽，镜像仓库存储膨胀，攻击面也变大。**怎么把镜像瘦到 20MB 以内？**

---

## 一、核心原理

### 1.1 单阶段 vs 多阶段

单阶段构建（一个 `FROM golang:1.22` + `go build`）的最终镜像 = Go 编译器 + 源码 + 构建缓存 + 二进制文件。**所有中间层都保留在镜像里**。

多阶段构建把编译和运行拆成两个 stage：

```dockerfile
# Stage 1: 构建
FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o server .

# Stage 2: 运行（只拷贝产物）
FROM alpine:3.19
COPY --from=builder /app/server /server
CMD ["/server"]
```

最终镜像 = alpine + 一个二进制文件。**构建环境整个丢弃**。

### 1.3 TL;DR 对比表

| 维度 | 单阶段 | 多阶段 |
|------|--------|--------|
| 镜像体积 | 1.2GB（Go 全工具链） | 15-25MB（alpine + 二进制） |
| 攻击面 | 大（含编译器、源码） | 小（仅运行时） |
| 构建缓存 | 一层搞定 | 分层独立，缓存更精确 |
| 部署速度 | 慢（拉取大镜像） | 快（镜像小，拉取秒级） |
| Dockerfile 复杂度 | 简单 | 略复杂（多一个 FROM） |

---

## 二、详解：进阶优化技巧

### 2.1 利用层缓存加速构建

```dockerfile
# 先拷贝 go.mod 和 go.sum（依赖不常变），利用缓存
COPY go.mod go.sum ./
RUN go mod download
# 再拷贝源码（变化频繁）
COPY . .
RUN go build -o server .
```

只要 `go.mod` 没变，`go mod download` 这层就走缓存，**构建时间从 2 分钟降到 10 秒**。

### 2.2 Distroless / 其他语言示例

**Distroless 镜像**（比 alpine 更小，甚至没有 shell，攻击者无法 `docker exec`）：

```dockerfile
FROM gcr.io/distroless/static-debian12
COPY --from=builder /app/server /server
```

**Java Spring Boot** 多阶段同理：builder 用 `eclipse-temurin:21-jdk` 编译，runtime 用 `21-jre` 只拷贝 jar，镜像从 800MB 瘦到 200MB。Node.js 前端类似：builder 用 `node:20`，runtime 用 `nginx:alpine` 只拷 `dist/`。

### 2.3 .dockerignore 不可忽视

不加 `.dockerignore`，`COPY . .` 会把 `.git`（几百 MB）、`node_modules` 全塞进构建上下文，**光传输就要几十秒**。必须维护，和 `.gitignore` 保持同步。

---

## 三、常见陷阱

### 陷阱 1：Stage 之间 COPY 路径写错

- **现象**：`COPY --from=builder /app/build/libs/app.jar` 报错文件不存在
- **真相**：检查 builder stage 里的实际输出路径，用 `RUN ls` 验证

### 陷阱 2：最终镜像缺少 CA 证书

- **现象**：应用启动后 HTTPS 请求报 `x509: certificate signed by unknown authority`
- **真相**：alpine / distroless 默认不带根证书，需要 `apk add ca-certificates` 或从 builder 拷贝

### 陷阱 3：缓存失效不彻底

- **现象**：`go mod download` 走缓存，但 `go.sum` 已经变了
- **真相**：只要 `go.sum` 文件变了，这层缓存自动失效 —— 前提是你把 `go.sum` 放在 `COPY . .` 之前单独拷贝

---

## 四、最佳实践

1. **永远用多阶段构建**：至少分 builder + runtime 两阶段，选最小基础镜像（alpine → distroless → scratch）
2. **优化层缓存顺序**：不常变的文件（依赖声明）先 COPY，常变的文件（源码）后 COPY
3. **维护 .dockerignore + 开启 BuildKit**：保持构建上下文干净，`DOCKER_BUILDKIT=1` 获得并行构建能力

---

## 五、面试话术（90 秒版本）

> "多阶段构建的核心思想是把编译环境和运行环境拆成两个 stage。第一个 stage 用完整的基础镜像（如 golang:1.22）做编译，第二个 stage 用最小镜像（如 alpine 或 distroless）只拷贝编译产物。
>
> 实际效果：一个 Go 应用从 1.2GB 瘦到 15-25MB，Java Spring Boot 从 800MB 瘦到 200MB。好处有三个：部署拉取快、存储省、攻击面小（最终镜像不含编译器和源码）。
>
> 进阶优化包括：利用层缓存（先拷 go.mod 再拷源码）、用 distroless 进一步缩小、维护 .dockerignore 减少构建上下文。生产环境我还推荐开启 BuildKit 获得并行构建能力。"

---

## 六、交叉引用

- 同栏目：[Git Rebase vs Merge](../git-rebase-vs-merge/README.md) — 版本管理工具链
- 同栏目：[Nginx 反向代理](../nginx-reverse-proxy/README.md) — 容器化后的流量入口
- 同栏目：[K8s Pod 生命周期](../k8s-pod-lifecycle/README.md) — 容器编排与调度
- 系统设计：[限流算法](../../04.system-design/rate-limiting/README.md) — 系统设计高频题

---

← [返回: 咬文嚼字 · 工具](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 工具 · ⭐⭐⭐⭐（高频面试 + 生产必会）
