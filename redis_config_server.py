import asyncio
import json

from pydantic import BaseModel

# 配置 Redis 客户端
# import time
# import redis
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
import valkey.asyncio as avalkey
import os

redis_client = avalkey.Valkey(
    host=os.getenv('REDIS_URL', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    password=os.getenv('REDIS_PASSWORD', None),
    max_connections=1
)


class ConfigGroup(BaseModel):
    group_name: str = None
    group_version: str = None
    config_dict: dict | None = None


class ConfigServer:
    def __init__(self, config_server_name: str):
        self.config_server_name = config_server_name

    async def insert_config_group(self, config_group: ConfigGroup):
        group_name = config_group.group_name
        # 使用哈希表存储配置组，键为 group_name
        json_config_group = {
            "group_name": group_name,
            "group_version": config_group.group_version,
            "config_dict": config_group.config_dict
        }
        await redis_client.hset(f"{self.config_server_name}", group_name, json.dumps(json_config_group))
        print(f"配置组 {group_name} 已添加/更新")

    async def get_config_group(self, group_name):
        config_group_data = await redis_client.hget(f"{self.config_server_name}", group_name)
        if config_group_data:
            val = json.loads(config_group_data)
            return ConfigGroup(
                group_name=val["group_name"],
                group_version=val["group_version"],
                config_dict=val["config_dict"]
            )
        else:
            print(f"配置组 {group_name} 不存在")
            return None

    async def delete_config_group(self, group_name):
        await redis_client.hdel(f"{self.config_server_name}", group_name)
        print(f"配置组 {group_name} 已删除")


config_server = ConfigServer(config_server_name="redis_config_groups")

# 测试示例：添加或更新配置组
if __name__ == "__main__":
    async def test():
        # await config_server.delete_config_group("default")
        # await config_server.delete_config_group("group_1")
        # await config_server.delete_config_group("group_2")
        # await config_server.delete_config_group("group_3")
        # await config_server.delete_config_group("group_4")
        # 插入服务端配置
        await config_server.insert_config_group(
            ConfigGroup(group_name="default", group_version="1", config_dict={"key": "value"}))
        await config_server.insert_config_group(
            ConfigGroup(group_name="group_1", group_version="1", config_dict={"key1": "value1"}))
        await config_server.insert_config_group(
            ConfigGroup(group_name="group_3", group_version="1", config_dict={"key3": "value3"}))
        await config_server.insert_config_group(
            ConfigGroup(group_name="group_2", group_version="1", config_dict={"key2": "value2"}))

        # 获取服务端当前配置组信息
        print(await config_server.get_config_group("group_1"))
        print(await config_server.get_config_group("group_2"))
        print(await config_server.get_config_group("group_3"))

        # 测试客户端
        from redis_config_client import config_client
        config_client.start()

        await asyncio.sleep(6)
        cur_config_group = await config_client.get_config_group()
        print(f"客户端当前配置为：{cur_config_group}")

        # 服务端更新，客户端同步更新配置
        await config_server.insert_config_group(ConfigGroup(group_name=cur_config_group.group_name, group_version="2",
                                                            config_dict=cur_config_group.config_dict))
        await asyncio.sleep(6)
        cur_config_group = await config_client.get_config_group()
        print(f"服务端配置更新，客户端当前配置为：{cur_config_group}")

        # 服务端配置组被删除，客户端重新分配配置组
        await config_server.delete_config_group(cur_config_group.group_name)
        await asyncio.sleep(6)
        cur_config_group = await config_client.get_config_group()
        print(f"服务端配置组删除，重新分配配置组，客户端当前配置为：{cur_config_group}")

        # 服务端新增配置组，客户端重新分配配置组
        await config_server.insert_config_group(
            ConfigGroup(group_name="group_4", group_version="1", config_dict={"key4": "value4"}))
        await asyncio.sleep(6)
        cur_config_group = await config_client.get_config_group()
        print(f"服务端新增配置组，重新分配配置组，客户端当前配置为：{cur_config_group}")


    asyncio.run(test())
