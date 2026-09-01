<!--
module:
  parent: tools
  slug: tools/docker-images
  type: article
  category: 主模块子文章
  summary: 常用中间件 Docker 镜像一键部署（Nginx/MySQL/Redis/MinIO 等 15+）
  depth: ⭐
-->

# Docker 镜像

> **Docker 镜像 = 15+ 常用中间件一键部署脚本集**

---

## Web 服务器

### Nginx
<!-- -d: 后台运行; -p 80:80: 端口映射; -v: 挂载日志/配置/HTML 目录 -->
```shell
docker run -d -p 80:80 --name mynginx nginx
docker cp mynginx:/etc/nginx/conf.d/default.conf path
docker stop mynginx
docker rm mynginx
docker run -p 80:80 --name mynginx -v path/log/:/var/log/nginx -v path/default.conf:/etc/nginx/conf.d/default.conf -v path/html/:/usr/share/nginx/html -d nginx
```

### Java
<!-- -v: 挂载 JAR 包到容器; 生产建议用 eclipse-temurin:17-jre 替代通用 java 镜像 -->
```shell
docker run -p 8080:8080 --name myjava -v path/jarname.jar:/usr/jarname.jar java java -jar /usr/jarname.jar
```

## 数据库

### Redis
<!-- -d: 后台运行; --requirepass: 设置密码; 生产建议加 -v 持久化 RDB/AOF -->
```shell
docker run -p 6379:6379 --name myredis -d  redis --requirepass "mypassword"
```

### Sqlserver
<!-- ACCEPT_EULA=Y: 接受许可协议; SA_PASSWORD: sysadmin 密码（需满足强密码策略） -->
```shell
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=mypassword" -p 1433:1433 --name mssql -d microsoft/mssql-server-linux
```

### mysql
```shell
docker run -p 3306:3306 --name my-mysql -e MYSQL_ROOT_PASSWORD=123456 -d mysql:8.0

# -p 3306:3306：指定宿主机端口与容器端口映射关系
#--name mysql：创建的容器名称
#--restart=always：总是跟随docker启动
#--privileged=true：获取宿主机root权限
#-v /usr/local/mysql/log:/var/log/mysql：映射日志目录，宿主机:容器
#-v /usr/local/mysql/data:/var/lib/mysql：映射数据目录，宿主机:容器
#-v /usr/local/mysql/conf:/etc/mysql：映射配置目录，宿主机:容器
#-v /etc/localtime:/etc/localtime:ro：让容器的时钟与宿主机时钟同步，避免时区的问题，ro是read only的意思，就是只读。
#-e MYSQL_ROOT_PASSWORD=123456：指定mysql环境变量，root用户的密码为123456
#-d mysql:8.0：后台运行mysql容器（固定版本号，避免 latest 带来的不可预期升级）
#
#进入docker-mysql容器
#docker exec -it  mysql /bin/bash
#连接mysql服务端
#mysql -u root -p
#
#use mysql;
#alter user 'root'@'%' identified with caching_sha2_password by 'Hongqi@20230906%mysql';
#flush privileges;
```

## 消息队列

### rabbitMQ
<!-- -p 15672: 管理界面端口; -p 5672: AMQP 协议端口; 建议用 rabbitmq:management 标签自带管理插件 -->
```shell
docker run -d --hostname my-rabbit --name rabbit -p 15672:15672 -p 5672:5672 rabbitmq

#用户名/密码 guest/guest
#安装管理插件
#	• 进入容器内部
#docker exec -it rabbit /bin/bash
#docker exec -it 1114cd9fcb59 /bin/bash
#	• 安装插件
#rabbitmq-plugins enable rabbitmq_management
#	• 查看插件情况
#rabbitmq-plugins list
```

### Zookeeper
<!-- -p 2181: 客户端连接端口; 生产建议加 -v 持久化 data 和 datalog 目录 -->
```shell
docker run --name zookeeper -d -p 2181:2181 zookeeper:3.9
```


### postgreSQL
```shell
docker run -p 5432:5432 --name my-postgres -e POSTGRES_PASSWORD=123456 -d postgres:16
# --name postgres：指定容器的名称；
# -e POSTGRES_PASSWORD=123456：设置环境变量，这里为设定PostgreSQL数据库的密码；
# -p 5432:5432：指定端口映射，前者为宿主机访问端口，后者为容器内端口。如果不指定端口映射，只有在容器内可以访问数据库，外部是无法访问的；
# -v /home/zx/postgres/data:/var/lib/postgresql/data：v是volume的简写，即绑定一个卷，冒号前的路径为宿主机的路径（如果指定路径不存在会自动创建目录），冒号后为容器内路径。容器会把宿主机的目录映射到容器内的路径，这样容器运行中生成的数据实际上就是写到了宿主机的指定路径上，即使容器删除了，此路径的文件也不会删除，这样就做到了数据库的持久化存储。还可以通过docker volume提供的相关命令显式地创建volume，然后再挂载到容器上，这里不做介绍，请自行查询相关内容；
# -d：表示后台运行容器；
# postgres：表示镜像的名称，docker基于上步拉取的镜像创建出容器；
```

