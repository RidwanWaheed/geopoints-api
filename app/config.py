import os
from pathlib import Path
from typing import Any, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GeoPoints API"
    PROJECT_DESCRIPTION: str = "API for managing geographic points of interest"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # PostgreSQL settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "geopointsdb")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    DATABASE_URI: Optional[str] = None

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "insecure_dev_key_change_this")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings
    BACKEND_CORS_ORIGINS: str = ""

    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):  # If DATABASE_URI is already a string, return it
            return v
        return (
            f"postgresql://{info.data.get('POSTGRES_USER', '')}:{info.data.get('POSTGRES_PASSWORD', '')}"
            f"@{info.data.get('POSTGRES_SERVER', '')}:{info.data.get('POSTGRES_PORT', 5432)}/"
            f"{info.data.get('POSTGRES_DB', '')}"
        )

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow",
    }

    @property
    def backend_cors_origins(self):
        return self.BACKEND_CORS_ORIGINS.split(",") if self.BACKEND_CORS_ORIGINS else []


settings = Settings()
