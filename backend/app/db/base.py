from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here so Alembic can autogenerate migrations.
# flake8: noqa
from app import models  # noqa: E402,F401

__all__ = ["Base"]
