import httpx
from ai_school_service.config.AISchoolConfig import ai_school_config


class AISchoolServerClient:

    def __init__(self):
        self.base_url = ai_school_config.aischool_base_url
        self.token = ai_school_config.aischool_token

    async def upload_file(self, file_path: str, is_orc: bool = False) -> str:
        """
        上传文件到 Java 服务，返回文件 URL。
        """
        url = f"{self.base_url}/file/oss/upload"
        async with httpx.AsyncClient(timeout=60) as client:
            with open(file_path, "rb") as f:
                response = await client.post(
                    url,
                    files={"file": f},
                    data={"isOrc": False},
                    headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXBhcnRtZW50X2NvZGUiOm51bGwsImxvZ2luX3R5cGUiOm51bGwsInVzZXJfbmFtZSI6ImFpdGVhY2hlciIsImlzX2FjY2VzcyI6bnVsbCwiaXNfY2hlY2tlciI6bnVsbCwiY2xpZW50X2lkIjoibXlqc3psIiwicG9zdF9uYW1lIjpudWxsLCJpZGVudGl0eSI6IjAiLCJzY29wZSI6WyJhbGwiXSwiZW5fbmFtZSI6bnVsbCwiZXhwIjoxNzczMjI0NTQ2LCJqdGkiOiI3YjFjOTM3ZC1iZGE0LTRlNmUtOTJmZi1jODIyZWMzMWYzZWYiLCJpc19yZXZpZXdlciI6bnVsbCwiZGVwYXJ0bWVudF9uYW1lIjpudWxsLCJtb2JpbGUiOm51bGwsIm1hbmFnZV9kZXB0X2lkIjpudWxsLCJhdWQiOlsicmVzMSJdLCJwb3N0X2lkIjpudWxsLCJpc19hdWRpdCI6bnVsbCwidXNlcl9pZCI6IjIwMTM0OTU2NjcwMTE0Nzc1MTIiLCJvcmdfaWQiOm51bGwsIm5pY2tfbmFtZSI6bnVsbCwicG9zdF9jb2RlIjpudWxsLCJuYW1lIjoiYWl0ZWFjaGVyIiwiZGVwYXJ0bWVudF9lbl9uYW1lIjpudWxsLCJkZXB0X2lkIjpudWxsLCJ1c2VybmFtZSI6ImFpdGVhY2hlciJ9.6NF49LE9OpnjMqWxbARKulL3Rn4oQRByDs-VUwc1r1s"},
                )
            response.raise_for_status()
            data = response.json()
            file_url = data.get("result", {}).get("url")
            if not file_url:
                raise ValueError(f"上传成功但未获取到 URL，响应: {data}")
            return file_url


ai_school_server_client = AISchoolServerClient()
