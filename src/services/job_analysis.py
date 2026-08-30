import json
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
