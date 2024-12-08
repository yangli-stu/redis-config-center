import asyncio
from redis_config_client import config_client

# 客户端快速开始示例：
async def test():
    await config_client.start()
    await asyncio.sleep(6)  # 等待足够的时间让配置刷新完成

    cur_config_group = config_client.get_config_group()
    test_val = config_client.get_config("test_key")

    print(f"客户端当前配置组信息为：{cur_config_group}")
    print(f"客户端当前配置'test_key'的值为：{test_val}")


if __name__ == "__main__":
    asyncio.run(test())