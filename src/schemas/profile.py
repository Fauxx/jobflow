from pydantic import BaseModel
from typing import List, Optional

class ProfileSkillBase(BaseModel):
    name: str
    proficiency: Optional[str] = None

class ProfileSkill(ProfileSkillBase):
    id: int
    profile_id: int
    class Config:
        from_attributes = True

class ProfileProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    role: Optional[str] = None
    url: Optional[str] = None

class ProfileProject(ProfileProjectBase):
    id: int
    profile_id: int
    class Config:
        from_attributes = True

class ProfileExperienceBase(BaseModel):
    company: str
    title: str
    description: Optional[str] = None
    achievements: Optional[str] = None

class ProfileExperience(ProfileExperienceBase):
    id: int
    profile_id: int
    class Config:
        from_attributes = True

class UserProfileBase(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    status: str
    career_goals: Optional[str] = None
    target_roles: Optional[str] = None
    target_industries: Optional[str] = None
    location_prefs: Optional[str] = None
    personalization_prefs: Optional[str] = None

class UserProfile(UserProfileBase):
    id: int
    user_id: int
    skills: List[ProfileSkill] = []
    projects: List[ProfileProject] = []
    experiences: List[ProfileExperience] = []
    
    class Config:
        from_attributes = True
