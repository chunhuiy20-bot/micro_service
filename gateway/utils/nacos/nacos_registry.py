# gateway/utils/nacos_registry.py

"""
Nacos 服务注册通用工具类
支持 FastAPI 应用的服务注册、心跳保活、优雅下线
"""
import asyncio
import socket
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, TYPE_CHECKING
from fastapi import FastAPI
import nacos
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from gateway.core.config import Config


class NacosConfig(BaseModel):
    """Nacos 配置"""
    server_addresses: str = Field(default="127.0.0.1:8848", description="Nacos 服务器地址")
    namespace: str = Field(default="", description="命名空间 ID")
    service_name: str = Field(..., description="服务名称")
    service_ip: Optional[str] = Field(default=None, description="服务 IP，默认自动获取")
    service_port: int = Field(..., description="服务端口")
    group_name: str = Field(default="DEFAULT_GROUP", description="服务分组")
    weight: float = Field(default=1.0, description="权重")
    metadata: Dict[str, str] = Field(default_factory=dict, description="元数据")
    username: Optional[str] = Field(default=None, description="Nacos 用户名")
    password: Optional[str] = Field(default=None, description="Nacos 密码")
    heartbeat_interval: int = Field(default=5, description="心跳间隔（秒）")
    enabled: bool = Field(default=True, description="是否启用 Nacos 注册")
    ephemeral: bool = Field(default=True, description="是否为临时实例")

    def __init__(self, **data):
        super().__init__(**data)
        # 自动获取本机 IP
        if not self.service_ip:
            self.service_ip = socket.gethostbyname(socket.gethostname())




class NacosRegistry:
    """Nacos 服务注册管理器"""

    def __init__(self, config: NacosConfig):
        self.config = config
        self.client: Optional[nacos.NacosClient] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

    def _create_client(self) -> nacos.NacosClient:
        """创建 Nacos 客户端"""
        client_kwargs = {
            "server_addresses": self.config.server_addresses,
            "namespace": self.config.namespace,
        }
        
        # 只有在提供了用户名和密码时才添加认证信息
        if self.config.username and self.config.password:
            client_kwargs["username"] = self.config.username
            client_kwargs["password"] = self.config.password
        
        return nacos.NacosClient(**client_kwargs)

    async def register(self) -> bool:
        """注册服务到 Nacos"""
        if not self.config.enabled:
            print(f"[Nacos] 注册已禁用，服务 {self.config.service_name} 正常启动")
            return False

        print(f"[Nacos] 正在注册服务: {self.config.service_name}")
        try:
            self.client = self._create_client()
            
            self.client.add_naming_instance(
                service_name=self.config.service_name,
                ip=self.config.service_ip,
                port=self.config.service_port,
                group_name=self.config.group_name,
                weight=self.config.weight,
                metadata=self.config.metadata,
                enable=True,
                healthy=True,
                ephemeral=self.config.ephemeral
            )
            
            print(f"[Nacos] 服务注册成功: {self.config.service_ip}:{self.config.service_port}")
            
            # 启动心跳任务
            self._heartbeat_task = asyncio.create_task(self._send_heartbeat())
            return True
            
        except Exception as e:
            print(f"[Nacos] 注册失败: {e}")
            print(f"[Nacos] 服务 {self.config.service_name} 将在没有 Nacos 注册的情况下继续运行")
            self.client = None
            return False

    async def deregister(self) -> bool:
        """从 Nacos 注销服务"""
        # 停止心跳任务
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # 注销服务
        if self.client:
            try:
                print(f"[Nacos] 正在注销服务: {self.config.service_name}")
                self.client.remove_naming_instance(
                    service_name=self.config.service_name,
                    ip=self.config.service_ip,
                    port=self.config.service_port,
                    group_name=self.config.group_name
                )
                print(f"[Nacos] 服务注销成功")
                return True
            except Exception as e:
                print(f"[Nacos] 注销失败: {e}")
                return False
        return False

    async def _send_heartbeat(self):
        """发送心跳到 Nacos"""
        while True:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                if self.client:
                    self.client.send_heartbeat(
                        service_name=self.config.service_name,
                        ip=self.config.service_ip,
                        port=self.config.service_port,
                        group_name=self.config.group_name
                    )
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Nacos] 心跳发送失败: {e}")

    def is_registered(self) -> bool:
        """检查服务是否已注册"""
        return self.client is not None

    @asynccontextmanager
    async def lifespan_context(self, app: FastAPI):
        """FastAPI 生命周期上下文管理器"""
        # 启动时注册
        await self.register()
        
        yield
        
        # 关闭时注销
        await self.deregister()


def create_nacos_lifespan(config: NacosConfig):
    """
    创建 Nacos 生命周期管理器的工厂函数
    
    使用示例:
        config = NacosConfig(
            service_name="my-service",
            service_port=8000
        )
        app = FastAPI(lifespan=create_nacos_lifespan(config))
    """
    registry = NacosRegistry(config)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with registry.lifespan_context(app):
            # 将 registry 实例附加到 app.state，方便后续访问
            app.state.nacos_registry = registry
            yield
    
    return lifespan