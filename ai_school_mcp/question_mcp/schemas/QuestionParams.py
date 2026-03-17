from typing import List, Literal
from pydantic import BaseModel, Field


class FileItem(BaseModel):
    fileName: str = Field(..., description="文件名")
    filePath: str = Field(..., description="文件路径/URL")


class OptionItem(BaseModel):
    optionKey: str = Field(..., description="选项键，如 A/B/C/D")
    text: str = Field(..., description="选项文本")
    isCorrect: bool = Field(..., description="是否正确")
    fileList: List[FileItem] = Field(default_factory=list, description="选项附件")


class QuestionItem(BaseModel):
    text: str = Field(..., description="题目内容，必须根据图片识别填写完整题目文本")
    type: str = Field(..., description="题型，如 single/multi/short")
    score: int = Field(..., ge=0, description="分值，必须根据试卷标注填写")
    correctAnswer: str = Field(..., description="参考答案，必须填写")
    knowledge_point: str = Field(..., description="该题对应的A-Level知识点考点内容，必须填写")
    options: List[OptionItem] = Field(default_factory=list, description="客观题选项，主观题可为空")
    fileList: List[FileItem] = Field(default_factory=list, description="题目附件")


class QuestionEntry(BaseModel):
    question_image_url: str = Field(..., description="试卷来源对应的题目照片URL，必须填写")
    parts: List[QuestionItem] = Field(..., min_length=1, description="题目小题列表，至少包含一个小题")
    total_score: int = Field(..., ge=0, description="该题总分，必须根据试卷标注填写")
    topics: List[str] = Field(..., min_length=1, description="题目对应的A-Level知识点大纲，如Data Representation/Probability/The Normal distribution等，必须填写")
    difficulty: float = Field(..., ge=-3.0, le=3.0, description="难度，取值范围 -3.00 ~ 3.00，必须根据题目内容评估填写")
    discrimination: float = Field(..., ge=-0.5, le=2.5, description="区分度，取值范围 -0.50 ~ 2.50，表示题目知识点覆盖广度和解题思路能否区分学生能力，必须评估填写")


class CreatePaperParams(BaseModel):
    subject: str = Field(
        ...,
        description="A-Level考试体系学科，如：Maths/Further Maths/Physics/Biology/Chemistry/Economics/Psychology/Computer Science/Business/Geography/History/Account",
    )
    paper_model: str = Field(
        ...,
        description="A-Level试卷设置，如：Pure Mathematics P1/Pure Mathematics P2/Pure Mathematics P3/Mechanics/Probability&Statistics S1/Probability&Statistics S2"
    )
    paper_source_url: str = Field(..., description="试卷来源URL，必须填写")
    questions: List[QuestionEntry] = Field(..., min_length=1, description="题目列表，至少包含一道题")
