# Jobflow
*Your Personal Autonomous Job Pipeline & AI Resume Builder*

Jobflow is a high-performance Python application designed to act as your personal recruitment pipeline. It automates the tedious parts of the job search process by allowing you to instantly import leads from any website, filtering out poor matches using your Master Profile, and dynamically writing highly-tailored PDF resumes for every single application.

## 🚀 Features

- **Triage Queue Import System**: Paste a job link (LinkedIn, Indeed, JobStreet, Kalibrr, etc.) and Jobflow runs a lightning-fast 3-second scrape to fetch just the Title and Company. This populates your "Concourse/Receiving Area" dashboard without wasting heavy AI processing on jobs you haven't reviewed yet.
- **Frictionless Native Authentication (Firefox)**: Say goodbye to login scripts or captchas. Jobflow seamlessly integrates with `browser-cookie3` to extract cookies directly from your active, day-to-day local Firefox session and injects them into the headless Playwright scraper. It naturally bypasses strict login walls (like LinkedIn and Indeed) because it's using your actual authenticated session!
- **Master Knowledge Base**: Store your entire career history—every project, bullet point, skill, and certification—in one centralized Master Profile database. 
- **Generative AI Resume Tailoring**: Click "Generate Tailored Resume" on an approved job, and Google's Gemini AI analyzes the specific Job Description to intelligently extract the precise experiences, skills, and projects from your Master Profile that best match the job. It even rewrites bullets for maximum ATS impact.
- **Interactive Builder & Live PDF Preview**: Review and manually edit the AI's suggestions in a sleek web UI. Everything auto-saves. Click "Preview" to instantly render a **Live 1-Page PDF** (using your browser's native PDF engine) to see exactly how your resume looks before exporting.
- **ATS-Optimized PDF Export**: Generates pixel-perfect, highly professional resumes using traditional executive fonts directly to PDF via WeasyPrint.

## 🛠️ Architecture & Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL / SQLite (via SQLAlchemy & Alembic)
- **Scraping Engine**: Playwright + `browser-cookie3` (Firefox Native Integration) + BeautifulSoup4.
- **AI Engine**: Google Gemini (v1beta API) using `gemini-3.5-flash` with robust fallback retry layers for rate limits (HTTP 429).
- **Templating & UI**: Jinja2, TailwindCSS, FontAwesome.
- **PDF Generation**: WeasyPrint.

## 📂 Project Structure
```text
jobflow/
├── src/
│   ├── core/           # Configs, DB sessions, Auth dependencies
│   ├── models/         # SQLAlchemy ORM definitions (User, Job, Profile, Resume)
│   ├── routers/        # FastAPI Endpoints (Dashboard, Jobs, Resumes, Applications)
│   ├── schemas/        # Pydantic validation models
│   └── services/       # Core business logic (Universal Importer, AI Tailor, Playwright Scraper)
├── static/             # Static assets (CSS/JS)
├── templates/          # Jinja2 HTML Templates (UI, Builder, Dashboard, PDF Layouts)
└── README.md
```

## ⚙️ Getting Started

1. **Environment Setup:**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY="your_google_gemini_api_key"
   ADMIN_PASSWORD="your_secure_password"
   SECRET_KEY="your_jwt_secret"
   ```

2. **Installation:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Database Migration:**
   ```bash
   alembic upgrade head
   ```

4. **Run the Application:**
   ```bash
   uvicorn src.main:app --reload --port 8001
   ```
   Open `http://localhost:8001` in your browser. Default login relies on the `ADMIN_PASSWORD` defined in your `.env`.

## 🔄 The Pipeline Workflow
1. **Triage / Add Link**: Paste a URL from any job board. Jobflow borrows your Firefox cookies to bypass the login wall and grabs the basic info in < 3 seconds.
2. **Review & Approve**: The job lands in your "New" dashboard. If it looks good, click "Tailor Resume".
3. **AI Generation**: Gemini extracts requirements and maps them to your Master Profile, writing a highly targeted resume draft. (Cached instantly to prevent wasting quota).
4. **Edit & Live Preview**: Tweak bullets in the Interactive Builder. Hit "Preview" to instantly render the PDF on screen without downloading it.
5. **Export**: Export the final A4-formatted PDF and apply!
