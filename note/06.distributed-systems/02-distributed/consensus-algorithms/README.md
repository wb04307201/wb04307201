<!--module:
  parent: system-design/02-distributed
  slug: 12.interview/04.system-design/02-distributed/consensus-algorithms
  type: article
  category: 主模块子文章
  summary: 分布式共识算法（Paxos / Raft / Gossip）的原理、实现、配置与故障场景分析
-->

# 共识算法

> ⬅️ [返回: 分布式系统](../README.md)

> **一句话定位**：共识算法是分布式系统的核心基础——让多个节点在存在故障的情况下就某个值达成一致。本文覆盖 Paxos / Raft / Gossip 三大算法的原理、流程、配置与故障场景。

---

## 🎯 学习目标

- 理解共识问题的本质（拜占庭将军问题、FLP 不可能性）
- 掌握 Paxos / Raft / Gossip 三大算法的核心思想与区别
- 学会配置 Etcd / Consul 集群
- 能分析常见故障场景（网络分区、节点宕机、脑裂）
- 了解实际生产中的最佳实践

---

## 📚 核心概念

### 什么是共识问题？

```text
分布式系统中，多个节点需要就某个值达成一致，即使部分节点故障。

核心挑战：
  1. 节点可能宕机（Fail-stop）
  2. 网络可能延迟或丢包
  3. 网络可能分区（部分节点不可达）
  4. 消息可能乱序

目标：
  - 一致性（Consistency）：所有正常节点最终达成相同的值
  - 可用性（Availability）：系统能继续处理请求
  - 分区容忍（Partition Tolerance）：网络分区时仍能工作

FLP 不可能性：
  在异步网络中，即使只有一个节点可能故障，
  也不存在确定性的共识算法能保证在有限时间内达成一致。
  
  → 实际算法都基于"最终一致性"或"概率性保证"
```

### 共识算法分类

| 类型 | 算法 | 特点 | 适用场景 |
|------|------|------|---------|
| **强一致** | Paxos / Raft | 多数派 quorum，线性一致 | Etcd / Consul / ZooKeeper |
| **最终一致** | Gossip | 反熵传播，弱一致 | Cassandra / Dynamo / Riak |
| **拜占庭容错** | PBFT | 容忍恶意节点 | 区块链 / 金融系统 |

---

## 🧠 Paxos 算法

### 核心思想

Paxos 是 Leslie Lamport 1989 年提出的经典共识算法，分为 Basic Paxos 和 Multi Paxos。

**Basic Paxos 两阶段提交**：

```text
角色：
  - Proposer（提案者）：发起提案
  - Acceptor（接受者）：投票表决
  - Learner（学习者）：学习最终结果

阶段 1：Prepare（准备）
  Proposer → Acceptor: PREPARE(n)
    "我提议一个值为 v，提案编号为 n"
  
  Acceptor → Proposer: PROMISE(n, v') 或 REJECT
    "我承诺不再接受编号 < n 的提案"
    v' = 已接受的最大编号提案的值（可选）

阶段 2：Accept（接受）
  Proposer → Acceptor: ACCEPT(n, v)
    "请接受编号 n，值为 v 的提案"
  
  Acceptor → Proposer: ACCEPTED(n) 或 REJECT
    "我接受了提案" 或 "我拒绝了（因为已承诺更大的编号）"

提交条件：
  当 Proposer 收到多数派（> N/2）的 ACCEPTED 响应时，
  提案被提交，所有节点学习该值。
```

**Paxos 伪代码**：

