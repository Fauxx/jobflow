import re

with open("alembic/env.py", "r") as f:
    content = f.read()

# Add imports for metadata
import_statements = """
from src.models.base import Base
from src.models.user import User
from src.models.profile import UserProfile, ProfileSkill, ProfileProject, ProfileExperience, ProfileEducation, ProfileAchievement, skill_evidence
from src.models.resume import MasterResume, ResumeVersion
from src.models.job import Job
from src.models.application import Application
from src.core.config import settings

target_metadata = Base.metadata
"""

content = content.replace("target_metadata = None", import_statements)

# Update sqlalchemy.url
def_run_migrations_offline = "def run_migrations_offline() -> None:"
offline_patch = """def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )"""

content = re.sub(
    r'def run_migrations_offline\(\) -> None:.*?context\.configure\([^)]+\)',
    offline_patch,
    content,
    flags=re.DOTALL
)

online_patch = """def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )"""

content = re.sub(
    r'def run_migrations_online\(\) -> None:.*?connectable = engine_from_config\([\s\S]*?poolclass=pool\.NullPool,\n    \)',
    online_patch,
    content,
    flags=re.DOTALL
)

with open("alembic/env.py", "w") as f:
    f.write(content)
