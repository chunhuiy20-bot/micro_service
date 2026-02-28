"""
输出解析器
  OutputParserException  - 解析失败异常
  OutputParser           - 抽象基类，可继承替换
  ReActOutputParser      - 标准 ReAct 格式解析器
"""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod

from .types import AgentAction, AgentFinish, AgentOutput


class OutputParserException(Exception):
    """LLM 输出不符合 ReAct 格式时抛出"""
    pass


class OutputParser(ABC):
    """
    输出解析器抽象基类。

    继承此类可完全替换解析逻辑，例如：
      - 支持 XML 格式的工具调用
      - 支持 JSON-only 输出
      - 集成 Structured Output
    """

    @abstractmethod
    def parse(self, text: str) -> AgentOutput:
        """
        将 LLM 原始输出解析为 AgentAction 或 AgentFinish。

        :raises OutputParserException: 格式不合法时抛出
        """
        ...


class ReActOutputParser(OutputParser):
    """
    标准 ReAct 文本格式解析器。

    期望格式::

        Thought: 分析...
        Action: tool_name
        Action Input: {"key": "value"}
        ── 或 ──
        Thought: 我知道答案了
        Final Answer: 最终回答
    """

    _FINAL_ANSWER_PREFIX = "Final Answer:"
    _RE_THOUGHT = re.compile(r"Thought:\s*(.+?)(?=Action:|Final Answer:|$)", re.DOTALL)
    _RE_ACTION = re.compile(r"Action:\s*(\S+)")
    _RE_ACTION_INPUT = re.compile(r"Action Input:\s*(\{.+?\})", re.DOTALL)

    def parse(self, text: str) -> AgentOutput:
        # ── 1. Final Answer ──────────────────────────────────────────
        if self._FINAL_ANSWER_PREFIX in text:
            idx = text.index(self._FINAL_ANSWER_PREFIX) + len(self._FINAL_ANSWER_PREFIX)
            return AgentFinish(output=text[idx:].strip(), log=text)

        # ── 2. Action ────────────────────────────────────────────────
        action_match = self._RE_ACTION.search(text)
        if not action_match:
            raise OutputParserException(
                "找不到 'Action:' 标记。\n"
                f"请按格式输出。原始内容：\n{text!r}"
            )
        tool_name = action_match.group(1).strip()

        # ── 3. Action Input ──────────────────────────────────────────
        input_match = self._RE_ACTION_INPUT.search(text)
        if not input_match:
            raise OutputParserException(
                "找不到 'Action Input:' 中的 JSON 对象。\n"
                f"请确保格式为 Action Input: {{\"key\": \"value\"}}。\n原始内容：\n{text!r}"
            )
        try:
            tool_input: dict = json.loads(input_match.group(1))
        except json.JSONDecodeError as e:
            raise OutputParserException(f"Action Input 不是合法 JSON：{e}") from e

        # ── 4. Thought（可选）────────────────────────────────────────
        thought = ""
        thought_match = self._RE_THOUGHT.search(text)
        if thought_match:
            thought = thought_match.group(1).strip()

        return AgentAction(
            tool=tool_name,
            tool_input=tool_input,
            thought=thought,
            log=text,
        )
