# Docker

## linux docker 安装
1. 检查内核版本，返回的值大于3.10即可`uname -r`
2. 使用root权限的用户登入终端
3. 确保yum是最新的`yum update`
4. 安装依赖环境`yum install -y yum-utils device-mapper-persistent-data lvm2`
5. 安装docker-ce(社区版)`yum install -y docker-ce`  安装成功后，可以使用`docker version`命令查看是否安装成功
6. 启动docker`service docker start`或者`systemctl start docker`
7. 验证启动是否成功可使用命令`docker images`
8. 设置开机自启动`systemctl enable docker`

## 查看容器名和对应ip
```shell
docker inspect -f '{{.Name}} - {{.NetworkSettings.IPAddress }}' $(docker ps -aq)
```

## 修改容器参数添加自启动
```shell
docker container update --restart=always 容器名字
#no - Container不重启
#on-failure - container推出状态非0时重启
#always - 始终重启
```

## Nginx
```shell
docker run -d -p 80:80 --name mynginx nginx
docker cp mynginx:/etc/nginx/conf.d/default.conf path
docker stop mynginx
docker rm mynginx
docker run -p 80:80 --name mynginx -v path/log/:/var/log/nginx -v path/default.conf:/etc/nginx/conf.d/default.conf -v path/html/:/usr/share/nginx/html -d nginx
```

## Java
```shell
docker run -p 8080:8080 --name myjava -v path/jarname.jar:/usr/jarname.jar java java -jar /usr/jarname.jar
```

## Redis
```shell
docker run -p 6379:6379 --name myredis -d  redis --requirepass "mypassword"
```

## Sqlserver
```shell
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=mypassword" -p 1433:1433 --name mssql -d microsoft/mssql-server-linux
```

## mysql
```shell
docker run -p 3306:3306 --name my-mysql -e MYSQL_ROOT_PASSWORD=123456 -d mysql:latest

# -p 3306:3306：指定宿主机端口与容器端口映射关系
#--name mysql：创建的容器名称
#--restart=always：总是跟随docker启动
#--privileged=true：获取宿主机root权限
#-v /usr/local/mysql/log:/var/log/mysql：映射日志目录，宿主机:容器
#-v /usr/local/mysql/data:/var/lib/mysql：映射数据目录，宿主机:容器
#-v /usr/local/mysql/conf:/etc/mysql：映射配置目录，宿主机:容器
#-v /etc/localtime:/etc/localtime:ro：让容器的时钟与宿主机时钟同步，避免时区的问题，ro是read only的意思，就是只读。
#-e MYSQL_ROOT_PASSWORD=123456：指定mysql环境变量，root用户的密码为123456
#-d mysql:latest：后台运行mysql容器，版本是latest。
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

## rabbitMQ
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

## Zookeper
```shell
docker run --name zookeeper -d -p 2181:2181 zookeeper:latest
```


## postgreSQL
```shell
docker run --name postgres -e POSTGRES_PASSWORD=Abc1234% -p 5432:5432 -v /home/zx/postgres/data:/var/lib/postgresql/data -d postgres
# --name postgres：指定容器的名称；
# -e POSTGRES_PASSWORD=Abc1234%：设置环境变量，这里为设定PostgreSQL数据库的密码；
# -p 5432:5432：指定端口映射，前者为宿主机访问端口，后者为容器内端口。如果不指定端口映射，只有在容器内可以访问数据库，外部是无法访问的；
# -v /home/zx/postgres/data:/var/lib/postgresql/data：v是volume的简写，即绑定一个卷，冒号前的路径为宿主机的路径（如果指定路径不存在会自动创建目录），冒号后为容器内路径。容器会把宿主机的目录映射到容器内的路径，这样容器运行中生成的数据实际上就是写到了宿主机的指定路径上，即使容器删除了，此路径的文件也不会删除，这样就做到了数据库的持久化存储。还可以通过docker volume提供的相关命令显式地创建volume，然后再挂载到容器上，这里不做介绍，请自行查询相关内容；
# -d：表示后台运行容器；
# postgres：表示镜像的名称，docker基于上步拉取的镜像创建出容器；
```

## onlyoffice
```shell
docker run --name onlyoffice -i -t -d -p 80:80 -e JWT_SECRET=my_jwt_secret -e onlyoffice/documentserver-de
#如果需要关闭使用JWT
docker run --name onlyoffice -i -t -d -p 80:80 -e JWT_ENABLED=false -e ALLOW_PRIVATE_IP_ADDRESS=true onlyoffice/documentserver-de
```
访问控制台`http://127.0.0.1`

## LibreOffice Online
```shell
#安装并启动docker版本lool
docker run --name lool -e "username=admin" -e "password=123456" -e "domain=your\\.cloud\\.domain" -e "extra_params=--o:ssl.enable=false --o:storage.filesystem[@allow]=true" -v D:/lool:/srv/data:Z -p 9980:9980 -d libreoffice/online

# extra_params=--o:ssl.enable=false 关闭ssl
# --o:storage.filesystem[@allow]=true 允许读取本地文件
# domain=your\\.cloud\\.domain 与许方文文件服务域名
# 测试可以可以设置.*允许所有地址
```
访问控制台`http://127.0.0.1:9980/loleaflet/dist/admin/admin.html`

## Collabora Online
```shell
docker run -t -d --name code -e "username=admin" -e "password=123456" -e "aliasgroup1=http://10.133.61.38:8090" -e "extra_params=--o:ssl.enable=false" -p 9980:9980 collabora/code

# extra_params=--o:ssl.enable=false 关闭ssl
# aliasgroup1=http://10.133.61.38:8090 配置允许wopi访问地址
```
访问控制台`http://127.0.0.1:9980/browser/dist/admin/admin.html`

## MinIO
```shell
docker run -p 9000:9000 -p 9001:9001 --name minio -e "MINIO_ROOT_USER=ROOTUSER" -e "MINIO_ROOT_PASSWORD=12345678" quay.io/minio/minio server /data --console-address ":9001"
```
访问控制台`http://127.0.0.1:9001`
用户名 ROOTUSER 密码 12345678


## Alist
```shell
# docker安装
docker run -d --restart=always -v /etc/alist:/opt/alist/data -p 5244:5244 -e PUID=0 -e PGID=0 -e UMASK=022 --name="alist" xhofe/alist:latest
# 查看用户名和密码
docker exec -it alist ./alist admin
```

## chroma
```shell
docker run -it --rm --name chroma -p 8000:8000 ghcr.io/chroma-core/chroma:1.0.0
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

Open WebUI
```shell
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui
```

## 01 [docker-compose 示例](docker-compose%2FREADME.md)