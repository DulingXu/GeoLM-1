"""
1. should be executed in root.

2. Develop based on docker

3. Defines a Cluster class for managing network latency settings in Docker containers.

4. By using the tc command (Traffic Control), simulate different network latency between containers.

- Initialize network latency configuration
- Dynamically adjust network latency
- Load latency data based on time series

"""

import subprocess
import time
from TimeSeries import LatencyTimeSeries

class Cluster:
    def __init__(self):
        self.node_list = []
        self.ips = []
        self.latency_matrix = []

    def set_node_list(self, node_list):
        self.node_list = node_list


    def set_ips(self, ips):
        self.ips = ips
    
    def set_latency(self, latency_mat):
        self.latency_matrix = latency_mat
    
    def get_node_list(self):
        return self.node_list

    
    def run_docker_command(self,command):
        try:
            # print("COMMAND:\n",command)
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # 输出结果
            # print("STDOUT:\n", result.stdout)
            # print("STDERR:", result.stderr)
        except subprocess.CalledProcessError as e:
            # 命令执行失败
            print("Error executing command:", e)

    # def clean_all_tc_conf(self):
    #     for i in self.node_list:
    #         cmd="docker exec "+i+" tc qdisc del dev eth0 root"
    #         # print(cmd)
    #         self.run_docker_command(command=cmd)
            
    def clean_all_tc_conf(self):
        for i in self.node_list:
            # 检查当前 qdisc 配置
            cmd_check = "docker exec " + i + " tc qdisc show dev eth0"
            result_check = subprocess.run(cmd_check, shell=True, capture_output=True, text=True)
            if result_check.returncode == 0 and "noqueue" not in result_check.stdout:
                cmd_del = "docker exec " + i + " tc qdisc del dev eth0 root"
                self.run_docker_command(command=cmd_del)
            else:
                print(f"\n No need to delete :  ")
                print(f" There is no qdisc configuration in container {i} or the qdisc configuration cannot be obtained.")

    """
    qdisc is a term used in the Linux kernel for traffic control 
    and stands for "Queueing Discipline". 

    qdiscs are part of the Traffic Control (tc) system 
    and are used to manage outbound traffic on network interfaces. 
    They define how packets are queued and transmitted on a network interface.

    """

    def add_qdisc_for_all_node(self):
        for i in self.node_list:
            cmd="docker exec "+i+" tc qdisc add dev eth0 root handle 1: prio bands 5"
            # print(cmd)
            self.run_docker_command(command=cmd)

    # 检查 时延矩阵 和 节点数量 匹配
    def add_latency(self):
        if len(self.node_list)!=len(self.latency_matrix) or len(self.node_list) !=len(self.latency_matrix[0]):
            print("Node number and mat len must match!")
            return
        print("\n")
        print(self.latency_matrix)
        print(self.node_list)
        
        # 假设时延为上三角矩阵，遍历对每个节点配置网络时延
        for i in range(len(self.node_list)-1):
            for j in range(i+1,len(self.latency_matrix[i])):
                tmp_latency = self.latency_matrix[i][j]
                # print(tmp_latency)
                # 设置好节点  i -> j 时延
                
                # docker 配置
                tmp_parent=j+2
                tmp_handle=j+11
                cmd="docker exec "+self.node_list[i]+" tc qdisc add dev eth0 parent 1:"+str(tmp_parent)+" handle "+str(tmp_handle)+": netem delay "+str(tmp_latency)+"ms 5ms"
                # print(cmd)
                self.run_docker_command(command=cmd)

                cmd="docker exec "+self.node_list[i]+" tc filter add dev eth0 protocol ip parent 1:0 prio 4 u32 match ip dst \'"+self.ips[j]+"\' flowid 1:"+str(tmp_parent)
                # print(cmd)
            
                self.run_docker_command(command=cmd)
    
    def change_latency(self):
        if len(self.node_list)!=len(self.latency_matrix) or len(self.node_list) !=len(self.latency_matrix[0]):
            print("Node number and mat len must match!")
            return
        # print(self.latency_matrix)
        # print(self.node_list)
        for i in range(len(self.node_list)-1):
            for j in range(i+1,len(self.latency_matrix[i])):
                tmp_latency = self.latency_matrix[i][j]
                # print(tmp_latency)
                tmp_parent=j+2
                tmp_handle=j+11
                # cmd="docker exec "+self.node_list[i]+" tc qdisc change dev eth0 parent 1:"+str(tmp_parent)+" handle "+str(tmp_handle)+": netem delay "+str(tmp_latency)+"ms"
                # cmd="docker exec "+self.node_list[i]+" tc qdisc change dev eth0 parent 1:"+str(tmp_parent)+" handle "+str(tmp_handle)+": netem delay "+str(tmp_latency)+"ms 10ms 25%"
                cmd="docker exec "+self.node_list[i]+" tc qdisc change dev eth0 parent 1:"+str(tmp_parent)+" handle "+str(tmp_handle)+": netem delay "+str(tmp_latency)+"ms 5ms"
                # cmd="docker exec "+self.node_list[i]+" tc qdisc change dev eth0 parent 1:"+str(tmp_parent)+" handle "+str(tmp_handle)+": netem delay "+str(tmp_latency)+"ms"

                # print(cmd)
                self.run_docker_command(command=cmd)

                # cmd="docker exec "+self.node_list[i]+" tc filter add dev eth0 protocol ip parent 1:0 prio 4 u32 match ip dst \'"+self.ips[j]+"\' flowid 1:"+str(tmp_parent)
                # print(cmd)
                # self.run_docker_command(command=cmd)
    
    def actDynamicallyAsTimeSeries(self, LatencyTimeSeries):
        array = LatencyTimeSeries.latency_time_series
        for i, LatencyElem in enumerate(array):
            # print_current_time()
            # print("Struct", i+1)
            # print("Time:", LatencyElem.time)
            # print("Array:")
            print("Time:"+str(LatencyElem.time)+"s")
            for row in LatencyElem.latency_matrix:
                print(row)
            self.set_latency(LatencyElem.latency_matrix)

            # self.clean_all_tc_conf()
            # self.add_qdisc_for_all_node()
            self.change_latency()
            if i<len(array)-1:
                time.sleep(array[i+1].time - array[i].time)
            print()
    def loadJsonTimeSeries(self, filename):
        my_time_series =  LatencyTimeSeries()
        my_time_series.read_from_json_file(filename=filename)
        self.actDynamicallyAsTimeSeries(my_time_series)


# my_cluster = Cluster()

# my_cluster.set_node_list(node_list=node_list)
# my_cluster.set_ips(ips=ips)
# my_cluster.set_latency(latency_mat=matrix)

# my_cluster.clean_all_tc_conf()
# my_cluster.add_qdisc_for_all_node()
# my_cluster.add_latency()
# clean_all_tc_conf(node_list=node_list)
# add_qdisc_for_all_node(node_list=node_list)

# add_latency(node_list=node_list,mat=matrix,ips=ips)

# run_docker_command("docker exec glee1 ping glee2 -i 0.5 -c 4")