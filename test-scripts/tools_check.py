"""

This script is used to check whether the tc tool is installed in the container. If not, install it directly on the spot.

Whether the network interface is correct,
and whether the tc tool is running normally.

Maybe you need to give the current user docker permissions in bash.

    sudo usermod -aG docker $USER

Then log in again to make the group change take effect, or reload the user group with the following command:

    newgrp docker

"""
import subprocess

# 列出所有容器
containers = ['glee1', 'glee2', 'glee3']

# 检查 tc 工具是否安装，并在必要时安装
def check_and_install_tc(container):
    cmd_check = f"sudo docker exec {container} which tc"
    result_check = subprocess.run(cmd_check, shell=True, capture_output=True, text=True)
    
    if result_check.returncode != 0:
        print(f"容器 {container} 中未找到 `tc`，正在安装...")
        install_commands = [
            f"sudo docker exec {container} apt-get update",
            f"sudo docker exec {container} apt-get install -y iproute2"
        ]
        for cmd in install_commands:
            result_install = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result_install.returncode != 0:
                raise RuntimeError(f"无法在容器 {container} 中安装 `tc`:\n{result_install.stderr}")
        print(f"`tc` 已成功安装在容器 {container} 中")
    else:
        print(f"`tc` 在容器 {container} 中已安装")

# 检查网络接口是否存在且命名正确
def check_network_interface(container):
    cmd = f"sudo docker exec {container} ip link"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"无法在容器 {container} 中列出网络接口: {result.stderr}")
    else:
        print(f"容器 {container} 中的网络接口:\n{result.stdout}")
        if "eth0" not in result.stdout:
            raise RuntimeError(f"容器 {container} 中未找到名为 `eth0` 的网络接口")

# 检查并删除 qdisc，如果存在的话
def delete_qdisc(container):
    # 检查当前 qdisc 配置
    cmd_show = f"sudo docker exec {container} tc qdisc show dev eth0"
    result_show = subprocess.run(cmd_show, shell=True, capture_output=True, text=True)
    if result_show.returncode != 0:
        print(f"无法在容器 {container} 中列出 qdisc: {result_show.stderr}")
        return
    
    # 如果 qdisc 存在，则删除
    if "noqueue" not in result_show.stdout:
        cmd_del = f"sudo docker exec {container} tc qdisc del dev eth0 root"
        result_del = subprocess.run(cmd_del, shell=True, capture_output=True, text=True)
        if result_del.returncode != 0:
            print(f"在容器 {container} 中执行命令时出错: {cmd_del}")
            print(result_del.stderr)
        else:
            print(f"命令在容器 {container} 中成功执行: {cmd_del}")
    else:
        print(f"容器 {container} 中没有 qdisc 配置")

# 检查和执行命令
for container in containers:
    try:
        check_and_install_tc(container)
        check_network_interface(container)
    except RuntimeError as e:
        print(e)
        continue  # 跳过检查失败的容器
    
    # 删除 qdisc
    delete_qdisc(container)
