import asyncio

from redis_config_server import config_server, ConfigGroup
from redis_config_client import config_client


if __name__ == "__main__":
    async def test():
        await config_server.delete_config_group("default")
        await config_server.delete_config_group("group_1")
        await config_server.delete_config_group("group_2")
        await config_server.delete_config_group("group_3")
        await config_server.delete_config_group("group_4")

        # 插入服务端配置
        await config_server.insert_config_group(
            ConfigGroup(group_name="default", group_version="1", config_dict={"default_key": "default_value"})
        )
        await config_server.insert_config_group(
            ConfigGroup(group_name="group_1", group_version="1", config_dict={"key1": "value1"})
        )
        await config_server.insert_config_group(
            ConfigGroup(group_name="group_3", group_version="1", config_dict={"key3": "value3"})
        )
        await config_server.insert_config_group(
            ConfigGroup(group_name="group_2", group_version="1", config_dict={"key2": "value2"})
        )

        # 获取服务端当前配置组信息
        print(await config_server.get_config_group("group_1"))
        print(await config_server.get_config_group("group_2"))
        print(await config_server.get_config_group("group_3"))

        # 测试客户端
        await config_client.start()

        await asyncio.sleep(6)
        cur_config_group = config_client.get_config_group()
        cur_config_val = config_client.get_config("youtube_apikey")
        print(f"客户端当前配置为：{cur_config_group}, cur_config_val: {cur_config_val}")

        # 模拟服务端更新，客户端同步更新配置
        await config_server.insert_config_group(ConfigGroup(group_name=cur_config_group.group_name, group_version="2",
                                                            config_dict=cur_config_group.config_dict))
        await asyncio.sleep(6)
        cur_config_group = config_client.get_config_group()
        cur_config_val = config_client.get_config("youtube_apikey")
        print(f"服务端配置更新，客户端当前配置为：{cur_config_group}, cur_config_val: {cur_config_val}")

        # 模拟服务端配置组被删除，客户端重新分配配置组
        await config_server.delete_config_group(cur_config_group.group_name)
        await asyncio.sleep(6)
        cur_config_group = config_client.get_config_group()
        cur_config_val = config_client.get_config("youtube_apikey")
        print(f"服务端配置组删除，重新分配配置组，客户端当前配置为：{cur_config_group}, cur_config_val: {cur_config_val}")

        # 模拟服务端新增配置组，客户端重新分配配置组
        await config_server.insert_config_group(
            ConfigGroup(group_name="group_4", group_version="1", config_dict={"key4": "value4"})
        )
        await asyncio.sleep(6)
        cur_config_group = config_client.get_config_group()
        cur_config_val = config_client.get_config("youtube_apikey")
        print(f"服务端新增配置组，重新分配配置组，客户端当前配置为：{cur_config_group}, cur_config_val: {cur_config_val}")


    asyncio.run(test())
