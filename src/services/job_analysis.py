import json
from google import genai
from google.genai import types

def extract_jd_requirements(jd_text: str) -> dict:
    client = genai.Client()
    system_instruction = (
        "You are a senior technical recruiter analyzing a job description. "
        "Extract the hard skills, responsibilities, domain, and seniority from the text."
    )
    
    schema = {
        "type": "OBJECT",
        "properties": {
            "hard_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
            "responsibilities": {"type": "ARRAY", "items": {"type": "STRING"}},
            "domain": {"type": "STRING"},
            "seniority": {"type": "STRING"}
        },
        "required": ["hard_skills", "responsibilities", "domain", "seniority"]
    }
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=jd_text,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=schema
        )
    )
    
    return json.loads(response.text)
