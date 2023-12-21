#!/bin/bash

# 添加时延的容器
CONTAINERS=(glee1 glee2 glee3)

# 各容器对应的时延
DELAYS=(70ms 60ms 10ms)

# for i in "${!CONTAINERS[@]}"
# do
#     # 获取容器的eth0接口
#    #  eth0=$(docker inspect ${CONTAINERS[$i]} | jq -r '.[0].NetworkSettings.Networks.bridge.EndpointID')
#    #  echo ${eth0}
#    #  eth0=$(docker inspect ${CONTAINERS[$i]} |grep -o '"EndpointID": "[^"]*"' | cut -d'"' -f4)
#    #  echo ${eth0}


#     # 在该接口上添加时延
#    #  tc qdisc add dev ${eth0} root netem delay ${DELAYS[$i]}
# done

# 遍历数组，为每个容器添加延迟
for ((i=0; i<${#CONTAINERS[@]}; i++)); do
    CONTAINER=${CONTAINERS[i]}
    DELAY=${DELAYS[i]}
    echo ${CONTAINER}
    echo ${DELAY}

    #删除存在的时延
    docker exec -it ${CONTAINER} tc qdisc del dev eth0 root

   #  docker exec -it  ${CONTAINER} apt-get update
   #  docker exec -it  ${CONTAINER} apt-get install -y iproute2

    # 使用 docker exec 在容器中执行 tc 命令
    docker exec -it ${CONTAINER} tc qdisc add dev eth0 root netem delay ${DELAY}
done

# docker exec -it glee1 tc qdisc add dev eth0 root netem delay 20ms
