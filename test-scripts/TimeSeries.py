import time
import json

class LatencyElem:
    def __init__(self, time, mat):
        self.time = time
        self.latency_matrix = mat

class LatencyTimeSeries:
    def __init__(self):
        self.latency_time_series = []
    
    def appendLatencyElem(self, LatencyElem):
        self.latency_time_series.append(LatencyElem)
    def read_from_json_file(self, filename):
        # 从 JSON 文件中读取结构体数组
        struct_array = []
        with open(filename, "r") as json_file:
            data = json.load(json_file)
            for item in data:
                my_struct = LatencyElem(item["time"], item["latency_matrix"])
                self.appendLatencyElem(my_struct)
    def getLatencyTimeSeries(self):
        return self.latency_time_series

# def print_current_time():
#     current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#     print("Current time:", current_time)

