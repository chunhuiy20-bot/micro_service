# middleware/trace.py
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from gateway.core.context import request_id_ctx


class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        print(f"赋追踪 的 trace id: {rid}")
        request_id_ctx.set(rid)

        response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        return response
