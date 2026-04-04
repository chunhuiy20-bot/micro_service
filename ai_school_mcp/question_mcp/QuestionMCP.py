from fastmcp import Context
from ai_school_mcp.config.ServiceConfig import token_ctx
from ai_school_mcp.decorators.require_auth import require_auth
from ai_school_mcp.question_mcp.remote_call.QuestionRemoteCallClient import QuestionRemoteCallClientService
from ai_school_mcp.question_mcp.schemas.QuestionParams import Paper, GetTopicsParams, GetCommandWordParams, \
    GetAllPaperModel
from ai_school_mcp.server import mcp
from common.schemas.CommonResult import Result


@mcp.tool()
@require_auth
def upload_paper(params: Paper, ctx: Context):
    """
    将试卷解析后的结构化题目数据录入题库（严格按 Paper 模型）。

    调用前建议流程：
    1) 先调用 `get_command_word_by_subject` 获取该科目可用的 `command_word` 编号
    2) 先调用 `get_topics_by_paper_name` 获取该 paper 对应可用的 `topics/sub_topics`
    3) 再调用本工具 `upload_paper`

    重要：参数命名必须使用 snake_case，且字段结构必须与 Pydantic `Paper` 模型一致。
    - 不要使用驼峰命名（如 `isCorrect`、`optionKey`）
    - 不要把对象字段写成字符串或错误类型

    ====================
    一、顶层参数（Paper）
    ====================
    - education_system: str
      例如 "A-Level"、"AP"
    - exam_board: str (枚举)
      仅允许: "CIE" | "Edexcel" | "AQA" | "OCR"
    - subject: str (枚举)
      例如 "Economics"、"Mathematics"、"Business" 等，必须为 Subject 枚举值
    - component: str
      例如 "Pure Mathematics P1"、"Introduction to Markets and Market Failure"
    - syllabus_code: str
      例如 "9709/12"、"8EC0/01"
    - year: int
      范围 2000~2600
    - session: str (枚举)
      仅允许: "May/June" | "October/November" | "February/March"
    - duration_minutes: int
      >= 30
    - total_marks: int
      >= 0
    - sections: List[Section]
      至少 1 个 section
    - paper_pdf_urls: List[str]
      试卷原卷 URL 列表（可空，但建议提供）

    ====================
    二、Section 结构
    ====================
    - section_label: str
      例如 "Section A"、"Section B"
    - instructions: str | null
      本区作答说明
    - required_questions: int | null
      本区需作答题目数量；null 表示“全部作答”
      注意：不能写字符串 "ALL"
    - questions: List[Question]
      至少 1 题
    - total_marks: int
      >= 0

    ====================
    三、Question 结构
    ====================
    - question_number: int (>=1)
    - question_type: str (枚举)
      "multiple_choice" | "structured" | "essay"
    - stem_materials: List[StemMaterial]
      题干材料列表（可空）
    - sub_questions: List[SubQuestion]
      至少 1 个
    - total_marks: int (>=0)
    - topics: List[str]（至少 1 个）
      必须从 `get_topics_by_paper_name` 返回结果中选择
    - sub_topics: List[str]（至少 1 个）
      必须从 `get_topics_by_paper_name` 返回结果中选择
    - difficulty: float
      范围 -3.0 ~ 3.0
    - discrimination: float
      范围 0.5 ~ 2.5
    - source_image_url: str | null
      原始题目图片 URL（建议提供可直接访问 URL）

    ====================
    四、StemMaterial 结构
    ====================
    - label: str | null
      例如 "Extract A"、"Figure 1"
    - text: str
    - diagrams: List[str]
      图表 URL 列表（可空）

    ====================
    五、SubQuestion 结构
    ====================
    - label: str
      例如 "(a)"、"(i)"、"(a)(ii)"
    - text: str
    - command_word: int | null
      指令词编号；建议通过 `get_command_word_by_subject` 获取
    - marks: int (>=0)
    - is_single_choice: bool
      选择题时使用；默认 true
    - options: List[OptionItem] | null
      仅选择题需要；非选择题建议省略或传 null
    - diagrams: List[str]
    - correct_answer: str
    - skills_tested: List[str]

    ====================
    六、OptionItem 结构（高频报错点）
    ====================
    options 必须是对象数组，每个选项必须是：
    {
      "key": "A",
      "text": "选项文本",
      "is_correct": false,
      "file_list": []
    }

    注意：
    - 不能把 options 写成字符串
    - 不能把 options 写成字符串数组
    - 不能用错误字段名（如 optionKey/isCorrect/fileList）

    ====================
    七、常见错误
    ====================
    - required_questions 传 "ALL"（错误）=> 应传 null 或整数
    - options 传 "A\\nB\\nC\\nD"（错误）=> 应传 OptionItem[]
    - topics/sub_topics 使用了未在接口返回中的值
    - 使用了 camelCase 字段名导致解析失败

    ====================
    八、最小示例
    ====================
    {
      "education_system": "A-Level",
      "exam_board": "Edexcel",
      "subject": "Economics",
      "component": "Introduction to Markets and Market Failure",
      "syllabus_code": "8EC0/01",
      "year": 2024,
      "session": "May/June",
      "duration_minutes": 90,
      "total_marks": 1,
      "paper_pdf_urls": ["https://example.com/paper.pdf"],
      "sections": [
        {
          "section_label": "Section A",
          "instructions": "Answer all questions.",
          "required_questions": 1,
          "total_marks": 1,
          "questions": [
                {
                  "question_number": 1,
                  "question_type": "single_question",
                  "stem_materials": [],
                  "sub_questions": [
                    {
                      "label": "(a)",
                      "text": "$g(x)=3x^3-20x^2+(k+17)x+k$, where k is a constant. Given that $(x-3)$ is a factor of $g(x)$, find the value of k.",
                      "command_word": 14,
                      "marks": 3,
                      "is_single_choice": false,
                      "diagrams": [],
                      "correct_answer": "Since $(x-3)$ is a factor, $g(3)=0$. So $81-180+3(k+17)+k=0 \\Rightarrow -48+4k=0 \\Rightarrow k=12$.",
                      "skills_tested": [
                        "AO1: Knowledge",
                        "AO2: Application"
                      ]
                    }
                  ],
                  "total_marks": 3,
                  "topics": [
                    "Algebra and Functions"
                  ],
                  "sub_topics": [
                    "Factor theorem and remainder theorem"
                  ],
                  "difficulty": -0.7,
                  "discrimination": 1.02,
                  "source_image_url": "https://sifc.oss-cn-shenzhen.aliyuncs.com/20260325/c41b4898-be79-48f5-b613-5dd1ff732994.png"
                },
                {
                  "question_number": 2,
                  "question_type": "structured",
                  "stem_materials": [
                    {
                      "label": "Figure 1",
                      "text": "Figure 1 is a sketch of $y=3|x-2|+5$ with vertex P.",
                      "diagrams": [
                        "https://sifc.oss-cn-shenzhen.aliyuncs.com/20260326/b51faa1e-b3dc-453d-b157-6b1cfcca1e63.png"
                      ]
                    }
                  ],
                  "sub_questions": [
                    {
                      "label": "(a)",
                      "text": "Find the coordinates of P.",
                      "command_word": 13,
                      "marks": 2,
                      "is_single_choice": false,
                      "diagrams": [],
                      "correct_answer": "The vertex occurs when $x=2$, so $y=3|0|+5=5$. Therefore $P=(2,5)$.",
                      "skills_tested": [
                        "AO2: Application"
                      ]
                    },
                    {
                      "label": "(b)",
                      "text": "Solve the equation $16-4x=3|x-2|+5$.",
                      "command_word": 14,
                      "marks": 2,
                      "is_single_choice": false,
                      "diagrams": [],
                      "correct_answer": "For $x\\ge2: 11-4x=3x-6 \\Rightarrow x=\\frac{17}{7}$. For $x<2: 11-4x=6-3x \\Rightarrow x=5 (invalid)$. So the solution is $x=\\frac{17}{7}$.",
                      "skills_tested": [
                        "AO2: Application"
                      ]
                    },
                    {
                      "label": "(c)",
                      "text": "A line l has equation $y=kx+4$, where k is a constant. Given that l intersects $y=3|x-2|+5$ at 2 distinct points, find the range of values of k.",
                      "command_word": 14,
                      "marks": 2,
                      "is_single_choice": false,
                      "diagrams": [],
                      "correct_answer": "Solving with branches gives $x_1=-\\frac{5}{k-3} (must$ satisfy $x_1\\ge2)$ and $x_2=\\frac{7}{k+3} (must$ satisfy $x_2<2)$. These conditions give $0.5\\le k<3$ and $(k<-3$ or $k>0.5)$. For 2 distinct intersections, $k\\ne0.5$. Hence $\\frac{1}{2}<k<3$.",
                      "skills_tested": [
                        "AO3: Analysis"
                      ]
                    }
                  ],
                  "total_marks": 6,
                  "topics": [
                    "Algebra and Functions",
                    "Coordinate Geometry"
                  ],
                  "sub_topics": [
                    "Algebraic manipulation"
                  ],
                  "difficulty": 0.32,
                  "discrimination": 1.18,
                  "source_image_url": "https://sifc.oss-cn-shenzhen.aliyuncs.com/20260325/35583038-41a3-490a-bea0-71ec869d403e.png"
                },
          ]
        }
      ]
    }

    补充约束：
    - 所有 URL 必须可直接访问
    - 若含数学/理化公式，请使用 LaTeX
    - 建议保证：题目 marks 求和与 total_marks 一致（题目级/section级/整卷级）
    """

    print(params)
    # return Result.success(data="录入成功")
    return QuestionRemoteCallClientService.create_paper(params=params)


