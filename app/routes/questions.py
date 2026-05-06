from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from database import get_db
from models import Question, KnowledgePoint, Chapter
from schemas import QuestionCreate, QuestionUpdate, QuestionResponse

router = APIRouter(prefix="/api/questions", tags=["题目"])


@router.get("/", response_model=List[QuestionResponse])
async def get_all_questions(
    knowledge_point_id: Optional[str] = None,
    chapter_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    type: Optional[str] = None,
    difficulty: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Question)

    if knowledge_point_id:
        query = query.where(Question.knowledge_point_id == knowledge_point_id)
    if type:
        query = query.where(Question.type == type)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)

    if chapter_id:
        kp_result = await db.execute(
            select(KnowledgePoint.id).where(KnowledgePoint.chapter_id == chapter_id)
        )
        kp_ids = [row[0] for row in kp_result.fetchall()]
        if kp_ids:
            query = query.where(Question.knowledge_point_id.in_(kp_ids))
        else:
            return []

    if subject_id:
        ch_result = await db.execute(
            select(Chapter.id).where(Chapter.subject_id == subject_id)
        )
        ch_ids = [row[0] for row in ch_result.fetchall()]
        if ch_ids:
            kp_result = await db.execute(
                select(KnowledgePoint.id).where(KnowledgePoint.chapter_id.in_(ch_ids))
            )
            kp_ids = [row[0] for row in kp_result.fetchall()]
            if kp_ids:
                query = query.where(Question.knowledge_point_id.in_(kp_ids))
            else:
                return []
        else:
            return []

    query = query.order_by(Question.knowledge_point_id, Question.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/grouped")
async def get_questions_grouped(
    subject_id: Optional[str] = None,
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    from models import Subject
    subjects_result = await db.execute(select(Subject).order_by(Subject.id))
    subjects = subjects_result.scalars().all()

    result_data = []
    for subj in subjects:
        if subject_id and subj.id != subject_id:
            continue

        chapters_result = await db.execute(
            select(Chapter).where(Chapter.subject_id == subj.id).order_by(Chapter.order_index)
        )
        chapters = chapters_result.scalars().all()

        chapter_data = []
        for ch in chapters:
            kp_result = await db.execute(
                select(KnowledgePoint).where(KnowledgePoint.chapter_id == ch.id).order_by(KnowledgePoint.order_index)
            )
            kps = kp_result.scalars().all()
            kp_ids = [kp.id for kp in kps]

            if not kp_ids:
                continue

            q_query = select(Question).where(Question.knowledge_point_id.in_(kp_ids))
            if type:
                q_query = q_query.where(Question.type == type)
            q_query = q_query.order_by(Question.id)
            q_result = await db.execute(q_query)
            questions = q_result.scalars().all()

            if not questions:
                continue

            kp_data = []
            for kp in kps:
                kp_questions = [q for q in questions if q.knowledge_point_id == kp.id]
                if kp_questions:
                    kp_data.append({
                        "knowledge_point_id": kp.id,
                        "knowledge_point_name": kp.name,
                        "questions": [
                            {
                                "id": q.id,
                                "type": q.type,
                                "question": q.question,
                                "options": q.options,
                                "answer": q.answer,
                                "explanation": q.explanation,
                                "difficulty": q.difficulty
                            } for q in kp_questions
                        ]
                    })

            if kp_data:
                chapter_data.append({
                    "chapter_id": ch.id,
                    "chapter_name": ch.name,
                    "knowledge_points": kp_data
                })

        if chapter_data:
            result_data.append({
                "subject_id": subj.id,
                "chapters": chapter_data
            })

    return {"subjects": result_data}


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question


@router.post("/", response_model=QuestionResponse)
async def create_question(data: QuestionCreate, db: AsyncSession = Depends(get_db)):
    question = Question(
        knowledge_point_id=data.knowledge_point_id,
        type=data.type,
        question=data.question,
        options=data.options,
        answer=data.answer,
        explanation=data.explanation,
        difficulty=data.difficulty
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, data: QuestionUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    if data.question is not None:
        question.question = data.question
    if data.options is not None:
        question.options = data.options
    if data.answer is not None:
        question.answer = data.answer
    if data.explanation is not None:
        question.explanation = data.explanation
    if data.difficulty is not None:
        question.difficulty = data.difficulty

    await db.commit()
    await db.refresh(question)
    return question


@router.delete("/{question_id}")
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    await db.delete(question)
    await db.commit()
    return {"message": "删除成功"}
