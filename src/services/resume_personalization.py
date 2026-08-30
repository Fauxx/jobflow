import json
from google import genai
from google.genai import types

def generate_tailored_application(candidate_context_md: str, jd_requirements: dict, job_title: str, company_name: str) -> dict:
    client = genai.Client()
    
    system_instruction = (
        "You are a Fact-Anchored Career Writing Engine. You ONLY use information present in the Candidate Knowledge Base. "
        "Never invent tools, metrics, or dates. Ensure all statements are strictly backed by the candidate's provided context."
    )
    
    schema = {
        "type": "OBJECT",
        "properties": {
            "email_subject": {"type": "STRING"},
            "hook": {"type": "STRING"},
            "evidence_bullets": {"type": "ARRAY", "items": {"type": "STRING"}},
            "closing": {"type": "STRING"},
            "matched_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
            "missing_skills": {"type": "ARRAY", "items": {"type": "STRING"}}
        },
        "required": ["email_subject", "hook", "evidence_bullets", "closing", "matched_skills", "missing_skills"]
    }
    
    prompt = f"""
Job Title: {job_title}
Company: {company_name}

Job Requirements:
{json.dumps(jd_requirements, indent=2)}

Candidate Knowledge Base:
{candidate_context_md}

Write a tailored application email. 
It must contain a 3-section email output: Hook, Evidence (mapping JD to candidate), Close.
Provide it in the requested JSON structure.
"""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=schema
        )
    )
    
    return json.loads(response.text)
