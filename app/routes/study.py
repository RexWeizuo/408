from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime, date, timedelta
from database import get_db
from models import StudyRecord, DailyPlan, ChapterProgress, KnowledgePoint, Question, UserAnswer
from schemas import StudyRecordCreate, StudyRecordResponse, DailyPlanResponse, ChapterProgressResponse, StudyDashboard
from scheduler import scheduler

router = APIRouter(prefix="/api/study", tags=["学习记录"])

CURRENT_USER_ID = 1


@router.post("/records", response_model=StudyRecordResponse)
async def create_study_record(data: StudyRecordCreate, db: AsyncSession = Depends(get_db)):
    today = date.today()

    result = await db.execute(
        select(StudyRecord).where(
            StudyRecord.user_id == CURRENT_USER_ID,
            StudyRecord.knowledge_point_id == data.knowledge_point_id,
            StudyRecord.study_date == today
        )
    )
    record = result.scalar_one_or_none()

    if record:
        if data.action_type == "learn":
            record.action_type = "learn"
        elif data.action_type == "review":
            record.review_count += 1
            record.last_review_date = today
            record.mastery_level = (record.mastery_level + data.correct_rate) / 2
            record.next_review_date = scheduler.calculate_next_review(
                today, record.review_count, record.mastery_level
            )
            record.interval_days = (record.next_review_date - today).days
        record.time_spent += data.time_spent
        if data.correct_rate > 0:
            record.correct_rate = (record.correct_rate + data.correct_rate) / 2
    else:
        review_count = 1 if data.action_type == "review" else 0
        next_review = scheduler.calculate_next_review(today, review_count, data.correct_rate)
        record = StudyRecord(
            user_id=CURRENT_USER_ID,
            knowledge_point_id=data.knowledge_point_id,
            action_type=data.action_type,
            study_date=today,
            time_spent=data.time_spent,
            correct_rate=data.correct_rate,
            mastery_level=data.correct_rate,
            review_count=review_count,
            next_review_date=next_review,
            last_review_date=today if data.action_type == "review" else None,
            interval_days=(next_review - today).days
        )
        db.add(record)

    await db.commit()
    await db.refresh(record)
    return record


@router.get("/records", response_model=List[StudyRecordResponse])
async def get_study_records(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(StudyRecord)
        .where(StudyRecord.user_id == CURRENT_USER_ID)
        .order_by(StudyRecord.study_date.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/today-reviews")
async def get_today_reviews(db: AsyncSession = Depends(get_db)):
    today = date.today()

    result = await db.execute(
        select(StudyRecord).where(
            StudyRecord.user_id == CURRENT_USER_ID,
            StudyRecord.next_review_date != None,
            StudyRecord.next_review_date <= today
        ).order_by(StudyRecord.next_review_date.asc())
    )
    reviews = result.scalars().all()

    review_list = []
    for r in reviews:
        kp_result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.id == r.knowledge_point_id))
        kp = kp_result.scalar_one_or_none()
        urgency = scheduler.get_review_urgency(r.next_review_date, today, r.mastery_level)
        review_list.append({
            "record_id": r.id,
            "knowledge_point_id": r.knowledge_point_id,
            "knowledge_point_name": kp.name if kp else "未知",
            "mastery_level": r.mastery_level,
            "review_count": r.review_count,
            "next_review_date": r.next_review_date.isoformat(),
            "urgency": urgency
        })

    return review_list


