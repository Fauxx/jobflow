from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MasterResumeBase(BaseModel):
    content: str
    format: str = "markdown"

class MasterResume(MasterResumeBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResumeVersionBase(BaseModel):
    adjusted_content: str

class ResumeVersion(ResumeVersionBase):
    id: int
    application_id: int
    master_resume_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
