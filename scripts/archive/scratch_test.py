import sys, os
sys.path.append('/home/zett/RiderProjects/jobflow')
from src.services.job_analysis import call_gemini

resp = call_gemini("{\"message\": \"Hello\"}")
print("Resp:", resp)
