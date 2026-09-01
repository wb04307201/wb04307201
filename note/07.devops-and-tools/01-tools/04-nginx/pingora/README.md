<!--
module:
  parent: tools
  slug: tools/pingora
  type: article
  category: 主模块子文章
  summary: Pingora — Cloudflare 开源的 Rust HTTP 代理框架（库），用于构建高性能反向代理、负载均衡与网关服务
  depth: ⭐⭐⭐⭐
-->

# Pingora

> **一句话定位**：Pingora 是 **Cloudflare 开源的 Rust HTTP 代理框架（库）**，用以替代 Nginx，专注 **极致性能 + 内存安全 + 可编程扩展**——不是独立二进制。

---

## 一、为什么需要 Pingora？

Nginx 配置成熟但扩展性差（C 模块），C/C++ 重型代理（如 HAProxy 的 Custom Lua）易出错。Cloudflare 2024 年开源的 Pingora 走了一条新路：

| 维度 | Nginx (C) | HAProxy (C) | Envoy (C++) | **Pingora (Rust)** |
|------|-----------|-------------|-------------|--------------------|
| **实现语言** | C | C | C++ | **Rust**（内存安全） |
| **形态** | 二进制 + DSL 配置 | 二进制 + 配置文件 | 二进制 + xDS API | **Rust crate 库**（需自行编译） |
| **扩展方式** | C 模块 / Lua（OpenResty） | Lua / 编译 | C++ Filter | **Rust trait impl**（类型安全） |
| **零停机升级** | `reload`（worker 平滑） | `reload`（有限支持） | xDS 热更新 | **原生支持**（程序内逻辑） |
| **单线程极限** | ~10 万 QPS | ~20 万 QPS | ~15 万 QPS | **> 100 万 QPS**（取决于负载） |
| **学习曲线** | 中（DSL） | 中（DSL） | 陡（xDS / C++） | **中（Rust 异步trait）** |

> **核心价值**：把"代理能力"做成一个库（crate），让你用 Rust 代码自由拼装——而不是写一堆配置。

---

## 二、仓库与 4 大子模块

GitHub：<https://github.com/cloudflare/pingora>（Apache-2.0 协议）

```text
pingora/                          # monorepo（单仓多 crate）
├── pingora-core/                 # ① 核心：异步 I/O、协议、连接池
├── pingora-proxy/                # ② HTTP/1+2 反向代理 + 过滤器
├── pingora-load-balancer/        # ③ 负载均衡算法（轮询 / 一致性哈希 / 自定义）
├── pingora-openssl/              # ④ OpenSSL / BoringSSL 适配层
├── pingora-signal/               # 信号处理
├── pingora-time-mock/            # 时间 mock（测试用）
└── examples/                     # 官方示例
```

| 模块 | 作用 | 何时用 |
|------|------|--------|
| **pingora-core** | 异步运行时、TCP/HTTP/2/TLS 协议栈、字节流抽象 | 所有场景必选 |
| **pingora-proxy** | 反向代理、L7 路由、request/response 过滤器、转发 | 写 HTTP 代理必选 |
| **pingora-load-balancer** | 健康检查、选择最优 upstream | 多后端负载均衡 |
| **pingora-openssl** | TLS 终结、证书加载、合规 FIPS | 需要 HTTPS |

---

## 三、快速开始：写你的第一个 Pingora 代理

> **核心前提**：Pingora **不是预编译二进制**——你需要在自己的 Cargo 工程里 `use pingora::*;` 来写代码。下面是官方示例风格的最小可运行代理。

### 3.1 创建工程

```bash
cargo new my-proxy --bin
cd my-proxy
```

### 3.2 `Cargo.toml` 添加依赖

```toml
[package]
name = "my-proxy"
version = "0.1.0"
edition = "2021"

[dependencies]
# 四个核心 crate，按需启用 feature
pingora-core = { git = "https://github.com/cloudflare/pingora", version = "0.3" }
pingora-proxy = { git = "https://github.com/cloudflare/pingora", version = "0.3" }
pingora-load-balancer = { git = "https://github.com/cloudflare/pingora", version = "0.3" }
pingora-openssl = { git = "https://github.com/cloudflare/pingora", version = "0.3" }
async-trait = "0.1"
tokio = { version = "1", features = ["full"] }
```

