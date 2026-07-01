<!--
module:
  parent: system-design
  slug: system-design/01-ebpf
  type: article
  category: 主模块子文章
  summary: 一份按场景梳理的 eBPF 速查手册：从可观测性到安全的内核级革命。
-->

# eBPF · 内核级可观测与网络编程实战

> 一份按场景梳理的 eBPF 速查手册：从可观测性到安全的内核级革命。

---
## 引言：反直觉代码

eBPF · 内核级可观测与网络编程实战 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、什么是 eBPF？

eBPF（extended Berkeley Packet Filter）是 Linux 内核的一项革命性技术，允许**在内核中安全运行沙箱程序**，无需修改内核源码或加载内核模块。

### 1.1 核心特性

- **内核态执行**：性能极高（无需上下文切换）
- **安全沙箱**：Verifier 验证程序安全性（无死循环 / 无越界）
- **动态加载**：无需重启内核 / 服务
- **JIT 编译**：本地机器码，性能接近原生 C
- **丰富 hook 点**：网络 / 性能 / 安全 / 跟踪

### 1.2 适用场景

| 场景 | 传统方案 | eBPF 方案 |
|------|---------|---------|
| **网络可观测** | tcpdump / iptables | eBPF 全流量采集 |
| **性能分析** | perf / strace | eBPF 零侵入分析 |
| **安全检测** | 流量镜像 | eBPF 实时阻断 |
| **服务网格** | iptables + sidecar | eBPF 内核加速 |

---

## 二、eBPF 工作原理

```
用户空间（User Space）
   ↓
eBPF 程序（C / Rust 写）
   ↓
LLVM 编译为 BPF 字节码
   ↓
Verifier 验证安全性
   ↓
JIT 编译为机器码
   ↓
内核空间（Kernel Space）
   ↓
挂载到 hook 点（如网络收发 / 系统调用）
```

---

## 三、4 大工具生态

### 3.1 可观测

| 工具 | 用途 |
|------|------|
| **Pixie** | K8s 自动可观测（New Relic）|
| **Parca** | 持续剖析（profiling）|
| **Bpftrace** | eBPF 高级跟踪语言 |

### 3.2 网络

| 工具 | 用途 |
|------|------|
| **Cilium** | K8s CNI 网络（替代 Calico）|
| **Calico eBPF** | K8s 网络策略 |

### 3.3 安全

| 工具 | 用途 |
|------|------|
| **Tetragon** | eBPF 实时安全（思科/Cilium 出品）|
| **Falco** | 运行时威胁检测 |

### 3.4 性能

| 工具 | 用途 |
|------|------|
| **bcc / bpftrace** | 性能分析工具包 |
| **parca** | 持续 profiling |

---

## 四、Cilium 实战（最流行的 eBPF 项目）

### 4.1 什么是 Cilium？

Cilium 是基于 eBPF 的 K8s CNI（容器网络），提供：
- 高性能网络（绕过 iptables）
- 细粒度网络策略
- 透明加密（WireGuard / IPsec）
- 替代 kube-proxy（无需 iptables）

### 4.2 Cilium 部署

```bash
# 通过 Helm 部署（替代 Calico）
helm repo add cilium https://helm.cilium.io
helm install cilium cilium/cilium \
  --namespace kube-system \
  --set kubeProxyReplacement=true \
  --set bpf.masquerade=true
```

### 4.3 性能对比

| 场景 | Calico（iptables）| Cilium（eBPF）|
|------|------------------|----------------|
| 1000 Pod 网络策略 | 5-10 秒（iptables 重写）| < 100ms（eBPF）|
| 服务间连接追踪 | 不可用 | 完整 L7 可见 |
| DNS 策略 | 需额外组件 | 内置（eBPF hook）|

---

## 五、Tetragon 实时安全实战

### 5.1 场景

```
检测异常：
  - 进程异常行为（如反弹 shell）
  - 文件篡改
  - 网络异常连接
  - 容器逃逸
   ↓
eBPF 内核级拦截
   ↓
自动告警 / 阻断
```

### 5.2 安装 Tetragon

