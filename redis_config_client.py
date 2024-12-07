import asyncio
import logging
import os
import socket
from typing import Optional, Any

from pydantic import BaseModel

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
REDIS_URL = os.getenv("REDIS_URL", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
DEFAULT_CONFIG_GROUP = os.getenv("MACHINE_ID", "default")

# 配置 Redis 客户端
import valkey.asyncio as avalkey

try:
    redis_client = avalkey.Valkey(
        host=REDIS_URL,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        max_connections=1
    )
except Exception as e:
    logger.error(f"[Redis Config Center] 初始化 Redis 客户端失败: {e}")
    raise


class ConfigGroup(BaseModel):
    group_name: str
    group_version: str
    config_dict: Optional[dict] = None


class ConfigClient:
    def __init__(self, config_server_name: str, refresh_time: int = 5):
        self.config_server_name = config_server_name
        self.config_group = ConfigGroup(group_name=DEFAULT_CONFIG_GROUP, group_version="-1", config_dict={})
        self.refresh_time = refresh_time
        self._refresh_task = None

    def get_config(self, key: str) -> Optional[Any]:
        config_group = self.get_config_group()
        if config_group and config_group.config_dict is not None:
            return config_group.config_dict.get(key, None)
        return None

    def get_config_group(self) -> Optional[ConfigGroup]:
        return self.config_group

    async def _get_config_group(self, group_name: str) -> Optional[ConfigGroup]:
        try:
            config_group_data = await redis_client.hget(self.config_server_name, group_name)
            if config_group_data:
                return ConfigGroup.model_validate_json(config_group_data)
            logger.warning(f"[ConfigClient] 配置组 {group_name} 不存在")
        except Exception as e:
            logger.error(f"[ConfigClient] 获取配置组失败: {e}")
        return None

    async def _extract_current_ip_to_group_name(self) -> str:
        try:
            group_names_bytes = await redis_client.hkeys(self.config_server_name)
            group_names = sorted([name.decode('utf-8') for name in group_names_bytes])

            if not group_names or DEFAULT_CONFIG_GROUP in group_names:
                return DEFAULT_CONFIG_GROUP

            current_ip = socket.gethostbyname(socket.gethostname()).split('.')[-1]
            index = int(current_ip) % len(group_names)
            return group_names[index]
        except Exception as e:
            logger.error(f"[ConfigClient] 提取当前IP对应的配置组名失败: {e}")
            return DEFAULT_CONFIG_GROUP

    async def _schedule_refresh(self):
        while True:
            try:
                new_group_name = await self._extract_current_ip_to_group_name()
                new_config_group = await self._get_config_group(new_group_name)

                if new_config_group and (
                    new_config_group.group_name != self.config_group.group_name or
                    new_config_group.group_version != self.config_group.group_version
                ):
                    self.config_group = new_config_group
                    logger.info(
                        f"[ConfigClient] 当前配置组 {new_group_name}, 版本 {new_config_group.group_version}, 配置已更新: {new_config_group.config_dict}"
                    )

                await asyncio.sleep(self.refresh_time)
            except Exception as e:
                logger.error(f"[ConfigClient] 刷新配置失败: {e}")

    async def start(self):
        # 确保启动刷新任务时使用当前事件循环
        loop = asyncio.get_event_loop()
        loop.create_task(self._schedule_refresh())
        logger.info("[ConfigClient] Redis client config center started.")


config_client = ConfigClient(config_server_name="redis_config_center", refresh_time=5)

