from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class KnowledgePointCreate(BaseModel):
    id: str
    chapter_id: str
    name: str
    content: str = ""
    order_index: int = 0
    pdf_page: Optional[int] = None


class KnowledgePointUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None


class KnowledgePointResponse(BaseModel):
    id: str
    chapter_id: str
    name: str
    content: str
    order_index: int
    pdf_page: Optional[int]

    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    knowledge_point_id: str
    type: str = "choice"
    question: str
    options: List[str]
    answer: str
    explanation: str = ""
    difficulty: int = 1


class QuestionUpdate(BaseModel):
    question: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[int] = None


class QuestionResponse(BaseModel):
    id: int
    knowledge_point_id: str
    type: str
    question: str
    options: List[str]
    answer: str
    explanation: str
    difficulty: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserAnswerCreate(BaseModel):
    question_id: int
    user_answer: str
    user_process: str = ""


class UserAnswerResponse(BaseModel):
    id: int
    user_id: int
    question_id: int
    user_answer: str
    is_correct: bool
    user_process: str
    answered_at: datetime

    class Config:
        from_attributes = True


class StudyRecordCreate(BaseModel):
    knowledge_point_id: str
    action_type: str
    time_spent: int = 0
    correct_rate: float = 0.0


class StudyRecordResponse(BaseModel):
    id: int
    user_id: int
    knowledge_point_id: str
    action_type: str
    study_date: date
    time_spent: int
    correct_rate: float
    mastery_level: float
    review_count: int
    next_review_date: Optional[date]
    last_review_date: Optional[date]
    interval_days: int

    class Config:
        from_attributes = True


class ChapterProgressResponse(BaseModel):
    id: int
    user_id: int
    subject_id: str
    chapter_id: str
    total_knowledge_points: int
    completed_knowledge_points: int
    total_questions: int
    completed_questions: int
    average_correct_rate: float
    last_studied_date: Optional[date]
    completion_percentage: float

    class Config:
        from_attributes = True


class DailyPlanResponse(BaseModel):
    id: int
    user_id: int
    plan_date: date
    new_knowledge_points: List[str]
    review_knowledge_points: List[str]
    practice_questions: List[int]
    is_completed: bool
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class StudyDashboard(BaseModel):
    today_new_count: int
    today_review_count: int
    today_question_count: int
    today_completed_percentage: float
    subject_progress: List[dict]
    urgent_reviews: List[dict]
    weak_points: List[dict]


class LionQuestionCreate(BaseModel):
    level2_id: str
    question: str
    user_answer: str = ""
    reference_answer: str = ""
    order_index: int = 0


class LionQuestionUpdate(BaseModel):
    question: Optional[str] = None
    user_answer: Optional[str] = None
    reference_answer: Optional[str] = None
    order_index: Optional[int] = None


class LionQuestionResponse(BaseModel):
    id: int
    level2_id: str
    question: str
    user_answer: str
    reference_answer: str
    order_index: int

    class Config:
        from_attributes = True
