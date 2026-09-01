import json
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from src.models.job import Job
from src.services.job_analysis import call_gemini
from urllib.parse import urlparse

class UniversalScraperService:
    @staticmethod
    def extract_text_from_url(url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "noscript", "meta", "link", "header", "footer"]):
                script.decompose()
                
            # Get text and collapse whitespace
            text = soup.get_text(separator=' ')
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit text to roughly 30,000 characters to fit well within context
            return text[:30000]
        except Exception as e:
            raise ValueError(f"Failed to fetch webpage: {str(e)}")

    @staticmethod
    def import_job(url: str, db: Session) -> Job:
        domain = urlparse(url).netloc.replace('www.', '')
        
        # 1. Fetch raw text
        raw_text = UniversalScraperService.extract_text_from_url(url)
        if not raw_text or len(raw_text) < 100:
            raise ValueError("Could not extract enough text from the URL. The page might be heavily JavaScript-rendered or protected.")
            
        # 2. Ask Gemini to extract job data
        prompt = f"""You are an expert AI Job Data Extractor.
I am providing you with the raw, scraped text from a webpage that contains a job posting.
Read the text and extract the exact job title, company name, location, and the full job description.

STRICT RULES:
1. Return ONLY raw JSON. No markdown fences, no explanations.
2. The description must be the FULL job description. Do not summarize it. Format the description cleanly using markdown (e.g. bullet points for requirements).
3. If the text does not appear to be a job posting at all, return {{"error": "Could not identify a job posting on this page."}}

RAW TEXT:
---
{raw_text}
---

EXPECTED JSON SCHEMA:
{{
    "title": "Job Title",
    "company": "Company Name",
    "location": "Location or Remote",
    "description": "Full markdown description..."
}}
"""
        ai_resp = call_gemini(prompt)
        
        # Clean JSON if model hallucinates markdown fences
        if "```json" in ai_resp:
            ai_resp = ai_resp.split("```json", 1)[1].rsplit("```", 1)[0].strip()
        elif "```" in ai_resp:
            ai_resp = ai_resp.split("```", 1)[1].rsplit("```", 1)[0].strip()
            
        try:
            data = json.loads(ai_resp)
        except Exception as e:
            raise ValueError(f"Failed to parse AI response: {ai_resp}")
            
        if "error" in data:
            raise ValueError(data["error"])
            
        if not data.get("title") or not data.get("company"):
            raise ValueError("AI failed to extract critical job details (Title or Company).")
            
        # 3. Save to Database
        new_job = Job(
            title=data.get("title", "Unknown Title"),
            company=data.get("company", "Unknown Company"),
            location=data.get("location", "Unspecified"),
            description=data.get("description", ""),
            source=domain,
            external_url=url,
            is_hydrated=True  # We fetched full JD immediately
        )
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        return new_job

    @staticmethod
    def hydrate_job(db: Session, job: Job):
        if job.is_hydrated:
            return
            
        if not job.external_url:
            return
            
        # Re-fetch full JD via Universal Scraper
        raw_text = UniversalScraperService.extract_text_from_url(job.external_url)
        if not raw_text: return
        
        prompt = f"""Extract ONLY the full job description from this raw web text. Return raw JSON: {{"description": "full markdown here"}}. Raw text:\n{raw_text}"""
        ai_resp = call_gemini(prompt)
        
        try:
            if "```json" in ai_resp: ai_resp = ai_resp.split("```json", 1)[1].rsplit("```", 1)[0].strip()
            data = json.loads(ai_resp)
            if data.get("description"):
                job.description = data["description"]
                job.is_hydrated = True
                db.commit()
        except Exception:
            pass
