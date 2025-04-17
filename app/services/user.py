from datetime import datetime, timedelta
from typing import Optional

from app.core.security import create_access_token
from app.core.utils import utc_now
from app.repositories.user import UserRepository
from app.schemas.user import Token
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create(self, *, obj_in: UserCreate) -> UserSchema:
        """Create a new user"""
        db_obj = self.repository.create(obj_in=obj_in)
        return UserSchema.model_validate(db_obj)

    def authenticate(self, *, email: str, password: str) -> Optional[UserSchema]:
        """Authenticate a user and return a token"""
        user = self.repository.authenticate(email=email, password=password)
        if not user:
            return None

        # Update last login
        user.last_login = utc_now()
        self.repository.session.commit()

        return UserSchema.model_validate(user)

    def create_token(self, *, user_id: int) -> Token:
        """Create access token for a user"""
        access_token = create_access_token(subject=str(user_id))
        return Token(access_token=access_token, token_type="bearer")
