import os
from typing import Dict, Any
import requests
from ai_school_mcp.config.ServiceConfig import  token_ctx
from ai_school_mcp.course_mcp.schemas.CoursesParams import GetCoursesParams, GetCourseDetailParams, CreateCourseParams, \
    EditCourseParams


class CourseRemoteCallClient:

    def __init__(self):
        self.base_url = "http://47.119.48.67:80/api"
        # self.base_url = ai_school_mcp_service_config.base_url
        # self.auth_token = "Bearer " + ai_school_mcp_service_config.auth_token

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

CourseRemoteCallClientService = CourseRemoteCallClient()
# params = GetCoursesParams(current=1,total=10)
# print(CourseRemoteCallClientService.get_courses_page(params=params))
# params = GetCourseDetailParams(course_id="2026938616653832193")
# print(CourseRemoteCallClientService.get_course_detail_byid(params=params))