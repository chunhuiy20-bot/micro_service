from fastapi import FastAPI
from fastapi import Request

app = FastAPI(title="user_service")


@app.get("/user/{user_id}")
async def get_user(user_id: int,request: Request):
    request_id = request.headers.get("X-Request-Id", "unknown")
    print(f"✅ GET 请求 请求id：{request_id} user_id={user_id}")
    return {"user_id": user_id, "message": f"获取user:{user_id}"}


@app.put("/user/{user_id}")
async def update_user(user_id: int,request: Request):
    request_id = request.headers.get("X-Request-Id", "unknown")
    print(f"✅ PUT 请求 请求id：{request_id} user_id={user_id}")
    return {"user_id": user_id, "message": f"更新user:{user_id}"}


@app.delete("/user/{user_id}")
async def delete_user(user_id: int, request: Request):
    request_id = request.headers.get("X-Request-Id", "unknown")
    print(f"✅ DELETE 请求 请求id：{request_id} user_id={user_id}")
    return {"user_id": user_id, "message": f"删除user:{user_id}"}