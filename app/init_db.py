import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session, engine
from models import Base, Subject, Chapter, KnowledgePoint
import os

async def init_db():
    """初始化数据库并导入大纲结构"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 导入大纲结构
    syllabus_path = os.path.join(os.path.dirname(__file__), "syllabus_structure.json")
    with open(syllabus_path, "r", encoding="utf-8") as f:
        syllabus = json.load(f)

    async with async_session() as session:
        async with session.begin():
            # 检查是否已导入
            result = await session.execute(Subject.__table__.select())
            if result.fetchall():
                print("大纲数据已存在，跳过导入")
                return

            for subject_data in syllabus["subjects"]:
                subject = Subject(
                    id=subject_data["id"],
                    name=subject_data["name"],
                    score=subject_data["score"]
                )
                session.add(subject)

                for idx_ch, chapter_data in enumerate(subject_data["chapters"]):
                    chapter = Chapter(
                        id=chapter_data["id"],
                        subject_id=subject_data["id"],
                        name=chapter_data["name"],
                        order_index=idx_ch
                    )
                    session.add(chapter)

                    for idx_kp, kp_data in enumerate(chapter_data["knowledge_points"]):
                        kp = KnowledgePoint(
                            id=kp_data["id"],
                            chapter_id=chapter_data["id"],
                            name=kp_data["name"],
                            content="",
                            order_index=idx_kp
                        )
                        session.add(kp)

            await session.commit()
            print("大纲数据导入成功")


if __name__ == "__main__":
    asyncio.run(init_db())
