from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .base import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    external_job_id = Column(String, index=True, nullable=True)
    source = Column(String, index=True, nullable=False)
    source_url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    date_posted = Column(DateTime(timezone=True), nullable=True)
    employment_type = Column(String, nullable=True)
    salary_display = Column(String, nullable=True)
    workplace_type = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    
    raw_scraped_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
