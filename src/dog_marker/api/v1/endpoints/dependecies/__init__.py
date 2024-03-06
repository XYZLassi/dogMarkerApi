__all__ = ["get_db"]

from dog_marker.database.base import SessionLocal


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
