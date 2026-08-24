import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "jobflow.db")))
RESUME_PATH = os.getenv("RESUME_PATH", "/home/zett/Downloads/Zet_Donaue_Samson_Resume-1.pdf")
RESUME_JSON_PATH = os.getenv("RESUME_JSON_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "resume.json")))
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USER)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
CANDIDATE_NAME = os.getenv("CANDIDATE_NAME", "Zet Donaue Samson")
CANDIDATE_PHONE = os.getenv("CANDIDATE_PHONE", "+63 908 377 6146")
CANDIDATE_LINKEDIN = os.getenv("CANDIDATE_LINKEDIN", "linkedin.com/in/zet02")
CANDIDATE_GITHUB = os.getenv("CANDIDATE_GITHUB", "github.com/Fauxx")

