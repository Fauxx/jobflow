import json
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import orm
from src.models.profile import UserProfile, ProfileProject, ProfileExperience
from src.models.resume import MasterResume
from src.models.job import Job

def build_context(db: Session, job: Job, user_id: int) -> str:
    """
    Build a comprehensive, structured markdown document containing EVERYTHING
    known about the candidate. This is the AI's sole source of truth for
    resume tailoring — the richer this is, the better the output.
    """
    profile = db.query(UserProfile).options(
        orm.selectinload(UserProfile.skills),
        orm.selectinload(UserProfile.projects).selectinload(ProfileProject.bullets),
        orm.selectinload(UserProfile.experiences).selectinload(ProfileExperience.bullets),
        orm.selectinload(UserProfile.education),
        orm.selectinload(UserProfile.achievements),
    ).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        return "Candidate Profile Not Found"
    
    # Also load the master_resume JSON for detailed_context
    master_resume = db.query(MasterResume).filter(MasterResume.user_id == user_id).order_by(MasterResume.id.desc()).first()
    master_data = {}
    if master_resume and master_resume.content:
        try:
            master_data = json.loads(master_resume.content) if isinstance(master_resume.content, str) else master_resume.content
        except Exception:
            master_data = {}

    lines = []

    # ── Identity & Contact ──────────────────────────────────
    lines.append("# Candidate Master Knowledge Base")
    lines.append("")
    if profile.name:
        lines.append(f"**Name:** {profile.name}")
    if profile.title:
        lines.append(f"**Title:** {profile.title}")
    if profile.location:
        lines.append(f"**Location:** {profile.location}")
    if profile.phone:
        lines.append(f"**Phone:** {profile.phone}")
    if profile.linkedin_url:
        lines.append(f"**LinkedIn:** {profile.linkedin_url}")
    if profile.github_url:
        lines.append(f"**GitHub:** {profile.github_url}")
    if profile.portfolio_url:
        lines.append(f"**Portfolio:** {profile.portfolio_url}")
    if profile.headline:
        lines.append(f"\n**Professional Headline:** {profile.headline}")

    # ── Career Targeting ────────────────────────────────────
    has_targeting = any([profile.career_goals, profile.target_roles, profile.target_industries, profile.location_prefs, profile.personalization_prefs])
    if has_targeting:
        lines.append("\n## Career Targeting & Preferences")
        if profile.career_goals:
            lines.append(f"**Career Goals:** {profile.career_goals}")
        if profile.target_roles:
            lines.append(f"**Target Roles:** {profile.target_roles}")
        if profile.target_industries:
            lines.append(f"**Target Industries:** {profile.target_industries}")
        if profile.location_prefs:
            lines.append(f"**Location Preferences:** {profile.location_prefs}")
        if profile.personalization_prefs:
            lines.append(f"**Personalization Notes:** {profile.personalization_prefs}")

    # ── Skills (grouped by category) ────────────────────────
    if profile.skills:
        lines.append("\n## Technical & Professional Skills")
        skills_by_cat = defaultdict(list)
        for s in profile.skills:
            cat = s.category or "General"
            skills_by_cat[cat].append(s.name)
        for cat in sorted(skills_by_cat.keys()):
            lines.append(f"\n**{cat}:** {', '.join(skills_by_cat[cat])}")

    # ── Experiences ─────────────────────────────────────────
    if profile.experiences:
        lines.append("\n## Professional Experience")
        for e in sorted(profile.experiences, key=lambda x: x.order):
            lines.append(f"\n### {e.title} at {e.company}")
            if e.location:
                lines.append(f"**Location:** {e.location}")
            date_parts = []
            if e.start_date: date_parts.append(e.start_date)
            if e.end_date: date_parts.append(e.end_date)
            if date_parts:
                lines.append(f"**Dates:** {' – '.join(date_parts)}")
            if e.description:
                lines.append(f"\n{e.description}")
            if e.achievements:
                lines.append(f"\n**Key Achievements:** {e.achievements}")
            if e.bullets:
                lines.append("\n**Bullet Points:**")
                for b in sorted(e.bullets, key=lambda x: x.order):
                    lines.append(f"- {b.raw_text}")
            # Inject detailed_context from master_resume if available
            mp = master_data.get("master_profile", {})
            for exp_ctx in mp.get("experience", []):
                if exp_ctx.get("company", "").lower() in e.company.lower():
                    lines.append(f"\n**Deep Context:** {exp_ctx.get('detailed_context', '')}")

    # ── Highlight Projects ──────────────────────────────────
    highlight_projects = [p for p in profile.projects if p.is_highlight]
    other_projects = [p for p in profile.projects if not p.is_highlight]
    
    if highlight_projects:
        lines.append("\n## Highlight Projects (Primary)")
        for p in sorted(highlight_projects, key=lambda x: x.order):
            _append_project(lines, p, master_data)

    if other_projects:
        lines.append("\n## Additional Projects")
        for p in sorted(other_projects, key=lambda x: x.order):
            _append_project(lines, p, master_data)
                
    # ── Education ───────────────────────────────────────────
    if profile.education:
        lines.append("\n## Education")
        for ed in profile.education:
            lines.append(f"\n**{ed.degree}**")
            lines.append(f"{ed.institution}")
            if ed.location:
                lines.append(f"Location: {ed.location}")
            if ed.date_str:
                lines.append(f"Date: {ed.date_str}")

    # ── Achievements / Certifications ───────────────────────
    if profile.achievements:
        lines.append("\n## Achievements & Certifications")
        for a in profile.achievements:
            lines.append(f"- **{a.title}**" + (f": {a.description}" if a.description else ""))

    # ── Master Profile Summary Context ──────────────────────
    mp = master_data.get("master_profile", {})
    if mp.get("summary_context"):
        lines.append("\n## Master Profile Summary Context")
        lines.append(mp["summary_context"])

    return "\n".join(lines)


def _append_project(lines: list, p, master_data: dict):
    """Append a single project's full context to the output lines."""
    lines.append(f"\n### {p.name}")
    if p.role:
        lines.append(f"**Role:** {p.role}")
    if p.date_range:
        lines.append(f"**Dates:** {p.date_range}")
    if p.tech_stack:
        lines.append(f"**Tech Stack:** {p.tech_stack}")
    if p.url:
        lines.append(f"**URL:** {p.url}")
    if p.description:
        lines.append(f"\n{p.description}")
    if p.bullets:
        lines.append("\n**Bullet Points:**")
        for b in sorted(p.bullets, key=lambda x: x.order):
            lines.append(f"- {b.raw_text}")
    # Inject detailed_context from master_resume if available
    mp = master_data.get("master_profile", {})
    for proj_ctx in mp.get("projects", []):
        if proj_ctx.get("title", "").lower() in p.name.lower() or p.name.lower() in proj_ctx.get("title", "").lower():
            lines.append(f"\n**Deep Context:** {proj_ctx.get('detailed_context', '')}")
