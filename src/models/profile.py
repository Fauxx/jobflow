from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table, Boolean
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
    Column('evidence_id', Integer, nullable=False)
)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    # Identity
    name = Column(String, nullable=True)
    title = Column(String, nullable=True)
    headline = Column(String, nullable=True)  # Short tagline e.g. "Cloud-Native DevOps Engineer"
    phone = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    location = Column(String, nullable=True)
    # Status & AI preferences
    status = Column(Enum(ProfileStatus), default=ProfileStatus.DRAFT, nullable=False)
    career_goals = Column(Text, nullable=True)
    target_roles = Column(Text, nullable=True)
    target_industries = Column(Text, nullable=True)
    location_prefs = Column(Text, nullable=True)
    personalization_prefs = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # Relationships
    skills = relationship("ProfileSkill", back_populates="profile", cascade="all, delete-orphan", order_by="ProfileSkill.id")
    projects = relationship("ProfileProject", back_populates="profile", cascade="all, delete-orphan", order_by="ProfileProject.order")
    experiences = relationship("ProfileExperience", back_populates="profile", cascade="all, delete-orphan", order_by="ProfileExperience.order")
    education = relationship("ProfileEducation", back_populates="profile", cascade="all, delete-orphan")
    achievements = relationship("ProfileAchievement", back_populates="profile", cascade="all, delete-orphan")

class ProfileSkill(Base):
    __tablename__ = "profile_skills"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    category = Column(String, nullable=True)  # e.g. "Cloud & IaC"
    name = Column(String, nullable=False)
    proficiency = Column(String, nullable=True)
    profile = relationship("UserProfile", back_populates="skills")

class ProfileProject(Base):
    __tablename__ = "profile_projects"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True) # Legacy summary
    problem_statement = Column(Text, nullable=True) # Deep Dive
    actions_taken = Column(Text, nullable=True) # Deep Dive
    measurable_results = Column(Text, nullable=True) # Deep Dive
    role = Column(String, nullable=True)
    url = Column(String, nullable=True)
    tech_stack = Column(Text, nullable=True)  # comma-separated
    date_range = Column(String, nullable=True)  # e.g. "Aug 2025 - June 2026"
    is_highlight = Column(Boolean, default=False, nullable=False)  # Main section toggle
    order = Column(Integer, default=0, nullable=False)
    bullets = relationship("ProfileBullet", back_populates="project", cascade="all, delete-orphan", order_by="ProfileBullet.order", foreign_keys="ProfileBullet.project_id")
    profile = relationship("UserProfile", back_populates="projects")

class ProfileExperience(Base):
    __tablename__ = "profile_experience"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    location = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)  # 'Present' or date string
    description = Column(Text, nullable=True) # Legacy summary
    problem_statement = Column(Text, nullable=True) # Deep Dive
    actions_taken = Column(Text, nullable=True) # Deep Dive
    measurable_results = Column(Text, nullable=True) # Deep Dive
    tech_stack = Column(Text, nullable=True) # Deep Dive
    achievements = Column(Text, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    bullets = relationship("ProfileBullet", back_populates="experience", cascade="all, delete-orphan", order_by="ProfileBullet.order", foreign_keys="ProfileBullet.experience_id")
    profile = relationship("UserProfile", back_populates="experiences")

class ProfileBullet(Base):
    """Individual bullet points for experiences and projects — stored separately for granular AI retrieval."""
    __tablename__ = "profile_bullets"
    id = Column(Integer, primary_key=True, index=True)
    experience_id = Column(Integer, ForeignKey('profile_experience.id', ondelete="CASCADE"), nullable=True)
    project_id = Column(Integer, ForeignKey('profile_projects.id', ondelete="CASCADE"), nullable=True)
    raw_text = Column(Text, nullable=False)
    action_verb = Column(String, nullable=True)
    technologies_used = Column(Text, nullable=True)  # comma-separated
    order = Column(Integer, default=0, nullable=False)
    experience = relationship("ProfileExperience", back_populates="bullets", foreign_keys=[experience_id])
    project = relationship("ProfileProject", back_populates="bullets", foreign_keys=[project_id])

class ProfileEducation(Base):
    __tablename__ = "profile_education"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    date_str = Column(String, nullable=True)
    location = Column(String, nullable=True)
    profile = relationship("UserProfile", back_populates="education")

class ProfileAchievement(Base):
    __tablename__ = "profile_achievements"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id', ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    profile = relationship("UserProfile", back_populates="achievements")
