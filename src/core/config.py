from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Jobflow"
    DATABASE_URL: str = "postgresql://jobflow:password@localhost:5432/jobflow"
    
    # We allow extra env vars from the existing .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
