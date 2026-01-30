# routers/proxy.py
from fastapi import APIRouter, Request, HTTPException, Response
import httpx
from gateway.core.config import config

router = APIRouter()


@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    print(f"🔍 请求服务: {service}, 路径: {path}")
    target = config.SERVICE_URLS_DICT.get(service)
    if not target:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")

    try:
        # 过滤掉不应该转发的请求头
        headers_to_forward = {
            k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v
            for k, v in request.headers.raw
            if k.lower() not in [b'host', b'connection', b'content-length']
        }

        # 添加请求追踪 ID，实现分布式追踪
        from gateway.core.context import request_id_ctx
        request_id = request_id_ctx.get()
        if request_id:
            headers_to_forward["X-Request-Id"] = request_id

        print(f"请求头：{headers_to_forward}")

        async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT) as client:
            print(f"请求路径：{target}/{path}")
            resp = await client.request(
                request.method,
                f"{target}/{path}",
                headers=headers_to_forward,
                content=await request.body(),
                params=request.query_params
            )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )
    except httpx.TimeoutException:
        raise HTTPException(504, "Upstream service timeout")

    except httpx.RequestError:
        raise HTTPException(502, "Bad gateway")
