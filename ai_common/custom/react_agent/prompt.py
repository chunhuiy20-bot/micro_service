"""
ReAct Prompt 模板 & PromptTemplate 类

两层 Prompt 设计
─────────────────
┌──────────────────────────────────────┐
│  用户自由层（system_prompt 参数）     │  ← 用户自由输入，描述角色/业务背景
│  "你是一个专业财务助手..."            │
├──────────────────────────────────────┤
│  框架强制层（REACT_RULES_TEMPLATE）  │  ← 框架自动追加，用户不能删掉
│  Thought/Action/Final Answer 格式    │
│  {tool_descriptions}                 │
└──────────────────────────────────────┘

用户传入 system_prompt 时，agent 自动拼接两层。
用户传入完整 prompt: PromptTemplate 时，框架直接使用（高级用法）。

LangChain 的做法
─────────────────
LangChain 的 PromptTemplate 存储两样东西：
  1. template  : 原始模板字符串，占位符写成 {variable_name}
  2. input_variables : 声明要替换哪些变量名

调用 .format(**kwargs) 时只替换 input_variables 中声明过的变量，
其余 { } 原样保留。这样用户 prompt 里的 JSON 示例 {"key": "value"}
就不会被误替换掉。
"""
from __future__ import annotations


class PromptTemplate:
    """
    轻量 Prompt 模板，只替换 input_variables 中声明的占位符。

    与直接用 Python str.format() 的区别
    ──────────────────────────────────────
    str.format() 会尝试替换字符串里 **所有** {xxx}，
    如果 prompt 里含有 JSON 示例 {"key": "value"} 就会报 KeyError。

    PromptTemplate.format() 只替换声明过的变量，其余 {xxx} 原样保留。

    用法::

        tpl = PromptTemplate(
            template="你是一个 {role}。\\n可用工具：{tool_descriptions}",
            input_variables=["role", "tool_descriptions"],
        )
        tpl.format(role="助手", tool_descriptions="- calc: 计算器")
    """

    def __init__(
        self,
        template: str,
        input_variables: list[str] | None = None,
    ) -> None:
        self.template = template
        self.input_variables: list[str] = input_variables or ["tool_descriptions"]

    def format(self, **kwargs: str) -> str:
        """只替换 input_variables 中声明的变量，其余 {xxx} 原样保留"""
        result = self.template
        for var in self.input_variables:
            placeholder = "{" + var + "}"
            value = kwargs.get(var, placeholder)   # 未传值时保留占位符
            result = result.replace(placeholder, value)
        return result

    def partial(self, **kwargs: str) -> "PromptTemplate":
        """
        预填充部分变量，返回剩余变量更少的新 PromptTemplate。

        用法::

            tpl = PromptTemplate(
                template="语言:{language}\\n工具:{tool_descriptions}",
                input_variables=["language", "tool_descriptions"],
            )
            cn_tpl = tpl.partial(language="中文")
            # cn_tpl 只剩 tool_descriptions 需要填充
            cn_tpl.format(tool_descriptions="- calc: 计算器")
        """
        remaining = [v for v in self.input_variables if v not in kwargs]
        return PromptTemplate(
            template=self.format(**kwargs),
            input_variables=remaining,
        )


# ── 框架强制层：ReAct 格式规则（用户不可删除）────────────────────────────────
# 这部分是 ReAct Agent 能正常工作的最小必要约束。
# 当用户传入自定义 system_prompt 时，框架会自动在其后追加这段规则。

REACT_RULES_TEMPLATE = """
    请严格按照以下格式循环推理，直到给出最终答案：
    
    Thought: 分析当前情况，决定下一步
    Action: tool_name
    Action Input: {"key": "value"}
    Observation: （工具执行结果，由系统填入，不要自己生成）
    ... （可循环多轮）
    Thought: 我已知道最终答案
    Final Answer: 最终回答
    
    ## 可用工具
    {tool_descriptions}
    
    ## 规则
    1. 每次只能调用一个工具
    2. Action 必须是上面工具列表中的名称
    3. Action Input 必须是合法 JSON
    4. 不要自己伪造 Observation，等待系统填入
    5. 无需工具时直接输出 Final Answer
"""

# ── 默认完整 Prompt（用户不传 system_prompt 时使用）────────────────────────────

DEFAULT_PROMPT = PromptTemplate(
    template="你是一个智能助手，使用 ReAct（推理+行动）框架解决问题。"
             + REACT_RULES_TEMPLATE,
    input_variables=["tool_descriptions"],
)

# LLM 遇到此标记停止生成，等待真实 Observation 注入
REACT_STOP_TOKENS = ["Observation:"]
