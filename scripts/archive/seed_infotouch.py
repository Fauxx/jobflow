"""
Seed script: Populate master profile with Infotouch internship data.
Context sources:
  - DWA (Daily Work Activities) PDF: /home/zett/Downloads/Updated_DWA.pdf
  - Sandhub API codebase: /home/zett/RiderProjects/sandhub-api
  - Internship: Software Developer Intern @ Infotouch (Sandhub), Training Station: Web Dev / Software Dev
  - Supervisor: Jaime II R. Licud & Chardsky Taopa (Senior Software Developers)
  - Duration: Feb – June (OJT, ~500+ hrs)
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/zett/RiderProjects/jobflow/jobflow.db"


def seed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ── 1. Create user & profile if not present ──────────────────────────────
    c.execute("SELECT id FROM users WHERE email = 'zet@infotouch.local'")
    user = c.fetchone()
    if not user:
        c.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            ("zet@infotouch.local", "placeholder", datetime.now().isoformat()),
        )
        user_id = c.lastrowid
        print(f"Created user id={user_id}")
    else:
        user_id = user[0]
        print(f"User already exists id={user_id}")

    c.execute("SELECT id FROM user_profiles WHERE user_id = ?", (user_id,))
    profile = c.fetchone()
    if not profile:
        c.execute(
            """INSERT INTO user_profiles
               (user_id, status, name, title, headline, location, created_at)
               VALUES (?, 'DRAFT', ?, ?, ?, ?, ?)""",
            (
                user_id,
                "Zet Donaue Samson",
                "Software Developer",
                "ASP.NET Core & REST API developer | TUP graduate",
                "Manila, Philippines",
                datetime.now().isoformat(),
            ),
        )
        profile_id = c.lastrowid
        print(f"Created profile id={profile_id}")
    else:
        profile_id = profile[0]
        print(f"Profile already exists id={profile_id}")

    # ── 2. Education ──────────────────────────────────────────────────────────
    c.execute("SELECT id FROM profile_education WHERE profile_id = ?", (profile_id,))
    if not c.fetchone():
        c.execute(
            """INSERT INTO profile_education (profile_id, institution, degree, date_str, location)
               VALUES (?, ?, ?, ?, ?)""",
            (
                profile_id,
                "Technological University of the Philippines",
                "Bachelor of Science in Information Technology",
                "2013 – 2018",
                "Ayala Blvd., Ermita, Manila",
            ),
        )
        print("Education inserted.")

    # ── 3. Experience: Infotouch (Sandhub) ───────────────────────────────────
    c.execute(
        "SELECT id FROM profile_experience WHERE profile_id = ? AND company = ?",
        (profile_id, "Infotouch (Sandhub Platform)"),
    )
    exp = c.fetchone()
    if not exp:
        c.execute(
            """INSERT INTO profile_experience
               (profile_id, company, title, description, location, start_date, end_date, "order",
                problem_statement, actions_taken, measurable_results, tech_stack)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                profile_id,
                "Infotouch (Sandhub Platform)",
                "Software Developer Intern",
                (
                    "OJT placement at Infotouch's web and software development team, "
                    "working on the Sandhub platform — a service-booking and field-agent "
                    "management system built with ASP.NET Core Minimal APIs, MySQL, and "
                    "mobile clients. Reported to Senior Software Developers and contributed "
                    "to backend API refactoring, QA testing, and full-stack integration work."
                ),
                "Manila, Philippines",
                "February 2025",
                "June 2025",
                1,  # order
                (
                    "The Sandhub platform had legacy Web API controllers that needed to be "
                    "modernised to Minimal APIs, and the mobile app required rigorous QA coverage "
                    "before public rollout."
                ),
                (
                    "Audited legacy endpoints, refactored controllers to Minimal API pattern, "
                    "implemented request validation, optimised SQL queries, wrote unit tests, "
                    "and conducted mobile app QA testing across multiple cycles."
                ),
                (
                    "Successfully migrated legacy controllers; validated CRUD operations end-to-end; "
                    "completed 500+ hours of OJT with consistent 8-hour daily logs across 18+ weeks."
                ),
                "C#, ASP.NET Core, Minimal APIs, MySQL, Dapper, Postman, Git, GitHub",
            ),
        )
        exp_id = c.lastrowid
        print(f"Experience inserted id={exp_id}")
    else:
        exp_id = exp[0]
        print(f"Experience already exists id={exp_id}")

    # ── 4. Bullets (master pool — AI tailoring will pick the best) ───────────
    c.execute(
        "SELECT COUNT(*) FROM profile_bullets WHERE experience_id = ?", (exp_id,)
    )
    if c.fetchone()[0] == 0:
        bullets = [
            # --- Onboarding & environment ---
            (
                "Set up local development environment for the Sandhub ASP.NET Core API, "
                "including Git repository cloning, branch configuration, and dependency installation.",
                "Set up", "C#, ASP.NET Core, Git, GitHub", 1,
            ),
            (
                "Reviewed overall system architecture and traced API call flows from the web "
                "frontend through backend controllers to the MySQL database layer.",
                "Reviewed", "ASP.NET Core, MySQL, REST API", 2,
            ),
            (
                "Familiarised with database schema and data models across the order, agent, "
                "client, service, and wallet domains of the Sandhub platform.",
                "Familiarised", "MySQL, Dapper, C#", 3,
            ),
            (
                "Practiced Git branching workflows and simulated pull request and code merge "
                "procedures following the team's version-control conventions.",
                "Practiced", "Git, GitHub", 4,
            ),
            # --- C# / language fundamentals ---
            (
                "Completed structured review of C# language syntax, fundamentals, and "
                "asynchronous programming patterns (async/await) as preparation for production work.",
                "Completed", "C#, .NET", 5,
            ),
            (
                "Applied asynchronous programming patterns (async/await) to controller actions "
                "and service-layer methods to improve API responsiveness.",
                "Applied", "C#, ASP.NET Core, async/await", 6,
            ),
            # --- API refactoring ---
            (
                "Audited legacy Web API controller endpoints to identify candidates for "
                "refactoring to ASP.NET Core Minimal APIs, reducing boilerplate code.",
                "Audited", "ASP.NET Core, C#", 7,
            ),
            (
                "Converted multiple Web API controllers to the ASP.NET Core Minimal API "
                "pattern, restructuring route handlers and service injection for improved maintainability.",
                "Converted", "C#, ASP.NET Core Minimal APIs", 8,
            ),
            (
                "Restructured route handlers and service dependencies during API migration, "
                "ensuring backward-compatible request and response contracts.",
                "Restructured", "ASP.NET Core, C#, REST API", 9,
            ),
            (
                "Refactored POST and PUT endpoints for data creation and update operations, "
                "aligning them with RESTful conventions and team coding standards.",
                "Refactored", "C#, ASP.NET Core, REST API, MySQL", 10,
            ),
            (
                "Implemented input validation on incoming API requests, adding model-binding "
                "guards and error-response formatting to prevent malformed data from reaching the database.",
                "Implemented", "C#, ASP.NET Core, Data Validation", 11,
            ),
            # --- Database & query optimisation ---
            (
                "Optimised database queries within the Orders and Wallet service layers using "
                "Dapper, reducing unnecessary joins and improving query clarity.",
                "Optimised", "MySQL, Dapper, C#", 12,
            ),
            (
                "Tested full CRUD operations on the order, agent, and client data domains, "
                "verifying data integrity across related tables (order, agent, client, service, wallet).",
                "Tested", "MySQL, Postman, C#", 13,
            ),
            # --- Testing & QA ---
            (
                "Tested refactored GET endpoints via Postman, validating response schemas, "
                "status codes, and data correctness against expected MySQL query results.",
                "Tested", "Postman, REST API, MySQL", 14,
            ),
            (
                "Conducted internal API performance testing to identify slow endpoints and "
                "validate response times under simulated load.",
                "Conducted", "Postman, ASP.NET Core, MySQL", 15,
            ),
            (
                "Tested authentication flows including login, token handling, token expiration "
                "detection, and session timeout behaviour across web and mobile clients.",
                "Tested", "ASP.NET Core, JWT, Auth", 16,
            ),
            (
                "Wrote and updated unit tests for newly refactored API endpoints, covering "
                "happy-path and edge-case scenarios to maintain code quality.",
                "Wrote", "C#, Unit Testing, ASP.NET Core", 17,
            ),
            (
                "Performed final code review and merged API refactoring branches into the "
                "main development branch, resolving conflicts and ensuring CI pipeline stability.",
                "Performed", "Git, GitHub, Code Review, CI", 18,
            ),
            # --- Frontend & analytics ---
            (
                "Updated frontend component styling and fixed responsive design alignment "
                "issues on the Sandhub web client to improve cross-device usability.",
                "Updated", "HTML, CSS, Responsive Design", 19,
            ),
            (
                "Integrated analytics tracking metrics into the web frontend to capture "
                "user engagement events for reporting purposes.",
                "Integrated", "JavaScript, Analytics, Frontend", 20,
            ),
            # --- Mobile QA ---
            (
                "Executed comprehensive QA testing cycles on the Sandhub mobile application, "
                "covering booking flows, agent dispatch, order tracking, wallet, and payment features.",
                "Executed", "Mobile QA, Manual Testing", 21,
            ),
            (
                "Validated mobile app login flows, session management, and token refresh "
                "behaviour to ensure secure and seamless user authentication.",
                "Validated", "Mobile QA, Auth, JWT", 22,
            ),
            (
                "Reported and documented mobile app defects across multiple QA cycles, "
                "collaborating with senior developers to verify fixes and re-test affected flows.",
                "Reported", "QA, Bug Reporting, Mobile", 23,
            ),
            (
                "Participated in 500+ hours of hands-on software development OJT under "
                "senior developer mentorship, gaining practical experience across the full "
                "backend-to-mobile development lifecycle.",
                "Participated", "ASP.NET Core, MySQL, Git, Mobile QA, Postman", 24,
            ),
        ]

        for text, action_verb, technologies, order in bullets:
            c.execute(
                """INSERT INTO profile_bullets
                   (experience_id, project_id, raw_text, action_verb, technologies_used, "order")
                   VALUES (?, NULL, ?, ?, ?, ?)""",
                (exp_id, text, action_verb, technologies, order),
            )
        print(f"{len(bullets)} bullets inserted for experience id={exp_id}.")
    else:
        print("Bullets already exist, skipping.")

    # ── 5. Skills ─────────────────────────────────────────────────────────────
    c.execute("SELECT COUNT(*) FROM profile_skills WHERE profile_id = ?", (profile_id,))
    if c.fetchone()[0] == 0:
        skills = [
            ("C# / .NET", "Intermediate", "Backend"),
            ("ASP.NET Core (Web API & Minimal APIs)", "Intermediate", "Backend"),
            ("MySQL", "Intermediate", "Database"),
            ("Dapper (micro-ORM)", "Intermediate", "Database"),
            ("REST API Design", "Intermediate", "Backend"),
            ("Git & GitHub", "Intermediate", "DevOps / Tools"),
            ("Postman (API Testing)", "Intermediate", "Testing"),
            ("Unit Testing (C#)", "Beginner", "Testing"),
            ("HTML / CSS (Responsive Design)", "Beginner", "Frontend"),
            ("JavaScript (Frontend)", "Beginner", "Frontend"),
            ("Mobile App QA (Manual Testing)", "Intermediate", "Testing"),
            ("JWT Authentication", "Beginner", "Backend"),
        ]
        for name, proficiency, category in skills:
            c.execute(
                "INSERT INTO profile_skills (profile_id, name, proficiency, category) VALUES (?, ?, ?, ?)",
                (profile_id, name, proficiency, category),
            )
        print(f"{len(skills)} skills inserted.")
    else:
        print("Skills already exist, skipping.")

    conn.commit()
    conn.close()
    print("\n✅ Seed complete. Profile, experience, bullets, education, and skills populated.")


if __name__ == "__main__":
    seed()
