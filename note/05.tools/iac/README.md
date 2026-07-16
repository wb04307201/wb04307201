<!--
module:
  parent: note
  slug: note/tools/iac
  type: article
  category: 主模块子文章
  summary: Infrastructure as Code 四大工具对比——Terraform / Ansible / Pulumi / CDK 与 GitOps 集成
-->

# Infrastructure as Code (IaC)

> 一句话定位：**用代码定义基础设施——声明式、版本化、可复现、可审计**

IaC（基础设施即代码）是云原生时代的基石实践。2026 年，几乎所有生产环境的云资源都通过 IaC 管理——从 Terraform 的 HCL 到 Pulumi 的编程语言原生，从 Ansible 的配置管理到 CDK 的框架抽象。

---

## 📚 核心内容

| 主题 | 内容 | 关键点 |
|------|------|--------|
| 一、核心概念 | 声明式 vs 命令式 / 幂等性 / 漂移检测 | IaC 理论基础 |
| 二、Terraform | HCL / State / Provider / 模块化 | 最广泛使用的 IaC 工具 |
| 三、Ansible | Playbook / Inventory / Role / 幂等模块 | 配置管理之王 |
| 四、Pulumi | 编程语言原生 IaC | TypeScript / Python / Go 写基础设施 |
| 五、CDK / CDKTF | 框架抽象 + 编译为声明式 | AWS CDK / CDK for Terraform |
| 六、工具对比 | 4 大工具横向对比表 | 选型决策 |
| 七、GitOps 集成 | ArgoCD / Flux | IaC + Git 工作流 |
| 八、最佳实践 | 状态锁 / 远程后端 / CI/CD | 生产级实践 |

---

## 一、IaC 核心概念

### 声明式 vs 命令式

| 方式 | 特征 | 代表工具 | 优劣 |
|------|------|---------|------|
| **声明式** | 描述"要什么"，引擎决定"怎么做" | Terraform / Pulumi / CDK | ✅ 幂等 / ❌ 灵活性受限 |
| **命令式** | 描述"怎么做"，逐步执行 | Shell 脚本 / Ansible（部分） | ✅ 灵活 / ❌ 不幂等 |

### 幂等性

```
幂等：无论执行多少次，结果都一致

# 幂等 ✅
resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}
# 无论 terraform apply 几次，实例数始终是 1

# 非幂等 ❌
aws ec2 run-instances --image-id ami-12345 --instance-type t3.micro
# 每次执行都会创建新实例
```

### 漂移检测

```
漂移（Drift）：实际基础设施状态偏离了代码定义的状态

检测方式：
  terraform plan     → 对比 state 与实际资源
  aws config rules   → AWS 原生漂移检测
  driftctl           → 专用漂移检测工具

修复方式：
  terraform apply    → 将实际状态拉回代码定义
  或更新代码匹配实际状态（手动变更后）
```

---

## 二、Terraform

### HCL 语法

```hcl
# main.tf — 声明式定义云资源

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # 远程后端（生产必备）
  backend "s3" {
    bucket         = "my-tf-state"
    key            = "prod/terraform.tfstate"
    region         = "ap-southeast-1"
    dynamodb_table = "tf-lock"          # 状态锁
    encrypt        = true
  }
}

provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = var.instance_type

  tags = {
    Name        = "web-server"
    Environment = var.environment
  }
}

# 变量定义
variable "ami_id" {
  type        = string
  description = "AMI ID for the EC2 instance"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "environment" {
  type    = string
  default = "dev"
}

# 输出
output "instance_ip" {
  value = aws_instance.web.public_ip
}
```

### State 管理

```bash
# 查看状态
terraform state list
terraform state show aws_instance.web

# 移动资源（重构时）
terraform state mv aws_instance.web module.compute.aws_instance.web

# 导入已有资源
terraform import aws_instance.web i-0123456789abcdef0

# 状态锁（防止并发修改）
# S3 + DynamoDB 是最常用的锁机制
```

### Provider 生态

| Provider | 云平台/服务 | 资源数 |
|----------|-----------|--------|
| AWS | Amazon Web Services | 1000+ |
| AzureRM | Microsoft Azure | 800+ |
| Google | Google Cloud | 600+ |
| Kubernetes | K8s 资源 | 50+ |
| Helm | Helm Charts | 2 |
| Alibaba Cloud | 阿里云 | 300+ |

### 模块化

```
terraform/
├── modules/
│   ├── vpc/          # 网络模块
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ecs/          # 计算模块
│   └── rds/          # 数据库模块
├── environments/
│   ├── dev/
│   │   └── main.tf   # 调用 modules
│   └── prod/
│       └── main.tf
└── terraform.tfvars
```

