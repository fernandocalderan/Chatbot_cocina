import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

disable_db = os.getenv("DISABLE_DB") == "1"
if disable_db:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, future=True)
else:
    engine = create_engine(settings.database_url, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_sessionmaker() -> sessionmaker:
    return SessionLocal
