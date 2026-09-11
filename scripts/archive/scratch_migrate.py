from sqlalchemy import create_engine, text
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.begin() as conn:
    print("Running migrations...")
    try:
        conn.execute(text("ALTER TABLE applications ADD COLUMN sub_status VARCHAR DEFAULT 'APPLIED' NOT NULL;"))
    except Exception as e:
        print("sub_status exists", e)
    try:
        conn.execute(text("ALTER TABLE applications ADD COLUMN recruiter_name VARCHAR;"))
    except Exception as e:
        pass
    try:
        conn.execute(text("ALTER TABLE applications ADD COLUMN interview_date TIMESTAMP WITH TIME ZONE;"))
    except Exception as e:
        pass
    try:
        conn.execute(text("ALTER TABLE applications ADD COLUMN salary_expected VARCHAR;"))
    except Exception as e:
        pass
    try:
        conn.execute(text("ALTER TABLE applications ADD COLUMN salary_offered VARCHAR;"))
    except Exception as e:
        pass
    try:
        conn.execute(text("ALTER TABLE applications ADD COLUMN pipeline_notes TEXT;"))
    except Exception as e:
        pass
    print("Migrations complete.")
