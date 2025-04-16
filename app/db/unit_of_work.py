from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.category import CategoryRepository
from app.repositories.point import PointRepository


class UnitOfWork:
    """Unit of Work pattern implementation"""

    def __init__(self):
        self._session = None

    @property
    def session(self):
        """Get or create the SQLAlchemy session"""
        if self._session is None:
            self._session = SessionLocal()
        return self._session

    @contextmanager
    def start(self) -> Generator["UnitOfWork", None, None]:
        """Start a new unit of work (database transaction)"""
        try:
            # Initialize repositories with session
            self.points = PointRepository(self.session)
            self.categories = CategoryRepository(self.session)

            yield self
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def close(self):
        """Explicitly close the session when needed"""
        if self._session is not None:
            self._session.close()
            self._session = None
