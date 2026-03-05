import os
from typing import Dict, Any
import requests
from ai_school_mcp.course_mcp.schemas.CoursesParams import GetCoursesParams


class CourseRemoteCallClient:

    def __init__(self):
        self.base_url = "http://47.119.48.67:80/api/serve/teacher/course/page"
        self.auth_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXBhcnRtZW50X2NvZGUiOm51bGwsImxvZ2luX3R5cGUiOm51bGwsInVzZXJfbmFtZSI6InRlYWNoZXIiLCJpc19hY2Nlc3MiOm51bGwsImlzX2NoZWNrZXIiOm51bGwsImNsaWVudF9pZCI6Im15anN6bCIsInBvc3RfbmFtZSI6bnVsbCwiaWRlbnRpdHkiOiIwIiwic2NvcGUiOlsiYWxsIl0sImVuX25hbWUiOm51bGwsImV4cCI6MTc3Mjc5OTg3OCwianRpIjoiOGExNTczNTUtMTc0Ni00ZDFhLWI2MjktZGQzZDQwNGIzMzVlIiwiaXNfcmV2aWV3ZXIiOm51bGwsImRlcGFydG1lbnRfbmFtZSI6bnVsbCwibW9iaWxlIjpudWxsLCJtYW5hZ2VfZGVwdF9pZCI6bnVsbCwiYXVkIjpbInJlczEiXSwicG9zdF9pZCI6bnVsbCwiaXNfYXVkaXQiOm51bGwsInVzZXJfaWQiOiIyMDEzNDk1NjY3MDExNDc3NTExIiwib3JnX2lkIjpudWxsLCJuaWNrX25hbWUiOm51bGwsInBvc3RfY29kZSI6bnVsbCwibmFtZSI6InRlYWNoZXIiLCJkZXBhcnRtZW50X2VuX25hbWUiOm51bGwsImRlcHRfaWQiOm51bGwsInVzZXJuYW1lIjoidGVhY2hlciJ9.5Ih4rmP0ChDtoykFGFlLOBEvR1KEg-5wMXYuGy3CBoY"

    def _send_request(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送 POST JSON 请求并返回 JSON。"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        resp = requests.post(url, json=data, headers=headers, timeout=10)
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
        return self._send_request(self.base_url, payload)



CourseRemoteCallClientService = CourseRemoteCallClient()
