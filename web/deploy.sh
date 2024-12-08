#!/bin/bash

# 获取宿主机的IP地址
HOST_IP=$(hostname -I | awk '{print $1}')

# 如果没有获取到有效的IP地址，则尝试使用ifconfig或ip命令
if [ -z "$HOST_IP" ]; then
  HOST_IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')
fi

if [ -z "$HOST_IP" ]; then
  HOST_IP=$(ip addr show | grep -Po 'inet \K[\d.]+(?=/\d+)' | grep -v '127.0.0.1' | head -n 1)
fi

if [ -z "$HOST_IP" ]; then
  echo "无法获取宿主机的IP地址，请手动设置环境变量 HOST_IP"
  exit 1
fi

# 删除旧的镜像和容器
docker image rm -f redis-config-center:latest || true
docker container rm -f redis-config-center || true

# 构建新的镜像，使用..设置构建路径为../上级目录，即从redis-config-center根路径开始构建
docker build -t redis-config-center:latest  -f Dockerfile ..

# 运行容器并使用宿主机的IP地址替换 localhost
docker run -d \
  -p 8079:8079 \
  --name redis-config-center \
  -e REDIS_URL=$HOST_IP \
  -e REDIS_PORT=6379 \
  -e REDIS_DB=0 \
  -e REDIS_PASSWORD= \
  -e Redis_Config_Center_TYPE=PRODUCTION \
  redis-config-center:latest

echo "使用宿主机 Redis IP 地址: $HOST_IP"

echo "应用已启动，可前往 http://127.0.0.1:8079/ 访问 Redis Config Center Web 服务端管理后台"