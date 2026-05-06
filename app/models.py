from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Date, JSON, Time
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    score = Column(Integer, nullable=False)


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String, primary_key=True)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=False)
    name = Column(String, nullable=False)
    order_index = Column(Integer, default=0)


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(String, primary_key=True)
    chapter_id = Column(String, ForeignKey("chapters.id"), nullable=False)
    name = Column(String, nullable=False)
    content = Column(Text, default="")
    order_index = Column(Integer, default=0)
    pdf_page = Column(Integer, nullable=True)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(String, ForeignKey("knowledge_points.id"), nullable=False)
    type = Column(String, default="choice")
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    answer = Column(String, nullable=False)
    explanation = Column(Text, default="")
    difficulty = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    exam_date = Column(Date, default="2026-12-19")
    daily_study_hours = Column(Integer, default=120)
    created_at = Column(DateTime, default=datetime.now)


class StudyRecord(Base):
    __tablename__ = "study_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_point_id = Column(String, ForeignKey("knowledge_points.id"), nullable=False)
    action_type = Column(String, nullable=False)
    study_date = Column(Date, nullable=False)
    time_spent = Column(Integer, default=0)
    correct_rate = Column(Float, default=0.0)
    mastery_level = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    next_review_date = Column(Date, nullable=True)
    last_review_date = Column(Date, nullable=True)
    interval_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class DailyPlan(Base):
    __tablename__ = "daily_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_date = Column(Date, nullable=False)
    new_knowledge_points = Column(JSON, default=[])
    review_knowledge_points = Column(JSON, default=[])
    practice_questions = Column(JSON, default=[])
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)


class ChapterProgress(Base):
    __tablename__ = "chapter_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(String, nullable=False)
    chapter_id = Column(String, nullable=False)
    total_knowledge_points = Column(Integer, default=0)
    completed_knowledge_points = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    completed_questions = Column(Integer, default=0)
    average_correct_rate = Column(Float, default=0.0)
    last_studied_date = Column(Date, nullable=True)
    completion_percentage = Column(Float, default=0.0)


class WeeklyStats(Base):
    __tablename__ = "weekly_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    week_end_date = Column(Date, nullable=False)
    study_days = Column(Integer, default=0)
    total_time_spent = Column(Integer, default=0)
    new_knowledge_points = Column(Integer, default=0)
    reviewed_knowledge_points = Column(Integer, default=0)
    questions_practiced = Column(Integer, default=0)
    average_correct_rate = Column(Float, default=0.0)
    weak_points = Column(JSON, default=[])


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    user_process = Column(Text, default="")
    answered_at = Column(DateTime, default=datetime.now)


class LionSubject(Base):
    __tablename__ = "lion_subjects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class LionLevel1(Base):
    __tablename__ = "lion_level1"

    id = Column(String, primary_key=True)
    lion_subject_id = Column(String, ForeignKey("lion_subjects.id"), nullable=False)
    name = Column(String, nullable=False)
    order_index = Column(Integer, default=0)


class LionLevel2(Base):
    __tablename__ = "lion_level2"

    id = Column(String, primary_key=True)
    level1_id = Column(String, ForeignKey("lion_level1.id"), nullable=False)
    name = Column(String, nullable=False)
    order_index = Column(Integer, default=0)


class LionLevel3(Base):
    __tablename__ = "lion_level3"

    id = Column(String, primary_key=True)
    level2_id = Column(String, ForeignKey("lion_level2.id"), nullable=False)
    name = Column(String, nullable=False)
    order_index = Column(Integer, default=0)


class LionLevel4(Base):
    __tablename__ = "lion_level4"

    id = Column(String, primary_key=True)
    level3_id = Column(String, ForeignKey("lion_level3.id"), nullable=False)
    name = Column(String, nullable=False)
    content = Column(Text, default="")
    order_index = Column(Integer, default=0)


class LionQuestion(Base):
    __tablename__ = "lion_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level2_id = Column(String, ForeignKey("lion_level2.id"), nullable=False)
    question = Column(Text, nullable=False)
    user_answer = Column(Text, default="")
    reference_answer = Column(Text, default="")
    order_index = Column(Integer, default=0)
