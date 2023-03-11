from src.db import SessionLocal
from functools import lru_cache
import src.config as config


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache()
def get_settings():
    return config.Settings()
