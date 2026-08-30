import json
from sqlalchemy.orm import Session
from src.models.job import Job
from src.models.profile import UserProfile

class ContextBuilder:
    @staticmethod
    def build_personalization_context(db: Session, job: Job, user_id: int) -> dict:
        # Fetch profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            return {"error": "No profile found"}
            
        # Mock logic for context building MVP
        # In a real implementation, we would extract required skills from the job
        # and match them against profile.skills, then traverse skill_evidence
        
        projects = [{"title": p.name, "description": p.description} for p in profile.projects]
        experiences = [{"company": e.company, "title": e.title, "description": e.description} for e in profile.experiences]
        
        return {
            "job_title": job.title,
            "company": job.company,
            "job_description": job.description,
            "candidate_context": {
                "projects": projects,
                "experiences": experiences
            }
        }