```hcl
# environments/prod/main.tf
module "vpc" {
  source = "../../modules/vpc"

  cidr_block = "10.0.0.0/16"
  azs        = ["ap-southeast-1a", "ap-southeast-1b"]
}

module "ecs" {
  source = "../../modules/ecs"

  vpc_id    = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
}
```

---

## 三、Ansible

### 核心概念

| 概念 | 说明 |
|------|------|
| **Playbook** | YAML 定义的任务编排（一个 Playbook 包含多个 Play） |
| **Inventory** | 目标主机清单（静态文件 / 动态脚本 / Ansible Tower） |
| **Module** | 执行具体操作的单元（yum / copy / service / template） |
| **Role** | 可复用的任务集合（tasks / handlers / templates / vars） |
| **Fact** | 自动收集的目标主机信息（OS / IP / 内存） |

### Playbook 示例

```yaml
# site.yml — 部署 Web 应用
---
- name: Deploy web application
  hosts: webservers
  become: yes
  vars:
    app_version: "2.1.0"
    nginx_port: 80

  tasks:
    - name: Install Nginx
      apt:
        name: nginx
        state: present
        update_cache: yes

    - name: Deploy application
      template:
        src: templates/app.conf.j2
        dest: /etc/nginx/sites-available/app
      notify: restart nginx

    - name: Enable site
      file:
        src: /etc/nginx/sites-available/app
        dest: /etc/nginx/sites-enabled/app
        state: link
      notify: restart nginx

    - name: Ensure Nginx is running
      service:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

### Role 结构

```
roles/
└── web-app/
    ├── tasks/
    │   └── main.yml      # 任务定义
    ├── handlers/
    │   └── main.yml      # 触发器
    ├── templates/
    │   └── app.conf.j2   # Jinja2 模板
    ├── vars/
    │   └── main.yml      # 变量
    ├── defaults/
    │   └── main.yml      # 默认值（最低优先级）
    └── files/
        └── app.tar.gz    # 静态文件
```

---

## 四、Pulumi

### 编程语言原生 IaC

Pulumi 让你用**真正的编程语言**定义基础设施——TypeScript / Python / Go / C#，享受 IDE 补全、类型检查、单元测试。

```typescript
// index.ts — TypeScript 定义 AWS 资源
import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

// VPC
const vpc = new aws.ec2.Vpc("main", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    tags: { Name: "main-vpc" },
});

// EC2 实例
const instance = new aws.ec2.Instance("web", {
    ami: "ami-12345",
    instanceType: "t3.micro",
    subnetId: vpc.publicSubnetIds.then(ids => ids[0]),
    tags: { Name: "web-server" },
});

export const publicIp = instance.publicIp;
```

### Pulumi vs Terraform

| 维度 | Pulumi | Terraform |
|------|--------|-----------|
| 语言 | TS / Python / Go / C# | HCL（DSL） |
| 类型检查 | 原生语言类型系统 | 有限的类型检查 |
| 测试 | 原生单元测试框架 | terratest（Go） |
| 状态管理 | Pulumi Cloud（默认） | 自选后端 |
| 社区 | 增长中 | 最成熟 |
| 学习成本 | 低（用已知语言） | 中（学 HCL） |

---

## 五、CDK / CDKTF

### AWS CDK

```typescript
// AWS CDK — 用 TypeScript 定义 CloudFormation 模板
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'WebStack');

const vpc = new ec2.Vpc(stack, 'Vpc', { maxAzs: 2 });
const cluster = new ecs.Cluster(stack, 'Cluster', { vpc });

new ecs.FargateService(stack, 'Service', {
  cluster,
  taskDefinition: new ecs.FargateTaskDefinition(stack, 'TaskDef', {
    memoryLimitMiB: 512,
  }),
});
```

### CDK for Terraform (CDKTF)

```typescript
// CDKTF — 用 TypeScript 生成 Terraform 配置
import { App, TerraformStack } from 'cdktf';
import { AwsProvider } from '@cdktf/provider-aws/lib/provider';
import { Instance } from '@cdktf/provider-aws/lib/instance';

