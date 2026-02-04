# os.getenv() 只能读取系统环境变量，而不会自动读取 .env 文件中的配置。需要使用 python-dotenv 库来加载 .env 文件
import json
import os
import socket
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Dict

from common.utils.nacos.NacosRegistry import NacosConfig

# 获取当前文件所在目录的父目录（即 gateway 目录）
BASE_DIR = Path(__file__).resolve().parent.parent
# 制定读取的.env
load_dotenv(dotenv_path=f"{BASE_DIR}/.env")

# 导入 NacosConfig


class Config:
    """网关配置类"""

    # 服务地址配置
    SERVICE_URLS_DICT = json.loads(os.getenv("SERVICE_URLS_DICT"))

    # 请求超时配置
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT"))

    # ==================== Nacos 配置对象 ====================
    NACOS_CONFIG: Optional[NacosConfig] = None
    
    @classmethod
    def _init_nacos_config(cls):
        """初始化 Nacos 配置对象"""
        try:
            cls.NACOS_CONFIG = NacosConfig(
                server_addresses=os.getenv("NACOS_SERVER_ADDRESSES", "127.0.0.1:8848"),
                namespace=os.getenv("NACOS_NAMESPACE", ""),
                service_name=os.getenv("NACOS_SERVICE_NAME", "gateway-service"),
                service_ip=os.getenv("NACOS_SERVICE_IP") or socket.gethostbyname(socket.gethostname()),
                service_port=int(os.getenv("NACOS_SERVICE_PORT", "8000")),
                group_name=os.getenv("NACOS_GROUP_NAME", "DEFAULT_GROUP"),
                weight=float(os.getenv("NACOS_WEIGHT", "1.0")),
                metadata=json.loads(os.getenv("NACOS_METADATA", '{"version": "1.0.0", "env": "prod"}')),
                username=os.getenv("NACOS_USERNAME"),
                password=os.getenv("NACOS_PASSWORD"),
                heartbeat_interval=int(os.getenv("NACOS_HEARTBEAT_INTERVAL", "5")),
                enabled=os.getenv("NACOS_ENABLED", "true").lower() in ("true", "1", "yes"),
                ephemeral=os.getenv("NACOS_EPHEMERAL", "true").lower() in ("true", "1", "yes"),
                max_retries=int(os.getenv("NACOS_MAX_RETRIES", "3")),
                retry_delay=int(os.getenv("NACOS_RETRY_DELAY", "5")),
            )
        except Exception as e:
            raise ValueError(f"Nacos 配置初始化失败: {e}")

    @classmethod
    def validate(cls):
        """验证必需的配置项"""
        required_fields = ["SERVICE_URLS_DICT"]
        missing = [field for field in required_fields if not getattr(cls, field)]
        if missing:
            raise ValueError(f"缺少必需的配置项: {', '.join(missing)}")
        
        # 初始化 Nacos 配置
        cls._init_nacos_config()
        
        # 验证 Nacos 配置是否成功初始化
        if cls.NACOS_CONFIG is None:
            raise ValueError("Nacos 配置初始化失败")


# 实例化配置（单例模式）
config = Config()

# 启动时验证配置
config.validate()