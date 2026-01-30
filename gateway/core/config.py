# os.getenv() 只能读取系统环境变量，而不会自动读取 .env 文件中的配置。需要使用 python-dotenv 库来加载 .env 文件
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# 获取当前文件所在目录的父目录（即 gateway 目录）
BASE_DIR = Path(__file__).resolve().parent.parent
# 制定读取的.env
load_dotenv(dotenv_path=f"{BASE_DIR}/.env")


class Config:
    """网关配置类"""

    # 服务地址配置
    SERVICE_URLS_DICT = json.loads(os.getenv("SERVICE_URLS_DICT"))

    # 请求超时配置
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT"))


    @classmethod
    def validate(cls):
        """验证必需的配置项"""
        required_fields = ["SERVICE_URLS_DICT"]
        missing = [field for field in required_fields if not getattr(cls, field)]
        if missing:
            raise ValueError(f"缺少必需的配置项: {', '.join(missing)}")


# 实例化配置（单例模式）
config = Config()
print(config.SERVICE_URLS_DICT)

# 启动时验证配置
config.validate()
