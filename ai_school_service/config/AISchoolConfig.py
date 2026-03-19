"""
文件名: AISchoolConfig.py
作者: yangchunhui
创建日期: 2026/3/19
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/3/19
描述: AI School 服务配置类，从环境变量加载服务配置

修改历史:
2026/3/19 - yangchunhui - 初始版本

依赖:
- pydantic_settings: 配置管理

配置项:
- OpenAI: API 密钥和接口地址配置

使用示例:
from ai_school_service.config.AISchoolConfig import ai_school_config

# 获取 OpenAI 客户端
client = ai_school_config.get_openai_client()
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from openai import OpenAI
from common.utils.env.EnvLoader import load_service_env

# 加载环境变量
load_service_env(caller_file=__file__)


class AISchoolConfig(BaseSettings):
    """
    AI School 服务配置类
    从环境变量或 .env 文件加载配置
    """

    # OpenAI 配置
    openai_api_key: str = Field(
        ...,
        alias="OPENAI_API_KEY",
        description="OpenAI API 密钥"
    )
    openai_base_url: str = Field(
        "https://api.openai.com/v1",
        alias="OPENAI_BASE_URL",
        description="OpenAI API 接口地址"
    )

    # AI School Java 服务配置
    aischool_base_url: str = Field(
        ...,
        alias="AISCHOOL_BASE_URL",
        description="AI School Java 服务地址"
    )
    aischool_token: str = Field(
        ...,
        alias="AISCHOOL_TOKEN",
        description="AI School Java 服务认证 Token"
    )

    def get_openai_client(self) -> OpenAI:
        """
        方法说明: 获取 OpenAI 客户端实例
        作者: yangchunhui
        创建时间: 2026/3/19
        修改历史:
        2026/3/19 - yangchunhui - 初始版本
        """
        return OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_base_url,
        )


@lru_cache()
def get_ai_school_config() -> AISchoolConfig:
    """
    方法说明: 获取服务配置单例（使用 lru_cache 确保配置只加载一次）
    作者: yangchunhui
    创建时间: 2026/3/19
    修改历史:
    2026/3/19 - yangchunhui - 初始版本
    """
    return AISchoolConfig()  # type: ignore


# 导出配置实例
ai_school_config = get_ai_school_config()
