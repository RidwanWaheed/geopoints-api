# app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set

from jose import jwt
from passlib.context import CryptContext

from app.config import settings
from app.core.utils import utc_now

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",  # Use the most common bcrypt identifier
    bcrypt__rounds=12    # Set a reasonable number of rounds for security/performance
)

# Token blacklist - for invalidated tokens
token_blacklist: Set[str] = set()


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    if expires_delta:
        expire = utc_now() + expires_delta
    else:
        expire = utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def blacklist_token(token: str) -> None:
    """Add a token to the blacklist"""
    token_blacklist.add(token)


def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted"""
    return token in token_blacklist


# Periodic cleanup function for expired tokens
def cleanup_blacklist() -> None:
    """Remove expired tokens from blacklist"""
    current_time = utc_now()
    to_remove = set()

    for token in token_blacklist:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            exp = datetime.fromtimestamp(payload.get("exp"), tz=current_time.tzinfo)
            if exp < current_time:
                to_remove.add(token)
        except:
            # If we can't decode, it's invalid anyway
            to_remove.add(token)

    token_blacklist.difference_update(to_remove)
