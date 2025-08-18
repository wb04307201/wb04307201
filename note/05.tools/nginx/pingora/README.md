# Pingora 

## 一、Pingora 核心介绍
Pingora 是由 Cloudflare 开源的高性能网络服务器框架，基于 Rust 编写，旨在替代 Nginx 提供更安全、高效且可定制的网络服务。其核心特性包括：

1. **极致性能**
    - **单线程处理能力**：在性能测试中，Pingora 单线程每秒可处理 **4000 万请求**，远超同类产品。
    - **资源效率**：多线程模型与连接池共享技术显著提升连接复用率，降低延迟与资源消耗。
    - **协议支持**：全面支持 HTTP/1、HTTP/2、TLS、gRPC、WebSocket，并计划支持 HTTP/3。

2. **安全与可靠性**
    - **内存安全**：Rust 语言特性消除内存泄漏与缓冲区溢出风险，提供比 C/C++ 更安全的运行环境。
    - **优雅重启**：零停机时间升级，确保服务连续性。
    - **合规性**：支持 OpenSSL 和 BoringSSL 库，符合 FIPS 标准及后量子加密要求。

3. **高度可定制**
    - **可编程 API**：提供过滤器与回调函数，支持自定义请求处理、转换与转发逻辑。
    - **负载均衡策略**：内置轮询、加权轮询、最小连接数等算法，并支持自定义策略。
    - **可观测性**：集成 Syslog、Prometheus、Sentry 等工具，实现实时监控与日志分析。

4. **应用场景**
    - **Web 服务器**：为网站提供高性能访问体验。
    - **反向代理**：负载均衡、故障转移与安全防护。
    - **API 网关**：灵活路由与流量管理。
    - **微服务架构**：服务注册、发现与通信协调。

## 二、安装指南

### 1. 基础环境要求
- **操作系统**：仅支持 Linux（推荐 Ubuntu 20.04+ 或 CentOS 7+）。
- **架构**：x86_64 或 aarch64。
- **依赖工具**：
    - Rust 1.72+（编译工具链）：
      ```bash
      curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
      source $HOME/.cargo/env
      ```
    - Clang 与 Perl 5（用于构建特定库）：
      ```bash
      # Ubuntu/Debian
      sudo apt-get install clang perl
  
      # CentOS/RHEL
      sudo yum install clang perl
      ```

### 2. 源码编译安装
1. **克隆代码库**：
   ```bash
   git clone https://github.com/cloudflare/pingora.git
   cd pingora
   ```

2. 编译项目：
   ```bash
   cargo build --release
   ```
    - 编译完成后，二进制文件位于 `./target/release/pingora`。

3. 验证安装：
   ```bash
   ./target/release/pingora --version
   ```
    - 输出版本号即表示安装成功。

### 3. 预编译包（可选）
- Cloudflare 官方提供预编译的 Linux 二进制包，可从 [GitHub Releases](https://github.com/cloudflare/pingora/releases) 下载，直接解压使用：
  ```bash
  tar -xzf pingora-x.x.x-linux-amd64.tar.gz
  cd pingora-x.x.x
  ./pingora --help
  ```

## 三、配置说明
Pingora 的配置通过 `config.toml` 文件完成，支持动态模块加载与灵活参数调整。以下为关键配置示例：

### 1. 全局设置
```toml
[global]
log_level = "info"       # 日志级别：debug/info/warn/error
pid_file = "/var/run/pingora.pid"  # PID 文件路径
worker_threads = 4       # 工作线程数（建议为 CPU 核心数 2 倍）
```

### 2. 网络监听
```toml
[network]
listen = ["0.0.0.0:80", "[::]:80"]  # 监听 IPv4 与 IPv6 的 80 端口
ssl_certificate = "/etc/ssl/certs/pingora.crt"  # TLS 证书路径
ssl_certificate_key = "/etc/ssl/private/pingora.key"  # TLS 私钥路径
```

### 3. 代理规则
```toml
[proxy]
[[proxy.rules]]
path = "/api/*"          # 匹配路径
upstream = "http://backend:8080"  # 后端服务地址
load_balancing = "round_robin"   # 负载均衡算法

[[proxy.rules]]
header = "X-Forwarded-For"  # 匹配请求头
upstream = "http://secondary:8080"
load_balancing = "least_conn"
```

### 4. 负载均衡
```toml
[load_balancing]
[[load_balancing.backends]]
name = "backend1"
address = "192.168.1.100:80"
weight = 2  # 权重（数值越大，分配流量越多）

[[load_balancing.backends]]
name = "backend2"
address = "192.168.1.101:80"
weight = 1
```

### 5. 健康检查
```toml
[health_check]
interval = 10  # 检查间隔（秒）
timeout = 5    # 超时时间（秒）
path = "/healthz"  # 健康检查端点
expected_status = [200, 204]  # 预期响应状态码
```

### 6. 启动与验证
1. **启动服务**：
   ```bash
   ./target/release/pingora -c /path/to/config.toml
   ```

2. **测试代理功能**：
   ```bash
   curl -I http://localhost/api/test
   ```
    - 返回后端服务响应头即表示配置生效。

3. **监控日志**：
   ```bash
   tail -f /var/log/pingora/access.log
   ```

## 四、进阶功能
1. **动态模块加载**：通过 `pingora-proxy` 扩展实现自定义逻辑。
2. **gRPC 代理**：在配置中启用 `grpc = true` 并指定后端服务。
3. **WebSocket 支持**：配置 `websocket = true` 以处理长连接。
4. **Prometheus 集成**：暴露 `/metrics` 端点供监控系统抓取数据。

## 五、总结
Pingora 凭借 Rust 的安全特性与异步模型，在性能、安全性与可定制性上全面超越传统代理工具。其安装与配置流程简洁，支持从基础负载均衡到复杂微服务架构的多样化场景。对于追求极致性能与灵活性的企业级应用，Pingora 是替代 Nginx 的理想选择。