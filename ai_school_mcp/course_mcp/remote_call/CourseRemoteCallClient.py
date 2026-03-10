import os
from dotenv import load_dotenv
from typing import Dict, Any
import requests
from ai_school_mcp.config.ServiceConfig import  token_ctx
from ai_school_mcp.course_mcp.schemas.CoursesParams import GetCoursesParams, GetCourseDetailParams, CreateCourseParams, \
    EditCourseParams, GetUnitsByCourseParams, GetUnitDetailParams, EditUnitParams, DeleteCourseParams, CreateUnitParams
load_dotenv()

class CourseRemoteCallClient:

    def __init__(self):
        self.base_url = os.getenv("BASE_URL", "http://47.119.48.67:80/api")

    def _send_post_request(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送 POST JSON 请求并返回 JSON。"""
        headers = {"Content-Type": "application/json"}
        auth_token = token_ctx.get()
        print(auth_token)
        if auth_token:
            headers["Authorization"] = auth_token if auth_token.startswith("Bearer ") else f"Bearer {auth_token}"

        resp = requests.post(self.base_url+url, json=data, headers=headers, timeout=100)
        resp.raise_for_status()
        return resp.json()

    def get_courses_page(self, params: GetCoursesParams) -> Dict[str, Any]:
        """
        分页查询课程。

        参数:
        - current: 当前页码(从1开始)
        - total: 每页数量
        """
        payload = {"current": params.current, "total": params.total}
        return self._send_post_request(url="/serve/teacher/course/page", data=payload)

    def get_course_detail_byid(self, params: GetCourseDetailParams):
        """
        根据课程id查询具体课程信息，如果不知道课程id，不要随意填写，请调用get_courses_page查询
        参数:
        - course_id: 课程id
        """
        payload = {"id": params.course_id}
        return self._send_post_request(url="/serve/teacher/course/byid", data=payload)

    def add_course(self, params: CreateCourseParams) -> Dict[str, Any]:
        """
        添加一门课程（支持仅创建课程壳子，units/lessons/tasks 可为空数组）
        """
        payload = params.model_dump(mode="json", exclude_none=True)
        # 按你后端实际路由改这个 URL；常见是 /add 或 /create
        return self._send_post_request(url="/serve/teacher/course/add", data=payload)

    def edit_course(self, params: EditCourseParams):
        """
        编辑课程
        """
        payload = params.model_dump(mode="json",exclude_none=True)
        return self._send_post_request(url="/serve/teacher/course/edit",data=payload)

    def get_units_by_course(self, params: GetUnitsByCourseParams) -> Dict[str, Any]:
        """
        根据课程id获取单元列表
        """
        payload = {"id": params.course_id}
        return self._send_post_request(url="/serve/teacher/course/getUnitByCourse", data=payload)

    def get_unit_detail_byid(self, params: GetUnitDetailParams) -> Dict[str, Any]:
        """
        根据单元id获取单元详情
        """
        payload = {"id": params.unit_id}
        return self._send_post_request(url="/serve/teacher/unit/byid", data=payload)

    def edit_unit(self, params: EditUnitParams) -> Dict[str, Any]:
        """
        覆盖更新单元
        """
        payload = params.model_dump(mode="json", exclude_none=True)
        return self._send_post_request(url="/serve/teacher/unit/edit", data=payload)

    def delete_course(self, params: DeleteCourseParams) -> Dict[str, Any]:
        """
        根据课程id删除课程
        """
        payload = {"id": params.course_id}
        return self._send_post_request(url="/serve/teacher/course/del", data=payload)

    def create_unit(self, params: CreateUnitParams) -> Dict[str, Any]:
        """
        在指定课程下创建新单元
        """
        payload = params.model_dump(mode="json", exclude_none=True)
        return self._send_post_request(url="/serve/teacher/unit/add", data=payload)

CourseRemoteCallClientService = CourseRemoteCallClient()