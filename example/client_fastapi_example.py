from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from redis_config_client import config_client

# FastAPI 集成 redis_config_client 示例：
# 1. 绑定 config_client.start() 到 FastAPI 的 lifespan，在应用启动时初始化配置客户端。
# 2. 在 config_client.start() 成功启动后，项目的任何地方都可以直接调用
#    redis_config_client.ConfigClient.get_config() 方法获取配置。

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动配置客户端
    await config_client.start()
    yield

# 创建 FastAPI 应用实例，并绑定 lifespan 函数
app = FastAPI(lifespan=lifespan)

# 示例路由，您可以根据需要添加更多路由和功能
@app.get("/")
async def read_root():
    return {
        "code": "200",
        "message": "Hello, Redis Config Center!",
        "data": config_client.get_config_group()
    }

if __name__ == "__main__":
    # 使用 uvicorn 运行 FastAPI 应用
    # 可直接访问 http://127.0.0.1:8089/ 查看当前最新配置
    uvicorn.run(app, host="127.0.0.1", port=8089)