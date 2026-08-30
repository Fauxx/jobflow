"""
Resume Tailor Service — The brain of the AI Resume Builder.

Takes a user's full profile (Master Knowledge Base) + a job description,
and generates SUGGESTED resume sections that the user can edit and approve.

AI is the assistant. Human is the decision maker.
"""
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from src.services.job_analysis import call_gemini, extract_jd_requirements
from src.services.context_builder import build_context
from sqlalchemy.orm import Session
from src.models.job import Job
from src.core.config import settings


class TailoredBullet(BaseModel):
    original_text: str = Field(description="The original bullet from the candidate's profile")
    tailored_text: str = Field(description="AI-rephrased version optimized for this job")


class TailoredExperience(BaseModel):
    company: str
    title: str
    location: str = ""
    date_range: str = ""
    bullets: List[TailoredBullet] = []


class TailoredProject(BaseModel):
    name: str
    role: str = ""
    date_range: str = ""
    tech_stack: str = ""
    bullets: List[TailoredBullet] = []


class SkillCategory(BaseModel):
    category: str
    skills: List[str]


class TailoredResume(BaseModel):
    """The full AI-suggested resume. Every field is a suggestion the user can edit."""
    summary: str = Field(description="AI-written professional summary tailored to this job")
    skills: List[SkillCategory] = Field(description="Skills grouped by category, prioritized by JD relevance")
    experiences: List[TailoredExperience] = Field(description="Selected experiences with tailored bullets")
    projects: List[TailoredProject] = Field(description="Selected projects relevant to this job")
    certifications: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list, description="Skills candidate has that JD wants")
    missing_skills: List[str] = Field(default_factory=list, description="Skills JD wants that candidate lacks")


class ResumeTailorService:
    """Generates AI-suggested resume content. All outputs are suggestions for human review."""

    @staticmethod
    def generate_tailored_resume(db: Session, job: Job, user_id: int) -> dict:
        """
        Main entry point. Returns a TailoredResume dict that the frontend
        renders as editable fields for the user to review and modify.
        """
        # 1. Build the full candidate context as markdown
        candidate_context = build_context(db, job, user_id)

        # 2. Extract structured requirements from JD
        jd_requirements = extract_jd_requirements(job.description or "")

        # 3. Call AI to generate tailored resume sections
        prompt = f"""You are a Fact-Anchored Resume Tailoring Engine.

STRICT RULES:
1. You ONLY use information from the Candidate Knowledge Base below. 
2. NEVER invent skills, tools, metrics, companies, dates, or achievements.
3. You may REPHRASE bullets (stronger action verbs, incorporate JD keywords) but the core factual claim must remain 100% true to the source.
4. If the JD requires a skill the candidate does NOT have, list it under "missing_skills" — do NOT pretend the candidate has it.
5. Follow ATS resume formatting: action verb + task + measurable result.

---

## JOB BEING APPLIED TO
Title: {job.title}
Company: {job.company}
Location: {job.location or 'Not specified'}

### Job Requirements (Extracted)
{json.dumps(jd_requirements, indent=2)}

### Full Job Description
{job.description or 'No description available'}

---

## CANDIDATE KNOWLEDGE BASE
{candidate_context}

---

## YOUR TASK
Generate a tailored resume for THIS specific job. Return JSON with this exact structure:

{{
  "summary": "A 3-4 sentence professional summary tailored to this job. Use keywords from the JD naturally. Reference the candidate's most relevant experience.",
  
  "skills": [
    {{"category": "Category Name", "skills": ["Skill1", "Skill2"]}}
  ],
  
  "experiences": [
    {{
      "company": "Company Name",
      "title": "Job Title", 
      "location": "City, Country",
      "date_range": "Month YYYY – Month YYYY",
      "bullets": [
        {{
          "original_text": "The exact original bullet from the candidate profile",
          "tailored_text": "The rephrased version optimized for this JD"
        }}
      ]
    }}
  ],
  
  "projects": [
    {{
      "name": "Project Name",
      "role": "Role in project",
      "date_range": "Date range",
      "tech_stack": "Key technologies",
      "bullets": [
        {{
          "original_text": "Original bullet",
          "tailored_text": "Tailored bullet"
        }}
      ]
    }}
  ],
  
  "certifications": ["Cert 1", "Cert 2"],
  
  "matched_skills": ["Skills the candidate HAS that the JD requires"],
  "missing_skills": ["Skills the JD requires that the candidate DOES NOT have"]
}}

IMPORTANT:
- Generate comprehensive suggestions. The user will manually trim them in the UI.
- Select all highly relevant experiences and projects.
- For each experience, pick 4-6 strong, tailored bullets.
- Skills should be grouped logically and ordered by JD relevance.
- Every tailored_text must have a corresponding real original_text from the profile.
"""

        try:
            resp = call_gemini(prompt)
            # Clean markdown code fences if present
            if "```json" in resp:
                resp = resp.split("```json", 1)[1].rsplit("```", 1)[0].strip()
            elif "```" in resp:
                resp = resp.split("```", 1)[1].rsplit("```", 1)[0].strip()

            result = json.loads(resp)

            # Validate with Pydantic (but return dict for JSON serialization)
            validated = TailoredResume(**result)
            return validated.model_dump()

        except Exception as e:
            print(f"[ResumeTailor] AI generation failed: {e}")
            # Return a skeleton so the UI still renders
            return TailoredResume(
                summary="AI generation failed. Please write your summary manually or click Regenerate.",
                skills=[],
                experiences=[],
                projects=[],
                matched_skills=[],
                missing_skills=[]
            ).model_dump()