```python
class Proposer:
    def __init__(self, id):
        self.id = id
        self.proposal_num = 0
        self.value = None
    
    def propose(self, value):
        self.value = value
        
        # 阶段 1：Prepare
        self.proposal_num += 1
        promises = []
        for acceptor in acceptors:
            response = acceptor.prepare(self.proposal_num)
            if response.type == 'PROMISE':
                promises.append(response)
        
        # 检查是否收到多数派响应
        if len(promises) < len(acceptors) // 2 + 1:
            return False  # 提案失败
        
        # 如果有已接受的值，使用它；否则使用自己的值
        accepted_values = [p.accepted_value for p in promises if p.accepted_value]
        if accepted_values:
            self.value = max(accepted_values, key=lambda x: x[0])[1]
        
        # 阶段 2：Accept
        accepted = []
        for acceptor in acceptors:
            response = acceptor.accept(self.proposal_num, self.value)
            if response.type == 'ACCEPTED':
                accepted.append(response)
        
        # 检查是否提交
        if len(accepted) >= len(acceptors) // 2 + 1:
            return True  # 提案提交成功
        return False

class Acceptor:
    def __init__(self, id):
        self.id = id
        self.promised_num = 0  # 已承诺的最大编号
        self.accepted_num = 0  # 已接受的最大编号
        self.accepted_value = None
    
    def prepare(self, proposal_num):
        if proposal_num > self.promised_num:
            self.promised_num = proposal_num
            return Promise(proposal_num, self.accepted_value)
        return Reject(proposal_num)
    
    def accept(self, proposal_num, value):
        if proposal_num >= self.promised_num:
            self.promised_num = proposal_num
            self.accepted_num = proposal_num
            self.accepted_value = value
            return Accepted(proposal_num)
        return Reject(proposal_num)
```

**优缺点**：

| 优点 | 缺点 |
|------|------|
| 理论完备，证明严格 | 实现复杂，难以理解 |
| 支持任意数量故障 | 性能较差（两阶段通信） |
| 可处理动态成员变化 | 需要精确的多数派 quorum |

---

## 🧠 Raft 算法

### 核心思想

Raft 是 Diego Ongaro 2013 年提出的"易于理解"的共识算法，与 Paxos 等价但更易实现。

**三大子问题**：
1. **Leader 选举**：选出一个 Leader 负责处理所有请求
2. **日志复制**：Leader 将日志复制到其他节点
3. **安全性保证**：确保日志一致性和状态机安全

### Leader 选举流程

```text
节点状态：
  - Follower：跟随者，响应 Leader 请求
  - Candidate：候选人，发起选举
  - Leader：领导者，处理客户端请求

选举流程：
  1. 初始状态：所有节点都是 Follower
  2. 超时触发：Follower 在选举超时（150-300ms 随机）内未收到 Leader 心跳
  3. 转为 Candidate：节点增加任期号（term），发起选举
  4. 请求投票：Candidate 向其他节点发送 RequestVote 请求
  5. 投票规则：
     - 每个节点在一个任期内只能投一票
     - 优先投给日志更长的 Candidate
  6. 成为 Leader：收到多数派（> N/2）投票的 Candidate 成为 Leader
  7. 心跳维持：Leader 定期发送心跳（AppendEntries），重置 Follower 超时

任期号（Term）：
  - 单调递增的逻辑时钟
  - 每次选举增加
  - 用于检测过期信息
```

**Raft Leader 选举流程图**：

```text
┌──────────────────────────────────────────────────────────┐
│                    Raft Leader 选举                       │
│                                                          │
│  初始状态：3 个节点（N1, N2, N3）都是 Follower             │
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │
│  │   N1    │  │   N2    │  │   N3    │                  │
│  │Follower │  │Follower │  │Follower │                  │
│  │ term=1  │  │ term=1  │  │ term=1  │                  │
│  └────┬────┘  └─────────┘  └─────────┘                  │
│       │                                                  │
│       │ 选举超时（150ms）                                 │
│       ↓                                                  │
│  ┌─────────┐                                             │
│  │   N1    │                                             │
│  │Candidate│                                             │
│  │ term=2  │                                             │
│  └────┬────┘                                             │
│       │                                                  │
│       │ RequestVote(term=2, lastLogIndex=0)              │
│       ├──────────────────────→ N2                        │
│       └──────────────────────→ N3                        │
│                                                          │
│  N2, N3 投票（term=2 未投票过）                            │
│       │                                                  │
│       │ ← VoteGranted(term=2)                            │
│       │ ← VoteGranted(term=2)                            │
│       │                                                  │
│       │ 收到 2/3 投票（多数派）                            │
│       ↓                                                  │
│  ┌─────────┐                                             │
│  │   N1    │                                             │
│  │ Leader  │                                             │
│  │ term=2  │                                             │
│  └────┬────┘                                             │
│       │                                                  │
│       │ 发送心跳（AppendEntries）                         │
│       ├──────────────────────→ N2                        │
│       └──────────────────────→ N3                        │
│                                                          │
│  N2, N3 重置选举超时，成为 Follower                        │
└──────────────────────────────────────────────────────────┘
```

