# Docker 命令

## 1. 镜像（Image）相关命令

| 命令                                  | 说明                                              |
|-------------------------------------|-------------------------------------------------|
| `docker images`                     | 列出本地所有镜像                                        |
| `docker pull <image>`               | 从仓库拉取镜像（如 `docker pull nginx`）                  |
| `docker build -t <name:tag> .`      | 从 Dockerfile 构建镜像（注意末尾的 `.` 表示构建上下文）            |
| `docker rmi <image>`                | 删除镜像（可加 `-f` 强制删除）                              |
| `docker tag <source> <target>`      | 给镜像打标签（如 `docker tag nginx:latest my-nginx:v1`） |
| `docker save -o <file.tar> <image>` | 将镜像保存为 tar 文件                                   |
| `docker load -i <file.tar>`         | 从 tar 文件加载镜像                                    |

---

## 2. 容器（Container）相关命令

| 命令                                                     | 说明                                                                                                                                                                       |
|--------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `docker ps`                                            | 列出正在运行的容器                                                                                                                                                                |
| `docker ps -a`                                         | 列出所有容器（包括已停止的）                                                                                                                                                           |
| `docker run [OPTIONS] <image>`                         | 创建并启动新容器<br>常用选项：<br> `-d` 后台运行<br> `-p 8080:80` 端口映射<br> `-v /host:/container` 挂载卷<br> `--name my-container` 指定容器名<br> `-it` 交互式终端（如 `docker run -it ubuntu /bin/bash`） |
| `docker start <container>`                             | 启动已停止的容器                                                                                                                                                                 |
| `docker stop <container>`                              | 停止运行中的容器                                                                                                                                                                 |
| `docker restart <container>`                           | 重启容器                                                                                                                                                                     |
| `docker rm <container>`                                | 删除容器（加 `-f` 可强制删除运行中的容器）                                                                                                                                                 |
| `docker exec -it <container> /bin/bash`                | 进入运行中的容器（执行命令）                                                                                                                                                           |
| `docker logs <container>`                              | 查看容器日志（加 `-f` 可实时跟踪）                                                                                                                                                     |
| `docker inspect <container                             | image>`                                                                                                                                                                  | 查看容器或镜像的详细信息（JSON 格式） |
| `docker cp <container>:<path> <local_path>`            | 在容器和本地之间复制文件                                                                                                                                                             |
| `docker container update --restart=always <container>` | 设置容器自动重启(#no - Container不重启 #on-failure - container推出状态非0时重启 #always - 始终重启)                                                                                             |

---

## 3. 网络（Network）相关

| 命令                                                | 说明         |
|---------------------------------------------------|------------|
| `docker network ls`                               | 列出所有网络     |
| `docker network create <name>`                    | 创建自定义网络    |
| `docker network connect <network> <container>`    | 将容器连接到网络   |
| `docker network disconnect <network> <container>` | 断开容器与网络的连接 |
| `docker network rm <network>`                     | 删除网络       |

---

## 4. 卷（Volume）相关

| 命令                                      | 说明     |
|-----------------------------------------|--------|
| `docker volume ls`                      | 列出所有卷  |
| `docker volume create <name>`           | 创建卷    |
| `docker volume rm <name>`               | 删除卷    |
| `docker volume inspect <name>`          | 查看卷详情  |
| `docker run -v <volume_name>:/path ...` | 挂载卷到容器 |

---

## 5. 系统与信息

| 命令                    | 说明                                 |
|-----------------------|------------------------------------|
| `docker info`         | 显示 Docker 系统信息                     |
| `docker version`      | 显示 Docker 客户端和服务器版本                |
| `docker system df`    | 显示磁盘使用情况（镜像、容器、卷等）                 |
| `docker system prune` | 清理未使用的容器、网络、镜像（加 `-a` 可删除所有未使用的镜像） |

---

## 6. Docker Compose（如果安装了）

| 命令                    | 说明                              |
|-----------------------|---------------------------------|
| `docker-compose up`   | 启动服务（默认读取 `docker-compose.yml`） |
| `docker-compose down` | 停止并删除服务                         |
| `docker-compose ps`   | 列出 compose 项目中的容器               |
| `docker-compose logs` | 查看服务日志                          |

> ⚠️ 注意：Docker Compose v2 以后命令变为 `docker compose`（无连字符），如 `docker compose up`

---

### 💡 小技巧

- **批量删除停止的容器**：
  ```bash
  docker container prune
  ```

- **删除所有未使用的镜像**：
  ```bash
  docker image prune -a
  ```

- **进入容器但不创建新进程**（调试用）：
  ```bash
  docker exec -it <container_id> sh
  ```

- **查看容器 IP 地址**：
  ```bash
  docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container>
  ```
  
- **linux docker 安装**：
1. 使用root权限的用户登入终端 
2. 确保yum是最新的`yum update`
3. 安装依赖环境`yum install -y yum-utils device-mapper-persistent-data lvm2`
4. 安装docker-ce(社区版)`yum install -y docker-ce`  安装成功后，可以使用`docker version`命令查看是否安装成功 
5. 启动docker`service docker start`或者`systemctl start docker`
6. 设置开机自启动`systemctl enable docker`

---

如果你有具体使用场景（比如部署 Nginx、MySQL，或构建镜像等），可以告诉我，我可以给出更具体的命令示例！