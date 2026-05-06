from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, async_session
from models import Base
from routes import knowledge_points, questions, answers, study, lion, lion_questions


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    from init_db import init_db
    await init_db()
    from init_lion_db import init_lion_db
    await init_lion_db()
    yield


app = FastAPI(title="408学习系统", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(knowledge_points.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(study.router)
app.include_router(lion.router)
app.include_router(lion_questions.router)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "408学习系统API", "version": "1.0.0", "tip": "请先运行 npm run build 构建前端"}


@app.get("/api/subjects")
async def get_subjects():
    """考纲科目列表"""
    from database import get_db
    from models import Subject, Chapter
    from sqlalchemy import select
    async for db in get_db():
        result = await db.execute(select(Subject).order_by(Subject.id))
        subjects = result.scalars().all()
        
        subject_list = []
        for subject in subjects:
            chapter_result = await db.execute(
                select(Chapter)
                .where(Chapter.subject_id == subject.id)
                .order_by(Chapter.order_index)
            )
            chapters = chapter_result.scalars().all()
            
            subject_list.append({
                "id": subject.id,
                "name": subject.name,
                "score": subject.score,
                "chapters": [{"id": ch.id, "name": ch.name} for ch in chapters]
            })
        
        return {"subjects": subject_list}
