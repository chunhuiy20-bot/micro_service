from fastmcp import Context

from ai_school_mcp.config.ServiceConfig import token_ctx
from ai_school_mcp.course_mcp.remote_call.CourseRemoteCallClient import CourseRemoteCallClientService
from ai_school_mcp.course_mcp.schemas.CoursesParams import GetCoursesParams, GetCourseDetailParams, CreateCourseParams, \
    EditCourseParams
from ai_school_mcp.decorators.require_auth import require_auth
from ai_school_mcp.server import mcp



@mcp.tool()
@require_auth
def get_all_courses(params: GetCoursesParams, ctx: Context):
    """
    分页获取课程列表。

    返回:
    - current: 当前页
    - total: 每页数量
    - items: 课程列表
    - total_count: 课程总数
    """
    # # 提取并设置 Token
    # headers = dict(ctx.request_context.request.headers)
    # auth_token = headers.get('authorization')
    # if not auth_token:
    #     # 直接返回错误描述，LLM 会据此提示用户配置 Token
    #     return {"error": "Authentication failed: No 'Authorization' header found in the request."}

    # token_ctx.set(auth_token)
    return CourseRemoteCallClientService.get_courses_page(params=params)

@mcp.tool()
@require_auth
def get_course_detail_byid(params: GetCourseDetailParams, ctx: Context):
    """
    根据course_id查询课程具体信息，course_id不要胡乱编
    """
    return CourseRemoteCallClientService.get_course_detail_byid(params=params)

@mcp.tool()
@require_auth
def add_course(params: CreateCourseParams, ctx: Context):
    """
    根据用户的需求和想法创建课程
    """
    return CourseRemoteCallClientService.add_course(params=params)

@mcp.tool()
@require_auth
def edit_course_byid(params: EditCourseParams, ctx: Context):
    """
    根据课程 ID 编辑课程。

    重要语义（必须遵守）：
    - 本接口对课程结构采用“覆盖更新”语义，不是追加接口。
    - `units` 会按本次提交内容整体生效；仅提交新增片段可能覆盖掉旧内容。

    调用流程（强约束）：
    1. 先调用 `get_course_detail_byid(course_id)` 获取课程最新完整结构。
    2. 在该结构基础上做最小改动（保留未修改节点）。
    3. 再调用 `edit_course_byid` 提交“合并后的完整目标结构”。



    参数要求：
    - `id` 必填，且必须与查询时的 `course_id` 一致。
    - 所有列表字段统一使用 `[]`，不要传 `null`。
    - 仅当“只修改课程基础信息（title/status/description）且不改结构”时，才可传 `units=[]`。
    - 如果要修改任意结构（units/lessons/competencys/tasks/questions），必须提交包含历史内容的完整 `units`。

    字段约束：
    - `status` 仅允许：`draft` / `published`
    - `passPercentage` 范围：0~100
    - `timeLimit` >= 0，`0` 表示不限时

    常见错误（需避免）：
    - 错误：第一次传 1 个 lesson，第二次只传新 lesson。
    - 后果：旧 lesson 可能被覆盖丢失。
    - 正确：第二次提交时应传“旧 lesson + 新 lesson”的完整 lessons 数组。
    """
    return CourseRemoteCallClientService.edit_course(params=params)

@mcp.tool()
def upload_image(image_b64: str, filename: str):
    """
    将base64格式的图片存储到云端的OSS，并得到一个url"
    Args:
        image_b64:
        filename:
    """
    print(f"iamge_base64:{image_b64}")
    return f"{filename}的url: http://{filename}.png"