from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.core.utils import utc_now
from app.models.user import User


class UserRepository:

    def __init__(self, session: Session):
        self.session = session

    def get(self, id: int) -> Optional[User]:

        return self.session.query(User).filter(User.id == id).first()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[User]:
        return self.session.query(User).offset(skip).limit(limit).all()

    def get_by_email(self, *, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def get_by_username(self, *, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.username == username).first()

    def create(
        self,
        *,
        email: str,
        username: str,
        password: str,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        hashed_password = get_password_hash(password)

        db_obj = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=is_active,
            is_superuser=is_superuser,
        )

        self.session.add(db_obj)
        return db_obj

    def update(self, *, db_obj: User, obj_data: Dict[str, Any]) -> User:
        if "password" in obj_data:
            hashed_password = get_password_hash(obj_data.pop("password"))
            db_obj.hashed_password = hashed_password

        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.add(db_obj)
        return db_obj

    def delete(self, *, id: int) -> Optional[User]:
        obj = self.get(id=id)
        if not obj:
            return None

        self.session.delete(obj)
        return obj

    def authenticate(self, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email=email)

        if not user:
            # Try by username if email lookup fails
            user = self.get_by_username(username=email)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    def update_last_login(self, *, user_id: int) -> Optional[User]:
        user = self.get(id=user_id)
        if not user:
            return None

        user.last_login = utc_now()

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def count(self) -> int:
        return self.session.query(func.count(User.id)).scalar()

    def email_exists(self, *, email: str, exclude_id: Optional[int] = None) -> bool:
        query = self.session.query(User).filter(User.email == email)
        if exclude_id is not None:
            query = query.filter(User.id != exclude_id)
        return self.session.query(query.exists()).scalar()

    def username_exists(
        self, *, username: str, exclude_id: Optional[int] = None
    ) -> bool:
        query = self.session.query(User).filter(User.username == username)
        if exclude_id is not None:
            query = query.filter(User.id != exclude_id)
        return self.session.query(query.exists()).scalar()
