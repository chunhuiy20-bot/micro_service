from pydantic import BaseModel, Field



class GetCoursesParams(BaseModel):
    current: int = Field(..., ge=1, description="当前页码，从 1 开始")
    total: int = Field(10, ge=1, le=100, description="每页返回数量（page size）")