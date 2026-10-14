import sys
import logging
from src.services.job_analysis import call_gemini

print("Testing Gemini API...")
try:
    response = call_gemini("Say 'Hello, the API is working!'", json_mode=False)
    print(f"Response: {response}")
except Exception as e:
    print(f"Error: {e}")
