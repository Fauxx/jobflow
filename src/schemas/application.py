from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from src.schemas.job import CanonicalJob
from src.schemas.resume import ResumeVersion

class ApplicationBase(BaseModel):
    status: str = "NEW"

class ApplicationCreate(ApplicationBase):
    job_id: int

class Application(ApplicationBase):
    id: int
    user_id: int
    job_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
