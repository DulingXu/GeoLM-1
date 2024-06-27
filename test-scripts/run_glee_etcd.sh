#!/bin/bash

# 确保日志目录存在
docker exec glee1 mkdir -p /expr/data
docker exec glee2 mkdir -p /expr/data
docker exec glee3 mkdir -p /expr/data

# 设置日志目录权限
docker exec glee1 chmod -R 777 /expr/data
docker exec glee2 chmod -R 777 /expr/data
docker exec glee3 chmod -R 777 /expr/data

# 复制编译后的二进制文件到容器中
docker cp ../bin/glee-etcd glee1:/expr/glee-etcd
docker cp ../bin/glee-etcdctl glee1:/expr/glee-etcdctl
docker cp ../bin/glee-etcd glee2:/expr/glee-etcd
docker cp ../bin/glee-etcdctl glee2:/expr/glee-etcdctl
docker cp ../bin/glee-etcd glee3:/expr/glee-etcd
docker cp ../bin/glee-etcdctl glee3:/expr/glee-etcdctl

# 确保 glee-etcd 文件有执行权限
docker exec glee1 chmod +x /expr/glee-etcd
docker exec glee2 chmod +x /expr/glee-etcd
docker exec glee3 chmod +x /expr/glee-etcd

# 启动 glee-etcd 并记录日志
docker exec -d glee1 bash -c '/expr/glee-etcd --data-dir=/expr/data --name infra1 --listen-client-urls http://192.168.37.11:2379 --advertise-client-urls http://192.168.37.11:2379 --listen-peer-urls http://192.168.37.11:2380 --initial-advertise-peer-urls http://192.168.37.11:2380 --initial-cluster-token etcd-cluster-1 --initial-cluster "infra1=http://192.168.37.11:2380,infra2=http://192.168.37.12:2380,infra3=http://192.168.37.13:2380" --initial-cluster-state new --enable-pprof > /expr/data/etcd.log 2>&1 &'

sleep 1

docker exec -d glee2 bash -c '/expr/glee-etcd --data-dir=/expr/data --name infra2 --listen-client-urls http://192.168.37.12:2379 --advertise-client-urls http://192.168.37.12:2379 --listen-peer-urls http://192.168.37.12:2380 --initial-advertise-peer-urls http://192.168.37.12:2380 --initial-cluster-token etcd-cluster-1 --initial-cluster "infra1=http://192.168.37.11:2380,infra2=http://192.168.37.12:2380,infra3=http://192.168.37.13:2380" --initial-cluster-state new --enable-pprof > /expr/data/etcd.log 2>&1 &'

sleep 1

docker exec -d glee3 bash -c '/expr/glee-etcd --data-dir=/expr/data --name infra3 --listen-client-urls http://192.168.37.13:2379 --advertise-client-urls http://192.168.37.13:2379 --listen-peer-urls http://192.168.37.13:2380 --initial-advertise-peer-urls http://192.168.37.13:2380 --initial-cluster-token etcd-cluster-1 --initial-cluster "infra1=http://192.168.37.11:2380,infra2=http://192.168.37.12:2380,infra3=http://192.168.37.13:2380" --initial-cluster-state new --enable-pprof > /expr/data/etcd.log 2>&1 &'


# docker exec -d glee1 /expr/glee-etcd \
# --data-dir=/expr/data \
# --name infra1 \
# --listen-client-urls http://192.168.37.11:2379 \
# --advertise-client-urls http://192.168.37.11:2379 \
# --listen-peer-urls http://192.168.37.11:2380 \
# --initial-advertise-peer-urls http://192.168.37.11:2380 \
# --initial-cluster-token etcd-cluster-1 \
# --initial-cluster 'infra1=http://192.168.37.11:2380,infra2=http://192.168.37.12:2380,infra3=http://192.168.37.13:2380' \
# --initial-cluster-state new \
# --enable-pprof

# sleep 1

# docker exec -d glee2 /expr/glee-etcd --data-dir=/expr/data --name infra2 --listen-client-urls http://192.168.37.12:2379 --advertise-client-urls http://192.168.37.12:2379 --listen-peer-urls http://192.168.37.12:2380 --initial-advertise-peer-urls http://192.168.37.12:2380 --initial-cluster-token etcd-cluster-1 --initial-cluster 'infra1=http://192.168.37.11:2380,infra2=http://192.168.37.12:2380,infra3=http://192.168.37.13:2380' --initial-cluster-state new --enable-pprof

# sleep 1

# docker exec -d glee3 /expr/glee-etcd --data-dir=/expr/data --name infra3 --listen-client-urls http://192.168.37.13:2379 --advertise-client-urls http://192.168.37.13:2379 --listen-peer-urls http://192.168.37.13:2380 --initial-advertise-peer-urls http://192.168.37.13:2380 --initial-cluster-token etcd-cluster-1 --initial-cluster 'infra1=http://192.168.37.11:2380,infra2=http://192.168.37.12:2380,infra3=http://192.168.37.13:2380' --initial-cluster-state new --enable-pprof