from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base

class ProfileStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    VERIFIED = "VERIFIED"

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, unique=True)
    
    # Identity
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    headline = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    master_summary_context = Column(Text, nullable=True)

    status = Column(Enum(ProfileStatus), default=ProfileStatus.DRAFT, nullable=False)
    career_goals = Column(Text, nullable=True)
    target_roles = Column(Text, nullable=True)
    target_industries = Column(Text, nullable=True)
    location_prefs = Column(Text, nullable=True)
    personalization_prefs = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    experiences = relationship("ProfileExperience", back_populates="profile", cascade="all, delete-orphan", order_by="ProfileExperience.order")
    projects = relationship("ProfileProject", back_populates="profile", cascade="all, delete-orphan", order_by="ProfileProject.order")
    skills = relationship("ProfileSkill", back_populates="profile", cascade="all, delete-orphan")
    education = relationship("ProfileEducation", back_populates="profile", cascade="all, delete-orphan")
    achievements = relationship("ProfileAchievement", back_populates="profile", cascade="all, delete-orphan")

class ProfileExperience(Base):
    __tablename__ = "experiences"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    company = Column(String, nullable=False)
    role = Column(String, nullable=True)
    location = Column(String, nullable=True)
    date_range = Column(String, nullable=True)
    detailed_context = Column(Text, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    bullets = relationship("ProfileBullet", back_populates="experience", cascade="all, delete-orphan", order_by="ProfileBullet.order")
    profile = relationship("UserProfile", back_populates="experiences")

class ProfileProject(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    role = Column(String, nullable=True)
    date_range = Column(String, nullable=True)
    tech_stack = Column(String, nullable=True)
    url = Column(String, nullable=True)
    detailed_context = Column(Text, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    bullets = relationship("ProfileBullet", back_populates="project", cascade="all, delete-orphan", order_by="ProfileBullet.order")
    profile = relationship("UserProfile", back_populates="projects")

class ProfileBullet(Base):
    __tablename__ = "bullets"
    id = Column(String, primary_key=True, index=True)
    experience_id = Column(Integer, ForeignKey("experiences.id", ondelete="CASCADE"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    text = Column(Text, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    experience = relationship("ProfileExperience", back_populates="bullets")
    project = relationship("ProfileProject", back_populates="bullets")

class ProfileSkill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    category = Column(String, nullable=True)
    items = Column(Text, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    profile = relationship("UserProfile", back_populates="skills")

class ProfileEducation(Base):
    __tablename__ = "profile_education"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    date_str = Column(String, nullable=True)
    location = Column(String, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    profile = relationship("UserProfile", back_populates="education")

class ProfileAchievement(Base):
    __tablename__ = "profile_achievements"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    date_str = Column(String, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    profile = relationship("UserProfile", back_populates="achievements")
