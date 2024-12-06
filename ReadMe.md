# Redis Config Center

[![GitHub release](https://img.shields.io/github/release/yourusername/redis-config-center.svg)](https://github.com/yourusername/redis-config-center/releases)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## 简介

Redis Config Center 是一个基于Redis实现的简易配置中心，旨在支持不同节点分配不同的配置组。它模仿了Nacos的设计理念，提供了配置的发布、自动更新和获取功能，并且能够根据当前节点的机器ID自动选择对应的配置组。

## 特性

- **配置管理**：通过Redis进行配置的存储和管理。
- **动态刷新**：客户端定时从服务器拉取最新的配置。
- **IP路由**：当特定配置组不存在时，基于IP地址分配配置组。
- **默认配置**：提供一个默认配置组，确保所有节点至少有一个可用配置。
- **异步非阻塞**: python 协程实现，非阻塞。

## 安装与使用

### 安装依赖

首先安装项目依赖：

```bash
pip install -r requirements.txt
```


### 使用方法

#### 发布配置 (服务端)

在 `redis_config_server.py` 中定义并启动配置服务器：

```python
from redis_config_server import config_server

async def test():
    await config_server.insert_config_group(
        ConfigGroup(group_name="default", group_version="1", config_dict={"key1": "value1"}))
    # ... 插入其他配置组 ...
    
    print(await config_server.get_config_group("default"))
    # ... 获取其他配置组 ...

if __name__ == "__main__":
    asyncio.run(test())
```

#### 获取配置 (客户端)

在 `redis_config_client.py` 中定义并启动配置客户端：

```python
from redis_config_client import config_client

config_client.start()
await asyncio.sleep(6)  # 等待足够的时间让配置刷新完成
cur_config_group = await config_client.get_config_group()
print(f"客户端当前配置为：{cur_config_group}")
```

*完整测试用例可参考：redis_config_server.py:64*

### 注意事项
- **错误处理**：虽然这里没有详细列出，但在实际应用中应当加入适当的错误处理逻辑，以提高系统的健壮性。
- **日志记录**：推荐使用Python的`logging`模块代替简单的`print`语句来进行日志记录，以便于管理和分析日志信息。


## 贡献指南

我们欢迎任何形式的贡献！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与开发。

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

---

*注意：以上示例代码仅供参考，请根据实际需要调整。*


