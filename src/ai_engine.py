import subprocess
import os
import json
import requests
from src.config import (
    GEMINI_API_KEY,
    RESUME_PATH,
    RESUME_JSON_PATH,
    CANDIDATE_NAME,
    CANDIDATE_PHONE,
    CANDIDATE_LINKEDIN,
    CANDIDATE_GITHUB
)

def extract_pdf_text(pdf_path):
    """Extracts text from PDF using the system's pdftotext utility."""
    if not os.path.exists(pdf_path):
        return ""
    try:
        result = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

def call_gemini(prompt):
    """Helper to query the Gemini API directly."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured in your environment/.env file.")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=35)
    if response.status_code == 200:
        data = response.json()
        text_response = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Clean any raw markdown blocks if model returns them
        if text_response.startswith("```json"):
            text_response = text_response.split("```json", 1)[1].rsplit("```", 1)[0].strip()
        elif text_response.startswith("```"):
            text_response = text_response.split("```", 1)[1].rsplit("```", 1)[0].strip()
        return text_response
    else:
        raise Exception(f"Gemini API returned status code {response.status_code}: {response.text}")

def generate_tailored_application(job_title, company, job_description):
    """Uses Gemini API to generate tailored cover letter, key matches, and screening answers."""
    # Read base resume text
    resume_text = extract_pdf_text(RESUME_PATH)
    if not resume_text:
        # Fallback to loading structured JSON resume
        if os.path.exists(RESUME_JSON_PATH):
            with open(RESUME_JSON_PATH, "r") as f:
                resume_text = json.dumps(json.load(f), indent=2)

    if not GEMINI_API_KEY:
        return {
            "subject": f"Application for {job_title} at {company} - {CANDIDATE_NAME}",
            "body": f"Please enter your GEMINI_API_KEY in your .env file to enable AI-powered cover letters.",
            "key_matches": [
                f"Matching skills for {job_title}",
                "Kubernetes & Docker container management",
                "Terraform Infrastructure as Code (IaC)"
            ],
            "screening_answers": {
                "Why are you a good fit?": "My background in computer engineering technology and hands-on projects with Kubernetes, Terraform, and GitHub Actions align well with this DevOps/IT role.",
                "Describe your experience with system administration": "Experienced with Fedora and Ubuntu systems administration, provisioning virtual environments, shell scripting, and configuring Nginx reverse-proxies."
            }
        }

    prompt = f"""
You are an expert career agent helping {CANDIDATE_NAME} apply for a job.
Analyze the following Job Details and Candidate Resume, and generate tailored application assets.

Job Title: {job_title}
Company: {company}
Job Description:
{job_description}

Candidate Resume:
{resume_text}

---
Format your output as raw JSON with these exact keys:
1. "subject": Tailored email/portal subject line.
2. "body": Full cover letter body. Include contact info at the bottom (Name: {CANDIDATE_NAME}, Phone: {CANDIDATE_PHONE}, LinkedIn: {CANDIDATE_LINKEDIN}, GitHub: {CANDIDATE_GITHUB}). Keep it to 3 short paragraphs.
3. "key_matches": Array of 3 short, high-impact bullet strings explaining why the candidate is a strong fit.
4. "screening_answers": A JSON object mapping 2 common screening questions (e.g. "Why are you a good fit?", "Describe your DevOps/cloud experience") to tailored, first-person answers.

Output ONLY valid JSON.
"""

    try:
        response_text = call_gemini(prompt)
        return json.loads(response_text)
    except Exception as e:
        print(f"Error generating tailored app: {e}")
        return {
            "subject": f"Application for {job_title} at {company} - {CANDIDATE_NAME}",
            "body": f"Dear Hiring Team,\n\nI am writing to apply for the {job_title} position at {company}.\n\nBest regards,\n{CANDIDATE_NAME}",
            "key_matches": ["Strong alignment with core requirements."],
            "screening_answers": {}
        }

def suggest_resume_optimizations(job_title, company, job_description):
    """Suggests targeted bullet point optimizations in the resume based on the job description."""
    if not os.path.exists(RESUME_JSON_PATH):
        return []

    with open(RESUME_JSON_PATH, "r") as f:
        resume_data = json.load(f)

    if not GEMINI_API_KEY:
        return []

    # Flatten bullets from projects and experience to send to Gemini, including Master Contexts
    master_proj_map = {p["title"]: p["detailed_context"] for p in resume_data.get("master_profile", {}).get("projects", [])}
    master_exp_map = {e["company"]: e["detailed_context"] for e in resume_data.get("master_profile", {}).get("experience", [])}

    candidates = []
    for idx, p in enumerate(resume_data.get("projects", [])):
        detailed = master_proj_map.get(p["title"], "")
        for b_idx, bullet in enumerate(p.get("bullets", [])):
            candidates.append({
                "source": "projects",
                "item_index": idx,
                "bullet_index": b_idx,
                "parent_title": p["title"],
                "text": bullet,
                "master_project_context": detailed
            })
    for idx, exp in enumerate(resume_data.get("experience", [])):
        detailed = master_exp_map.get(exp["company"], "")
        for b_idx, bullet in enumerate(exp.get("bullets", [])):
            candidates.append({
                "source": "experience",
                "item_index": idx,
                "bullet_index": b_idx,
                "parent_title": exp["company"],
                "text": bullet,
                "master_experience_context": detailed
            })

    prompt = f"""
You are an expert resume writer. Help the candidate tailor their resume to a specific job description.
Identify exactly 2 bullet points from the list of candidates below that can be optimized to better match the target job.
Using the provided "master_project_context" or "master_experience_context" (which lists the full technical details of the candidate's work),
rewrite the selected bullets to highlight relevant technologies/skills in the job description while staying truthful to the context.

Job Title: {job_title}
Company: {company}
Job Description:
{job_description}

Bullet Point Candidates (with master profile background details):
{json.dumps(candidates, indent=2)}

---
Format your output as a raw JSON array of objects. Each object must have:
- "source": "projects" or "experience"
- "item_index": The integer item index
- "bullet_index": The integer bullet index
- "parent_title": Title or company name
- "original_bullet": The exact original bullet text
- "optimized_bullet": The rewritten optimized bullet text
- "rationale": Brief sentence explaining why this change matches the job description

Output ONLY valid JSON.
"""

    try:
        response_text = call_gemini(prompt)
        return json.loads(response_text)
    except Exception as e:
        print(f"Error suggesting resume optimizations: {e}")
        return []
