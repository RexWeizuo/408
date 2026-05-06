from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from database import get_db
from models import KnowledgePoint, Chapter
from schemas import KnowledgePointCreate, KnowledgePointUpdate, KnowledgePointResponse

router = APIRouter(prefix="/api/knowledge-points", tags=["知识点"])


@router.get("/", response_model=List[KnowledgePointResponse])
async def get_all_knowledge_points(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgePoint).order_by(KnowledgePoint.id))
    return result.scalars().all()


@router.get("/by-chapter/{chapter_id}", response_model=List[KnowledgePointResponse])
async def get_knowledge_points_by_chapter(chapter_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(KnowledgePoint)
        .where(KnowledgePoint.chapter_id == chapter_id)
        .order_by(KnowledgePoint.order_index)
    )
    return result.scalars().all()


@router.get("/{kp_id}", response_model=KnowledgePointResponse)
async def get_knowledge_point(kp_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.id == kp_id))
    kp = result.scalar_one_or_none()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    return kp


@router.post("/", response_model=KnowledgePointResponse)
async def create_knowledge_point(data: KnowledgePointCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(KnowledgePoint).where(KnowledgePoint.id == data.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="知识点ID已存在")

    kp = KnowledgePoint(
        id=data.id,
        chapter_id=data.chapter_id,
        name=data.name,
        content=data.content,
        order_index=data.order_index,
        pdf_page=data.pdf_page
    )
    db.add(kp)
    await db.commit()
    await db.refresh(kp)
    return kp


@router.put("/{kp_id}", response_model=KnowledgePointResponse)
async def update_knowledge_point(kp_id: str, data: KnowledgePointUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.id == kp_id))
    kp = result.scalar_one_or_none()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")

    if data.name is not None:
        kp.name = data.name
    if data.content is not None:
        kp.content = data.content

    await db.commit()
    await db.refresh(kp)
    return kp


@router.delete("/{kp_id}")
async def delete_knowledge_point(kp_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.id == kp_id))
    kp = result.scalar_one_or_none()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")

    await db.delete(kp)
    await db.commit()
    return {"message": "删除成功"}
