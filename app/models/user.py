from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.timezone("UTC", func.current_timestamp()),
    )
    last_login = Column(DateTime(timezone=True),
        server_default=func.timezone("UTC", func.current_timestamp()), nullable=True)