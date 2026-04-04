# from typing import List, Literal
# from pydantic import BaseModel, Field
#
#
# class FileItem(BaseModel):
#     fileName: str = Field(..., description="文件名")
#     filePath: str = Field(..., description="文件路径/URL")
#
#
# class OptionItem(BaseModel):
#     optionKey: str = Field(..., description="选项键，如 A/B/C/D")
#     text: str = Field(..., description="选项文本")
#     isCorrect: bool = Field(..., description="是否正确")
#     fileList: List[FileItem] = Field(default_factory=list, description="选项附件")
#
#
# class QuestionItem(BaseModel):
#     text: str = Field(..., description="题目内容必填，数学/物理/化学等公式必须使用LaTeX格式，如 $x^2 + 2x + 1 = 0$")
#     type: str = Field(..., description="题型，如 single/multi/short")
#     score: int = Field(..., ge=0, description="分值，必须根据试卷标注填写")
#     correctAnswer: str = Field(..., description="参考答案，必须填写")
#     knowledge_point: str = Field(..., description="该题对应的A-Level知识点考点内容，必须填写")
#     options: List[OptionItem] = Field(default_factory=list, description="客观题选项，主观题可为空")
#     fileList: List[FileItem] = Field(default_factory=list, description="题目附件")
#
#
# class QuestionEntry(BaseModel):
#     question_image_url: str = Field(..., description="试卷来源对应的题目照片URL，必须填写")
#     parts: List[QuestionItem] = Field(..., min_length=1, description="题目小题列表，至少包含一个小题")
#     total_score: int = Field(..., ge=0, description="该题总分，必须根据试卷标注填写")
#     topics: List[str] = Field(..., min_length=1,max_length=1, description="题目对应的A-Level知识点大纲，如Data Representation/Probability/The Normal distribution等，必须填写能概括这个题目的知识点，而不是Pure Mathematics P1，2024 June Paper这类东西")
#     difficulty: float = Field(..., ge=-3.0, le=3.0, description="难度，取值范围 -3.00 ~ 3.00，必须根据题目内容评估填写")
#     discrimination: float = Field(..., ge=-0.5, le=2.5, description="区分度，取值范围 -0.50 ~ 2.50，表示题目知识点覆盖广度和解题思路能否区分学生能力，必须评估填写")
#
#
# class GetTopicsParams(BaseModel):
#     paper_model: str = Field(
#         ...,
#         description="A-Level试卷类型，如：Pure Mathematics P1/Pure Mathematics P2/Pure Mathematics P3/Mechanics/Probability&Statistics S1/Probability&Statistics S2"
#     )
#
#
# class CreatePaperParams(BaseModel):
#     subject: str = Field(
#         ...,
#         description="A-Level考试体系学科，如：Maths/Further Maths/Physics/Biology/Chemistry/Economics/Psychology/Computer Science/Business/Geography/History/Account",
#     )
#     paper_model: str = Field(
#         ...,
#         description="A-Level试卷设置，如：Pure Mathematics P1/Pure Mathematics P2/Pure Mathematics P3/Mechanics/Probability&Statistics S1/Probability&Statistics S2"
#     )
#     paper_source_url: str = Field(..., description="试卷来源URL，必须填写")
#     questions: List[QuestionEntry] = Field(..., min_length=1, description="题目列表，至少包含一道题")















