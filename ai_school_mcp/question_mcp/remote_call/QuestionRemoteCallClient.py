import os
from dotenv import load_dotenv
from typing import Dict, Any
import requests
from ai_school_mcp.config.ServiceConfig import token_ctx
from ai_school_mcp.question_mcp.schemas.QuestionParams import CreatePaperParams

load_dotenv()


class QuestionRemoteCallClient:

    def __init__(self):
        self.base_url = os.getenv("BASE_URL", "http://47.119.48.67:80/api")

    def _send_post_request(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        auth_token = token_ctx.get()
        if auth_token:
            headers["Authorization"] = auth_token if auth_token.startswith("Bearer ") else f"Bearer {auth_token}"

        resp = requests.post(self.base_url + url, json=data, headers=headers, timeout=100)
        resp.raise_for_status()
        return resp.json()

    def create_paper(self, params: CreatePaperParams) -> Dict[str, Any]:
        """创建试卷并入题库"""
        payload = params.model_dump(mode="json", exclude_none=True)
        return self._send_post_request(url="/serve/teacher/question/add", data=payload)


QuestionRemoteCallClientService = QuestionRemoteCallClient()
