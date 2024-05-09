import datetime
import re


# 读取文件并统计每秒操作数
def count_operations_per_second(file_path):
    operations_per_second = {}
    # 正则表达式
    pattern = r'^(READ|UPDATE),(\d+),(\d+)$'
    with open(file_path, 'r') as file:
        start_timestamp = None
        cnt = 0
        for line in file:
            match = re.match(pattern, line)
            if not match:
                continue
            # if skip_line<23:
            #     skip_line = skip_line+1
            #     continue
            operation, timestamp_us_str, _ = line.strip().split(',')
            if operation == 'TOTAL':
                continue
            timestamp_us = int(timestamp_us_str)
            if start_timestamp is None:
                start_timestamp = timestamp_us
            if timestamp_us - start_timestamp >= 1_000_000:
                start_timestamp = timestamp_us
                cnt = cnt+1

            if cnt not in operations_per_second:
                operations_per_second[cnt] = {'UPDATE': 0, 'READ': 0}

            if operation == 'READ':
                operations_per_second[cnt]['READ'] += 1
            elif operation == 'UPDATE':
                operations_per_second[cnt]['UPDATE'] += 1

    return operations_per_second

# 测试
file_path = './tmp/ycsb-run-output-raw-3.log'
operations_per_second = count_operations_per_second(file_path)
for second, operations in operations_per_second.items():
    print(f"During {second} s, {operations['UPDATE']} updates and {operations['READ']} reads were performed.")

outputfile = file_path+".analyzed"
# 将时延信息写入输出文件
with open(outputfile, "w") as file:
    for second, operations in operations_per_second.items():

        file.write(str(second)+","+str(operations['UPDATE'])+","+str(operations['READ']) + "\n")
file.close()
