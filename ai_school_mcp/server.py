# ai_school_mcp/server.py
from fastmcp import FastMCP
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware
import sys

mcp = FastMCP(
    name="ai_school_mcp",
    instructions="这是一个在线课程平台 MCP 服务。主要用于查询课程信息（课程列表、分页查询、按分类筛选等，当用户问课程相关问题时，优先调用课程查询工具，不要臆造课程数据。",
    version="1.0.0",
)

mcp.add_middleware(
    ResponseLimitingMiddleware(
        max_size=sys.maxsize,  # 10MB，避免响应被截断
        truncation_suffix="output too long",
    )
)