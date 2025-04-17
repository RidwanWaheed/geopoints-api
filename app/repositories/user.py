from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: Session):
        super().__init__(session=session, model=User)

    def get_by_email(self, *, email: str) -> Optional[User]:
        """Get user by email"""
        return self.session.query(User).filter(User.email == email).first()

    def get_by_username(self, *, username: str) -> Optional[User]:
        """Get user by username"""
        return self.session.query(User).filter(User.username == username).first()

    def create(self, *, obj_in: UserCreate) -> User:
        """Create a new user with hashed password"""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def authenticate(self, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username or email and password
        The username parameter could be either a username or email
        """
        # First try as email
        user = self.get_by_email(email=email)

        # If not found, try as username
        if not user:
            user = self.get_by_username(username=email)

        # If still not found or password doesn't match
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None

        return user
