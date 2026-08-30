from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CanonicalJob(BaseModel):
    external_job_id: str
    source: str
    source_url: str
    title: str
    company: str
    location: Optional[str] = None
    description: str
    date_posted: Optional[datetime] = None
    employment_type: Optional[str] = None
    salary_display: Optional[str] = None
    workplace_type: Optional[str] = None
    experience_level: Optional[str] = None
