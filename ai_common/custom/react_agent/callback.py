"""
回调系统
  AgentCallback       - 抽象基类，所有钩子默认空实现
  LoggingCallback     - 打印每步推理过程（彩色控制台输出）
  StepTrackerCallback - 记录所有 LLM 原始输出，用于调试/测试
"""
from __future__ import annotations

from .types import AgentAction, AgentStep, AgentResult


class AgentCallback:
    """
    Agent 回调基类，所有钩子默认为空实现，按需重写。

    钩子触发顺序::

        on_agent_start
          └── [loop]
                on_llm_end
                on_parse_error  (仅当解析失败且 handle_parsing_errors=True)
                on_tool_start
                on_tool_end
          └── [end]
        on_agent_finish
    """

    def on_agent_start(self, user_input: str) -> None:
        """Agent 开始处理用户输入"""

    def on_llm_end(self, output: str, step_num: int) -> None:
        """LLM 生成完一次输出"""

    def on_tool_start(self, action: AgentAction) -> None:
        """即将执行工具"""

    def on_tool_end(self, step: AgentStep) -> None:
        """工具执行完毕，拿到 Observation"""

    def on_parse_error(self, error: Exception, step_num: int) -> None:
        """输出解析失败（handle_parsing_errors=True 时会重试）"""

    def on_agent_finish(self, result: AgentResult) -> None:
        """Agent 运行结束"""


# ── 内置实现 ────────────────────────────────────────────────────────────────

class LoggingCallback(AgentCallback):
    """
    将推理过程格式化打印到控制台。

    示例输出::

        [Agent] 开始：请计算 1+1
        ── Step 1 ─────────────────
        [LLM] Thought: 需要计算...
              Action: calculator
        [Tool] calculator({expression: "1+1"})
        [Obs]  2
        ── Finish ─────────────────
        [Agent] 3 步完成，消耗 820 tokens
    """

    _SEP = "─" * 40

    def on_agent_start(self, user_input: str) -> None:
        print(f"\n[Agent] 开始：{user_input}")

    def on_llm_end(self, output: str, step_num: int) -> None:
        print(f"\n── Step {step_num} {self._SEP[:30]}")
        print(f"[LLM]\n{output.strip()}")

    def on_tool_start(self, action: AgentAction) -> None:
        print(f"[Tool] {action.tool}({action.tool_input})")

    def on_tool_end(self, step: AgentStep) -> None:
        print(f"[Obs]  {step.observation}")

    def on_parse_error(self, error: Exception, step_num: int) -> None:
        print(f"[ParseError step={step_num}] {error}")

    def on_agent_finish(self, result: AgentResult) -> None:
        print(f"\n── Finish {self._SEP[:29]}")
        print(f"[Agent] {len(result.steps)} 步完成，消耗 {result.total_tokens} tokens")


class StepTrackerCallback(AgentCallback):
    """
    记录所有 LLM 原始输出和解析错误，方便单测断言或离线分析。

    用法::

        tracker = StepTrackerCallback()
        agent = ReactAgent(..., callbacks=[tracker])
        agent.run("...")
        print(tracker.llm_outputs)
        print(tracker.parse_errors)
    """

    def __init__(self) -> None:
        self.llm_outputs: list[str] = []
        self.parse_errors: list[str] = []

    def on_llm_end(self, output: str, step_num: int) -> None:
        self.llm_outputs.append(output)

    def on_parse_error(self, error: Exception, step_num: int) -> None:
        self.parse_errors.append(f"[step={step_num}] {error}")

    def reset(self) -> None:
        self.llm_outputs.clear()
        self.parse_errors.clear()
