from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Jobflow"
    DATABASE_URL: str = "postgresql://jobflow:password@localhost:5432/jobflow"
    GEMINI_API_KEY: Optional[str] = None
    ADMIN_PASSWORD: str = "admin"
    SECRET_KEY: str = "changeme-super-secret-key-32chars"
    
    # We allow extra env vars from the existing .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
