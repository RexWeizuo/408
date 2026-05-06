from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import LionSubject, LionLevel1, LionLevel2, LionLevel3, LionLevel4

router = APIRouter(prefix="/api/lion", tags=["LION层级"])


def _build_level4_map(level4s):
    """Build {level3_id: [level4_dict, ...]}"""
    m = {}
    for l4 in level4s:
        m.setdefault(l4.level3_id, []).append({
            "id": l4.id,
            "name": l4.name,
            "content": l4.content,
            "order_index": l4.order_index,
        })
    return m


def _build_level3_list(level3s, l4_map):
    """Build list of level3 dicts with children."""
    result = []
    for l3 in level3s:
        result.append({
            "id": l3.id,
            "name": l3.name,
            "order_index": l3.order_index,
            "children": l4_map.get(l3.id, []),
        })
    return result


def _build_level2_list(level2s, l3_map):
    result = []
    for l2 in level2s:
        result.append({
            "id": l2.id,
            "name": l2.name,
            "order_index": l2.order_index,
            "children": l3_map.get(l2.id, []),
        })
    return result


def _build_level1_list(level1s, l2_map):
    result = []
    for l1 in level1s:
        result.append({
            "id": l1.id,
            "name": l1.name,
            "order_index": l1.order_index,
            "children": l2_map.get(l1.id, []),
        })
    return result


def _group_by(key_attr, items):
    m = {}
    for item in items:
        m.setdefault(getattr(item, key_attr), []).append(item)
    return m


@router.get("/subjects")
async def get_lion_subjects(db: AsyncSession = Depends(get_db)):
    """一次性加载所有层级，在内存中组装树（避免 N+1 查询）"""
    # 批量加载所有数据
    subjects_result = await db.execute(select(LionSubject).order_by(LionSubject.id))
    subjects = subjects_result.scalars().all()

    level1s_result = await db.execute(
        select(LionLevel1).order_by(LionLevel1.lion_subject_id, LionLevel1.order_index)
    )
    level1s = level1s_result.scalars().all()

    level2s_result = await db.execute(
        select(LionLevel2).order_by(LionLevel2.level1_id, LionLevel2.order_index)
    )
    level2s = level2s_result.scalars().all()

    level3s_result = await db.execute(
        select(LionLevel3).order_by(LionLevel3.level2_id, LionLevel3.order_index)
    )
    level3s = level3s_result.scalars().all()

    level4s_result = await db.execute(
        select(LionLevel4).order_by(LionLevel4.level3_id, LionLevel4.order_index)
    )
    level4s = level4s_result.scalars().all()

    # 内存中组装
    l1_by_subject = _group_by("lion_subject_id", level1s)
    l2_by_l1 = _group_by("level1_id", level2s)
    l3_by_l2 = _group_by("level2_id", level3s)
    l4_map = _build_level4_map(level4s)

    subject_list = []
    for subject in subjects:
        l1s = l1_by_subject.get(subject.id, [])
        l1_list = []
        for l1 in l1s:
            l2s = l2_by_l1.get(l1.id, [])
            l2_list = []
            for l2 in l2s:
                l3s = l3_by_l2.get(l2.id, [])
                l3_list = _build_level3_list(l3s, l4_map)
                l2_list.append({
                    "id": l2.id,
                    "name": l2.name,
                    "order_index": l2.order_index,
                    "children": l3_list,
                })
            l1_list.append({
                "id": l1.id,
                "name": l1.name,
                "order_index": l1.order_index,
                "children": l2_list,
            })
        subject_list.append({
            "id": subject.id,
            "name": subject.name,
            "children": l1_list,
        })

    return {"subjects": subject_list}


@router.get("/{subject_id}")
async def get_lion_subject_detail(subject_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LionSubject).where(LionSubject.id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="LION学科不存在")

    # 批量加载该学科的所有层级
    level1s_result = await db.execute(
        select(LionLevel1)
        .where(LionLevel1.lion_subject_id == subject_id)
        .order_by(LionLevel1.order_index)
    )
    level1s = level1s_result.scalars().all()
    l1_ids = [l1.id for l1 in level1s]

    level2s = []
    l2_by_l1 = {}
    if l1_ids:
        l2_result = await db.execute(
            select(LionLevel2)
            .where(LionLevel2.level1_id.in_(l1_ids))
            .order_by(LionLevel2.order_index)
        )
        level2s = l2_result.scalars().all()
        l2_by_l1 = _group_by("level1_id", level2s)

    l2_ids = [l2.id for l2 in level2s]
    level3s = []
    l3_by_l2 = {}
    if l2_ids:
        l3_result = await db.execute(
            select(LionLevel3)
            .where(LionLevel3.level2_id.in_(l2_ids))
            .order_by(LionLevel3.order_index)
        )
        level3s = l3_result.scalars().all()
        l3_by_l2 = _group_by("level2_id", level3s)

    l3_ids = [l3.id for l3 in level3s]
    l4_map = {}
    if l3_ids:
        l4_result = await db.execute(
            select(LionLevel4)
            .where(LionLevel4.level3_id.in_(l3_ids))
            .order_by(LionLevel4.order_index)
        )
        l4_map = _build_level4_map(l4_result.scalars().all())

    l1_list = []
    for l1 in level1s:
        l2s = l2_by_l1.get(l1.id, [])
        l2_list = []
        for l2 in l2s:
            l3s = l3_by_l2.get(l2.id, [])
            l3_list = _build_level3_list(l3s, l4_map)
            l2_list.append({
                "id": l2.id,
                "name": l2.name,
                "order_index": l2.order_index,
                "children": l3_list,
            })
        l1_list.append({
            "id": l1.id,
            "name": l1.name,
            "order_index": l1.order_index,
            "children": l2_list,
        })

    return {
        "id": subject.id,
        "name": subject.name,
        "children": l1_list,
    }
