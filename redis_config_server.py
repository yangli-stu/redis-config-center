import logging
import os
from typing import Optional

from pydantic import BaseModel

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
REDIS_URL = os.getenv("REDIS_URL", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# 配置 Redis 客户端
import valkey.asyncio as avalkey

try:
    redis_client = avalkey.Valkey(
        host=REDIS_URL,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        max_connections=10
    )
except Exception as e:
    logger.error(f"[Redis Config Center] 初始化 Redis 客户端失败: {e}")
    raise


class ConfigGroup(BaseModel):
    group_name: str
    group_version: int
    config_dict: Optional[dict] = None


class ConfigServer:
    def __init__(self, config_server_name: str):
        self.config_server_name = config_server_name

    async def insert_config_group(self, config_group: ConfigGroup):
        try:
            # 如果配置组存在，则增加版本号
            existing_config_group = await self.get_config_group(config_group.group_name)
            if existing_config_group:
                config_group.group_version = existing_config_group.group_version + 1
            else:
                config_group.group_version = 0

            await redis_client.hset(self.config_server_name, config_group.group_name, config_group.model_dump_json())
            logger.info(f"[ConfigServer] 配置组 {config_group.group_name} 已（添加/更新）")
        except Exception as e:
            logger.error(f"[ConfigServer]（添加/更新） 配置组失败: {e}")

    async def get_config_group(self, group_name: str) -> Optional[ConfigGroup]:
        try:
            config_group_data = await redis_client.hget(self.config_server_name, group_name)
            if config_group_data:
                return ConfigGroup.model_validate_json(config_group_data)
            logger.warning(f"[ConfigServer] 配置组 {group_name} 不存在")
        except Exception as e:
            logger.error(f"[ConfigServer] 获取配置组失败: {e}")
        return None

    async def delete_config_group(self, group_name: str):
        try:
            await redis_client.hdel(self.config_server_name, group_name)
            logger.info(f"[ConfigServer] 配置组 {group_name} 已删除")
        except Exception as e:
            logger.error(f"[ConfigServer] 删除配置组失败: {e}")

    async def get_all_config_groups(self):
        try:
            keys = sorted(await redis_client.hkeys(self.config_server_name))
            groups = [await config_server.get_config_group(key.decode('utf-8')) for key in keys]
            return [g for g in groups if g is not None]
        except Exception as e:
            logger.error(f"[ConfigServer] 获取所有配置组失败: {e}")
            return []


config_server = ConfigServer(config_server_name="rcc::redis_config_center")