@router.get("/dashboard", response_model=StudyDashboard)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    today = date.today()

    today_plan_result = await db.execute(
        select(DailyPlan).where(
            DailyPlan.user_id == CURRENT_USER_ID,
            DailyPlan.plan_date == today
        )
    )
    today_plan = today_plan_result.scalar_one_or_none()

    today_new_count = len(today_plan.new_knowledge_points) if today_plan else 0
    today_review_count = len(today_plan.review_knowledge_points) if today_plan else 0
    today_question_count = len(today_plan.practice_questions) if today_plan else 0

    today_completed_percentage = 0
    if today_plan and (today_new_count + today_review_count + today_question_count) > 0:
        total = today_new_count + today_review_count + today_question_count
        done = 0
        if today_plan.is_completed:
            done = total
        today_completed_percentage = (done / total) * 100

    chapter_result = await db.execute(
        select(ChapterProgress).where(ChapterProgress.user_id == CURRENT_USER_ID)
    )
    chapters = chapter_result.scalars().all()
    subject_progress = {}
    for cp in chapters:
        if cp.subject_id not in subject_progress:
            subject_progress[cp.subject_id] = {"chapters": []}
        subject_progress[cp.subject_id]["chapters"].append({
            "chapter_id": cp.chapter_id,
            "completion_percentage": cp.completion_percentage,
            "average_correct_rate": cp.average_correct_rate
        })

    today_reviews = await get_today_reviews(db)
    urgent_reviews = [r for r in today_reviews if r["urgency"] in ["overdue", "due_today"]]

    weak_result = await db.execute(
        select(StudyRecord).where(
            StudyRecord.user_id == CURRENT_USER_ID,
            StudyRecord.mastery_level < 0.6
        ).order_by(StudyRecord.mastery_level.asc()).limit(10)
    )
    weak_records = weak_result.scalars().all()
    weak_points = []
    for wr in weak_records:
        kp_result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.id == wr.knowledge_point_id))
        kp = kp_result.scalar_one_or_none()
        weak_points.append({
            "knowledge_point_id": wr.knowledge_point_id,
            "name": kp.name if kp else "未知",
            "mastery_level": wr.mastery_level
        })

    return StudyDashboard(
        today_new_count=today_new_count,
        today_review_count=today_review_count,
        today_question_count=today_question_count,
        today_completed_percentage=today_completed_percentage,
        subject_progress=[{"subject_id": k, **v} for k, v in subject_progress.items()],
        urgent_reviews=urgent_reviews,
        weak_points=weak_points
    )


@router.get("/chapter-progress/{chapter_id}", response_model=ChapterProgressResponse)
async def get_chapter_progress(chapter_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChapterProgress).where(
            ChapterProgress.user_id == CURRENT_USER_ID,
            ChapterProgress.chapter_id == chapter_id
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        kp_result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.chapter_id == chapter_id))
        kps = kp_result.scalars().all()
        total_kp = len(kps)

        q_result = await db.execute(
            select(func.count(Question.id)).where(Question.knowledge_point_id.in_([kp.id for kp in kps]))
        )
        total_q = q_result.scalar() or 0

        progress = ChapterProgress(
            user_id=CURRENT_USER_ID,
            subject_id="",
            chapter_id=chapter_id,
            total_knowledge_points=total_kp,
            completed_knowledge_points=0,
            total_questions=total_q,
            completed_questions=0,
            average_correct_rate=0.0,
            last_studied_date=None,
            completion_percentage=0.0
        )
        db.add(progress)
        await db.commit()
        await db.refresh(progress)

    return progress


@router.get("/weekly-stats")
async def get_weekly_stats(db: AsyncSession = Depends(get_db)):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    result = await db.execute(
        select(StudyRecord).where(
            StudyRecord.user_id == CURRENT_USER_ID,
            StudyRecord.study_date >= week_start,
            StudyRecord.study_date <= week_end
        )
    )
    records = result.scalars().all()

    study_days = len(set(r.study_date for r in records))
    total_time = sum(r.time_spent for r in records)
    new_kp = sum(1 for r in records if r.action_type == "learn")
    reviewed_kp = sum(1 for r in records if r.action_type == "review")

    answer_result = await db.execute(
        select(UserAnswer).where(
            UserAnswer.user_id == CURRENT_USER_ID,
            UserAnswer.answered_at >= datetime.combine(week_start, datetime.min.time()),
            UserAnswer.answered_at <= datetime.combine(week_end, datetime.max.time())
        )
    )
    answers = answer_result.scalars().all()
    questions_practiced = len(answers)
    avg_correct = (sum(1 for a in answers if a.is_correct) / questions_practiced * 100) if questions_practiced > 0 else 0

    weak_points = [r.knowledge_point_id for r in records if r.mastery_level < 0.6]

    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "study_days": study_days,
        "total_time_spent": total_time,
        "new_knowledge_points": new_kp,
        "reviewed_knowledge_points": reviewed_kp,
        "questions_practiced": questions_practiced,
        "average_correct_rate": round(avg_correct, 2),
        "weak_points": list(set(weak_points))
    }
