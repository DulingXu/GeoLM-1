FROM ubuntu:22.04

# 将源列表写入/etc/apt/sources.list
RUN echo '# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释' > /etc/apt/sources.list \
    && echo 'deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse' >> /etc/apt/sources.list \
    && echo '# deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse' >> /etc/apt/sources.list \
    && echo 'deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse' >> /etc/apt/sources.list \
    && echo '# deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse' >> /etc/apt/sources.list \
    && echo 'deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse' >> /etc/apt/sources.list \
    && echo '# deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse' >> /etc/apt/sources.list \
    && echo 'deb http://security.ubuntu.com/ubuntu/ jammy-security main restricted universe multiverse' >> /etc/apt/sources.list \
    && echo '# deb-src http://security.ubuntu.com/ubuntu/ jammy-security main restricted universe multiverse' >> /etc/apt/sources.list

# 更新源并安装所需软件包
RUN apt update && apt upgrade -y \
    && apt install iputils-ping vim -y

# 清理缓存
RUN apt clean

CMD ["/bin/bash"]
