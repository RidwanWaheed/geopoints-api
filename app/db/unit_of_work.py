from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.category import CategoryRepository
from app.repositories.point import PointRepository


class UnitOfWork:
    """
    The Unit of Work pattern ensures that repositories share the same database
    session and provides transaction management.
    """

    def __init__(self):
        self.session_factory = SessionLocal

    @contextmanager
    def start(self) -> Generator["UnitOfWork", None, None]:
        """Start a new unit of work (database transaction)"""
        session = self.session_factory()
        try:
            self.points = PointRepository(session)
            self.categories = CategoryRepository(session)
            
            yield self
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()