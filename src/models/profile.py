from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table
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
