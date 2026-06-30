# WebAssembly (WASM) · 跨平台高性能运行时实战

> 一份按场景梳理的 WebAssembly 速查手册：从浏览器到边缘计算到插件系统的全场景革命。

---
## 引言：性能对比（[AUTO] 自动生成，待人工 review）

WebAssembly (WASM) · 跨平台高性能运行时实战 的一份按场景梳理的 WebAssembly 速查手册：从浏览器到边缘计算到插件系统的全场景革命

**但实际**：常被问起'为什么我的版本慢 10 倍'、'怎么排查'。本篇用'对比数字'切入，把'常见 vs 极端'两种场景拆给你看。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、什么是 WebAssembly？

WebAssembly（缩写 WASM）是一种**可移植的二进制指令格式**，设计目标是**接近原生的执行速度** + **跨平台**。最初为浏览器设计，现已扩展到服务端、边缘计算、嵌入式等场景。

### 1.1 核心特性

- **高性能**：接近原生的执行速度（比 JS 快 10-100 倍）
- **跨平台**：浏览器 / 服务器 / 边缘 / 嵌入式
- **多语言**：C / C++ / Rust / Go / AssemblyScript
- **沙箱安全**：强隔离（线性内存 / 类型安全）
- **小体积**：二进制格式（KB 级）
- **WASI**：标准系统接口（让 WASM 访问文件 / 网络）

### 1.2 适用场景

| 场景 | 传统方案 | WASM 优势 |
|------|---------|---------|
| **浏览器高性能** | JavaScript | 10-100x 性能 |
| **边缘计算** | 容器（启动慢）| 毫秒级冷启动 |
| **插件系统** | 动态库（unsafe）| 安全沙箱 |
| **跨平台 SDK** | 各平台编译 | 一次编译多平台运行 |

---

## 二、WASM vs 容器 vs JavaScript

| 维度 | WASM | 容器 | JavaScript |
|------|------|------|-----------|
| 启动时间 | 毫秒 | 秒 | 毫秒 |
| 性能 | 接近原生 | 原生 | 解释执行 |
| 隔离性 | 强（沙箱）| 中（OS 级）| 弱（共享堆）|
| 多语言 | ✅ | ✅ | ❌（仅 JS）|
| 跨平台 | ✅ | ✅（需镜像）| ✅（浏览器）|
| 资源占用 | 小（KB）| 大（MB-GB）| 极小 |
| 适用 | 边缘 / 插件 | 完整应用 | Web UI |

---

## 三、WASM 在浏览器

### 3.1 应用场景

| 场景 | 案例 |
|------|------|
| **图像处理** | Figma / Photoshop Web |
| **游戏** | Unity / Unreal Engine 编译 WASM |
| **音视频** | Zoom / Google Meet 客户端 |
| **CAD / 3D** | AutoCAD Web / Figma |
| **加密** | 浏览器端加密库 |
| **AI 推理** | 浏览器跑 LLM（llama.cpp WASM）|

### 3.2 性能优势

```
任务：100 万像素的图像模糊

JavaScript：850ms
WebAssembly：45ms  （19x 速度）
原生 C：40ms
```

---

## 四、WASI · 浏览器外的 WASM

### 4.1 什么是 WASI？

WASI（WebAssembly System Interface）是 WASM 的**系统调用标准**，让 WASM 模块能访问文件、网络、时钟等系统资源。

### 4.2 WASI 与传统编译对比

```text
传统 C 程序：
  C 代码 → gcc 编译 → Linux 机器码（x86_64）
  → 在 ARM Mac 上：❌ 不能运行

WASI 程序：
  C 代码 → clang 编译 → WASM 字节码
  → 在任何平台：✅ 都能运行（通过 WASI runtime）
```

---

## 五、5 大 WASM 运行时

| Runtime | 语言 | 特点 |
|---------|------|------|
| **Wasmtime** | Rust | 字节码联盟官方 |
| **Wasmer** | Rust | 多语言 SDK |
| **WasmEdge** | C++ | CNCF 项目，边缘计算 |
| **Wazero** | Go | 纯 Go 实现，零依赖 |
| **Wasmtime / WAMR** | C | 微嵌入式运行时 |

### 5.1 Wasmtime 示例

