<!--
module:
  parent: tools
  slug: tools/k8s-storage
  type: article
  category: 主模块子文章
  summary: K8s 存储 PV/PVC/StorageClass
-->

# K8s 存储：PV / PVC / StorageClass 实战

> 一份按层次梳理的 K8s 存储速查手册：从 Volume 到动态供给的完整路径。

---
---

## 一、K8s 存储架构

```
┌────────────────────────────────────────────────┐
│  Pod                                              │
│  ┌─────────────┐                                │
│  │ 容器         │                                │
│  │  ↓ mount     │                                │
│  └─────────────┘                                │
│         ↓ Volume Mount                          │
│  ┌──────────────────────────────────┐           │
│  │ Volume (emptyDir / hostPath / PVC) │           │
│  └──────────────────────────────────┘           │
│         ↓                                        │
│  ┌──────────────────────────────────┐           │
│  │ PersistentVolumeClaim (PVC)       │           │
│  │ "我要 100Gi 的 SSD 存储"             │           │
│  └──────────────────────────────────┘           │
│         ↓ Binding                                │
│  ┌──────────────────────────────────┐           │
│  │ PersistentVolume (PV)              │           │
│  │ "我有 1Ti 的 NFS 存储"              │           │
│  └──────────────────────────────────┘           │
│         ↓                                        │
│  ┌──────────────────────────────────┐           │
│  │ 实际存储后端                         │           │
│  │ NFS / Ceph / 云厂商存储（EBS/Aliyun）│           │
│  └──────────────────────────────────┘           │
└────────────────────────────────────────────────┘
```

---

## 二、Volume 类型对比

| 类型 | 生命周期 | 适用场景 | 是否持久 |
|------|---------|---------|---------|
| **emptyDir** | Pod 生命周期 | 临时存储 / 缓存 | ❌ |
| **hostPath** | Node 生命周期 | 节点访问 | ⚠️ 风险 |
| **configMap / Secret** | ConfigMap 生命周期 | 配置注入 | ❌ |
| **PVC** | PV 生命周期 | 持久数据 | ✅ |
| **nfs** | 手动管理 | NFS 共享存储 | ✅ |
| **cephfs / glusterfs** | 集群管理 | 分布式存储 | ✅ |
| **awsElasticBlockStore / aliyunDisk** | 云厂商管理 | 云盘 | ✅ |

---

## 三、emptyDir（临时存储）

```yaml
spec:
  containers:
  - name: app
    volumeMounts:
    - name: cache
      mountPath: /tmp/cache
  volumes:
  - name: cache
    emptyDir: {}                  # 简单空目录
  # 或指定大小和介质
  - name: cache-large
    emptyDir:
      sizeLimit: 1Gi              # 1Gi 大小限制
      medium: Memory              # 内存介质（极快）
```

**适用**：临时缓存、Sidecar 之间共享数据。

---

## 四、hostPath（节点路径）

```yaml
spec:
  volumes:
  - name: host-data
    hostPath:
      path: /data
      type: Directory
```

⚠️ **风险**：Pod 漂移到其他 Node 时数据丢失。生产慎用。

---

## 五、PV / PVC（核心持久化）

### 5.1 PV（PersistentVolume）：集群管理员创建

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs-001
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce              # RWO
  persistentVolumeReclaimPolicy: Retain  # 保留
  storageClassName: nfs
  nfs:
    server: 192.168.1.100
    path: "/exports/data"
```

### 5.2 PVC（PersistentVolumeClaim）：应用开发者创建

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data-pvc
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 50Gi               # 申请 50Gi
  storageClassName: nfs            # 指定存储类
```

### 5.3 Pod 使用 PVC

```yaml
spec:
  containers:
  - name: app
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: app-data-pvc
```

---

## 六、StorageClass（动态供给）

手动创建 PV 繁琐，生产环境使用 **StorageClass + 动态供给**：

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ssd
provisioner: kubernetes.io/aws-ebs   # 或 aliyun/disk 等
parameters:
  type: gp3
  fsType: ext4
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
```

**PVC 申请时指定 storageClassName → 自动创建 PV**：

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data-auto
spec:
  storageClassName: ssd            # 自动从 AWS EBS 创建 PV
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 100Gi
```

---

## 七、CSI（Container Storage Interface）

K8s 通过 CSI 插件对接各种存储后端：

| 存储后端 | CSI 驱动 |
|---------|---------|
| AWS EBS | `ebs.csi.aws.com` |
| 阿里云盘 | `diskplugin.csi.alibabacloud.com` |
| 腾讯云 CBS | `bs.csi.tencentcloud.com` |
| Ceph RBD | `rook-ceph.rbd.csi.ceph.com` |
| NFS | `nfs.csi.k8s.io` |
| GlusterFS | `gluster.org/glusterfs-csi-driver` |

---

## 八、有状态应用实战（StatefulSet + PVC）

StatefulSet 自动为每个 Pod 创建独立 PVC：

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  template:
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: ssd
      resources:
        requests:
          storage: 100Gi
```

**自动生成 PVC**：
- `data-mysql-0`（挂给 mysql-0）
- `data-mysql-1`（挂给 mysql-1）
- `data-mysql-2`（挂给 mysql-2）

---

## 九、PV 回收策略

| 策略 | 行为 | 适用 |
|------|------|------|
| **Retain（默认）** | PV 保留，需手动清理 | 重要数据 |
| **Delete** | PV 自动删除 | 临时数据 / 测试 |
| **Recycle** | 简单清除数据（已废弃）| —— |

生产推荐 **Retain**，删除 Pod 后保留数据备查。

---

## 十、最佳实践

1. **有状态用 StatefulSet + PVC**：不要用 Deployment + 共享卷
2. **StorageClass 自动供给**：避免手动创建 PV
3. **生产用云盘 / Ceph**：不要用 hostPath
4. **快照备份**：重要数据必须定期 PV 快照
5. **StorageClass 选择**：性能（SSD/HDD）+ 持久性（Reclaim Policy）

---

← [返回 K8s 总览](../README.md) · 📅 2026-06-28