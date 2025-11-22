import os
from collections.abc import Generator

from app.db.session import SessionLocal


class DummyQuery:
    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return None

    def all(self):
        return []


class DummySession:
    def query(self, *args, **kwargs):
        return DummyQuery()

    def add(self, *args, **kwargs):
        return None

    def commit(self):
        return None

    def rollback(self):
        return None

    def close(self):
        return None


def get_db() -> Generator:
    if os.getenv("DISABLE_DB") == "1":
        dummy = DummySession()
        try:
            yield dummy
        finally:
            dummy.close()
        return

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
