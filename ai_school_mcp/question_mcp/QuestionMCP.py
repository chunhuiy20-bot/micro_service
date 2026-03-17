from fastmcp import Context

from ai_school_mcp.decorators.require_auth import require_auth
from ai_school_mcp.question_mcp.remote_call.QuestionRemoteCallClient import QuestionRemoteCallClientService
from ai_school_mcp.question_mcp.schemas.QuestionParams import CreatePaperParams
from ai_school_mcp.server import mcp
from common.schemas.CommonResult import Result


@mcp.tool()
@require_auth
def create_paper(params: CreatePaperParams, ctx: Context):
    """
    将A-Level试卷解析后的题目录入题库。paper_source_url 需要试卷原卷对应的课直接访问的url，question_image_url需要png图片可直接访问的url。请查看本地配套的ai-school-mcp的agent skill，使用这些得到url。

    参数说明：
    - subject: A-Level学科，如 Maths/Physics/Chemistry/Economics 等
    - paper_model: 试卷类型，如 Pure Mathematics P1/Pure Mathematics P2/Mechanics/Probability&Statistics S1 等
    - paper_source_url: 试卷来源URL（可选）
    - questions: 题目列表，每道题包含：
      - question_image_url: 题目原图URL
      - parts: 小题列表（QuestionItem），每个小题含 text/type/score/correctAnswer/knowledge_point/options
      - total_score: 该题总分
      - topics: 知识点大纲标签
      - difficulty: 难度（-3.00 ~ 3.00）
      - discrimination: 区分度（-0.50 ~ 2.50）,表示这道题目知识点覆盖广度和解题思路能否区分学生能力
    """
    print(params)
    return Result.success(data="录入成功")
    # return QuestionRemoteCallClientService.create_paper(params=params)
