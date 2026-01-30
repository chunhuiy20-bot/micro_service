from contextvars import ContextVar

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
user_id_ctx: ContextVar[int | None] = ContextVar("user_id", default=None)