**日志复制流程**：

```text
1. 客户端发送请求到 Leader
2. Leader 将请求追加到本地日志
3. Leader 发送 AppendEntries 请求到 Follower
4. Follower 追加日志到本地
5. Leader 等待多数派确认
6. Leader 提交日志，应用到状态机
7. Leader 返回响应给客户端

安全性保证：
  - 日志匹配：如果两个日志在相同索引位置的条目任期号相同，
    则它们存储相同的命令
  - Leader 完整性：已提交的日志条目不会丢失
```

**Raft 伪代码**：

```python
class RaftNode:
    def __init__(self, id):
        self.id = id
        self.state = 'FOLLOWER'
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        
        # Leader 状态
        self.next_index = {}
        self.match_index = {}
        
        # 定时器
        self.election_timeout = random.randint(150, 300)
        self.heartbeat_interval = 50
    
    def start_election(self):
        self.current_term += 1
        self.state = 'CANDIDATE'
        self.voted_for = self.id
        votes = 1  # 自己投自己
        
        for node in other_nodes:
            response = node.request_vote(
                self.current_term,
                self.id,
                len(self.log) - 1,
                self.log[-1].term if self.log else 0
            )
            if response.granted:
                votes += 1
        
        if votes > len(all_nodes) // 2:
            self.become_leader()
    
    def become_leader(self):
        self.state = 'LEADER'
        for node in other_nodes:
            self.next_index[node.id] = len(self.log)
            self.match_index[node.id] = 0
    
    def append_entries(self, entries):
        if self.state != 'LEADER':
            return False
        
        # 追加到本地日志
        self.log.extend(entries)
        
        # 发送给 Follower
        successes = 1
        for node in other_nodes:
            response = node.append_entries(
                self.current_term,
                self.id,
                self.commit_index,
                entries
            )
            if response.success:
                successes += 1
        
        # 检查是否多数派确认
        if successes > len(all_nodes) // 2:
            self.commit_index = len(self.log) - 1
            return True
        return False

class Follower:
    def request_vote(self, term, candidate_id, last_log_index, last_log_term):
        if term > self.current_term:
            self.current_term = term
            self.state = 'FOLLOWER'
            self.voted_for = None
        
        if term < self.current_term:
            return VoteResponse(granted=False)
        
        if self.voted_for is None or self.voted_for == candidate_id:
            # 检查候选人的日志是否至少和自己一样新
            if last_log_term > self.log[-1].term or \
               (last_log_term == self.log[-1].term and 
                last_log_index >= len(self.log) - 1):
                self.voted_for = candidate_id
                return VoteResponse(granted=True)
        
        return VoteResponse(granted=False)
    
    def append_entries(self, term, leader_id, commit_index, entries):
        if term < self.current_term:
            return AppendResponse(success=False)
        
        self.current_term = term
        self.state = 'FOLLOWER'
        self.log.extend(entries)
        self.commit_index = max(self.commit_index, commit_index)
        
        return AppendResponse(success=True)
```

**优缺点**：

| 优点 | 缺点 |
|------|------|
| 易于理解和实现 | 只能处理 Fail-stop 故障 |
| 性能优于 Paxos | 不支持拜占庭故障 |
| 强一致性保证 | Leader 是单点（虽有选举恢复） |
| 工程实现成熟 | 需要精确的时钟（超时机制） |

---

## 🧠 Gossip 协议

### 核心思想

Gossip（谣言传播）是一种最终一致性的分布式协议，节点通过随机选择邻居交换信息，最终所有节点达到一致。

**两种模式**：
1. **反熵（Anti-Entropy）**：定期交换完整状态，修复不一致
2. **谣言传播（Rumor Mongering）**：新事件快速传播，类似谣言

**反熵流程**：

