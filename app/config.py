from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

print(BASE_DIR)

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GeoPoints API"
    PROJECT_DESCRIPTION: str = "API for managing geographic points of interest"
    DEBUG: bool = False
    
    
    # PostgreSQL settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    DATABASE_URI: Optional[PostgresDsn] = None
    
    # CORS settings
    BACKEND_CORS_ORIGINS: str = ""
    
    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER", ""),
            password=info.data.get("POSTGRES_PASSWORD", ""),
            host=info.data.get("POSTGRES_SERVER", ""),
            port=info.data.get("POSTGRES_PORT", ""),
            path=f"/{info.data.get('POSTGRES_DB', '')}",
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

    @property
    def backend_cors_origins(self):
        # Split the comma-separated string into a list
        return self.BACKEND_CORS_ORIGINS.split(",") if self.BACKEND_CORS_ORIGINS else []

# Create settings instance
settings = Settings()