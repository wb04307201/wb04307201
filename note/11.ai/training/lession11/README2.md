# 使用 Docker Compose 部署 Dify

## 部署前准备

请确保你的机器满足以下最低系统要求。

### 硬件

* CPU >= 2 Core
* RAM >= 4 GiB

### 软件

| 操作系统                | 所需软件                                          | 说明                                                                                                                                                                           |
| :------------------ | :-------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| macOS 10.14 或更高版本   | Docker Desktop                                | 将 Docker 虚拟机配置为至少 2 个虚拟 CPU 和 8 GiB 内存。<br /><br />安装说明请参阅 [Mac 版 Docker Desktop 安装指南](https://docs.docker.com/desktop/mac/install/)。                                        |
| Linux 平台            | Docker 19.03+<br /><br />Docker Compose 1.28+ | 安装说明请参阅 [Docker 引擎安装指南](https://docs.docker.com/engine/install/) 和 [Docker Compose 安装指南](https://docs.docker.com/compose/install/)。                                          |
| 启用了 WSL 2 的 Windows | Docker Desktop                                | 建议将源代码和绑定到 Linux 容器的数据存储在 Linux 文件系统中，而不是 Windows 文件系统中。<br /><br />安装说明请参阅 [Windows 版 Docker Desktop 安装指南](https://docs.docker.com/desktop/windows/install/#wsl-2-backend)。 |

## Docker Desktop 安装

在部署 Dify 之前，需要先安装 Docker Desktop。

### Windows 系统安装

1. **下载 Docker Desktop**
   - 访问 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
   - 点击下载按钮获取安装包

2. **系统要求**
   - Windows 10 64位：专业版、企业版或教育版（Build 15063 或更高版本）
   - Windows 11 64位：家庭版或专业版（Build 22000 或更高版本）
   - 启用 WSL 2（Windows Subsystem for Linux 2）
   - BIOS 中启用虚拟化功能

3. **安装步骤**
   - 运行下载的 `Docker Desktop Installer.exe`
   - 在安装向导中，确保勾选 "Use WSL 2 instead of Hyper-V" 选项
   - 点击 "OK" 开始安装
   - 安装完成后，点击 "Close and restart" 重启计算机

4. **验证安装**
   ```bash
   docker --version
   docker compose version
   ```

## 部署并启动

### 克隆 Dify
将 Dify 源代码克隆到本地机器。

```bash
git clone https://github.com/langgenius/dify.git
```

### 启动 Dify
1. 导航到 Dify 源代码中的 `docker` 目录：

   ```bash
   cd dify/docker
   ```

2. 复制示例环境配置文件：

   ```bash
   cp .env.example .env  
   ```

3. 根据你的 Docker Compose 版本选择相应命令启动容器：

   ```bash Docker Compose V2
   docker compose up -d
   ```

   > 运行 `docker compose version` 检查你的 Docker Compose 版本。

   将启动以下容器：

   * 5 个核心服务：`api`、`worker`、`worker_beat`、`web`、`plugin_daemon`
   * 6 个依赖组件：`weaviate`、`db_postgres`、`redis`、`nginx`、`ssrf_proxy`、`sandbox`

   你应该会看到类似以下的输出，显示每个容器的状态和启动时间：

     ```bash
     [+] Running 13/13
     ✔ Network docker_ssrf_proxy_network  Created                                                                10.0s 
     ✔ Network docker_default             Created                                                                 0.1s 
     ✔ Container docker-sandbox-1         Started                                                                 0.3s 
     ✔ Container docker-db_postgres-1     Healthy                                                                 2.8s 
     ✔ Container docker-web-1             Started                                                                 0.3s 
     ✔ Container docker-redis-1           Started                                                                 0.3s 
     ✔ Container docker-ssrf_proxy-1      Started                                                                 0.4s 
     ✔ Container docker-weaviate-1        Started                                                                 0.3s 
     ✔ Container docker-worker_beat-1     Started                                                                 3.2s 
     ✔ Container docker-api-1             Started                                                                 3.2s 
     ✔ Container docker-worker-1          Started                                                                 3.2s 
     ✔ Container docker-plugin_daemon-1   Started                                                                 3.2s 
     ✔ Container docker-nginx-1           Started                                                                 3.4s 
     ```

4. 验证所有容器是否成功运行：

   ```bash
   docker compose ps
   ```

   你应该会看到类似以下的输出，每个容器的状态应为 `Up` 或 `healthy`：

     ```bash
     NAME                     IMAGE                                       COMMAND                  SERVICE         CREATED          STATUS                             PORTS
     docker-api-1             langgenius/dify-api:1.10.1                  "/bin/bash /entrypoi…"   api             26 seconds ago   Up 22 seconds                      5001/tcp
     docker-db_postgres-1     postgres:15-alpine                          "docker-entrypoint.s…"   db_postgres     26 seconds ago   Up 25 seconds (healthy)            5432/tcp
     docker-nginx-1           nginx:latest                                "sh -c 'cp /docker-e…"   nginx           26 seconds ago   Up 22 seconds                      0.0.0.0:80->80/tcp, :::80->80/tcp, 0.0.0.0:443->443/tcp, :::443->443/tcp
     docker-plugin_daemon-1   langgenius/dify-plugin-daemon:0.4.1-local   "/bin/bash -c /app/e…"   plugin_daemon   26 seconds ago   Up 22 seconds                      0.0.0.0:5003->5003/tcp, :::5003->5003/tcp
     docker-redis-1           redis:6-alpine                              "docker-entrypoint.s…"   redis           26 seconds ago   Up 25 seconds (health: starting)   6379/tcp
     docker-sandbox-1         langgenius/dify-sandbox:0.2.12              "/main"                  sandbox         26 seconds ago   Up 25 seconds (health: starting)   
     docker-ssrf_proxy-1      ubuntu/squid:latest                         "sh -c 'cp /docker-e…"   ssrf_proxy      26 seconds ago   Up 25 seconds                      3128/tcp
     docker-weaviate-1        semitechnologies/weaviate:1.27.0            "/bin/weaviate --hos…"   weaviate        26 seconds ago   Up 25 seconds                      
     docker-web-1             langgenius/dify-web:1.10.1                  "/bin/sh ./entrypoin…"   web             26 seconds ago   Up 25 seconds                      3000/tcp
     docker-worker-1          langgenius/dify-api:1.10.1                  "/bin/bash /entrypoi…"   worker          26 seconds ago   Up 22 seconds                      5001/tcp
     docker-worker_beat-1     langgenius/dify-api:1.10.1                  "/bin/bash /entrypoi…"   worker_beat     26 seconds ago   Up 22 seconds                      5001/tcp
     ```

## 访问

1. 打开管理员初始化页面以设置管理员账户：

   ```bash
   # 本地环境
   http://localhost/install

   # 服务器环境
   http://your_server_ip/install
   ```

2. 完成管理员账户设置后，在以下地址登录 Dify：

   ```bash
   # 本地环境
   http://localhost  

   # 服务器环境
   http://your_server_ip
   ```

## 自定义

修改本地 `.env` 文件中的环境变量值，然后重启 Dify 以应用更改：

```bash
docker compose down
docker compose up -d
```

> 更多信息请参阅 [环境变量](/zh/self-host/configuration/environments)。

## 升级

不同版本的升级步骤可能有所不同。请参阅 [Releases](https://github.com/langgenius/dify/releases) 页面中提供的目标版本升级指南。

> 升级后，请检查 `.env.example` 文件是否有变更，并相应更新你的本地 `.env` 文件。
