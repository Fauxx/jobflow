from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete="CASCADE"), nullable=False)
    status = Column(String, default="NEW", nullable=False)
    email_subject = Column(String, nullable=True)
    email_body = Column(String, nullable=True)
    ai_draft_json = Column(String, nullable=True)
    
    # CRM Pipeline fields
    sub_status = Column(String, default="APPLIED", nullable=False)
    recruiter_name = Column(String, nullable=True)
    interview_date = Column(DateTime(timezone=True), nullable=True)
    salary_expected = Column(String, nullable=True)
    salary_offered = Column(String, nullable=True)
    pipeline_notes = Column(String, nullable=True)
    
    # Pipeline Timestamps
    date_applied = Column(DateTime(timezone=True), nullable=True)
    date_screening = Column(DateTime(timezone=True), nullable=True)
    date_interview = Column(DateTime(timezone=True), nullable=True)
    date_offer = Column(DateTime(timezone=True), nullable=True)
    date_rejected = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    job = relationship("Job")
    resume_versions = relationship("ResumeVersion", backref="application", cascade="all, delete-orphan")
