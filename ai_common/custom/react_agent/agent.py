"""
ReactAgent 核心（插件化重设计版）

设计要点
─────────
1. parse() 返回 AgentAction | AgentFinish，用 isinstance 分支，类型清晰
2. output_parser 参数可替换任意 OutputParser 子类
3. callbacks 列表可注入任意 AgentCallback，不改源码加日志/监控
4. handle_parsing_errors=True 时，解析失败自动将错误作为 Observation
   反馈给 LLM，让它修正格式后继续，而不是直接崩溃
"""
from __future__ import annotations

from openai import OpenAI

from .callback import AgentCallback
from .parser import OutputParser, OutputParserException, ReActOutputParser
from .prompt import DEFAULT_PROMPT, REACT_STOP_TOKENS, REACT_RULES_TEMPLATE, PromptTemplate
from .tool import Tool, ToolRegistry
from .types import AgentAction, AgentFinish, AgentResult, AgentStep


class ReactAgent:
    """
    插件化 ReAct Agent

    用法示例::

        from ai_common.react_agent import ReactAgent, LoggingCallback
        from ai_common.custom import CalculatorTool

        agent = ReactAgent(
            api_key="sk-...",
            model="gpt-4o-mini",
            callbacks=[LoggingCallback()],
            handle_parsing_errors=True,
        )
        agent.register_tool(CalculatorTool())
        result = agent.run("123 * 456 = ?")
        print(result.final_answer)
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str | None = None,
        max_steps: int = 10,
        temperature: float = 0.0,
        system_prompt: str | None = None,
        prompt: PromptTemplate | None = None,
        output_parser: OutputParser | None = None,
        callbacks: list[AgentCallback] | None = None,
        handle_parsing_errors: bool = False,
    ) -> None:
        """
        参数优先级（由高到低）：

        prompt（完整 PromptTemplate）
          > system_prompt（用户自由文本，框架自动追加 ReAct 规则）
          > 默认 Prompt

        :param system_prompt: 用户自由输入的角色/背景描述，无需包含 ReAct 格式规则，
                              框架会自动在其后追加 Thought/Action/Final Answer 等规范。
        :param prompt:        高级用法，传入完整 PromptTemplate，框架直接使用，
                              适合需要完全控制格式的场景（需自行保证包含 ReAct 规则）。
        """
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._max_steps = max_steps
        self._temperature = temperature
        self._parser: OutputParser = output_parser or ReActOutputParser()
        self._callbacks: list[AgentCallback] = callbacks or []
        self._handle_parsing_errors = handle_parsing_errors
        self._registry = ToolRegistry()

        # 按优先级确定最终 Prompt
        if prompt is not None:
            # 高级：用户提供完整模板，直接使用
            self._prompt = prompt
        elif system_prompt is not None:
            # 普通：用户只写角色描述，框架自动追加 ReAct 规则
            self._prompt = PromptTemplate(
                template=system_prompt + REACT_RULES_TEMPLATE,
                input_variables=["tool_descriptions"],
            )
        else:
            self._prompt = DEFAULT_PROMPT

    def register_tool(self, tool: Tool) -> "ReactAgent":
        """注册工具，支持链式调用"""
        self._registry.register(tool)
        return self

    # ── 公开入口 ────────────────────────────────────────────────────────────

    def run(self, user_input: str) -> AgentResult:
        self._emit("on_agent_start", user_input)
        messages = [
            {
                "role": "system",
                "content": self._prompt.format(
                    tool_descriptions=self._registry.all_descriptions()
                ),
            },
            {"role": "user", "content": user_input},
        ]

        steps: list[AgentStep] = []
        total_tokens = 0

        for step_num in range(1, self._max_steps + 1):
            # ── 1. 调用 LLM ────────────────────────────────────────────────
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                stop=REACT_STOP_TOKENS,
            )
            llm_output = response.choices[0].message.content or ""
            total_tokens += response.usage.total_tokens if response.usage else 0
            self._emit("on_llm_end", llm_output, step_num)

            # ── 2. 解析 → AgentAction | AgentFinish ────────────────────────
            try:
                parsed = self._parser.parse(llm_output)
            except OutputParserException as e:
                self._emit("on_parse_error", e, step_num)
                if not self._handle_parsing_errors:
                    raise
                # 把解析错误作为 Observation 反馈给 LLM，让它修正格式
                error_obs = f"格式解析失败：{e}。请严格按照 ReAct 格式重新输出。"
                messages.append(
                    {"role": "assistant", "content": llm_output + f"Observation: {error_obs}\n"}
                )
                continue

            # ── 3. AgentFinish → 返回结果 ───────────────────────────────────
            if isinstance(parsed, AgentFinish):
                result = AgentResult(
                    final_answer=parsed.output,
                    steps=steps,
                    total_tokens=total_tokens,
                )
                self._emit("on_agent_finish", result)
                return result

            # ── 4. AgentAction → 执行工具 ───────────────────────────────────
            self._emit("on_tool_start", parsed)
            observation = self._execute_tool(parsed)
            step = AgentStep(action=parsed, observation=observation)
            self._emit("on_tool_end", step)
            steps.append(step)

            # 将本轮内容追加到消息历史
            messages.append(
                {"role": "assistant", "content": llm_output + f"Observation: {observation}\n"}
            )

        # ── 超出最大步数 ─────────────────────────────────────────────────────
        result = AgentResult(
            final_answer="已达到最大推理步数，未能得出答案。",
            steps=steps,
            total_tokens=total_tokens,
        )
        self._emit("on_agent_finish", result)
        return result

    # ── 私有方法 ────────────────────────────────────────────────────────────

    def _execute_tool(self, action: AgentAction) -> str:
        tool = self._registry.get(action.tool)
        if tool is None:
            available = ", ".join(self._registry.names()) or "无"
            return f"错误：工具 '{action.tool}' 不存在。可用工具：{available}"
        try:
            return str(tool.run(**action.tool_input))
        except Exception as e:
            return f"工具执行出错：{e}"

    def _emit(self, hook: str, *args) -> None:
        for cb in self._callbacks:
            getattr(cb, hook)(*args)
