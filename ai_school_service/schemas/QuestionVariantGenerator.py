from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    """题目类型"""
    MULTIPLE_CHOICE = "multiple_choice"
    STRUCTURED = "structured"
    SINGLE_QUESTION = "single_question"
    # CALCULATION = "calculation"
    # DATA_RESPONSE = "data_response"
    # EXPERIMENT = "experiment"
    # GRAPH = "graph"
    # PROOF = "proof"
    # CASE_STUDY = "case_study"


# ==================== 文件与媒体 ====================



class OptionItem(BaseModel):
    """选择题选项"""
    key: str = Field(..., description="选项键，如 A/B/C/D")
    text: str = Field(..., description="选项文本，如果包含数学、物理、化学公式必须使用LaTeX数学公式")
    is_correct: bool = Field(..., description="是否正确")
    file_list: List[str] = Field(default_factory=list, description="选项附件（如图片）")






class StemMaterial(BaseModel):
    """
    题干材料单元
    一道题的题干可能包含多段材料，每段材料有各自的文本和图表
    例如经济学: 材料A(文字+供需曲线图) + 材料B(文字+数据表)
    """
    label: Optional[str] = Field(None, description="材料标签，如 'Extract A', 'Material B', 'Figure 1', 'Table 1'")
    text: str = Field(..., description="材料文本内容，如果包含数学、物理、化学公式必须使用LaTeX数学公式")
    diagrams: List[str] = Field(default_factory=list, description="该材料关联的图表URL列表")


# ==================== 题目结构 ====================

class SubQuestion(BaseModel):
    """
    最小题目单元 - 对应试卷中的子问题
    例如: Question 3(a)(ii)
    """
    label: str = Field(..., description="子题编号，如 '(a)', '(i)', '(a)(i)'")
    text: str = Field(..., description="题目文本，如果包含数学、物理、化学公式必须使用LaTeX数学公式")
    command_word: int = Field(None, description="指令词编号，必须调用mcp接口get_command_word_by_subject")
    marks: int = Field(..., ge=0, description="本小题分值")

    # 选择题专用
    is_single_choice: bool = Field(default=True, description="是否单选，false 为多选")
    options: Optional[List[OptionItem]] = Field(
        None,
        description="选择题选项"
    )

    # 图表与附件
    diagrams: List[str] = Field(default_factory=list, description="题目包含的图表")

    # 答案与评分
    correct_answer: str = Field(..., description="参考答案 如果包含数学、物理、化学公式必须使用LaTeX数学公式")

    # 考查技能
    skills_tested: List[str] = Field(
        default_factory=list,
        description="考查技能，如 ['AO1: Knowledge', 'AO2: Application', 'AO3: Analysis']"
    )






class Question(BaseModel):
    """
    大题 - 对应试卷中的一道完整题目
    例如: Question 7 (可能包含 (a)(b)(c) 等小题)
    """
    question_number: int = Field(..., ge=1, description="题号")
    question_type: QuestionType = Field(..., description="题目类型，multiple_choice表示单选、多选或判断题，structured表示有题干的题目，single_question表示单体题")
    stem_materials: List[StemMaterial] = Field(
        default_factory=list,
        description="题干材料列表，如 [材料A(文字+图表), 材料B(文字)，材料C(文字+图表)]"
    )
    sub_questions: List[SubQuestion] = Field(
        ...,
        min_length=1,
        description="子题列表"
    )
    total_marks: int = Field(..., ge=0, description="大题总分")
    topics: List[str] = Field(..., min_length=1, description="题目所属章节，如 ['Number', 'Algebra']")
    sub_topics: List[str] = Field(..., min_length=1, description="章节下的具体考点，如 topic 为 'Number' 时: ['Arithmetic', 'Standard form']")
    difficulty: float = Field(..., ge=-3.0, le=3.0, description="难度，取值范围 -3.00 ~ 3.00")
    discrimination: float = Field(..., ge=0.5, le=2.5, description="区分度，表示题目章节和考点的覆盖程度，取值范围 0.50 ~ 2.50")
    source_image_url: Optional[str] = Field(..., description="原始试卷题目图片URL")



class FigureSpec(BaseModel):
    """图片生成规格"""
    prompt: str = Field(..., description="图片详细描述")
    type: str = Field(..., description="生成类型：'matplotlib' 或 'gemini'")


class QuestionOutput(BaseModel):
    """AI 输出的题目结构，包含需要生成的图片描述"""
    question: Question = Field(..., description="生成的题目")
    stem_materials_need_figures: List[List[FigureSpec]] = Field(
        default_factory=list,
        description="每个 stem_material 需要的图片描述列表"
    )