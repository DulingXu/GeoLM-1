
import os
import threading
import subprocess
import re
import time
import logging
from cluster import Cluster

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

node_list = ['glee1', 'glee2', 'glee3']
ips = ['192.168.37.11', '192.168.37.12', '192.168.37.13']

trace_file = "./data2.json"
result_dir = "./tmp/result/"

matrix = [
    [0.0, 20.0, 10.0],
    [20.0, 0.0, 30.0],
    [10.0, 30.0, 0.0]
]

def ping_container(source_container, target_container, output_file):
    time.sleep(0.3)
    command = f"docker exec {source_container} ping -c 100 {target_container}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        logging.error(f"Ping 命令失败: {result.stderr}")
        return

    delays = re.findall(r"time=(\d+(\.\d+)?)", result.stdout)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as file:
        for i, (delay, _) in enumerate(delays):
            file.write(str(i) + "," + delay + "\n")

def reset_cluster():
    logging.info("重置集群")
    my_cluster = Cluster()
    my_cluster.set_node_list(node_list=node_list)
    my_cluster.set_ips(ips=ips)
    my_cluster.set_latency(latency_mat=matrix)
    my_cluster.clean_all_tc_conf()

def init_cluster():
    logging.info("初始化集群延迟")
    my_cluster = Cluster()
    my_cluster.set_node_list(node_list=node_list)
    my_cluster.set_ips(ips=ips)
    my_cluster.set_latency(latency_mat=matrix)
    my_cluster.clean_all_tc_conf()
    my_cluster.add_qdisc_for_all_node()
    my_cluster.add_latency()

def run_cluster():
    logging.info("运行集群并设置延迟")
    my_cluster = Cluster()
    my_cluster.set_node_list(node_list=node_list)
    my_cluster.set_ips(ips=ips)
    my_cluster.set_latency(latency_mat=matrix)
    my_cluster.clean_all_tc_conf()
    my_cluster.add_qdisc_for_all_node()
    my_cluster.add_latency()
    my_cluster.loadJsonTimeSeries(trace_file)

def ycsb_load():
    command = "go-ycsb load etcd -P ./basic.properties -P ../../go-ycsb/workloads/workloadc -p threadcount=20 -p recordcount=10000 -p operationcount=9999 > /home/chenzheng/dl/output/ycsb-load-output-1.log"
    subprocess.run(command, shell=True, timeout=300)

def ycsb_run(is_raw=False):
    if is_raw:
        command = "go-ycsb run etcd -P ./basic.properties -P ../../go-ycsb/workloads/workloada -p threadcount=20 -p recordcount=10000 -p operationcount=9999 -p measurementtype=raw > /home/chenzheng/dl/output/opt-ycsb-run-output-raw-10w-3nodes-a.log"
    else:
        command = "go-ycsb run etcd -P ./basic.properties -P ../../go-ycsb/workloads/workloada -p threadcount=20 -p recordcount=10000 -p operationcount=9999 > /home/chenzheng/dl/output/opt-ycsb-run-output.log"
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        logging.error(f"YCSB 运行命令失败: {result.stderr}")

def expr1():
    containers = ["glee1", "glee2", "glee3"]
    logging.info("开始 expr1")
    reset_cluster()
    logging.info("集群延迟已清除")
    init_cluster()
    logging.info("集群已初始化")
    time.sleep(0.5)

    threads = []
    logging.info("创建线程")

    cluster_thread = threading.Thread(target=run_cluster)
    threads.append(cluster_thread)

    ycsb_thread = threading.Thread(target=ycsb_run, args=(True,))
    threads.append(ycsb_thread)

    for source in containers:
        for target in containers:
            if source != target:
                output_file = f"./tmp/ping_{source}_{target}.log"
                thread = threading.Thread(target=ping_container, args=(source, target, output_file))
                threads.append(thread)

    logging.info("启动所有线程")
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    logging.info("所有线程已完成")

    reset_cluster()
    logging.info("集群重置完成")

if __name__ == "__main__":
    expr1()