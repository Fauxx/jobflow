# Jobflow 🌊
*Your Personal Autonomous Job Pipeline & AI Resume Builder*

Jobflow is a high-performance Python application designed to act as your personal recruitment pipeline. It automates the tedious parts of the job search process by allowing you to instantly import leads from any website, intelligently mapping them against your Master Profile, and dynamically writing highly-tailored PDF resumes for every single application.

---

## 🚀 Features

- **Triage Queue Import System**: Paste a job link (LinkedIn, Indeed, JobStreet, Kalibrr, etc.) and Jobflow runs a lightning-fast scrape to fetch just the Title and Company. This populates your dashboard without wasting heavy AI processing on jobs you haven't reviewed yet.
- **Frictionless Native Authentication (Cross-Browser)**: Say goodbye to login scripts or captchas. Jobflow seamlessly integrates with `browser-cookie3` to extract cookies directly from your active, day-to-day local browser (Chrome, Firefox, Edge, Safari, Brave) and injects them into the headless Playwright scraper. It naturally bypasses strict login walls (like LinkedIn and Indeed) because it's using your actual authenticated session!
- **Master Knowledge Base**: Store your entire career history—every project, bullet point, skill, and certification—in one centralized Master Profile database. 
- **Generative AI Resume Tailoring**: Click "Generate Tailored Resume" on an approved job, and Google's Gemini AI analyzes the specific Job Description to intelligently extract the precise experiences, skills, and projects from your Master Profile that best match the job. It even rewrites bullets for maximum ATS impact without hallucinating facts.
- **Interactive Builder & AI Adjustments**: Review and manually edit the AI's suggestions in a sleek web UI. Highlight text, hit the **"Ask AI to Adjust"** chat bar, and watch Gemini seamlessly rewrite specific bullets while referencing your Master Profile.
- **Live 1-Page PDF Preview**: Click "Preview" to instantly render a **Live 1-Page PDF** (using your browser's native PDF engine) to see exactly how your resume looks before exporting.
- **ATS-Optimized PDF Export**: Generates pixel-perfect, highly professional resumes directly to PDF via WeasyPrint.

---

## 🛠️ Architecture & Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL / SQLite (via SQLAlchemy & Alembic)
- **Scraping Engine**: Playwright + `browser-cookie3` (Native Integration) + BeautifulSoup4.
- **AI Engine**: Google Gemini (v1beta API) using `gemini-3.5-flash` with robust fallback retry layers for rate limits (HTTP 429).
- **Templating & UI**: Jinja2, TailwindCSS, FontAwesome.
- **PDF Generation**: WeasyPrint.

---

## ⚙️ Configuration (.env)

Before installing, create a `.env` file in the root directory.

```env
# Required: Your Google Gemini API Key
GEMINI_API_KEY="your_google_gemini_api_key"

# Required: The password you will use to log into the Jobflow Web UI
ADMIN_PASSWORD="jobflow2026"

# Optional: JWT Secret (can be any random string)
SECRET_KEY="your_jwt_secret"

# Optional: Defaults to local SQLite if omitted. Add for Postgres.
# DATABASE_URL="postgresql://user:pass@localhost:5432/jobflow"
```

---

## 🚀 Installation Guide

Because Jobflow's "magical" login-bypass feature relies on reading your host machine's browser cookies, we highly recommend running it **natively** rather than in Docker. We have provided instructions for both.

### Option A: Native Local Install (Highly Recommended ⭐)
*Running natively allows Jobflow to see your local Chrome/Firefox/Edge cookies and flawlessly bypass LinkedIn/Indeed login walls.*

**1. Install System Dependencies (For WeasyPrint PDF Generation)**
- **Fedora/RHEL**: `sudo dnf install pango pango-devel cairo cairo-devel libffi-devel`
- **Ubuntu/Debian**: `sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libffi-dev`
- **macOS**: `brew install pango libffi`
- **Windows**: Install [GTK3 for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) and add it to your System PATH.

**2. Install Python Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Install Playwright Browsers**
```bash
playwright install firefox
```

**4. Run Database Migrations & Start Server**
```bash
alembic upgrade head
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```
Open `http://localhost:8001` in your browser!

---

### Option B: Docker Install (Quickest Setup)
*Note: Docker runs in an isolated sandbox and **cannot** read your local browser cookies. The LinkedIn/Indeed auto-login bypass feature will not work in Docker. You will only be able to scrape public job boards or APIs.*

```bash
# Make sure your .env file is created first
docker compose up --build
```
Open `http://localhost:8001` in your browser!

---

## 🔄 The Pipeline Workflow

1. **Import Job Link**: Paste a URL from any job board into the dashboard. Jobflow uses your native browser cookies to bypass the login wall and grabs the basic info in < 3 seconds.
2. **Review & Approve**: The job lands in your "New" Triage dashboard. If it looks good, click "Approve & Tailor".
3. **AI Generation**: Gemini extracts requirements and maps them to your Master Profile, writing a highly targeted resume draft. (Cached instantly to prevent wasting API quota).
4. **Edit & Live Preview**: Tweak bullets manually or use the "Ask AI" chat bar at the bottom of the Builder. Hit "Preview" to instantly render the PDF on screen.
5. **Export**: Export the final A4-formatted PDF and apply!

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
