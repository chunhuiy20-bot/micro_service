# ai_school_mcp/main.py
from ai_school_mcp.server import mcp
import ai_school_mcp.course_mcp.CourseMcp  # 触发工具注册
import ai_school_mcp.question_mcp.QuestionMCP
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8100)