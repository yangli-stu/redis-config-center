import asyncio
from redis_config_server import config_server, ConfigGroup

# 服务端快速开始示例：
async def test():
    await config_server.insert_config_group(
        ConfigGroup(group_name="default", group_version=1, config_dict={"key1": "value1"}))
    # ... 插入其他配置组 ...

    print(await config_server.get_config_group("default"))
    # ... 获取其他配置组 ...


if __name__ == "__main__":
    asyncio.run(test())