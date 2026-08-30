import os

# Create base.py
with open('src/models/base.py', 'w') as f:
    f.write("""from sqlalchemy.orm import declarative_base

Base = declarative_base()
""")

# Create user.py
with open('src/models/user.py', 'w') as f:
    f.write("""from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""")

# Create profile.py
with open('src/models/profile.py', 'w') as f:
    f.write("""from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base

class ProfileStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    VERIFIED = "VERIFIED"

class EvidenceType(str, enum.Enum):
    PROJECT = "PROJECT"
    EXPERIENCE = "EXPERIENCE"

skill_evidence = Table(
    'skill_evidence',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('skill_id', Integer, ForeignKey('profile_skills.id', ondelete="CASCADE")),
    Column('evidence_type', Enum(EvidenceType), nullable=False),
    Column('evidence_id', Integer, nullable=False) # ID of project or experience
)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    status = Column(Enum(ProfileStatus), default=ProfileStatus.DRAFT, nullable=False)
    career_goals = Column(Text, nullable=True)
    target_roles = Column(Text, nullable=True) # e.g., JSON or comma separated
    target_industries = Column(Text, nullable=True)
    location_prefs = Column(Text, nullable=True)
    personalization_prefs = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    skills = relationship("ProfileSkill", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("ProfileProject", back_populates="profile", cascade="all, delete-orphan")
    experiences = relationship("ProfileExperience", back_populates="profile", cascade="all, delete-orphan")

class ProfileSkill(Base):
    __tablename__ = "profile_skills"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    proficiency = Column(String, nullable=True)
    
    profile = relationship("UserProfile", back_populates="skills")
    
class ProfileProject(Base):
    __tablename__ = "profile_projects"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    role = Column(String, nullable=True)
    url = Column(String, nullable=True)
    
    profile = relationship("UserProfile", back_populates="projects")

class ProfileExperience(Base):
    __tablename__ = "profile_experience"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    achievements = Column(Text, nullable=True)
    
    profile = relationship("UserProfile", back_populates="experiences")

class ProfileEducation(Base):
    __tablename__ = "profile_education"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    date_str = Column(String, nullable=True)

class ProfileAchievement(Base):
    __tablename__ = "profile_achievements"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
""")

# Create resume.py
with open('src/models/resume.py', 'w') as f:
    f.write("""from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
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
""")

# Create job.py
with open('src/models/job.py', 'w') as f:
    f.write("""from sqlalchemy import Column, Integer, String, Text, DateTime
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
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
""")

# Create application.py
with open('src/models/application.py', 'w') as f:
    f.write("""from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete="CASCADE"), nullable=False)
    status = Column(String, default="NEW", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    job = relationship("Job")
    resume_versions = relationship("ResumeVersion", backref="application", cascade="all, delete-orphan")
""")

# Create core files
with open('src/core/config.py', 'w') as f:
    f.write("""from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Jobflow"
    DATABASE_URL: str = "postgresql://jobflow:password@localhost:5432/jobflow"
    
    class Config:
        env_file = ".env"

settings = Settings()
""")

with open('src/core/database.py', 'w') as f:
    f.write("""from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

with open('src/core/exceptions.py', 'w') as f:
    f.write("""class JobflowException(Exception): pass
class PlatformBlockedError(JobflowException): pass
class ParsingError(JobflowException): pass
class DatabaseError(JobflowException): pass
""")

with open('src/core/logging.py', 'w') as f:
    f.write("""import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jobflow")
""")

