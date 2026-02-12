"""
文件名: ServiceConfig.py
作者: yangchunhui
创建日期: 2026/2/12
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/12
描述: 账户服务配置类，从环境变量加载服务配置

修改历史:
2026/2/12 - yangchunhui - 初始版本

依赖:
- pydantic_settings: 配置管理
- EmailConfig: 邮件配置类
- RedisConfig: Redis 配置类

配置项:
- MySQL: 数据库连接配置
- Redis: 缓存配置
- Email: 邮件发送配置
- Service: 服务监听配置
- JWT: 认证配置

使用示例:
from account_service.config import account_service_config

# 获取邮件配置
email_config = account_service_config.get_email_config()

# 获取 Redis 配置
redis_config = account_service_config.get_redis_config()
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from common.utils.env.EnvLoader import load_service_env
from common.utils.func.email.BaseEmailSender import EmailConfig
from common.utils.db.redis.AsyncRedisClient import RedisConfig

# 加载环境变量
load_service_env(caller_file=__file__)

class ServiceConfig(BaseSettings):
    """
    账户服务配置类
    从环境变量或 .env 文件加载配置
    """

    # MySQL 配置
    mysql_config_async: str = Field(
        ...,
        alias="MYSQL_CONFIG_ASYNC",
        description="MySQL 异步连接字符串"
    )

    # Redis 配置
    redis_host: str = Field(..., alias="HOST", description="Redis 主机地址")
    redis_port: int = Field(6379, alias="PORT", description="Redis 端口")
    redis_password: str = Field(..., alias="PASSWORD", description="Redis 密码")
    redis_database: int = Field(0, alias="DATABASE", description="Redis 数据库编号")

    # 邮件配置（可选）
    smtp_server: Optional[str] = Field(None, alias="SMTP_SERVER", description="SMTP 服务器地址")
    smtp_port: Optional[int] = Field(None, alias="SMTP_PORT", description="SMTP 端口")
    sender_email: Optional[str] = Field(None, alias="SENDER_EMAIL", description="发件人邮箱")
    sender_password: Optional[str] = Field(None, alias="SENDER_PASSWORD", description="发件人密码或授权码")
    sender_name: Optional[str] = Field(None, alias="SENDER_NAME", description="发件人显示名称")
    use_ssl: bool = Field(True, alias="USE_SSL", description="是否使用 SSL")

    # 服务配置
    service_host: str = Field("0.0.0.0", alias="SERVICE_HOST", description="服务监听地址")
    service_port: int = Field(8000, alias="SERVICE_PORT", description="服务监听端口")

    # JWT 配置（可选）
    jwt_secret_key: Optional[str] = Field(None, alias="JWT_SECRET_KEY", description="JWT 密钥")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM", description="JWT 算法")
    jwt_expire_minutes: int = Field(30, alias="JWT_EXPIRE_MINUTES", description="JWT 过期时间（分钟）")

    def get_email_config(self) -> EmailConfig:
        """
        方法说明: 获取邮件配置对象
        作者: yangchunhui
        创建时间: 2026/2/12
        修改历史:
        2026/2/12 - yangchunhui - 初始版本
        """
        if not all([self.smtp_server, self.smtp_port, self.sender_email, self.sender_password]):
            raise ValueError("邮件配置不完整，请检查 SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD")

        return EmailConfig(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            sender_email=self.sender_email,
            sender_password=self.sender_password,
            sender_name=self.sender_name or "系统通知",
            use_ssl=self.use_ssl
        )

    def get_redis_config(self) -> RedisConfig:
        """
        方法说明: 获取 Redis 配置对象
        作者: yangchunhui
        创建时间: 2026/2/12
        修改历史:
        2026/2/12 - yangchunhui - 初始版本
        """
        return RedisConfig(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            db=self.redis_database
        )



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
account_service_config = get_service_config()
