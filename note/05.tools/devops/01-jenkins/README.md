# Jenkins · 老牌 CI/CD 工具实战

> 一份按场景梳理的 Jenkins 速查手册：从安装到分布式构建的完整实战。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

Jenkins · 老牌 CI/CD 工具实战 本应该很简单，一份按场景梳理的 Jenkins 速查手册：从安装到分布式构建的完整实战

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、Jenkins 简介

Jenkins 是开源 CI/CD 工具的"鼻祖"，由 Hudson 分支而来，插件生态最丰富（1800+ 插件）。

### 1.1 核心特性

- **插件丰富**：1800+ 插件，覆盖所有 CI/CD 场景
- **Pipeline as Code**：Jenkinsfile 描述流水线
- **分布式构建**：Master-Agent 架构，可扩展到上千节点
- **生态成熟**：大量企业实践案例

### 1.2 适用场景

- ✅ 大型企业 / 复杂流水线
- ✅ 需要自定义插件
- ✅ 自托管（数据敏感）
- ❌ 小团队 / 简单场景（推荐 GitHub Actions）

---

## 二、Jenkins 架构（Master-Agent）

```
┌──────────────────────────────────────────┐
│  Jenkins Master（控制节点）                  │
│  ┌────────────────────────────────┐      │
│  │ - Web UI                        │      │
│  │ - 任务调度                       │      │
│  │ - 插件管理                       │      │
│  │ - 凭证管理                       │      │
│  └────────┬───────────────────────┘      │
│           │ 任务分发                         │
│  ┌────────┼────────┬────────┐              │
│  ↓        ↓        ↓        ↓              │
│ ┌──┐   ┌──┐   ┌──┐   ┌──┐                │
│ │A1│   │A2│   │A3│   │A4│                │
│ └──┘   └──┘   └──┘   └──┘                │
│ Agent   Agent   Agent   Agent             │
└──────────────────────────────────────────┘
```

- **Master**：调度任务 + UI，不执行实际构建
- **Agent**：实际执行构建（容器 / 物理机 / VM）

---

## 三、安装方式

### 3.1 Docker 单机版（快速试用）

```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

### 3.2 K8s 部署（推荐生产）

```bash
# 使用 Helm
helm repo add jenkins https://charts.jenkins.io
helm install jenkins jenkins/jenkins \
  --namespace jenkins --create-namespace

# 暴露 NodePort
kubectl --namespace jenkins get services jenkins
```

### 3.3 自托管（Ubuntu/CentOS）

```bash
# Java 17 安装
sudo apt install openjdk-17-jdk

