"""
This script is used to manage experiments involving network latency and performance testing,
using Docker containers and go-ycsb. The script includes the following functions:

Set up and reset a cluster of nodes with specific latency.
Run latency tests between Docker containers.
Use go-ycsb to execute load and run commands.
Manage multiple threads to perform these tasks in parallel.

"""
# python3 one-round.py

import os
import threading
import subprocess
import re
import time
import argparse
import subprocess


from cluster import Cluster
# from TimeSeries import LatencyTimeSeriesz


# 需要提前准备 docker，创建对应的 glee# 容器
node_list = ['glee1', 'glee2', 'glee3']
ips = ['192.168.37.11','192.168.37.12','192.168.37.13']

# # 检查 tc 工具是否安装
# def check_tc_installed(container):
#     cmd = f"docker exec {container} which tc"
#     result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#     if result.returncode != 0:
#         raise RuntimeError(f"容器 {container} 中未找到 `tc`")
#     else:
#         print(f"`tc` 在容器 {container} 中已安装")
        
# 确保目录存在且设置目录权限
def ensure_directory(directory):
    os.makedirs(directory, exist_ok=True)
    os.chmod(directory, 0o755)  
    
# xdl:need update the trace file here
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

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 将时延信息写入输出文件，用于检查实际控制时延是否按照设定运行
    with open(output_file, "w") as file:
        for i, (delay, _) in enumerate(delays):
            file.write(str(i) + "," + delay + "\n")
    file.close()

#   清空测试集群时延
def resetCluster():
    print("\n Reset Cluster over! ")

    my_cluster = Cluster()

    my_cluster.set_node_list(node_list=node_list)
    my_cluster.set_ips(ips=ips)
    my_cluster.set_latency(latency_mat=matrix)

    my_cluster.clean_all_tc_conf()

#   初始化测试集群时延
def initCluster():
    print("\n Latency initialing … …  ")

    my_cluster = Cluster()

    my_cluster.set_node_list(node_list=node_list)
    my_cluster.set_ips(ips=ips)
    my_cluster.set_latency(latency_mat=matrix)

    my_cluster.clean_all_tc_conf()
    my_cluster.add_qdisc_for_all_node()
    my_cluster.add_latency()

#   以给定的时序数据设置测试集群时延并运行
def runCluster():
    print("\n RunCluster begin: ")
    print("\n Latency setting  … …  ")

    # 创建集群实例
    my_cluster = Cluster()

    # 配置集群
    # 设置集群中的节点列表。
    my_cluster.set_node_list(node_list = node_list)
    # 指定集群中每个节点的IP地址。
    my_cluster.set_ips(ips=ips)
    # 设定节点间的网络延迟矩阵
    my_cluster.set_latency(latency_mat = matrix)

    my_cluster.clean_all_tc_conf()
    my_cluster.add_qdisc_for_all_node()
    
    my_cluster.add_latency()

    my_cluster.loadJsonTimeSeries(trace_file)


def ycsb_load():
    command = f"etcd -P ./basic.properties  -P ../../go-ycsb/workloads/workloadc -p threadcount=20 -p recordcount=10000 -p operationcount=9999 > /home/chenzheng/dl/output/ycsb-load-output-1.log"
    subprocess.run(command, shell=True)

def ycsb_run(isRaw = False):
    if isRaw:
        command = f"go-ycsb run etcd -P ./basic.properties  -P ../../go-ycsb/workloads/workloada -p threadcount=20 -p recordcount=10000 -p operationcount=100000 -p  measurementtype=raw > /home/chenzheng/dl/output/ycsb-run-output-raw-10w-3nodes-a.log"
    else:
        command = f"go-ycsb run etcd -P ./basic.properties  -P ../../go-ycsb/workloads/workloada -p threadcount=20 -p recordcount=10000 -p operationcount=9999  > /home/chenzheng/dl/output/ycsb-run-output.log"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

