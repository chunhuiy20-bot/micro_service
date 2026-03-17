from fastmcp import Context

from ai_school_mcp.config.ServiceConfig import token_ctx
from ai_school_mcp.course_mcp.remote_call.CourseRemoteCallClient import CourseRemoteCallClientService
from ai_school_mcp.course_mcp.schemas.CoursesParams import GetCoursesParams, GetCourseDetailParams, CreateCourseParams, \
    EditCourseParams, GetUnitsByCourseParams, GetUnitDetailParams, EditUnitParams, DeleteCourseParams, CreateUnitParams
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
@require_auth
def get_units_by_course(params: GetUnitsByCourseParams, ctx: Context):
    """
    根据课程ID获取该课程下的单元列表（仅返回单元概要，不含课时/任务等详细内容）。

    适用场景：
    - 课程内容较多时，先用此工具获取单元列表，再按需调用 get_unit_detail_byid 获取某个单元的详情。
    - 避免直接调用 get_course_detail_byid 导致返回数据过大被截断。
    """
    return CourseRemoteCallClientService.get_units_by_course(params=params)

@mcp.tool()
@require_auth
def get_unit_detail_byid(params: GetUnitDetailParams, ctx: Context):
    """
    根据单元ID获取单元详情（含该单元下的课时、能力点、任务、题目等完整结构）。

    调用流程建议：
    1. 先调用 get_units_by_course 获取单元列表，拿到 unit_id。
    2. 再调用本工具获取具体某个单元的完整内容。
    """
    return CourseRemoteCallClientService.get_unit_detail_byid(params=params)

@mcp.tool()
@require_auth
def edit_unit_byid(params: EditUnitParams, ctx: Context):
    """
    根据单元 ID 覆盖更新单元内容。

    重要语义（必须遵守）：
    - 本接口采用"覆盖更新"语义，lessons 列表会整体替换，不是追加。
    - `lessons` 会按本次提交内容整体生效；仅提交新增片段可能覆盖掉旧内容。

    调用流程（强约束）：
    1. 先调用 get_unit_detail_byid(unit_id) 获取单元最新完整结构。
    2. 在该结构基础上做最小改动（保留未修改节点）。
    3. 再调用本工具提交合并后的完整目标结构。

    参数要求：
    - `id` 必填，且必须与查询时的 单元id 一致。
    - 所有列表字段统一使用 `[]`，不要传 `null`。
    - 仅当“只修改单元基础信息（title/description）且不改结构”时，才可传 `lessons=[]`。
    - 如果要修改任意结构（lessons/competencys/tasks/questions），必须提交包含历史内容的完整 `lessons`。

    常见错误（需避免）：
    - 错误：第一次传 1 个 lesson，第二次只传新的 lesson。
    - 后果：旧 lesson 可能被覆盖丢失。
    - 正确：第二次提交时应传“旧 lesson + 新 lesson”的完整 lessons 数组。
    """
    return CourseRemoteCallClientService.edit_unit(params=params)

@mcp.tool()
@require_auth
def delete_course_byid(params: DeleteCourseParams, ctx: Context):
    """
    根据课程 ID 删除课程。

    调用前请确认：
    - 删除操作不可恢复，执行前应向用户二次确认。
    - 如果不知道 course_id，请先调用 get_all_courses 获取课程列表。
    """
    return CourseRemoteCallClientService.delete_course(params=params)

@mcp.tool()
@require_auth
def add_unit(params: CreateUnitParams, ctx: Context):
    """
    在指定课程下创建新单元。

    参数要求：
    - `courseId` 必填，所属课程ID，如不知道可先调用 get_all_courses 获取。
    - `title` 单元标题，必填
    - `lessons` / `tasks` 可传空数组，表示创建一个空单元。
    """
    return CourseRemoteCallClientService.create_unit(params=params)
