CONTAINERS=("glee1" "glee2" "glee3")

PORTS=(2379 2380 2381)

ETCD_DIR="/home/chenzheng/dl"

docker pull ubuntu:20.04

for i in "${!CONTAINERS[@]}"; do
  CONTAINER=${CONTAINERS[$i]}
  PORT=${PORTS[$i]}
  docker run -d --name "$CONTAINER" -p "$PORT":2379 -v "$ETCD_DIR":/glee-etcd-directory ubuntu:20.04 /bin/bash -c "cd /glee-etcd-directory && ./glee-etcd --listen-client-urls=http://0.0.0.0:2379 --advertise-client-urls=http://192.168.37.11:2379"
done

docker ps
