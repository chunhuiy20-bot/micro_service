
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from common.utils.env.EnvLoader import load_service_env


# 加载环境变量
load_service_env(caller_file=__file__)

class ServiceConfig(BaseSettings):
    """
    账户服务配置类
    从环境变量或 .env 文件加载配置
    """

    #token 配置
    auth_token: str = Field(...,alias="AUTH_TOKEN",description="认证授权token")
    base_url: str = Field(...,alias="BASE_URL",description="ai_school的基础url")





@lru_cache()
def get_service_config() -> ServiceConfig:
    """
    方法说明: 获取服务配置单例（使用 lru_cache 确保配置只加载一次）
    作者: yangchunhui
    创建时间: 2026/2/12
    修改历史:
    2026/2/12 - yangchunhui - 初始版本
    """
    return ServiceConfig()  # type: ignore


# 导出配置实例
ai_school_mcp_service_config = get_service_config()