"""
A-Level 试卷数字化结构设计 Demo

试卷层级结构：
  Paper (试卷)
    └── Section (部分，如 Section A / Section B)
          └── Question (大题，如 Question 1)
                └── SubQuestion (小题，如 (a)(i))

A-Level 题型分类：
  - multiple_choice:    选择题 (常见于 Paper 1 / MCQ Paper)
  - structured:         结构化问答题 (最常见，分步骤作答并分步给分)
  - essay:              论述题 (常见于文科类科目)
  - calculation:        计算题 (数学/物理/化学)
  - data_response:      数据分析题 (经济学/地理等)
  - experiment:         实验设计/分析题 (物理/化学/生物)
  - graph:              图表绘制/分析题
  - proof:              证明题 (纯数学)
  - case_study:         案例分析题 (商科/经济学)
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


# ==================== 枚举定义 ====================

class ExamBoard(str, Enum):
    """考试局"""
    CIE = "CIE"            # Cambridge International (CAIE)
    EDEXCEL = "Edexcel"     # Pearson Edexcel (IAL)
    AQA = "AQA"
    OCR = "OCR"


class ExamSession(str, Enum):
    """考试季"""
    MAY_JUNE = "May/June"
    OCT_NOV = "October/November"
    FEB_MAR = "February/March"


class Subject(str, Enum):
    """科目"""
    MATHEMATICS = "Mathematics"
    FURTHER_MATHEMATICS = "Further Mathematics"
    PHYSICS = "Physics"
    CHEMISTRY = "Chemistry"
    BIOLOGY = "Biology"
    ECONOMICS = "Economics"
    BUSINESS = "Business"
    ACCOUNTING = "Accounting"
    COMPUTER_SCIENCE = "Computer Science"
    PSYCHOLOGY = "Psychology"
    ENGLISH_LITERATURE = "English Literature"
    HISTORY = "History"
    GEOGRAPHY = "Geography"




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






class Section(BaseModel):
    """
    试卷分区 - 对应 Section A / Section B
    部分 A-Level 试卷会分成不同 Section，有不同的作答要求
    """
    section_label: str = Field(..., description="分区标签，如 'Section A', 'Section B'")
    instructions: Optional[str] = Field(
        ...,
        description="试卷本区作答要求，如 'Answer ALL questions' / 'Answer TWO questions from this section'"
    )
    required_questions: Optional[int] = Field(
        None,
        description="需要作答的题目数量 (None=全部作答)"
    )
    questions: List[Question] = Field(..., min_length=1, description="本区题目列表")
    total_marks: int = Field(..., ge=0, description="本区总分")


# ==================== 试卷顶层结构 ====================

class Paper(BaseModel):
    """
    A-Level 试卷 - 完整试卷的顶层结构
    """
    # ---- 试卷元数据 ----
    education_system:str = Field(...,description="教育体系，如:A-Level、AP等")
    exam_board: ExamBoard = Field(..., description="A-Level或AP对应的考试局，如:Edexcel, CIE, Oxford等")
    subject: Subject = Field(..., description="A-Level或AP对应的科目，如：Maths、Further Maths、Economics等")
    component: str = Field(..., description="不同机构的学科考试对应的模块名称，如：Pure Mathematics P1，Pure Mathematics P2，Unit 1: Markets in Action等")
    syllabus_code: str = Field(..., description="试卷大纲代码，如 '9709/12'")
    year: int = Field(..., ge=2000, le=2600, description="试卷年份")
    session: ExamSession = Field(..., description="考试季")

    # ---- 考试规则 ----
    duration_minutes: int = Field(..., ge=30, description="考试时长(分钟)")
    total_marks: int = Field(..., ge=0, description="试卷总分")

    # ---- 试卷内容 ----
    sections: List[Section] = Field(..., min_length=1, description="试卷分区列表，默认最少有一个Section A")

    # ---- 来源信息 ----
    paper_pdf_urls: List[str] = Field(
        default_factory=list,
        description="试卷原卷url"
    )






class GetTopicsParams(BaseModel):
    education_system: str = Field(None, description="教育体系，如:A-Level、AP等")
    exam_board: str = Field(None, description="考试局，如：Edexcel, CIE, Oxford等")
    year: int = Field(None, description="大纲年份，如 2026")
    key: str = Field(..., description="试卷模块组件名称，如 Pure Mathematics P1")


class GetCommandWordParams(BaseModel):
    subject_name:str = Field(...,description="科目名称，必须小写")


class GetAllPaperModel(BaseModel):
    educationSystem:str = Field(...,description="教育体系，如:A-Level、AP等")
    examBoard:str = Field(..., description="考试局，如：Edexcel, CIE, Oxford等")



