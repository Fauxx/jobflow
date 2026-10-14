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
    id: str = Field(default="", description="The unique ID of the bullet selected from the master profile")
    original_text: str = Field(default="", description="The exact original bullet from the candidate's profile")
    tailored_text: str = Field(default="", description="Must be IDENTICAL to the original_text. Do not rewrite or rephrase.")
    highly_recommended: bool = Field(description="True if this is an absolute perfect match for the job description")
    reason: str = Field(description="Brief reason why this bullet was chosen")

class TailoredExperience(BaseModel):
    company: str
    title: str
    location: str = ""
    date_range: str = ""
    bullets: List[TailoredBullet] = Field(description="Select exactly 3-5 of the most relevant bullets verbatim from the master profile. Do not rewrite them.")

class TailoredProject(BaseModel):
    name: str
    role: str = ""
    date_range: str = ""
    tech_stack: str = ""
    bullets: List[TailoredBullet] = Field(description="Select exactly 3-5 of the most relevant bullets verbatim from the master profile. Do not rewrite them.")

class TailoredResume(BaseModel):
    """The full AI-suggested resume. Every field is a suggestion the user can edit."""
    summary: str = Field(description="AI-written professional summary tailored to this job")
    skills: List[str] = Field(description="A flat list of the most relevant skills for this job")
    experiences: List[TailoredExperience] = Field(description="ALL experiences from the candidate's profile, each with 3-5 verbatim bullets")
    projects: List[TailoredProject] = Field(description="ALL projects from the candidate's profile, each with 3-5 verbatim bullets")
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

        # 2. Call AI to generate tailored resume sections directly from the Job Description
        prompt = f"""You are a Fact-Anchored Resume Curator Engine.

STRICT RULES:
1. FACTUAL ANCHORING: You ONLY use information from the Candidate Knowledge Base below. NEVER invent skills, tools, metrics, companies, dates, or achievements.
2. VERBATIM SELECTION: DO NOT REWRITE OR REPHRASE BULLETS. Your job is to SELECT the most relevant existing bullets verbatim from the candidate's master profile.
3. EXACT MAPPING: When selecting a bullet, you MUST provide its exact ID and its exact original text.
4. INCLUDE ALL: You MUST include EVERY project and EVERY experience from the candidate's profile. Do NOT skip any.
5. BULLETS PER SECTION: Select exactly 3 to 5 bullets per experience and per project. Pick the ones most relevant to the JD.
6. HIGHLY RECOMMENDED: Set `highly_recommended` to `true` for the 2-3 bullets per section that are the absolute best match for this specific job.
7. MISSING SKILLS GAP: If the JD requires a skill the candidate does NOT have, list it under "missing_skills" — do NOT pretend the candidate has it.

---

## JOB BEING APPLIED TO
Title: {job.title}
Company: {job.company}
Location: {job.location or 'Not specified'}

### Full Job Description
Read this description carefully, extract the core requirements mentally, and use them to select the best matching bullets:
{job.description or 'No description available'}

---

## CANDIDATE KNOWLEDGE BASE
{candidate_context}

---

## YOUR TASK
Generate a curated resume for THIS specific job. Return JSON with this exact structure:

{{
  "summary": "A 3-4 sentence professional summary tailored to this job. Use keywords from the JD naturally. Reference the candidate's most relevant experience.",
  
  "skills": ["Skill1", "Skill2", "Skill3"],
  
  "experiences": [
    {{
      "company": "Company Name",
      "title": "Role Title",
      "location": "Location",
      "date_range": "Dates",
      "bullets": [
        {{
          "id": "The exact ID of the bullet (e.g. uuid)",
          "original_text": "The exact text of the bullet",
          "tailored_text": "The exact text of the bullet (IDENTICAL to original_text)",
          "highly_recommended": true,
          "reason": "Why this bullet was chosen"
        }}
      ]
    }}
  ],
  
  "projects": [
    {{
      "name": "Project Name",
      "role": "Role",
      "date_range": "Dates",
      "tech_stack": "Technologies",
      "bullets": [
        {{
          "id": "The exact ID of the bullet",
          "original_text": "The exact text of the bullet",
          "tailored_text": "The exact text of the bullet (IDENTICAL to original_text)",
          "highly_recommended": true,
          "reason": "Why this bullet was chosen"
        }}
      ]
    }}
  ],
  
  "certifications": ["Cert 1", "Cert 2"],
  
  "matched_skills": ["Skills the candidate HAS that the JD requires"],
  "missing_skills": ["Skills the JD requires that the candidate DOES NOT have"]
}}

IMPORTANT REMINDERS:
- Include ALL experiences and ALL projects — do not drop any.
- Each section must have exactly 3 to 5 bullets, no more, no less.
- Every tailored_text must be IDENTICAL to the original_text from the profile.
- Output a single, flat list of the most relevant skills.
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

    @staticmethod
    def adjust_summary(db: Session, job: Job, user_id: int, current_summary: str, instruction: str) -> str:
        """
        Rewrites only the professional summary based on user instruction.
        """
        candidate_context = build_context(db, job, user_id)
        
        prompt = f"""You are an expert Resume Writer.
