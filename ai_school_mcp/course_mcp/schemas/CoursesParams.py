from typing import List, Literal, Optional

from pydantic import BaseModel, Field



class GetCoursesParams(BaseModel):
    current: int = Field(..., ge=1, description="当前页码，从 1 开始")
    total: int = Field(10, ge=1, le=100, description="每页返回数量（page size）")

class GetCourseDetailParams(BaseModel):
    course_id: str = Field(...,description="具体课程id，如果不知道可以调用get_courses_page 可以获取到课程id")

class DeleteCourseParams(BaseModel):
    course_id: str = Field(..., description="要删除的课程id，如果不知道可以调用get_courses_page 获取")

class GetUnitsByCourseParams(BaseModel):
    course_id: str = Field(..., description="课程id，用于查询该课程下的单元列表")

class GetUnitDetailParams(BaseModel):
    unit_id: str = Field(..., description="单元id，用于查询单元详情")


# 添加课程
class FileItem(BaseModel):
    fileName: str = Field(..., description="文件名")
    filePath: str = Field(..., description="文件路径/URL")


class OptionItem(BaseModel):
    optionKey: str = Field(..., description="选项键，如 A/B/C/D")
    text: str = Field("", description="选项文本")
    isCorrect: bool = Field(False, description="是否正确")
    fileList: List[FileItem] = Field(default_factory=list, description="选项附件")


class QuestionItem(BaseModel):
    text: str = Field(..., description="题目内容")
    type: str = Field(..., description="题型，如 single/multi/short")
    score: int = Field(0, ge=0, description="分值")
    correctAnswer: str = Field("", description="参考答案（主观题可用）")
    options: List[OptionItem] = Field(default_factory=list, description="客观题选项")
    fileList: List[FileItem] = Field(default_factory=list, description="题目附件")


class TaskItem(BaseModel):
    title: str = Field(..., description="任务标题")
    type: str = Field(..., description="任务类型：learn/practice/quiz")
    description: str = Field("", description="任务描述")
    instructions: str = Field("", description="任务说明")
    passPercentage: int = Field(0, ge=0, le=100, description="通过百分比")
    timeLimit: int = Field(0, ge=0, description="时限，0 表示不限时")
    questions: List[QuestionItem] = Field(default_factory=list, description="任务题目")
    fileList: List[FileItem] = Field(default_factory=list, description="任务附件")


class CompetencyItem(BaseModel):
    title: str = Field(..., description="能力点标题")
    tasks: List[TaskItem] = Field(default_factory=list, description="能力点下任务")


class LessonItem(BaseModel):
    title: str = Field(..., description="课时标题")
    competencys: List[CompetencyItem] = Field(default_factory=list, description="课时下能力点")


class UnitItem(BaseModel):
    title: str = Field(..., description="单元标题")
    lessons: List[LessonItem] = Field(default_factory=list, description="单元下课时")
    tasks: List[TaskItem] = Field(default_factory=list, description="单元直属任务")


# ---------- Create ----------
class CreateCourseParams(BaseModel):
    title: str = Field(..., description="课程标题")
    status: Literal["draft", "published"] = Field("draft", description="课程状态")
    units: List[UnitItem] = Field(default_factory=list, description="课程单元，可空数组")


# ---------- Edit ----------
class EditCourseParams(BaseModel):
    id: str = Field(..., description="课程ID,如果不知道可以调用get_courses_page 可以获取到课程id")
    title: str = Field(..., description="课程标题")
    status: Literal["draft", "published"] = Field("draft", description="课程状态")
    description: str = Field("", description="课程描述")
    units: List[UnitItem] = Field(default_factory=list, description="课程内容结构，可空数组")



class EditUnitParams(BaseModel):
    id: int = Field(..., description="单元ID，必填，可通过 get_units_by_course 获取单元ID")
    title: str = Field(..., description="单元标题")
    lessons: List[LessonItem] = Field(default_factory=list, description="单元下的课时，覆盖更新")
    tasks: List[TaskItem] = Field(default_factory=list, description="单元直属任务，覆盖更新")


class CreateUnitParams(BaseModel):
    courseId: str = Field(..., description="所属课程ID，可通过 get_all_courses 获取")
    title: str = Field(..., description="单元标题")
    lessons: List[LessonItem] = Field(default_factory=list, description="单元下的课时，可空数组")
    tasks: List[TaskItem] = Field(default_factory=list, description="单元直属任务，可空数组")