### Redis Stack
<!-- Redis 增强版，含 RediSearch/RedisJSON/RedisTimeSeries 等模块 -->
```shell
docker run -d --name redis-stack -p 9379:6379 -e REDIS_ARGS="--requirepass 123456" redis/redis-stack:latest
```

## 办公协作

### onlyoffice
```shell
docker run --name onlyoffice -i -t -d -p 80:80 -e JWT_SECRET=my_jwt_secret onlyoffice/documentserver-de
#如果需要关闭使用JWT
docker run --name onlyoffice -i -t -d -p 80:80 -e JWT_ENABLED=false -e ALLOW_PRIVATE_IP_ADDRESS=true onlyoffice/documentserver-de
```
访问控制台`http://127.0.0.1`

### LibreOffice Online
```shell
#安装并启动docker版本lool
docker run --name lool -e "username=admin" -e "password=123456" -e "domain=your\\.cloud\\.domain" -e "extra_params=--o:ssl.enable=false --o:storage.filesystem[@allow]=true" -v D:/lool:/srv/data:Z -p 9980:9980 -d libreoffice/online

# extra_params=--o:ssl.enable=false 关闭ssl
# --o:storage.filesystem[@allow]=true 允许读取本地文件
# domain=your\\.cloud\\.domain 与许方文文件服务域名
# 测试可以可以设置.*允许所有地址
```
访问控制台`http://127.0.0.1:9980/loleaflet/dist/admin/admin.html`

### Collabora Online
```shell
docker run -t -d --name code -e "username=admin" -e "password=123456" -e "aliasgroup1=http://10.133.61.38:8090" -e "extra_params=--o:ssl.enable=false" -p 9980:9980 collabora/code

# extra_params=--o:ssl.enable=false 关闭ssl
# aliasgroup1=http://10.133.61.38:8090 配置允许wopi访问地址
```
访问控制台`http://127.0.0.1:9980/browser/dist/admin/admin.html`

## 存储

### MinIO
<!-- -p 9000: S3 API 端口; -p 9001: 控制台端口; /data: 数据存储路径 -->
```shell
docker run -p 9000:9000 -p 9001:9001 --name minio -e "MINIO_ROOT_USER=ROOTUSER" -e "MINIO_ROOT_PASSWORD=12345678" quay.io/minio/minio server /data --console-address ":9001"
```
访问控制台`http://127.0.0.1:9001`
用户名 ROOTUSER 密码 12345678


### Alist
<!-- -v /etc/alist: 配置目录挂载; --restart=always: 自动重启; PUID/PGID=0: 以 root 运行 -->
```shell
# docker安装
docker run -d --restart=always -v /etc/alist:/opt/alist/data -p 5244:5244 -e PUID=0 -e PGID=0 -e UMASK=022 --name="alist" xhofe/alist:latest
# 查看用户名和密码
docker exec -it alist ./alist admin
```

## AI 工具

### chroma
<!-- -p 8000: Chroma API 端口; 向量数据库，常用于 RAG 场景 -->
```shell
docker run -d --name chroma -p 8000:8000 ghcr.io/chroma-core/chroma:1.0.0
```

## docker mirrors

### 使用 Docker File
```shell
{
  "registry-mirrors": ["https://registry.dockermirror.com"]
}
```
### 命令行使用配置
```shell
docker pull ubuntu --registry-mirror=https://registry.dockermirror.com
```

### Open WebUI
<!-- -p 3000:8080: 宿主机 3000 映射容器 8080; --add-host: 允许容器访问宿主机 localhost -->
```shell
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui
```

## 注册中心

### Nacos
```shell
# ⚠️ NACOS_AUTH_TOKEN 为 base64 密钥，生产环境请替换为自己的密钥（当前值仅为示例，存在安全风险）
docker run --name nacos-standalone-derby -e MODE=standalone -e NACOS_AUTH_TOKEN=VGhpc0lzTXlDdXN0b21TZWNyZXRLZXkwMTIzNDU2Nzg= -e NACOS_AUTH_IDENTITY_KEY=custom_identity_key -e NACOS_AUTH_IDENTITY_VALUE=custom_identity_value -p 8080:8080 -p 8848:8848 -p 9848:9848 -d nacos/nacos-server:v2.3.2
```

## 搜索引擎

### SearXNG
```shell
docker run -p 6080:8080 --name searxng -d --restart=always -v "${SEARXNG_DATA_DIR:-./SearXNG}:/etc/searxng" -e "BASE_URL=http://localhost:6080/" -e "INSTANCE_NAME=${INSTANCE_NAME:-my-instance}" searxng/searxng:latest
```

## 01 [docker-compose 示例](../../../README.md)

---

- 相关：[docker-compose 组合部署](../docker-compose/README.md) | [Spring Boot 容器化部署](../../../../04.spring-backend/)

← [返回 Docker](../README.md)