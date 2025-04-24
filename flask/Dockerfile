# 指定基础镜像 即新镜像基于谁来构建 
FROM python:3.11-alpine

ENV FLASK_APP=run.py
ENV FLASK_CONFIG=docker

# 创建新用户 -D默认选项——不设置密码不询问交互信息
RUN adduser -D flasky

# 接下来用户操作都以flasky用户身份执行，一般不以root身份执行保证安全性
USER flasky

# 设置容器内的工作目录，后续的所有指令(RUN CMD COPY都会基于这个文件工作)，该目录位于DOCKER容器内部的虚拟文件系统
WORKDIR /app

COPY requirements requirements

# RUN是构建镜像时执行的命令

# 创建虚拟环境
RUN python -m venv venv 
# 安装依赖
RUN venv/bin/pip install -r requirements/docker.txt

COPY app app 
COPY migrations migrations
# 复制多个到当前目录下
COPY run.py config.py boot.sh ./


# 声明要监听的端口
EXPOSE 5000
# 容器启动时要运行的脚本
ENTRYPOINT [ "./boot.sh" ]

