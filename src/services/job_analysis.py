"""
Job Analysis Service — Gemini AI integration for JD parsing and content generation.
"""
import json
import requests
from src.core.config import settings


import time

def call_gemini(prompt: str) -> str:
    """Call Gemini API and return raw text response."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        print("[Gemini] No GEMINI_API_KEY set in .env")
        return "{}"

    models = [
        "gemini-3.5-flash",
        "gemini-flash-latest"
    ]
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        retries = 3
        
        while retries > 0:
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                elif response.status_code == 429:
                    print(f"[Gemini] Model {model} hit rate limit (429). Retrying in 5s... ({retries} left)")
                    time.sleep(5)
                    retries -= 1
                    continue
                elif response.status_code in [503, 404]:
                    print(f"[Gemini] Model {model} failed ({response.status_code}). Trying fallback...")
                    time.sleep(1)
                    break
                else:
                    print(f"[Gemini] API error {response.status_code}: {response.text[:200]}")
                    return "{}"
            except Exception as e:
                print(f"[Gemini] Request failed for {model}: {e}")
                break
            
    print("[Gemini] All fallback models exhausted or rate limit hit.")
    return "{}"


def extract_jd_requirements(jd_text: str) -> dict:
    """Extract structured requirements from a job description using AI."""
    if not jd_text or not jd_text.strip():
        return {"hard_skills": [], "responsibilities": [], "domain": "", "seniority": ""}

    prompt = f"""Analyze this job description and extract structured requirements.

Job Description:
{jd_text}

Return JSON with this exact structure:
{{
  "hard_skills": ["list of specific technical skills, tools, languages required"],
  "responsibilities": ["list of core job responsibilities"],
  "domain": "the industry or domain (e.g. FinTech, SaaS, Healthcare)",
  "seniority": "the experience level (e.g. Junior, Mid-level, Senior)"
}}
"""

    try:
        resp = call_gemini(prompt)
        if "```json" in resp:
            resp = resp.split("```json", 1)[1].rsplit("```", 1)[0].strip()
        elif "```" in resp:
            resp = resp.split("```", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(resp)
    except Exception as e:
        print(f"[JDAnalysis] Failed to parse: {e}")
        return {"hard_skills": [], "responsibilities": [], "domain": "", "seniority": ""}

def extract_clean_jd(raw_text: str) -> str:
    """Extract ONLY the full job description from raw web text and format as markdown."""
    prompt = f"""You are an expert AI Job Data Extractor.
I am providing you with raw scraped text from a job posting webpage.
Your task is to extract the EXACT job description and format it cleanly using Markdown (headers, bullet points).
Do not summarize it, extract the full requirements and responsibilities.
Ignore cookie banners, navigation links, and other website noise.

Return ONLY the Markdown text. No JSON, no explanations.

RAW TEXT:
---
{raw_text}
---
"""
    try:
        resp = call_gemini(prompt)
        # Strip potential markdown fences if the model wraps the whole thing in ```markdown
        if resp.startswith("```markdown"):
            resp = resp.split("```markdown", 1)[1].rsplit("```", 1)[0].strip()
        elif resp.startswith("```"):
            resp = resp.split("```", 1)[1].rsplit("```", 1)[0].strip()
        return resp
    except Exception as e:
        print(f"[JDAnalysis] Failed to extract clean JD: {e}")
        return raw_text # Fallback to raw text if AI fails
