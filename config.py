from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Bot Configuration
    BOT_TOKEN: str
    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_PATH: str = "/webhook"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./queue_bot.db"
    
    # Web Configuration
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 8000
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Admin Configuration
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    # Notification Configuration
    REMINDER_HOURS_BEFORE: int = 1
    
    class Config:
        env_file = ".env"


settings = Settings()
