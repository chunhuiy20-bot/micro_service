from ai_school_mcp.course_mcp.remote_call.CourseRemoteCallClient import CourseRemoteCallClientService
from ai_school_mcp.course_mcp.schemas.CoursesParams import GetCoursesParams
from ai_school_mcp.server import mcp



@mcp.tool()
def get_all_courses(params=GetCoursesParams):
    """
    分页获取课程列表。

    返回:
    - current: 当前页
    - total: 每页数量
    - items: 课程列表
    - total_count: 课程总数
    """
    res = CourseRemoteCallClientService.get_courses_page(params=params)
    return res