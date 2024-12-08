# 使用官方Python镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 将项目的根目录添加到 PYTHONPATH 环境变量中，以防止找不到redis_config_server.py
ENV PYTHONPATH="${PYTHONPATH}:/app"

# 复制当前目录内容到容器中的/app目录
COPY . .

# 安装依赖
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 设置工作目录为web目录
WORKDIR /app/web

# 命令行启动uvicorn服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8079"]