# 完整实验示例，expr1:
def expr1():
    containers = ["glee1","glee2", "glee3"]
    print('\n - - -  "glee1","glee2", "glee3"  - - -')

    # 清空时延
    resetCluster()
    print('\n - - - Delay has been cleared - - -')
    # 载入数据
    # 初始化时延
    initCluster()
    print('\n - - - The cluster has been initialized - - -')
    # 初始化时间，等待时延设置
    time.sleep(0.5)

    # 创建线程列表
    threads = []
    print('\n - - - Threads has been created- - -')
    
    #添加动态时延工作线程
    cluster_thread = threading.Thread(target=runCluster)
    threads.append(cluster_thread)
    # cluster_thread.start()

    #添加ycsb工作线程
    ycsb_thread = threading.Thread(target=ycsb_run, args=(True,))
    threads.append(ycsb_thread)
    print('\n - - - Ycsb_thread apending - - -')
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
    print('\n - - - thread starting - - -')
    for thread in threads:
        thread.start()
    print('\n - - - thread started - - -')
    
    # 等待所有线程结束
    for thread in threads:
        thread.join()
    print('\n - - - all threads finished - - -')
    
    # 实验最后将所有的时延复原
    print('\n - - - reset cluster  - - -')
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
    print('Set latency … … ')

    my_cluster.clean_all_tc_conf()
    my_cluster.add_qdisc_for_all_node()
    my_cluster.add_latency()


    command = f"go-ycsb run etcd -P ./basic.properties  -P ./workloads/workloadc -p threadcount=20 -p recordcount=100000 -p operationcount=30000 -p  measurementtype=raw > ./ycsb-run-output-raw-expr2.log"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print('\n  - - - to : ./tmp/ycsb-run-output-raw-expr2.log - - -  ')

if __name__ == "__main__":
    expr1()
    #expr2()
    

"""
    etcd 
    
    -P ./basic.properties  
    
    -P ../../go-ycsb/workloads/workloadc 
    
    -p threadcount=20 
    
    -p recordcount=10000 
    
    -p operationcount=9999 
    
    > /home/chenzheng/dl/output/ycsb-load-output-1.log
    
    工作负载 a b c d
    线程数 <= 20
    记录数据 >= 操作数据
    输出路径输出文件
    
    """

# # 自定义时延执行自定义命令
# def expr2():
#     containers = ["glee1","glee2", "glee3"]

#     # 定义一个 3x3 的二维矩阵
#     matrix2 = [
#         [0.0, 20.0, 30.0],
#         [20.0, 0.0, 50.0],
#         [30.0, 50.0, 0.0]
#     ]
#     my_cluster = Cluster()
#     my_cluster.set_node_list(node_list=node_list)
#     my_cluster.set_ips(ips=ips)
#     my_cluster.set_latency(latency_mat=matrix2)
#     print('Set latency … … ')
#     my_cluster.clean_all_tc_conf()
#     my_cluster.add_qdisc_for_all_node()
#     my_cluster.add_latency()

#     # command = f"go-ycsb run etcd -P ./basic.properties  -P ./workloads/workloadc -p threadcount=20 -p recordcount=100000 -p operationcount=30000 -p  measurementtype=raw > ./tmp/ycsb-run-output-raw-3.log"
#     # result = subprocess.run(command, shell=True, capture_output=True, text=True)
#     # print('\n  - - - to : ./tmp/ycsb-run-output-raw-3.log - - -  ')
#     # my_cluster.clean_all_tc_conf()
    
#     output_file = './tmp/ycsb-run-output-raw-expr2.log'
#     ensure_directory(os.path.dirname(output_file))  # 确保目录存在并可写
#     command = "go-ycsb run etcd -P ./basic.properties -P ./workloads/workloadc -p threadcount=20 -p recordcount=100000 -p operationcount=30000 -p measurementtype=raw > " + output_file
#     # command = f"go-ycsb run etcd -P ./basic.properties  -P ./workloads/workloadc -p threadcount=20 -p recordcount=100000 -p operationcount=30000 -p  measurementtype=raw > ./tmp/ycsb-run-output-raw-3.log"
#     result = subprocess.run(command, shell=True, capture_output=True, text=True)
#     print('Return Code:', result.returncode)
#     print('STDERR:', result.stderr)
#     print('\n  - - - to : ./tmp/ycsb-run-output-raw-expr2.log - - -  ')
#     my_cluster.clean_all_tc_conf()