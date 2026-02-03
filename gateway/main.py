"""
    这里所谓的网关是指的逻辑网关，而不是java概念中的流量网关
    逻辑网关只负责：
        1、BFF（Backend For Frontend）
        2、聚合多个服务，路由到不同后端服务
        3、权限判断
        4、少量兜底（重试、超时）
        FastAPI 逻辑网关实现
            + httpx (异步服务调用)
            + Pydantic (请求/响应契约)
            + Tenacity (重试 & 兜底)
            + ContextVar (请求上下文)
"""
from fastapi import FastAPI, Request
from gateway.middleware.trace import TraceMiddleware
from gateway.router.proxy import router as proxy_router
from gateway.core.config import config
from gateway.utils.nacos.nacos_registry import create_nacos_lifespan

# 创建 FastAPI 应用，使用 Nacos 生命周期管理
app = FastAPI(
    title="Logic Gateway",
    lifespan=create_nacos_lifespan(config.NACOS_CONFIG)
)

app.add_middleware(TraceMiddleware)
app.include_router(proxy_router)


@app.get("/health")
async def health_check(request: Request):
    """健康检查接口"""
    # 从 app.state 获取 nacos_registry 实例
    registry = getattr(request.app.state, "nacos_registry", None)
    nacos_config = config.NACOS_CONFIG

    return {
        "status": "UP",
        "nacos_enabled": nacos_config.enabled if nacos_config else False,
        "nacos_registered": registry.is_registered() if registry else False,
        "service": {
            "name": nacos_config.service_name if nacos_config else "unknown",
            "ip": nacos_config.service_ip if nacos_config else "unknown",
            "port": nacos_config.service_port if nacos_config else 0
        }
    }