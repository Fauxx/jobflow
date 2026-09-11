import sys, requests
sys.path.append('/home/zett/RiderProjects/jobflow')
from src.core.config import settings

api_key = settings.GEMINI_API_KEY
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
response = requests.post(url, headers={"Content-Type": "application/json"}, json={"contents": [{"parts": [{"text": "Hello"}]}]})
print(response.status_code)
print(response.text)