# Jenkins 安装
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins
```

---

## 四、Jenkinsfile（Pipeline as Code）

### 4.1 声明式 Pipeline（推荐）

```groovy
pipeline {
  agent any

  options {
    timeout(time: 30, unit: 'MINUTES')
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }

  triggers {
    pollSCM('H/5 * * * *')          // 每 5 分钟轮询
  }

  environment {
    DOCKER_REGISTRY = 'registry.example.com'
    APP_NAME = 'myapp'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build') {
      steps {
        sh 'mvn clean package -DskipTests'
      }
    }

    stage('Test') {
      parallel {
        stage('Unit Test') {
          steps {
            sh 'mvn test'
          }
        }
        stage('Integration Test') {
          steps {
            sh 'mvn verify -Pintegration'
          }
        }
      }
    }

    stage('Code Quality') {
      steps {
        sh 'mvn sonar:sonar'
      }
    }

    stage('Build Image') {
      steps {
        script {
          docker.build("${DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}")
        }
      }
    }

    stage('Deploy') {
      when {
        branch 'main'
      }
      steps {
        sh 'kubectl apply -f k8s/'
      }
    }
  }

  post {
    success {
      slackSend(channel: '#deploys', message: "✅ ${APP_NAME} deployed: ${BUILD_NUMBER}")
    }
    failure {
      slackSend(channel: '#alerts', message: "❌ ${APP_NAME} build failed")
    }
  }
}
```

### 4.2 脚本式 Pipeline（灵活）

```groovy
node {
  stage('Build') {
    sh 'mvn clean package'
  }
  stage('Test') {
    try {
      sh 'mvn test'
    } catch (err) {
      currentBuild.result = 'FAILURE'
      throw err
    }
  }
  stage('Deploy') {
    if (env.BRANCH_NAME == 'main') {
      sh 'kubectl apply -f k8s/'
    }
  }
}
```

---

## 五、常用插件

| 类别 | 插件 | 用途 |
|------|------|------|
| **源码** | Git / GitHub / GitLab | 代码拉取 |
| **构建** | Maven / Gradle / NodeJS | 编译 |
| **测试** | JUnit / Cobertura / JaCoCo | 单元测试 + 覆盖率 |
| **代码质量** | SonarQube Scanner | 代码扫描 |
| **镜像** | Docker Pipeline / Kaniko | 镜像构建（无需 Docker daemon） |
| **部署** | Kubernetes CLI / ArgoCD | K8s 部署 |
| **通知** | Slack / Email-ext | 通知 |
| **凭证** | Credentials / HashiCorp Vault | 密钥管理 |
| **流水线** | Pipeline / Blue Ocean | 可视化 |

---

## 六、分布式构建（Master-Agent）

### 6.1 为什么需要 Agent？

- **Master 单点**：单机性能有限
- **环境隔离**：不同 Agent 跑不同环境（Java 8 / Java 17）
- **并行加速**：100 个 Agent 同时跑 100 个任务

### 6.2 添加 Agent

**永久 Agent（推荐）**：

```bash
# Agent 节点（需安装 Java）
java -jar agent.jar -jnlpUrl http://jenkins-master:8080/computer/agent1/slave-agent.jnlp \
  -secret <secret> -workDir "/home/jenkins/agent"
```

**JNLP 动态 Agent（K8s 推荐）**：

Jenkins K8s Plugin 自动为每个 Pipeline 启动 Pod：

```groovy
pipeline {
  agent {
    kubernetes {
      yaml '''
        apiVersion: v1
        kind: Pod
        spec:
          containers:
          - name: maven
            image: maven:3.9
            command:
            - cat
            tty: true
        '''
    }
  }
  stages {
    stage('Build') {
      steps {
        container('maven') {
          sh 'mvn clean package'
        }
      }
    }
  }
}
```

---

## 七、Shared Library（共享库）

把通用函数封装为共享库，多个 Pipeline 复用：

```groovy
// vars/buildJavaApp.groovy
def call() {
  sh 'mvn clean package'
  archiveArtifacts 'target/*.jar'
}
```

```groovy
// Jenkinsfile
@Library('my-shared-library') _

pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        buildJavaApp()
      }
    }
  }
}
```

---

## 八、与 K8s 集成（生产标准）

### 8.1 Jenkins in K8s

- Jenkins Master 部署在 K8s
- 每个 Pipeline 启动 Jenkins Agent Pod
- Job 完成后 Pod 自动销毁

### 8.2 配置 Jenkins K8s Plugin

```
Manage Jenkins → System → Cloud → Kubernetes
- Kubernetes URL: https://kubernetes.default.svc
- Kubernetes Namespace: jenkins
- Jenkins URL: http://jenkins.jenkins.svc.cluster.local:8080
- Connection Timeout: 5
- Jenkins Channel: 50
```

---

## 九、最佳实践

1. **Pipeline as Code**：所有 Jenkinsfile 进 Git，禁止 UI 配置
2. **插件管理**：定期清理不用插件，避免依赖地狱
3. **凭证管理**：用 Credentials Plugin + Vault
4. **备份**：JENKINS_HOME 定期备份（主从都要备份）
5. **升级**：每年升级一次 LTS 版本（升级前备份 + 测试）
6. **监控**：Prometheus 监控 Jenkins 指标
7. **Agent 资源**：分配足够的 CPU / 内存给 Agent

---

← [返回 DevOps 总览](../README.md) · 📅 2026-06-28