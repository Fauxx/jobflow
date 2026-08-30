import os

with open('src/services/context_builder.py', 'w') as f:
    f.write("""import json
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
""")

with open('src/services/job_analysis.py', 'w') as f:
    f.write("""import json
import requests
from src.core.config import settings

def call_gemini(prompt: str) -> str:
    if not settings.OPENAI_API_KEY: # Using as generic AI key for now, could rename to GEMINI_API_KEY
        return "{}"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={settings.OPENAI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=35)
    if response.status_code == 200:
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return "{}"

class JobAnalysisService:
    @staticmethod
    def extract_required_skills(job_description: str) -> list:
        # Dummy implementation
        return []
""")

with open('src/services/resume_personalization.py', 'w') as f:
    f.write("""import json
from src.services.job_analysis import call_gemini

class ResumePersonalizationService:
    @staticmethod
    def generate_tailored_application(context: dict, candidate_name: str) -> dict:
        if not context.get("job_description"):
            return {}
            
        prompt = f'''
        You are an expert career agent helping {candidate_name} apply for a job.
        Job Title: {context.get("job_title")}
        Company: {context.get("company")}
        Description: {context.get("job_description")}
        
        Candidate Context:
        {json.dumps(context.get("candidate_context", {}), indent=2)}
        
        Format output as JSON:
        1. "subject"
        2. "body" (cover letter)
        3. "key_matches"
        '''
        
        try:
            resp = call_gemini(prompt)
            # clean json blocks
            if resp.startswith("```json"):
                resp = resp.split("```json", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(resp)
        except Exception:
            return {}
""")