```text
1. 节点 A 随机选择节点 B
2. A 发送自己的状态摘要（如 Merkle Tree）给 B
3. B 比较差异，返回缺失的数据
4. A 和 B 交换缺失的数据
5. 重复上述过程，最终所有节点一致

优点：
  - 容忍节点故障和网络分区
  - 最终一致性保证
  - 适合大规模集群

缺点：
  - 收敛速度慢（O(log N) 轮）
  - 只保证最终一致，非强一致
  - 网络开销较大
```

**Gossip 伪代码**：

```python
class GossipNode:
    def __init__(self, id, state):
        self.id = id
        self.state = state  # 本地状态
        self.peers = []
    
    def gossip_round(self):
        # 随机选择一个 peer
        peer = random.choice(self.peers)
        
        # 发送自己的状态
        peer.receive_state(self.state)
    
    def receive_state(self, remote_state):
        # 合并状态（取最新版本或合并）
        self.state = merge(self.state, remote_state)
    
    def anti_entropy(self):
        # 反熵：定期与随机 peer 交换完整状态
        while True:
            self.gossip_round()
            time.sleep(ANTI_ENTROPY_INTERVAL)
    
    def rumor_mongering(self, event):
        # 谣言传播：新事件快速扩散
        for _ in range(RUMOR_ROUNDS):
            peer = random.choice(self.peers)
            peer.receive_event(event)
```

**优缺点**：

| 优点 | 缺点 |
|------|------|
| 高度容错 | 只保证最终一致 |
| 去中心化，无单点 | 收敛速度慢 |
| 适合大规模集群 | 网络开销较大 |
| 动态成员变化容易 | 不适合需要强一致的场景 |

---

## 🛠️ 实际配置：Etcd

Etcd 是基于 Raft 的分布式 KV 存储，广泛用于 Kubernetes。

**集群配置示例**：

```bash
# 节点 1
etcd --name node1 \
     --data-dir /var/lib/etcd/node1 \
     --listen-client-urls http://0.0.0.0:2379 \
     --advertise-client-urls http://192.168.1.1:2379 \
     --listen-peer-urls http://0.0.0.0:2380 \
     --initial-advertise-peer-urls http://192.168.1.1:2380 \
     --initial-cluster node1=http://192.168.1.1:2380,node2=http://192.168.1.2:2380,node3=http://192.168.1.3:2380 \
     --initial-cluster-token etcd-cluster-1 \
     --initial-cluster-state new

# 节点 2
etcd --name node2 \
     --data-dir /var/lib/etcd/node2 \
     --listen-client-urls http://0.0.0.0:2379 \
     --advertise-client-urls http://192.168.1.2:2379 \
     --listen-peer-urls http://0.0.0.0:2380 \
     --initial-advertise-peer-urls http://192.168.1.2:2380 \
     --initial-cluster node1=http://192.168.1.1:2380,node2=http://192.168.1.2:2380,node3=http://192.168.1.3:2380 \
     --initial-cluster-token etcd-cluster-1 \
     --initial-cluster-state new

# 节点 3
etcd --name node3 \
     --data-dir /var/lib/etcd/node3 \
     --listen-client-urls http://0.0.0.0:2379 \
     --advertise-client-urls http://192.168.1.3:2379 \
     --listen-peer-urls http://0.0.0.0:2380 \
     --initial-advertise-peer-urls http://192.168.1.3:2380 \
     --initial-cluster node1=http://192.168.1.1:2380,node2=http://192.168.1.2:2380,node3=http://192.168.1.3:2380 \
     --initial-cluster-token etcd-cluster-1 \
     --initial-cluster-state new
```

**关键参数**：

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `--heartbeat-interval` | 心跳间隔（ms） | 100-500 |
| `--election-timeout` | 选举超时（ms） | 1000-5000 |
| `--snapshot-count` | 触发快照的提交数 | 10000 |
| `--max-snapshots` | 保留的最大快照数 | 5 |

---

## 🛠️ 实际配置：Consul

Consul 是 HashiCorp 出品的服务发现与配置工具，使用 Raft 共识。

**集群配置示例**：

