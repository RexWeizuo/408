import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    _db_dir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    _db_path: str = os.path.join(_db_dir, "408_study.db")
    DATABASE_URL: str = f"sqlite+aiosqlite:///{_db_path}"
    EXAM_DATE: str = "2026-12-19"

    model_config = {"env_file": ".env"}


settings = Settings()
