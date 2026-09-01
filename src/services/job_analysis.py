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
        "gemini-3.6-flash",
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-pro-latest"
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
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            elif response.status_code in [503, 404, 429]:
                print(f"[Gemini] Model {model} failed ({response.status_code}). Trying fallback...")
                time.sleep(1)
                continue
            else:
                print(f"[Gemini] API error {response.status_code}: {response.text[:200]}")
                return "{}"
        except Exception as e:
            print(f"[Gemini] Request failed for {model}: {e}")
            continue
            
    print("[Gemini] All fallback models exhausted.")
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
