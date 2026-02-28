"""
Tool 基类 & 工具注册器（与 custom/ 接口一致）
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """工具抽象基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称，Agent 用此名称调用"""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """
        工具说明，写入 Prompt 告诉 LLM 何时用、怎么用。
        建议包含 Action Input 格式示例。
        """
        ...

    @abstractmethod
    def run(self, **kwargs: Any) -> str:
        """执行工具，返回字符串结果"""
        ...

    def to_prompt_line(self) -> str:
        return f"- {self.name}: {self.description}"


class ToolRegistry:
    """工具注册表"""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> "ToolRegistry":
        self._tools[tool.name] = tool
        return self

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def all_descriptions(self) -> str:
        if not self._tools:
            return "（暂无可用工具）"
        return "\n".join(f"- {t.name}: {t.description}" for t in self._tools.values())
