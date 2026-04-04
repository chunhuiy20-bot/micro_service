import os
from dotenv import load_dotenv
from typing import Dict, Any
import requests
from ai_school_mcp.config.ServiceConfig import token_ctx
from ai_school_mcp.question_mcp.schemas.QuestionParams import Paper, GetTopicsParams, GetCommandWordParams, \
    GetAllPaperModel

load_dotenv()


class QuestionRemoteCallClient:

    def __init__(self):
        self.base_url = os.getenv("BASE_URL", "http://47.119.48.67:80/api")

    def _send_post_request(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        auth_token = token_ctx.get()
        print(auth_token)
        if auth_token:
            headers["Authorization"] = auth_token if auth_token.startswith("Bearer ") else f"Bearer {auth_token}"

        resp = requests.post(self.base_url + url, json=data, headers=headers, timeout=100)
        resp.raise_for_status()
        return resp.json()

    def create_paper(self, params: Paper) -> Dict[str, Any]:
        """创建试卷并入题库"""
        payload = params.model_dump(mode="json", exclude_none=True)
        return self._send_post_request(url="/serve/problem/import", data=payload)

    def get_topics_by_paper_model(self, params: GetTopicsParams) -> Dict[str, Any]:
        """根据试卷类型查询知识点大纲标签"""
        payload = params.model_dump(mode="json", exclude_none=True)
        if "paper" in payload:
            payload["key"] = payload.pop("paper")
        return self._send_post_request(url="/serve/baseTopic/getList", data=payload)

    def get_command_word_by_subject(self, params: GetCommandWordParams) -> Dict[str, Any]:
        payload = {"subjectCode": params.subject_name}
        return self._send_post_request(url="/serve/student/questionType/getList", data=payload)

    def get_all_paper_name(self,params: GetAllPaperModel)->Dict[str, Any]:
        payload = params.model_dump(mode="json", exclude_none=True)
        return self._send_post_request(url="/serve/baseTopic/getTopicKeyList", data=payload)


QuestionRemoteCallClientService = QuestionRemoteCallClient()
