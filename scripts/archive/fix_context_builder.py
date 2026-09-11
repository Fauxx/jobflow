with open("src/services/context_builder.py", "r") as f:
    content = f.read()

new_content = """import json
from collections import defaultdict
from sqlalchemy import orm
from sqlalchemy.orm import Session

from src.models.profile import UserProfile, ProfileProject, ProfileExperience, ProfileBullet
from src.models.job import Job

def build_context(db: Session, job: Job, user_id: int) -> str:
    \"\"\"
    Build a comprehensive, structured markdown document containing EVERYTHING
    known about the candidate. This is the AI's sole source of truth for
    resume tailoring.
    \"\"\"
    profile = db.query(UserProfile).options(
        orm.selectinload(UserProfile.skills),
        orm.selectinload(UserProfile.education),
        orm.selectinload(UserProfile.achievements),
        orm.selectinload(UserProfile.experiences).selectinload(ProfileExperience.bullets),
        orm.selectinload(UserProfile.projects).selectinload(ProfileProject.bullets),
    ).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        return "No candidate profile found."

    lines = []

    # ── Identity & Contact ──────────────────────────────────
    lines.append("# Candidate Master Knowledge Base")
    lines.append("")
    if profile.name:
        lines.append(f"**Name:** {profile.name}")
    if profile.title:
        lines.append(f"**Title:** {profile.title}")
    
    # ── Skills (grouped by category) ────────────────────────
    if profile.skills:
        lines.append("\\n## Technical & Professional Skills")
        for s in sorted(profile.skills, key=lambda x: x.order):
            lines.append(f"\\n**{s.category}:** {s.items}")

    # ── Experiences ──────────────────────
    if profile.experiences:
        lines.append("\\n## Professional Experience")
        for e in sorted(profile.experiences, key=lambda x: x.order):
            lines.append(f"\\n### {e.role or ''} at {e.company or ''}")
            if e.location:
                lines.append(f"**Location:** {e.location}")
            if e.date_range:
                lines.append(f"**Dates:** {e.date_range}")
            
            if e.bullets:
                lines.append("\\n**Bullet Points:**")
                for b in sorted(e.bullets, key=lambda x: x.order):
                    lines.append(f"- [ID: {b.id}] {b.text}")
                        
            # Deep context
            if e.detailed_context:
                lines.append(f"\\n**Deep Context:** {e.detailed_context}")

    # ── Projects ─────────────────────────
    if profile.projects:
        lines.append("\\n## Projects")
        for p in sorted(profile.projects, key=lambda x: x.order):
            lines.append(f"\\n### {p.title or ''}")
            if p.role:
                lines.append(f"**Role:** {p.role}")
            if p.date_range:
                lines.append(f"**Dates:** {p.date_range}")
            
            if p.bullets:
                lines.append("\\n**Bullet Points:**")
                for b in sorted(p.bullets, key=lambda x: x.order):
                    lines.append(f"- [ID: {b.id}] {b.text}")
                        
            # Deep context
            if p.detailed_context:
                lines.append(f"\\n**Deep Context:** {p.detailed_context}")

    # ── Education ───────────────────────────────────────────
    if profile.education:
        lines.append("\\n## Education")
        for ed in sorted(profile.education, key=lambda x: x.order):
            lines.append(f"\\n**{ed.degree}**")
            lines.append(f"{ed.institution}")
            if ed.location:
                lines.append(f"Location: {ed.location}")
            if ed.date_str:
                lines.append(f"Date: {ed.date_str}")

    # ── Master Profile Summary Context ──────────────────────
    if profile.master_summary_context:
        lines.append("\\n## Master Profile Summary Context")
        lines.append(profile.master_summary_context)

    return "\\n".join(lines)
"""

with open("src/services/context_builder.py", "w") as f:
    f.write(new_content)