```bash
# 安装
curl https://wasmtime.dev/install.sh | bash

# 运行 WASM 模块
wasmtime run hello.wasm

# 启用 WASI
wasmtime run --dir=. app.wasm
```

---

## 六、边缘计算：WASM 的杀手锏

### 6.1 为什么 WASM 适合边缘计算？

| 需求 | 传统容器 | WASM |
|------|---------|------|
| 冷启动 | 秒级 | **毫秒级** |
| 镜像大小 | MB-GB | KB-MB |
| 多语言 | 单语言镜像 | 一份 WASM 多语言 |
| 安全 | 弱 | 强沙箱 |

### 6.2 Cloudflare Workers（生产代表）

```javascript
// Cloudflare Workers（底层是 WASM）
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  return new Response('Hello from edge!', {
    headers: { 'content-type': 'text/plain' }
  });
}
```

**性能**：冷启动 < 5ms，99% 请求 < 50ms。

### 6.3 Fastly Compute@Edge

```rust
// Rust 编译为 WASM
#[fastly::main]
fn main(req: Request) -> Result<Response, Error> {
    Ok(Response::builder()
        .status(200)
        .body("Hello from Fastly edge!")
        .build()?)
}
```

---

## 七、插件系统：WASM 安全沙箱

### 7.1 传统插件系统的困境

```
宿主（Host）需要执行不可信代码：
  - 浏览器执行第三方 JS（XSS 风险）
  - 数据库执行 UDF（SQL 注入）
  - Proxmox 执行客户插件（逃逸风险）
```

### 7.2 WASM 插件优势

```
WASM 沙箱特性：
  ✅ 线性内存（无法越界）
  ✅ 类型安全
  ✅ 系统调用受限（需要 WASI 显式声明）
  ✅ 无网络 / 文件访问（除非显式 allow）
  ✅ 不可执行 native 代码
```

### 7.3 Envoy WASM 扩展

```yaml
# EnvoyFilter 用 WASM 实现自定义 filter
apiVersion: extensions.istio.io/v1alpha1
kind: WasmPlugin
metadata:
  name: custom-auth
spec:
  url: oci://registry/auth-filter:v1
  # WASM filter 部署到 Envoy
  filterConfig:
    config:
      api_key: "xxx"
```

---

## 八、主流 WASM 应用案例

| 公司 | 场景 | 收益 |
|------|------|------|
| **Cloudflare** | Workers（边缘计算）| 冷启动 < 5ms |
| **Fastly** | Compute@Edge | 边缘函数 |
| **Figma** | 浏览器内设计工具 | 性能提升 10x |
| **Photoshop Web** | 浏览器内 PS | 原生级性能 |
| **Envoy / Istio** | WASM Filter | 安全的扩展机制 |
| **Docker + WASM** | wasm-to-oci | 容器内运行 WASM |
| **Shopify** | Functions 平台 | 多语言函数 |

---

## 九、WASM 开发实战

### 9.1 Rust → WASM

```bash
# 安装目标
rustup target add wasm32-wasi

# 编译
cargo build --target wasm32-wasi --release
```

### 9.2 C / C++ → WASM

```bash
# 使用 Emscripten
emcc hello.c -o hello.html

# 使用 Clang + WASI
clang --target=wasm32-wasi -o hello.wasm hello.c
```

### 9.3 Go → WASM

```bash
GOOS=js GOARCH=wasm go build -o app.wasm
```

### 9.4 AssemblyScript（TypeScript-like）

```typescript
// hello.ts
export function add(a: i32, b: i32): i32 {
  return a + b;
}
```

```bash
asc hello.ts --outFile hello.wasm
```

---

## 十、最佳实践

1. **边缘计算首选 WASM**：冷启动 + 性能 + 安全
2. **浏览器高性能模块**：用 WASM 替代 JS（计算密集型）
3. **插件系统用 WASM 沙箱**：安全执行不可信代码
4. **多语言 SDK**：WASM 一次编译多平台
5. **小工具 / CLI**：用 Go/Rust → WASM 分发（无需目标机器装运行时）
6. **避免 WASM 用于**：纯 UI（用 JS）、大内存（受 4GB 限制）
7. **持续关注**：Component Model / WASI 0.2 标准化进展

---

← [返回系统设计总览](../../README.md) · 📅 2026-06-28