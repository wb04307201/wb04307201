# MAC（Mandatory Access Control，强制访问控制）

> 一句话定位：MAC 用主体与客体的密级标签做强制裁决，所有者不能自主转让权限。

## 1. 概念与起源

**MAC（强制访问控制）** 与 DAC 的根本区别在于：**权限不由资源所有者决定，而由系统按"密级标签"强制裁决**。每个主体和客体都被赋予一个安全级别（如"绝密 / 机密 / 秘密 / 公开"），访问能否发生取决于双方级别的数学关系。

- **历史背景**：1970 年代由美国国防部为多级安全（MLS, Multi-Level Security）系统设计。理论奠基是 **Bell-LaPadula 模型（1973）**（保密性）与 **Biba 模型（1977）**（完整性）。
- **核心思想**：系统强制执行"无上读、无下写"（BLP）或"无下读、无上写"（Biba）这类不变量，主体无法绕过。

**与 DAC 的关键区别**：DAC 中所有者可"自主"转让权限；MAC 中即使你是资源所有者，也不能把"绝密"文件授予"公开"级别的主体——系统会拒绝。

## 2. 核心模型图

```text
            ┌───────────────────────────────┐
            │   密级标签（Label）            │
            │                               │
主体 S ────▶│ Clearance: 机密                │
            │                               │
客体 O ────▶│ Classification: 秘密            │
            │                               │
            │ BLP 规则: Clearance ≥ Class    │
            │ → 允许读                      │
            └───────────────────────────────┘
```

### Bell-LaPadula（保密性）

- **No Read Up（NRU）**：主体只能读 ≤ 自己密级的客体（防止高级别信息泄露给低级别主体）
- **No Write Down（NWD）**：主体只能写 ≥ 自己密级的客体（防止高级别主体把信息"下沉"给低级别客体）

### Biba（完整性）

- **No Read Down（NRD）**：主体只能读 ≥ 自己密级的客体（防止低完整性数据污染高完整性主体）
- **No Write Up（NWU）**：主体只能写 ≤ 自己密级的客体（防止高完整性主体被低完整性数据污染）

## 3. 表/数据结构

```sql
-- 主体（含安全许可级别）
CREATE TABLE mac_subject (
    id        BIGINT PRIMARY KEY AUTO_INCREMENT,
    username  VARCHAR(64) NOT NULL,
    clearance INT NOT NULL,             -- 安全许可级别，数值越大越高级
    -- 1=公开, 2=秘密, 3=机密, 4=绝密
);

-- 客体（含密级）
CREATE TABLE mac_object (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    name          VARCHAR(128) NOT NULL,
    classification INT NOT NULL,        -- 客体密级
);

-- 访问决策（通常不需要这张表，决策由函数实时计算）
-- 若需审计可加：
CREATE TABLE mac_audit (
    id         BIGINT PRIMARY KEY AUTO_INCREMENT,
    subject_id BIGINT,
    object_id  BIGINT,
    action     VARCHAR(16),
    decision   VARCHAR(8),  -- PERMIT / DENY
    ts         TIMESTAMP
);
```

## 4. 代码/伪代码示例

```java
public class MacEngine {

    /**
     * BLP 决策：能否 "读" 客体
     */
    public boolean canRead(MacSubject subject, MacObject object) {
        // No Read Up: 主体 clearance ≥ 客体 classification
        return subject.getClearance() >= object.getClassification();
    }

    /**
     * BLP 决策：能否 "写" 客体
     */
    public boolean canWrite(MacSubject subject, MacObject object) {
        // No Write Down: 主体 clearance ≤ 客体 classification
        return subject.getClearance() <= object.getClassification();
    }
}
```

### 现实例子：SELinux

```bash
# SELinux 是 Linux 内核的 MAC 实现
# 给文件打标签
chcon -t httpd_sys_content_t /var/www/html/index.html

# 给进程（主体）授权
setsebool -P httpd_read_user_content 1
```

## 5. 优缺点

**优点**:
- **安全性最强**：系统强制执行，主体无法绕过
- **抗木马**：即使主体被植入木马，也无法读取更高密级信息
- **可证明性**：基于形式化模型（BLP/Biba），可通过数学证明安全性
- **合规友好**：满足军方、政务、金融的高安全要求

**缺点**:
- **实现工作量大**：每个主体/客体都要打标签
- **灵活性差**：新增业务维度（如"只能编辑自己创建的文档"）需新增标签维度
- **运维成本高**：用户无法自助授权，所有授权需走流程
- **不适合互联网产品**：用户量级大、场景多变，标签管理会爆炸

## 6. 适用与不适用场景

**适用**:
- 军事 / 政务系统的涉密数据
- 金融核心系统的"四类用户"分级
- 医疗系统的 HIPAA 合规
- SELinux / AppArmor 等操作系统级强制访问控制

**不适用**:
- 互联网产品的 C 端用户（量级与灵活度不匹配）
- 协作型 SaaS（用户需要自主分享）
- 快速迭代的内部业务系统（标签跟不上变化）
- 需要"按时间/IP 限制访问"的场景（用 ABAC）

## 相关章节

- 族内：[DAC](dac.md) — DAC 与 MAC 是访问控制的两条根本路线
- 05-security 主题：[加密与密钥管理](../../encryption/README.md) — 加密是 MAC 之外的另一道防线
- 05-security 主题：[OWASP Top 10](../../owasp-top10/README.md) — A01 失效的访问控制
