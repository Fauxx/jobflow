import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "jobflow.db"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create jobs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT,
        description_url TEXT,
        contact_email TEXT,
        source TEXT,
        discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'NEW' CHECK(status IN ('NEW', 'SKIPPED', 'APPROVED', 'APPLIED', 'REJECTED', 'INTERVIEWING'))
    )
    """)
    
    # Create applications tracking table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        email_subject TEXT,
        email_body_sent TEXT,
        follow_up_count INTEGER DEFAULT 0,
        last_follow_up_date TIMESTAMP,
        FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")

if __name__ == "__main__":
    init_db()
