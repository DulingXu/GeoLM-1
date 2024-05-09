import threading
import subprocess
import re
import time
import argparse


from cluster import Cluster
# from TimeSeries import LatencyTimeSeries
# This should be executed in root.  --zdf

# python3 one-round.py


node_list = ['glee1', 'glee2', 'glee3']
ips = ['192.168.37.11','192.168.37.12','192.168.37.13']

trace_file = "./data2.json"
result_dir = "./tmp/result/"

# 定义一个 3x3 的二维矩阵
matrix = [
    [0.0, 20.0, 10.0],
    [20.0, 0.0, 30.0],
    [10.0, 30.0, 0.0]
]


def ping_container(source_container, target_container, output_file):

    time.sleep(0.3)
    command = f"docker exec {source_container} ping -c 100 {target_container}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # 正则提取时延信息
    delays = re.findall(r"time=(\d+(\.\d+)?)", result.stdout)

    # 将时延信息写入输出文件
    with open(output_file, "w") as file:
        for i, (delay, _) in enumerate(delays):
            file.write(str(i)+","+delay + "\n")
    file.close()

#   清空测试集群时延
def resetCluster():
    print("Latency zero")

    my_cluster = Cluster()

    my_cluster.set_node_list(node_list=node_list)
    my_cluster.set_ips(ips=ips)
    my_cluster.set_latency(latency_mat=matrix)

    my_cluster.clean_all_tc_conf()

#   初始化测试集群时延
def initCluster():
    print("Latency initialing")

    my_cluster = Cluster()

    my_cluster.set_node_list(node_list=node_list)
    my_cluster.set_ips(ips=ips)
    my_cluster.set_latency(latency_mat=matrix)

    my_cluster.clean_all_tc_conf()
    my_cluster.add_qdisc_for_all_node()
    my_cluster.add_latency()

#   以给定的时序数据设置测试集群时延并运行
def runCluster():
    print("Latency setting")

    my_cluster = Cluster()

    my_cluster.set_node_list(node_list=node_list)
    my_cluster.set_ips(ips=ips)
    my_cluster.set_latency(latency_mat=matrix)

    my_cluster.clean_all_tc_conf()
    my_cluster.add_qdisc_for_all_node()
    my_cluster.add_latency()

    my_cluster.loadJsonTimeSeries(trace_file)



def ycsb_load():
    command = f"go-ycsb load etcd -P ./basic.properties  -P ./workloads/workloadc -p threadcount=20 -p recordcount=100000 -p operationcount=40000 > ./tmp/ycsb-load-output.log"
    subprocess.run(command, shell=True)

def ycsb_run(isRaw = False):
    if isRaw:
        
        command = f"go-ycsb run etcd -P ./basic.properties  -P ./workloads/workloadc -p threadcount=20 -p recordcount=100000 -p operationcount=50000 -p  measurementtype=raw > ./tmp/ycsb-run-output-raw.log"
    else:
        command = f"go-ycsb run etcd -P ./basic.properties  -P ./workloads/workloadc -p threadcount=20 -p recordcount=100000 -p operationcount=50000  > ./tmp/ycsb-run-output.log"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

#完整实验示例
def expr1():
    containers = ["glee1","glee2", "glee3"]

    #清空时延
    resetCluster()
    #载入数据
    # ycsb_load()
    #初始化时延
    initCluster()

    time.sleep(0.5)

    # 创建线程列表
    threads = []

    #添加动态时延工作线程
    cluster_thread = threading.Thread(target=runCluster)
    threads.append(cluster_thread)
    # cluster_thread.start()

    #添加ycsb工作线程
    ycsb_thread = threading.Thread(target=ycsb_run, args=(True))
    threads.append(ycsb_thread)
    # ycsb_thread.start()

    # 添加网络状况收集线程
    for source in containers:
        for target in containers:
            if source!=target:
                output_file = f"./tmp/ping_{source}_{target}.log"
                thread = threading.Thread(target=ping_container, args=(source, target,output_file))
                threads.append(thread)
                # thread.start()
    
    # 启动所有线程
    for thread in threads:
        thread.start()

    # 等待所有线程结束
    for thread in threads:
        thread.join()
    
    #实验最后将所有的时延复原
    resetCluster()


# 自定义时延执行自定义命令
def expr2():
    containers = ["glee1","glee2", "glee3"]

    # 定义一个 3x3 的二维矩阵
    matrix2 = [
        [0.0, 20.0, 30.0],
        [20.0, 0.0, 50.0],
        [30.0, 50.0, 0.0]
    ]
    my_cluster = Cluster()

    my_cluster.set_node_list(node_list=node_list)
    my_cluster.set_ips(ips=ips)
    my_cluster.set_latency(latency_mat=matrix2)

    my_cluster.clean_all_tc_conf()
    my_cluster.add_qdisc_for_all_node()
    my_cluster.add_latency()


    command = f"go-ycsb run etcd -P ./basic.properties  -P ./workloads/workloadc -p threadcount=20 -p recordcount=100000 -p operationcount=30000 -p  measurementtype=raw > ./tmp/ycsb-run-output-raw-3.log"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    my_cluster.clean_all_tc_conf()


if __name__ == "__main__":
    expr1()
    # expr2()