```json
// node1.json
{
  "node_name": "node1",
  "data_dir": "/var/lib/consul",
  "bind_addr": "192.168.1.1",
  "server": true,
  "bootstrap_expect": 3,
  "retry_join": ["192.168.1.2", "192.168.1.3"],
  "raft_protocol": 3,
  "performance": {
    "raft_multiplier": 1
  }
}

// node2.json
{
  "node_name": "node2",
  "data_dir": "/var/lib/consul",
  "bind_addr": "192.168.1.2",
  "server": true,
  "bootstrap_expect": 3,
  "retry_join": ["192.168.1.1", "192.168.1.3"]
}

// node3.json
{
  "node_name": "node3",
  "data_dir": "/var/lib/consul",
  "bind_addr": "192.168.1.3",
  "server": true,
  "bootstrap_expect": 3,
  "retry_join": ["192.168.1.1", "192.168.1.2"]
}
```

**启动命令**：

```bash
consul agent -config-file=node1.json
```

---

## ⚠️ 故障场景分析

### 1. 网络分区（Network Partition）

```text
场景：
  3 节点集群（N1, N2, N3），N1 和 N2 之间网络不通

影响（Raft）：
  - 如果 N1 是 Leader：
    - N1 无法复制日志到 N2，但可以复制到 N3
    - N1 仍然是 Leader（有 2/3 多数派）
    - N2 超时后发起选举，但无法获得多数派（只有 N2 自己）
    - 系统继续可用，但 N2 无法参与
  
  - 如果 N2 是 Leader：
    - 同理，N1 无法参与，N2 和 N3 继续工作

CAP 定理：
  Raft 选择 CP（一致性 + 分区容忍），牺牲可用性
  少数派节点无法提供服务
```

### 2. 节点宕机（Node Failure）

```text
场景：
  3 节点集群，1 个节点宕机

影响（Raft）：
  - 如果宕机的是 Follower：
    - 系统继续工作（2/3 多数派）
    - Leader 继续处理请求
    - 宕机节点恢复后，通过日志复制追上进度
  
  - 如果宕机的是 Leader：
    - Follower 超时后发起选举
    - 存活的 Follower 选出新 Leader
    - 选举期间（几秒）系统不可用

容错能力：
  - 3 节点集群：容忍 1 个节点故障
  - 5 节点集群：容忍 2 个节点故障
  - N 节点集群：容忍 (N-1)/2 个节点故障
```

### 3. 脑裂（Split Brain）

```text
场景：
  网络分区导致两个分区都声称自己是 Leader

Raft 防御机制：
  1. 任期号（Term）：
     - 每个 Leader 有唯一的任期号
     - Follower 只接受任期号更大的 Leader
     - 旧 Leader 发现更高任期号后自动退位
  
  2. 多数派 quorum：
     - 只有获得多数派投票的才能成为 Leader
     - 网络分区时，只有一个分区能获得多数派
     - 另一个分区无法选出 Leader

Paxos 防御机制：
  - 类似 Raft，通过提案编号和多数派 quorum 防止脑裂
```

### 4. 时钟漂移（Clock Drift）

```text
场景：
  节点之间时钟不同步，导致超时判断错误

影响：
  - 选举超时不准确
  - 心跳检测误判
  - 可能导致不必要的选举

解决方案：
  1. 使用 NTP 同步时钟
  2. Raft 使用随机化超时（150-300ms）
  3. 不依赖绝对时间，使用相对时间（心跳计数）
```

---

## 📊 3 大算法对比表

| 算法 | 一致性 | 性能 | 复杂度 | 容错 | 适用场景 |
|------|--------|------|--------|------|---------|
| **Paxos** | 强一致 | 中 | 高 | 多数派 | 理论完备，工程实现少 |
| **Raft** | 强一致 | 高 | 中 | 多数派 | Etcd / Consul / 工程首选 |
| **Gossip** | 最终一致 | 低 | 低 | 任意 | Cassandra / 大规模集群 |

---

## 🔗 相关章节

- [Paxos 详解](paxos/README.md) — Basic Paxos / Multi Paxos 深入推导
- [Raft 详解](raft/README.md) — Leader 选举 / 日志复制 / 安全性证明
- [Gossip 详解](gossip/README.md) — 反熵 / 谣言传播 / Merkle Tree
- [分布式事务](../distributed-transaction/README.md) — 2PC / 3PC / TCC

---

← [返回: 分布式系统](../README.md)

