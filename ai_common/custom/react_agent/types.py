"""
核心数据类型定义
  AgentAction  - 解析结果：继续调用工具
  AgentFinish  - 解析结果：得出最终答案
  AgentOutput  - Union 类型，parse() 的返回值
  AgentStep    - 一次完整工具调用记录（action + observation）
  AgentResult  - Agent 整体运行结果
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Union


@dataclass
class AgentAction:
    """解析结果：需要继续调用工具"""
    tool: str                    # 工具名称
    tool_input: dict[str, Any]   # 工具参数
    thought: str                 # 本轮 Thought 内容
    log: str                     # LLM 原始输出（用于调试）


@dataclass
class AgentFinish:
    """解析结果：已得出最终答案"""
    output: str   # Final Answer 内容
    log: str      # LLM 原始输出


# parse() 的返回类型：继续 or 结束
AgentOutput = Union[AgentAction, AgentFinish]


@dataclass
class AgentStep:
    """一次完整的工具调用记录"""
    action: AgentAction
    observation: str


@dataclass
class AgentResult:
    """Agent 运行最终结果"""
    final_answer: str
    steps: list[AgentStep] = field(default_factory=list)
    total_tokens: int = 0
