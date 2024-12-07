# Redis Config Center

[![GitHub release](https://img.shields.io/github/release/yourusername/redis-config-center.svg)](https://github.com/yourusername/redis-config-center/releases)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## 简介

Redis Config Center 是一个基于Redis实现的简易版配置中心，旨在支持不同节点动态分配不同的配置组。它模仿了Nacos的设计理念，提供了配置的发布、自动更新，获取，配置组隔离等功能，并且能够根据当前节点的机器ID自动分配对应的配置组。

### 实现背景
我们有一批能动态扩缩容的集群节点，需要为不同节点设置不同的配置组信息，除了支持常规的配置组动态刷新外，我们还希望能动态上下线配置组，并在上下线过程中，为节点自动分配新的配置组。

## 特性

- **配置管理**：通过Redis进行配置的存储和管理。
- **动态刷新**：客户端定时从服务器拉取最新的配置。
- **配置组隔离**：基于配置组隔离不同配置，可在环境变量中指定配置组。
- **IP路由/配置组动态分配**：当指定的配置组不存在或者被删除时，基于IP地址自动重新分配配置组，保证服务至少有一个配置组可用且无需重启。
- **异步非阻塞**: python 协程实现，非阻塞。
- **可扩展性强**：核心代码仅100行左右，高可读性与可扩展性

## 安装与使用

### 安装依赖

首先安装项目依赖：

```bash
pip install -r requirements.txt
```


### 使用方法

#### 发布配置 (服务端)

基于 `redis_config_server.py` 发布配置：

```python
import asyncio
from redis_config_server import config_server, ConfigGroup

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

基于 `redis_config_client.py` 启动配置中心客户端，并获取配置：

```python
import asyncio
from redis_config_client import config_client

async def test():
    await config_client.start()
    await asyncio.sleep(6)  # 等待足够的时间让配置刷新完成
    
    cur_config_group = config_client.get_config_group()
    test_val = config_client.get_config("test_key")
    
    print(f"客户端当前配置组信息为：{cur_config_group}")
    print(f"客户端当前配置'test_key'的值为：{test_val}")

if __name__ == "__main__":
    asyncio.run(test())

```

*完整测试用例可参考：redis_config_test.py*


## 贡献指南

我们欢迎任何形式的贡献！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与开发。

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

---

*注意：以上示例代码仅供参考，请根据实际需要调整。*


