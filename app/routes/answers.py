from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
from database import get_db
from models import UserAnswer, Question, StudyRecord
from schemas import UserAnswerCreate, UserAnswerResponse

router = APIRouter(prefix="/api/answers", tags=["答题"])

CURRENT_USER_ID = 1


@router.post("/", response_model=UserAnswerResponse)
async def submit_answer(data: UserAnswerCreate, db: AsyncSession = Depends(get_db)):
    question_result = await db.execute(select(Question).where(Question.id == data.question_id))
    question = question_result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    is_correct = data.user_answer.upper() == question.answer.upper()

    answer = UserAnswer(
        user_id=CURRENT_USER_ID,
        question_id=data.question_id,
        user_answer=data.user_answer.upper(),
        is_correct=is_correct,
        user_process=data.user_process
    )
    db.add(answer)
    await db.commit()
    await db.refresh(answer)

    return answer


@router.get("/{question_id}", response_model=List[UserAnswerResponse])
async def get_question_answers(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserAnswer)
        .where(UserAnswer.user_id == CURRENT_USER_ID, UserAnswer.question_id == question_id)
        .order_by(UserAnswer.answered_at.desc())
    )
    return result.scalars().all()


@router.get("/history", response_model=List[UserAnswerResponse])
async def get_answer_history(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserAnswer)
        .where(UserAnswer.user_id == CURRENT_USER_ID)
        .order_by(UserAnswer.answered_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/stats")
async def get_answer_stats(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(
        select(UserAnswer).where(UserAnswer.user_id == CURRENT_USER_ID)
    )
    total_answers = total_result.scalars().all()

    total_count = len(total_answers)
    if total_count == 0:
        return {
            "total_questions": 0,
            "correct_count": 0,
            "wrong_count": 0,
            "correct_rate": 0.0
        }

    correct_count = sum(1 for a in total_answers if a.is_correct)
    wrong_count = total_count - correct_count
    correct_rate = correct_count / total_count * 100 if total_count > 0 else 0

    return {
        "total_questions": total_count,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "correct_rate": round(correct_rate, 2)
    }
