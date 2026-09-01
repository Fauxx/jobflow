# Jobflow
*Your Personal Autonomous Job Pipeline & AI Resume Builder*

Jobflow is a high-performance Python application designed to act as your personal recruitment pipeline. It automates the tedious parts of the job search process by allowing you to instantly import leads from any website, filtering out poor matches using your Master Profile, and dynamically writing highly-tailored PDF resumes for every single application.

## 🚀 Features

- **Universal AI Link Importer**: Say goodbye to fragile, hardcoded web scrapers. Simply paste a job URL from **any website** (LinkedIn, Greenhouse, Workday, Lever, or a startup's custom site). The backend downloads the raw page text and uses Google's Gemini AI to intelligently extract the exact Job Title, Company, and Description. Zero IP bans, 100% reliability.
- **Master Knowledge Base**: Store your entire career history—every project, bullet point, skill, and certification—in one centralized Master Profile database. 
- **AI Match Scoring**: Automatically grades incoming job leads against your Master Profile skills to bubble up your best opportunities.
- **Generative AI Resume Tailoring**: Connects to Gemini to analyze a specific Job Description and intelligently extract the precise experiences, skills, and bullets from your Master Profile that best match the job. It even rewrites bullets for maximum ATS impact.
- **Interactive Builder**: Review and manually edit the AI's suggestions in a sleek web UI. Add, remove, or modify experiences, projects, and skills.
- **ATS-Optimized PDF Export**: Generates pixel-perfect, highly professional resumes using traditional executive fonts (Garamond/Georgia) directly to PDF via WeasyPrint.

## 🛠️ Architecture & Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL (via SQLAlchemy & Alembic) + SQLite (for local testing)
- **AI Engine**: Google Gemini (v1beta API) using `gemini-3.6-flash` with robust fallback layers (2.5-flash, pro-latest).
- **Templating & UI**: Jinja2, TailwindCSS, FontAwesome.
- **PDF Generation**: WeasyPrint.
- **Ingestion**: Custom Universal Web Reader (`BeautifulSoup4` + `Requests`) paired with LLM extraction.

## 📂 Project Structure
```text
jobflow/
├── src/
│   ├── core/           # Configs, DB sessions, Auth dependencies
│   ├── models/         # SQLAlchemy ORM definitions (User, Job, Profile, Resume)
│   ├── routers/        # FastAPI Endpoints (Dashboard, Jobs, Resumes, Applications)
│   ├── schemas/        # Pydantic validation models
│   └── services/       # Core business logic (Universal Importer, AI Context Builder, Resume Tailor)
├── static/             # Static assets (CSS/JS)
├── templates/          # Jinja2 HTML Templates (UI, Builder, Dashboard, PDF Layouts)
└── README.md
```

## ⚙️ Getting Started

1. **Environment Setup:**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL="postgresql://user:pass@localhost:5432/jobflow"
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
   uvicorn src.main:app --reload --port 8080
   ```
   Open `http://localhost:8080` in your browser. Default login relies on the `ADMIN_PASSWORD` defined in your `.env`.

## 🔄 The Pipeline Workflow
1. **Import**: Click "Import Job Link" on the dashboard and paste a URL from any job board to pull it into the `NEW` pipeline.
2. **Filter**: Use the built-in Match Score and keyword filters to flush out bad leads into the `SKIPPED` bin (or hit "Empty Trash" to hard-delete them).
3. **Approve**: Click "Approve & Tailor" on a good lead. Gemini will instantly write your custom resume based on the Job Description.
4. **Build & Export**: Edit the AI suggestions in the Builder. Click "Save & Download PDF" when ready!
