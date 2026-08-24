import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "jobflow.db")))
RESUME_PATH = os.getenv("RESUME_PATH", "/home/zett/RiderProjects/FireMonitoringSystem/Zet_Donaue_Samson_Resume.pdf")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USER)
