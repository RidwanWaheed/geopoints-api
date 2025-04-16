from app.base import Base
from app.database import SessionLocal, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
