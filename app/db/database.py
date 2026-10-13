from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,     # 断线自动重连
    pool_recycle=3600,      # 1 小时回收
    echo=False,             # True 会打印 SQL，调试用
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_db():
    """FastAPI 依赖注入：每个请求一个 Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()