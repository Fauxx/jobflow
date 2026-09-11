import sys
from sqlalchemy import create_engine, text
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)

alter_statements = [
    "ALTER TABLE applications ADD COLUMN date_applied TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE applications ADD COLUMN date_screening TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE applications ADD COLUMN date_interview TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE applications ADD COLUMN date_offer TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE applications ADD COLUMN date_rejected TIMESTAMP WITH TIME ZONE;"
]

with engine.begin() as conn:
    for stmt in alter_statements:
        try:
            conn.execute(text(stmt))
            print(f"Executed: {stmt}")
        except Exception as e:
            print(f"Failed (might exist): {stmt} - {e}")

print("Migration done.")