class MyStack extends TerraformStack {
  constructor(scope: App, id: string) {
    super(scope, id);
    new AwsProvider(this, 'aws', { region: 'ap-southeast-1' });
    new Instance(this, 'web', {
      ami: 'ami-12345',
      instanceType: 't3.micro',
    });
  }
}
```

---

## 六、4 大工具对比表

| 维度 | Terraform | Ansible | Pulumi | CDK / CDKTF |
|------|-----------|---------|--------|-------------|
| **定位** | 基础设施供给 | 配置管理 + 编排 | 基础设施供给 | 基础设施供给 |
| **语言** | HCL (DSL) | YAML | TS/Py/Go/C# | TS/Py/Java/C# |
| **范式** | 声明式 | 混合（声明+命令） | 声明式 | 声明式（编译） |
| **状态** | tfstate 文件 | 无（幂等模块） | Pulumi Cloud | CloudFormation/State |
| **Agent** | 无（API 调用） | 无（SSH/WinRM） | 无（API 调用） | 无 |
| **多云** | ✅ 强（Provider 生态） | ✅ 强 | ✅ 强 | AWS CDK 仅 AWS |
| **学习成本** | 中（学 HCL） | 低（YAML） | 低（已有语言） | 中 |
| **社区生态** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐（AWS） |
| **适用阶段** | 资源供给 | 配置管理 | 资源供给 | 资源供给 |
| **典型组合** | TF + Ansible | 单独 / + TF | 单独 | 单独 |

> 💡 **最佳组合**：Terraform 管资源供给（VPC / ECS / RDS），Ansible 管配置管理（安装软件 / 部署应用），二者通过 Inventory 插件联动。

---

## 七、GitOps 集成

### ArgoCD + Terraform

```
┌──────────┐    push     ┌──────────┐    detect    ┌──────────┐
│ Developer│ ──────────→ │   Git    │ ──────────→  │  ArgoCD  │
│          │             │  Repo    │              │ (K8s)    │
└──────────┘             └──────────┘              └────┬─────┘
                                                        │ sync
                                                   ┌────┴─────┐
                                                   │  K8s     │
                                                   │ Cluster  │
                                                   └──────────┘

GitOps 工作流：
1. 开发者修改 IaC 代码 → push to Git
2. CI pipeline 执行 terraform plan → PR 评论 diff
3. 合并后 terraform apply 创建/更新资源
4. ArgoCD 检测 K8s manifest 变更 → 自动 sync
```

### Flux

```yaml
# Flux Kustomization — 自动同步 IaC 变更
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: infrastructure
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: infra-repo
  path: ./k8s/
  prune: true           # 删除不再定义的 K8s 资源
  validation: client    # 部署前验证
```

---

## 八、最佳实践

| 实践 | 说明 |
|------|------|
| **远程后端** | 状态文件存 S3/GCS/OSS，不要放本地 |
| **状态锁** | S3 + DynamoDB / Consul / Terraform Cloud |
| **模块化** | 按业务域拆 module，可复用 |
| **环境隔离** | dev / staging / prod 独立 state + workspace |
| **CI/CD 集成** | PR 触发 plan，merge 触发 apply |
| **版本锁定** | Provider 版本 + Terraform 版本锁定 |
| **敏感信息管理** | Vault / SSM Parameter / KMS，不硬编码 |
| **代码审查** | plan 输出附加到 PR，人工审批后 apply |
| **漂移检测** | 定期 `terraform plan` 或专用工具 |
| **最小权限** | IaC 使用的 IAM 角色遵循最小权限原则 |

### CI/CD Pipeline 示例

```yaml
# .github/workflows/terraform.yml
name: Terraform CI/CD

on:
  pull_request:
    paths: ['terraform/**']
  push:
    branches: [main]
    paths: ['terraform/**']

jobs:
  plan:
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: terraform plan -out=tfplan
      - uses: actions/upload-artifact@v4
        with:
          name: tfplan
          path: tfplan

  apply:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: terraform apply -auto-approve
```

---

## 🔗 相关章节

- **Docker**：[02-docker](../02-docker/README.md) — 容器化（IaC 管理的核心资源之一）
- **Kubernetes**：[kubernetes](../kubernetes/README.md) — 容器编排（GitOps 的主要目标平台）
- **DevOps**：[devops](../devops/README.md) — CI/CD 工具链（IaC 的执行环境）
- **系统设计**：[04.system-design](../../04.system-design/README.md) — 基础设施架构设计

---

## 📖 开源参考

| 项目 | 说明 | 链接 |
|------|------|------|
| Terraform | HashiCorp IaC 引擎 | [terraform.io](https://www.terraform.io) |
| Ansible | Red Hat 配置管理 | [ansible.com](https://www.ansible.com) |
| Pulumi | 编程语言原生 IaC | [pulumi.com](https://www.pulumi.com) |
| AWS CDK | AWS 云开发框架 | [aws.amazon.com/cdk](https://aws.amazon.com/cdk) |
| ArgoCD | K8s GitOps 控制器 | [argo-cd.readthedocs.io](https://argo-cd.readthedocs.io) |
| Flux | CNCF GitOps 工具 | [fluxcd.io](https://fluxcd.io) |
| driftctl | 漂移检测 | [github.com/snyk/driftctl](https://github.com/snyk/driftctl) |

---

← [返回: 工具链](../README.md)
