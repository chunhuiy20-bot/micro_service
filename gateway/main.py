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
from fastapi import FastAPI
from gateway.middleware.trace import TraceMiddleware
from gateway.router.proxy import router as proxy_router

app = FastAPI(title="Logic Gateway")

app.add_middleware(TraceMiddleware)
app.include_router(proxy_router)