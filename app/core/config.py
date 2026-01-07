"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./hotel_pms.db"
    
    # JWT Configuration
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin User
    ADMIN_EMAIL: str = "admin@hotel.com"
    ADMIN_PASSWORD: str = "admin123"
    
    # Client Configuration
    CLIENT_NAME: str = "PMS-CYNERZA"
    CLIENT_TIER: str = "professional"  # starter, standard, professional, enterprise
    MAX_ROOMS: int = 200
    MAX_ROOM_TYPES: int = 20
    
    # Module Feature Flags (optional overrides)
    ENABLE_HOUSEKEEPING: bool = True
    ENABLE_NIGHT_AUDIT: bool = True
    ENABLE_ALLOTMENTS: bool = True
    ENABLE_BLOCKS: bool = True
    
    # Inventory
    INVENTORY_DAYS_AHEAD: int = 90
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
