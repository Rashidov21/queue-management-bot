import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Simple configuration class without pydantic_settings"""
    
    # Bot Configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")
    WEBHOOK_PATH: str = "/webhook"
    
    # Database Configuration (SQLite for Windows compatibility)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./queue_bot.db")
    
    # Web Configuration
    WEB_HOST: str = os.getenv("WEB_HOST", "0.0.0.0")
    WEB_PORT: int = int(os.getenv("WEB_PORT", "8001"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    # Admin Configuration
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Notification Configuration
    REMINDER_HOURS_BEFORE: int = int(os.getenv("REMINDER_HOURS_BEFORE", "1"))


settings = Settings()