> 注：以上版本号仅作示例，请以 [crates.io](https://crates.io/crates/pingora-core) 上发布的最新版本为准。

### 3.3 `src/main.rs` —— 完整 HTTP 反向代理

```rust
use async_trait::async_trait;
use pingora::prelude::*;
use pingora_load_balancer::prelude::*;
use std::sync::Arc;

fn main() {
    // 1. 启动日志
    env_logger::init();

    // 2. 拿到一个"服务器配置"
    let mut my_server = Server::new(Some(Opt::default())).unwrap();
    my_server.bootstrap();  // 初始化线程池等

    // 3. 构造 upstream 池（用 round_robin）
    let upstreams = LoadBalancer::try_from_iter(["127.0.0.1:8081", "127.0.0.1:8082"]).unwrap();

    // 4. 构造代理服务
    let lb = my_server.add_service(
        MyProxy { upstream: Arc::new(upstreams) },
    );

    // 5. 监听 0.0.0.0:6188，反代到 upstream 池
    let mut proxy_service = http_proxy_service(
        &my_server.configuration,
        lb,
    );
    proxy_service.add_tcp("0.0.0.0:6188");
    my_server.add_service(proxy_service);

    // 6. run_forever() 才会启动事件循环 + 优雅重启监听
    my_server.run_forever();
}

// ====== 业务代理 ======

pub struct MyProxy {
    pub upstream: Arc<LoadBalancer<RoundRobin>>,
}

#[async_trait]
impl ProxyHttp for MyProxy {
    /// 核心入口：根据请求上下文选一个后端
    type CTX = ();
    fn new_ctx(&self) -> Self::CTX { () }

    async fn upstream_peer(
        &self,
        _session: &mut Session,
        _ctx: &mut Self::CTX,
    ) -> Result<Box<HttpPeer>> {
        // 从负载均衡器选一个上游
        let upstream = self.upstream.select(b"", 256).unwrap();
        // 把请求转发到这个 upstream 的 80 端口，且不做 TLS
        let peer = Box::new(HttpPeer::new(upstream, true, "one.example".to_string()));
        Ok(peer)
    }

    async fn response_filter(
        &self,
        _session: &mut Session,
        _upstream_response: &mut ResponseHeader,
        _ctx: &mut Self::CTX,
    ) -> Result<()> {
        // 可在此注入 / 修改响应头（如加 CORS、加监控埋点头）
        Ok(())
    }
}
```

### 3.4 编译 + 运行

```bash
cargo run --release
# 监听 0.0.0.0:6188，将 HTTP 请求代理到 8081/8082
curl http://localhost:6188/
```

---

## 四、5 大核心特性

| 特性 | 说明 | 对比优势 |
|------|------|---------|
| **1. HTTP/1+2 全协议** | 同时支持文本协议、h2 | 不需要 nginx stream 模块做混合 |
| **2. 异步 I/O (Tokio)** | 基于 tokio 运行时 | 写法和普通 Rust 异步工程完全一致 |
| **3. 零拷贝 / 内存池** | 字节流抽象避免反复分配 | O(1) 内存压力，与 traffic 量解耦 |
| **4. 可编程代理 (ProxyHttp trait)** | `upstream_peer` / `request_filter` / `response_filter` | 不需要写 C 模块或 Lua 脚本 |
| **5. 自定义负载均衡** | 实现 `Backend` trait 即可插入任意选择算法 | 一致性哈希 / 地理位置 / 权重全由你定 |

### 4.1 过滤器链（Filter Pipeline）

```rust
#[async_trait]
impl ProxyHttp for MyProxy {
    async fn request_filter(
        &self,
        session: &mut Session,
        ctx: &mut Self::CTX,
    ) -> Result<bool> {
        // 返回 Ok(true) 表示"我直接处理，不用再转发"
        if session.req_header().uri.path() == "/healthz" {
            let _ = session.respond_error(200).await;
            return Ok(true);
        }
        Ok(false)
    }
}
```

### 4.2 优雅重启 / 零停机升级

```rust
// 启动时自动监听 SIGUSR1
my_server.run_forever();
// 收到 SIGUSR1 → 老进程停止接受新连接 + 等旧连接 drain → 启动新进程
kill -USR1 <pid>
```

---

## 五、真实部署方式（3 种）

> **重要澄清**：Pingora **没有官方预编译的 `pingora` 二进制**，也没有 `pingora config.toml` 这种"内置配置语言"。下面三种方式都是社区和 Cloudflare 自己用的：

### 方式 1：直接用 cargo 编译（开发 / 测试）

```bash
git clone https://github.com/cloudflare/pingora
cd pingora
cargo build --release     # 编译完后 .so / .rlib 在 target/release，不会出现可执行文件
cargo run --example <name>  # 跑 examples/ 里的小 demo
```

适用：本地读源码、改 example、跑性能测试。

### 方式 2：嵌入到你自己的 Rust 服务（**推荐**）

这就是 pingora 的核心用法——把 pingora 当 crate，混入业务服务里：

```text
你的 Rust 服务（一个进程）
├── pingora::Server 跑事件循环
├── pingora-proxy 反代业务 API
├── 业务逻辑（鉴权 / 限流 / 业务转发）
└── 监控上报（Prometheus / Sentry）
```

优势：
- **单一二进制部署**：不需要"先装 Nginx 再装 Lua-模块"
- **类型安全**：路由表、CORS、限流全用 Rust 写
- **可观测**：天然能从业务上下文里拿到 traceid

### 方式 3：Cloudflare 的生产 workflow

参考 Cloudflare 官方博客（[2024-02-27 发布文](https://blog.cloudflare.com/pingora-open-source/)）：

```bash
# 生产环境大致流程
1. 在 CI 编译 cross target（Docker 镜像里 cargo build --release）
2. 推到内部 registry（ghcr.io / ECR）
3. k8s / 物理机拉镜像启动
4. 进程拉 SIGUSR1 完成优雅滚动
```

> ⚠️ Cloudflare 没有开源"完整生产编排脚本"——上面的工作流是社区总结的最佳实践。

---

## 六、3 个 ❌/✅ 反例对比

### ❌ 反例 1：把 pingora 当成 nginx 二进制用

```bash
# ❌ 错！根本不存在这个命令
pingora -c /etc/pingora.conf
pingora start
systemctl start pingora
```

```rust
// ✅ 对：用 Rust 代码驱动
fn main() {
    let mut server = Server::new(Some(Opt::default())).unwrap();
    server.bootstrap();
    // ... 添加 service ...
    server.run_forever();
}
```

### ❌ 反例 2：以为有 pingora 自带配置文件

```toml
# ❌ 错！没有这种官方格式
[global]
worker_threads = 4

[[proxy.rules]]
path = "/api/*"
upstream = "http://backend:8080"
```

```rust
// ✅ 对：所有配置都是 Rust 代码（常量、结构体、命令行参数）
let listen_addr = std::env::var("LISTEN").unwrap_or("0.0.0.0:6188".into());
let backends: Vec<_> = std::env::var("BACKENDS")
    .unwrap_or_default()
    .split(',')
    .map(|s| s.to_string())
    .collect();

let upstreams = LoadBalancer::try_from_iter(backends).unwrap();
```

### ❌ 反例 3：把 upstream 选择写在主流程

```rust
// ❌ 这样写性能差（请求级 mutex）
fn upstream_peer(&self, _: &mut Session, _: &mut ()) -> Result<Box<HttpPeer>> {
    let mut backends = self.backends.lock().unwrap();
    let next = backends.pop().unwrap();
    Ok(Box::new(HttpPeer::new(next, true, "one".into())))
}
```

```rust
// ✅ 用官方 LoadBalancer（lock-free / 一致性哈希都可）
fn upstream_peer(&self, _: &mut Session, _: &mut ()) -> Result<Box<HttpPeer>> {
    let backend = self.upstreams.select(b"", 256).unwrap();
    Ok(Box::new(HttpPeer::new(backend, true, "one".into())))
}
```

---

## 七、5 大反模式（生产避坑）

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | **在过滤器里做阻塞 I/O**（如调 HTTP 鉴权服务） | 阻塞整个 worker 线程 | 用非阻塞客户端或加缓存层 |
| 2 | **upstream peer 锁长持有** | 头延迟抖动 + QPS 受限 | 把 upstream 池构造一次，复用 `Arc` |
| 3 | **不实现 graceful shutdown** | SIGTERM 杀掉活跃连接 | 监听 `SIGTERM` → 停止接受 → `tokio::time::sleep` 等待 drain |
| 4 | **把请求路径字符串硬编码** | 多路由时变 spaghetti | 用 `match` + 结构化路由表 |
| 5 | **忽略了TLS 验证配置** | 中间人风险 | `HttpPeer::new(addr, true, SNI)` 中正确配置 SNI/CA |

---

## 八、3 个常见陷阱

### 陷阱 1：把 pingora 当作"独立服务"而非"库"

很多人搜索 `install pingora` / `docker pull pingora`——**都没有**。
✅ 解决：用 `cargo new` 起你自己的工程，把 pingora 当依赖。

### 陷阱 2：版本号漂移

`pingora` 还在活跃迭代，crate 版本号与 GitHub tag 可能不一致。
✅ 解决：以 GitHub Releases 为准，pin 到具体 commit 短期稳定。

### 陷阱 3：on Windows 编译坑多

Pingora 依赖 OpenSSL/BoringSSL，Windows 下链接复杂。
✅ 解决：开发/测试在 Linux（WSL2 / 容器）；生产用 Linux 镜像。

---

## 九、30 秒话术

> **Pingora 是 Cloudflare 在 2024 年开源的 Rust HTTP 代理**框架，**库而非二进制**——你只需要 `cargo new` 一个工程、引入 `pingora` crate、写一段 `async_trait impl ProxyHttp`，就能跑起来一个支持 HTTP/1+2、零停机升级、自定义负载均衡的反向代理。它的核心卖点是**用 Rust 的类型安全和 async trait 替代 Nginx 的 DSL 配置**，让代理逻辑变成可编译的 Rust 代码——而不是 yaml/json/toml 拼出来的脆弱规则。Cloudflare 自己用它扛住了日均数万亿请求。

---

## 十、相关链接

- 官方仓库：<https://github.com/cloudflare/pingora>
- 发布公告：<https://blog.cloudflare.com/pingora-open-source/>
- 同主题：[Nginx 基础与替代](../README.md)
- 上游：[工具链总览](../../README.md)

---

← [返回 Nginx](../README.md)