@mcp.tool()
@require_auth
def get_all_paper_name(params:GetAllPaperModel,ctx: Context):
    """
    获取数据库中所有可用的试卷模块组件名称
    """
    return QuestionRemoteCallClientService.get_all_paper_name(params=params)



@mcp.tool()
@require_auth
def get_topics_by_paper_name(params: GetTopicsParams, ctx: Context):
    """
    根据试卷模块组件名称查询该模块可用的知识点大纲标签（topics / sub_topics）。

    用途：
    - 在调用 `upload_paper` 前先查询本工具
    - 将返回结果中的标签用于 `questions[].topics` 与 `questions[].sub_topics`
    - 仅应使用本接口返回的标签值，避免因不匹配导致入库失败

    参数：
    - education_system (str, 可选)：教育体系
      例如：`A-Level`、`AP`
    - exam_board (str, 可选)：考试局
      例如：`Edexcel`、`CIE`、`AQA`
    - year (int, 可选)：大纲年份
      例如：`2026`
    - key (str, 必填)：试卷模块组件名名称
      例如：`Pure Mathematics P1`、`Mechanics`、`Probability&Statistics S1`

    返回：
    - code: 状态码
    - date: 响应日期
    - result: 大纲标签列表（可能为空）
      常见字段：
      - topicKey: 模块名/分组键
      - topicValue: 章节名（可作为 topics 候选）
      - subList: 子章节/考点列表（可作为 sub_topics 候选）

    注意：
    - `key` 必填，且建议与系统中的标准模块名完全一致（大小写与空格尽量一致）
    - 当 `education_system / exam_board / year` 与数据源不匹配时，可能返回空数组
    - 返回空数组不一定是接口异常，也可能是该组合下暂无配置
    """
    return QuestionRemoteCallClientService.get_topics_by_paper_model(params=params)


@mcp.tool()
@require_auth
def get_command_word_by_subject(params: GetCommandWordParams, ctx: Context):
    """
    根据科目名称获取可用的“指令词编号”列表。

    用途：
    - 在调用 `upload_paper` 前，先查询该科目的指令词
    - 将返回的 `id` 填入 `sub_questions[].command_word`

    参数：
    - subject_name (str, 必填)：科目名称，必须为全小写英文
      例如：`economics`、`maths`、`business`

    返回：
    - code: 状态码
    - date: 响应日期
    - result: 指令词列表
      每项通常包含：
      - id: 指令词编号
      - typeCode: 指令词代码（如 DEFINE/EXPLAIN/EVALUATE）
      - typeName: 指令词名称（中文说明）

    注意：
    - `subject_name` 不是小写时，可能返回空结果或报错
    - 不同科目返回的指令词集合可能不同，请勿跨科目复用
    """
    return QuestionRemoteCallClientService.get_command_word_by_subject(params=params)