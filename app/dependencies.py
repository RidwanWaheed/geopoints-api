from typing import Generator
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models.base import Base

# Initialize database tables
def init_db() -> None:
    Base.metadata.create_all(bind=engine)

# Database session dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()