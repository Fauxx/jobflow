import json
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
