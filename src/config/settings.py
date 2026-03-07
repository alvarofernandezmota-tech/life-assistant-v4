"""
settings.py - Configuración centralizada desde .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

class Settings:
    """Configuración global de la aplicación"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/life.db")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    # RPG System
    DEFAULT_USER_ID: int = int(os.getenv("DEFAULT_USER_ID", "1"))
    STARTING_XP: int = int(os.getenv("STARTING_XP", "0"))
    STARTING_WYRD: int = int(os.getenv("STARTING_WYRD", "100"))
    STARTING_LEVEL: int = int(os.getenv("STARTING_LEVEL", "1"))
    
    # Reminders
    REMINDERS_ENABLED: bool = os.getenv("REMINDERS_ENABLED", "True").lower() == "true"
    REMINDER_CHECK_INTERVAL: int = int(os.getenv("REMINDER_CHECK_INTERVAL", "300"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")

settings = Settings()