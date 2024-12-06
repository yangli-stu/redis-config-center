import json
import socket

import asyncio
from threading import Thread
from typing import List

from pydantic import BaseModel

# 配置 Redis 客户端
# import time
# import redis
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
import valkey.asyncio as avalkey
import os

redis_client = avalkey.Valkey(
    host=os.getenv('REDIS_URL', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    password=os.getenv('REDIS_PASSWORD', None),
    max_connections=1
)

DEFAULT_CONFIG_GROUP = os.getenv("CONFIG_GROUP", "default")


class ConfigGroup(BaseModel):
    group_name: str = None
    group_version: str = None
    config_dict: dict | None = None


class ConfigClient:
    def __init__(self, config_server_name: str, refresh_time: int = 5):
        self.config_server_name = config_server_name
        self.config_group = ConfigGroup()
        self.refresh_time = refresh_time

    async def get_config_group(self):
        return self.config_group

    async def _get_config_group(self, group_name):
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

    async def _extract_current_ip_to_group_name(self):

        group_names_bytes: List[bytes] = await redis_client.hkeys(f"{self.config_server_name}")
        group_names: List[str] = sorted([name.decode('utf-8') for name in group_names_bytes])

        if not group_names:
            return DEFAULT_CONFIG_GROUP

        # 如果存在与 DEFAULT_CONFIG_GROUP 匹配的配置组，则直接返回
        if DEFAULT_CONFIG_GROUP in group_names:
            return DEFAULT_CONFIG_GROUP

        # 如果不存在与 DEFAULT_CONFIG_GROUP 匹配的配置组，按当前ip取余映射对应的配置组
        current_ip = socket.gethostbyname(socket.gethostname())
        ip_int = int(current_ip.split('.')[-1])  # 取 IP 最后一段并转为整数
        index = ip_int % len(group_names)
        return group_names[index]

    async def _schedule_refresh(self):
        while True:
            new_group_name = await self._extract_current_ip_to_group_name()
            new_config_group = await self._get_config_group(new_group_name)

            if new_config_group and (
                    new_config_group.group_name != self.config_group.group_name or new_config_group.group_version != self.config_group.group_version):
                self.config_group = new_config_group
                print(
                    f"当前配置组 {new_group_name}, 版本 {new_config_group.group_version}, 配置已更新: {new_config_group.config_dict}")

            await asyncio.sleep(self.refresh_time)

    def start(self):
        def run_event_loop():
            asyncio.run(self._schedule_refresh())

        Thread(target=run_event_loop, name='redis-config-client-looper', daemon=True).start()
        print('Redis client config center started.')


config_client = ConfigClient("redis_config_groups", 5)