The user wants you to rewrite their Professional Summary for the job: {job.title} at {job.company}.

USER INSTRUCTION:
"{instruction}"

CURRENT SUMMARY:
"{current_summary}"

## JOB DESCRIPTION (for context):
{job.description or 'No description available'}

## MASTER CANDIDATE PROFILE:
{candidate_context}

INSTRUCTIONS:
Write ONLY the new professional summary. Do not output JSON, do not include markdown blocks like ```, just return the raw text of the updated summary.
Make it punchy, professional, and directly aligned with the user's instructions.
"""
        result = call_gemini(prompt).strip()
        
        # Guard against the model disobeying and returning JSON
        if result.startswith("{") or result.startswith("["):
            try:
                import json
                parsed = json.loads(result)
                if isinstance(parsed, list) and len(parsed) > 0:
                    parsed = parsed[0]
                if isinstance(parsed, dict):
                    # extract 'summary' or 'professional_summary'
                    result = parsed.get("professional_summary", parsed.get("summary", result))
            except Exception:
                pass
                
        # Guard against markdown code blocks
        if result.startswith("```"):
            result = result.replace("```json", "").replace("```text", "").replace("```", "").strip()
            
        return result

    @staticmethod
    def adjust_skills(db: Session, job: Job, user_id: int, current_skills: list, instruction: str) -> list:
        """
        Rewrites only the skills section based on user instruction.
        """
        candidate_context = build_context(db, job, user_id)
        
        prompt = f"""You are an expert Resume Writer.
The user wants you to adjust the Skills section of their tailored resume for the job: {job.title} at {job.company}.

USER INSTRUCTION:
"{instruction}"

CURRENT SKILLS:
{json.dumps(current_skills)}

## JOB DESCRIPTION (for context):
{job.description or 'No description available'}

## MASTER CANDIDATE PROFILE:
{candidate_context}

INSTRUCTIONS:
Return a JSON array of strings representing the updated skills list.
Example: ["Python", "FastAPI", "React"]
Do not invent skills the user does not have. Only use skills from the Master Candidate Profile.
Output ONLY a valid JSON array. Do not wrap it in markdown.
"""
        result = call_gemini(prompt).strip()
        if result.startswith("```"):
            result = result.replace("```json", "").replace("```", "").strip()
            
        try:
            parsed = json.loads(result)
            if isinstance(parsed, list):
                return [str(s) for s in parsed]
            elif isinstance(parsed, dict) and "skills" in parsed:
                return [str(s) for s in parsed["skills"]]
        except Exception:
            pass
            
        return current_skills

    @staticmethod
    def adjust_resume(db: Session, job: Job, user_id: int, current_draft: dict, instruction: str) -> dict:
        """
        Takes the current resume draft and a user instruction, and returns an updated draft.
        """
        # Fetch the master profile so the AI can pull in new projects/experiences if requested
        candidate_context = build_context(db, job, user_id)

        prompt = f"""You are a Fact-Anchored Resume Curator Engine.
The user wants to adjust their currently tailored resume for the job: {job.title} at {job.company}.

STRICT RULES:
1. NEVER invent skills, metrics, companies, dates, or achievements.
2. DO NOT REWRITE OR REPHRASE BULLETS. If you add new bullets, SELECT them verbatim from the master profile.
3. Every tailored_text must be IDENTICAL to the original_text.

USER INSTRUCTION:
"{instruction}"

CURRENT RESUME DRAFT (JSON):
{json.dumps(current_draft, indent=2)}

## JOB DESCRIPTION (for context):
{job.description or 'No description available'}

## MASTER CANDIDATE PROFILE (Knowledge Base):
Use this if the user asks you to add an experience, project, or skill that is not in the current draft.
{candidate_context}

Please modify the resume draft according to the user's instruction.
Return the updated resume strictly as a JSON object matching the EXACT SAME SCHEMA as the current draft.
Do not include any conversational text, markdown formatting blocks, or explanations outside the JSON.
"""
        try:
            resp = call_gemini(prompt)
            # Clean markdown code fences if present
            if "```json" in resp:
                resp = resp.split("```json", 1)[1].rsplit("```", 1)[0].strip()
            elif "```" in resp:
                resp = resp.split("```", 1)[1].rsplit("```", 1)[0].strip()

            result = json.loads(resp)
            # Ensure it matches schema
            validated = TailoredResume(**result)
            return validated.model_dump()
        except Exception as e:
            print(f"[ResumeTailor] AI adjustment failed: {e}")
            return current_draft