```bash
helm install tetragon cilium/tetragon -n kube-system
```

### 5.3 TracingPolicy 示例

```yaml
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: detect-suspicious-process
spec:
  kprobes:
  - call: "security_bpf_prog"  # 内核函数
    syscall: false
  tracepoints:
  - subsystem: "sched"
    event: "sched_process_exec"
  filters:
  - matchArgs:
    - index: 0
      operator: "Not"
      values:
      - "/usr/bin/bash"
      - "/usr/bin/ls"
  action: "sigkill"   # 自动杀死异常进程
```

---

## 六、bpftrace 实战

### 6.1 一行命令统计系统调用

```bash
# 统计每个进程的系统调用次数
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'
```

### 6.2 跟踪 HTTP 请求延迟

```bash
bpftrace -e '
kprobe:tcp_sendmsg {
  $ts = nsecs;
  @start[tid] = $ts;
}
kretprobe:tcp_sendmsg /@start[tid]/ {
  @usecs = hist((nsecs - @start[tid]) / 1000);
  delete(@start[tid]);
}
'
```

### 6.3 自定义 eBPF 程序（C）

```c
#include <linux/bpf.h>

SEC("tracepoint/syscalls/sys_enter_openat")
int trace_openat(struct trace_event_raw_syscalls_args *ctx) {
    char filename[256];
    bpf_probe_read_user_str(filename, sizeof(filename), ctx->args[1]);
    bpf_printk("openat: %s\n", filename);
    return 0;
}

char _license[] SEC("license") = "GPL";
```

---

## 七、eBPF 在 K8s 中的应用

### 7.1 CNI（容器网络）

| CNI | eBPF 支持 | 性能 |
|-----|----------|------|
| **Cilium** | ✅ 完全 eBPF | ⭐⭐⭐⭐⭐ |
| **Calico eBPF** | ✅ 部分 | ⭐⭐⭐⭐ |
| **Flannel** | ❌ | ⭐⭐ |

### 7.2 替代 kube-proxy

- **传统 kube-proxy**：iptables 规则（O(n²)）
- **Cilium 替代**：eBPF（O(1) hash map）

**效果**：1000+ Service 时，kube-proxy 性能下降，Cilium 保持稳定。

### 7.3 Service Mesh 加速

- **Istio + Envoy**：每个 Pod 一个 sidecar 代理（资源消耗大）
- **Cilium Service Mesh**：eBPF 内核态实现（无需 sidecar）

**性能对比**：
- Istio：增加 1-3ms 延迟（sidecar）
- Cilium SM：增加 < 0.1ms 延迟（eBPF）

---

## 八、eBPF 限制与挑战

| 限制 | 说明 |
|------|------|
| **Linux 内核版本** | 需要 4.19+（推荐 5.10+）|
| **Verifier 限制** | 程序不能太大（1M 指令）|
| **学习曲线** | 内核态编程（需要懂 C / Rust）|
| **调试困难** | 工具链尚不完善 |
| **跨平台** | 仅 Linux（Windows / macOS 不支持）|

---

## 九、生产实践

### 9.1 选型建议

| 需求 | 推荐方案 |
|------|---------|
| **K8s CNI** | Cilium（首选）|
| **可观测** | Pixie / Parca |
| **安全检测** | Tetragon / Falco |
| **性能分析** | bpftrace / perf |

### 9.2 性能优化

- 启用 BPF JIT（默认开启）
- 减少 BPF 程序大小（Verifier 限制）
- 使用 RingBuf 替代 perf event

---

## 十、最佳实践

1. **生产用 Cilium**：Cilium 是最成熟的 eBPF CNI
2. **K8s 替代 kube-proxy**：启用 kubeProxyReplacement
3. **可观测 + 安全**：用 Tetragon / Falco 检测异常
4. **升级内核**：5.10+ 才能用全部 eBPF 特性
5. **谨慎使用自定义 eBPF 程序**：先学工具，再自己写
6. **配合传统工具**：eBPF + Prometheus + Grafana

---

← [返回系统设计总览](../../README.md) · 📅 2026-06-28