#!/bin/bash

# 定义一个函数，用于解除端口绑定
release_port() {
  container=$1
  port=$2
  while true; do
    PID=$(docker exec $container lsof -ti :$port)
    if [ ! -z "$PID" ]; then
      echo "Stopping process $PID in $container using port $port"
      docker exec $container kill $PID
      sleep 1 # 等待进程完全停止
    else
      echo "Port $port is free in $container"
      break
    fi
  done
}

# 清空 etcd 数据目录的函数
clear_etcd_data() {
  container=$1
  echo "Clearing etcd data directory in $container"
  docker exec $container rm -rf /expr/data/
}

# 获取所有运行中的容器
CONTAINERS=$(docker ps --format '{{.Names}}')

# 检查每个容器的2380和2379端口并解除绑定
for container in $CONTAINERS; do
  release_port $container 2380
  release_port $container 2379
done

echo "All containers have free ports."

# #!/bin/bash

# # 定义一个函数，用于解除端口绑定
# release_port() {
#   container=$1
#   port=$2
#   while true; do
#     PID=$(docker exec $container lsof -ti :$port)
#     if [ ! -z "$PID" ]; then
#       echo "Stopping process $PID in $container using port $port"
#       docker exec $container kill $PID
#       sleep 1 # 等待进程完全停止
#     else
#       echo "Port $port is free in $container"
#       break
#     fi
#   done
# }

# # 获取所有运行中的容器
# CONTAINERS=$(docker ps --format '{{.Names}}')

# # 检查每个容器的2380端口并解除绑定
# for container in $CONTAINERS; do
#   release_port $container 2380
# done

# echo "All containers have free ports."

  
# #   # 检查2379端口
# #   PID=$(docker exec $container lsof -ti :2379)
# #   if [ ! -z "$PID" ]; then  
# #     docker exec ${container} kill ${PID}
# #   fi
# # done

# # 清空etcd数据目录
# for container in ${CONTAINERS[@]}
# do
#   # docker exec ${container} kill -9 `pidof glee-etcd`
#   echo ${container}
#   docker exec ${container} rm -rf /expr/data/
# done

