from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from database import get_db
from models import LionQuestion, LionLevel2, LionLevel1, LionSubject
from schemas import LionQuestionCreate, LionQuestionUpdate, LionQuestionResponse

router = APIRouter(prefix="/api/lion-questions", tags=["知识点问题"])


@router.get("/tree")
async def get_questions_tree(
    subject_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """批量加载数据，在内存中组装树（避免 N+1 查询）"""
    # 一次性加载所有相关数据
    subjects_result = await db.execute(select(LionSubject).order_by(LionSubject.id))
    subjects = subjects_result.scalars().all()

    l1_result = await db.execute(
        select(LionLevel1).order_by(LionLevel1.lion_subject_id, LionLevel1.order_index)
    )
    all_level1s = l1_result.scalars().all()

    l2_result = await db.execute(
        select(LionLevel2).order_by(LionLevel2.level1_id, LionLevel2.order_index)
    )
    all_level2s = l2_result.scalars().all()

    # 只查出有题目的 level2
    q_result = await db.execute(
        select(LionQuestion).order_by(LionQuestion.level2_id, LionQuestion.order_index, LionQuestion.id)
    )
    all_questions = q_result.scalars().all()

    # 按 level2_id 分组题目
    q_by_l2 = {}
    for q in all_questions:
        q_by_l2.setdefault(q.level2_id, []).append(q)

    # 需要保留的 level2/level1/subject（只有含题目的路径）
    l2_ids_with_q = set(q_by_l2.keys())
    l1_to_l2s = {}
    l2_objects = {}
    for l2 in all_level2s:
        l2_objects[l2.id] = l2
        if l2.id in l2_ids_with_q:
            l1_to_l2s.setdefault(l2.level1_id, []).append(l2)

    l1_objects = {l1.id: l1 for l1 in all_level1s if l1.id in l1_to_l2s}
    subject_ids_with_q = {l1_objects[l1_id].lion_subject_id for l1_id in l1_to_l2s}

    result_data = []
    for subject in subjects:
        if subject_id and subject.id != subject_id:
            continue
        if subject.id not in subject_ids_with_q:
            continue

        level1_list = []
        for l1 in all_level1s:
            if l1.lion_subject_id != subject.id:
                continue
            if l1.id not in l1_to_l2s:
                continue

            l2_list = []
            for l2 in l1_to_l2s[l1.id]:
                questions = q_by_l2.get(l2.id, [])
                if questions:
                    l2_list.append({
                        "id": l2.id,
                        "name": l2.name,
                        "questions": [{
                            "id": q.id,
                            "question": q.question,
                            "user_answer": q.user_answer,
                            "reference_answer": q.reference_answer,
                        } for q in questions],
                    })

            if l2_list:
                level1_list.append({
                    "id": l1.id,
                    "name": l1.name,
                    "level2s": l2_list,
                })

        if level1_list:
            result_data.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "level1s": level1_list,
            })

    return {"subjects": result_data}


@router.get("/{question_id}", response_model=LionQuestionResponse)
async def get_question(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LionQuestion).where(LionQuestion.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="问题不存在")
    return question


@router.post("/", response_model=LionQuestionResponse)
async def create_question(data: LionQuestionCreate, db: AsyncSession = Depends(get_db)):
    question = LionQuestion(
        level2_id=data.level2_id,
        question=data.question,
        user_answer=data.user_answer,
        reference_answer=data.reference_answer,
        order_index=data.order_index
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


@router.put("/{question_id}", response_model=LionQuestionResponse)
async def update_question(question_id: int, data: LionQuestionUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LionQuestion).where(LionQuestion.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="问题不存在")

    if data.question is not None:
        question.question = data.question
    if data.user_answer is not None:
        question.user_answer = data.user_answer
    if data.reference_answer is not None:
        question.reference_answer = data.reference_answer
    if data.order_index is not None:
        question.order_index = data.order_index

    await db.commit()
    await db.refresh(question)
    return question


@router.delete("/{question_id}")
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LionQuestion).where(LionQuestion.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="问题不存在")

    await db.delete(question)
    await db.commit()
    return {"message": "删除成功"}
