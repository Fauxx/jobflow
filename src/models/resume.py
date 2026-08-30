from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class MasterResume(Base):
    __tablename__ = "master_resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False) # Store markdown/json
    format = Column(String, default="markdown")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ResumeVersion(Base):
    __tablename__ = "resume_versions"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey('applications.id', ondelete="CASCADE"), nullable=False)
    master_resume_id = Column(Integer, ForeignKey('master_resumes.id', ondelete="SET NULL"), nullable=True)
    adjusted_content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
