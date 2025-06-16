"""
FastAPI configuration settings
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DF naar CSV API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for processing Excel/CSV files for VDP generation"
    
    # File Upload Settings
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {".xlsx", ".xls", ".csv"}
    
    # Processing Settings
    DEFAULT_MES: int = 4
    DEFAULT_VDP_AANTAL: int = 1
    DEFAULT_EXTRA_ETIKETTEN: int = 10
    DEFAULT_WIKKEL: int = 1
    DEFAULT_KERN: int = 76
    DEFAULT_FORMAAT_HOOGTE: int = 80
    DEFAULT_FORMAAT_BREEDTE: int = 80
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",  # React default
        "http://localhost:8080",  # Vue default
        "http://localhost:4200",  # Angular default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:4200",
    ]
    
    # Development Settings
    DEBUG: bool = True
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(exist_ok=True)
