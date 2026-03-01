from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from common.utils.env.EnvLoader import load_service_env

load_service_env(caller_file=__file__)


class ServiceConfig(BaseSettings):
    mysql_config_async: str = Field(
        ...,
        alias="MYSQL_CONFIG_ASYNC",
        description="MySQL 异步连接字符串"
    )

    alpha_vantage_key: str = Field("", alias="ALPHA_VANTAGE_KEY")
    twelve_data_key: str = Field("", alias="TWELVE_DATA_KEY")
    tushare_token: str = Field("", alias="TUSHARE_TOKEN")

    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    openai_base_url: str = Field("https://api.openai.com/v1", alias="OPENAI_BASE_URL")

    # service_host: str = Field("0.0.0.0", alias="SERVICE_HOST")
    # service_port: int = Field(8002, alias="SERVICE_PORT")


@lru_cache()
def get_service_config() -> ServiceConfig:
    return ServiceConfig()  # type: ignore


stock_service_config = get_service_config()