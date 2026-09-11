import json
import datetime
from sqlalchemy import create_engine, text
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)

backup = {
    "timestamp": datetime.datetime.now().isoformat(),
    "users": [],
    "jobs": [],
    "applications": [],
    "master_resumes": [],
    "user_profiles": []
}

def fetch_table(conn, table_name):
    try:
        result = conn.execute(text(f"SELECT * FROM {table_name}"))
        rows = []
        for row in result.mappings():
            row_dict = dict(row)
            # Convert datetime to string for JSON serialization
            for k, v in row_dict.items():
                if isinstance(v, datetime.datetime):
                    row_dict[k] = v.isoformat()
            rows.append(row_dict)
        return rows
    except Exception as e:
        print(f"Warning: Could not fetch {table_name}: {e}")
        return []

with engine.connect() as conn:
    backup["users"] = fetch_table(conn, "users")
    backup["jobs"] = fetch_table(conn, "jobs")
    backup["applications"] = fetch_table(conn, "applications")
    backup["master_resumes"] = fetch_table(conn, "master_resumes")
    backup["user_profiles"] = fetch_table(conn, "user_profiles")

with open("jobflow_backup.json", "w") as f:
    json.dump(backup, f, indent=4)

print(f"Backup complete! Saved {len(backup['users'])} users, {len(backup['jobs'])} jobs, {len(backup['applications'])} applications, and {len(backup['master_resumes'])} master resumes.")
