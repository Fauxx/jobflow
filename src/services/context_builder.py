from sqlalchemy.orm import Session
from sqlalchemy import orm
from src.models.profile import UserProfile, ProfileProject, ProfileExperience
from src.models.job import Job

def build_context(db: Session, job: Job, user_id: int) -> str:
    profile = db.query(UserProfile).options(
        orm.selectinload(UserProfile.skills),
        orm.selectinload(UserProfile.projects).selectinload(ProfileProject.bullets),
        orm.selectinload(UserProfile.experiences).selectinload(ProfileExperience.bullets),
        orm.selectinload(UserProfile.education)
    ).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        return "Candidate Profile Not Found"
    
    lines = []
    lines.append("# Candidate Context")
    if profile.name:
        lines.append(f"Name: {profile.name}")
    if profile.title:
        lines.append(f"Title: {profile.title}")
    if profile.headline:
        lines.append(f"Headline: {profile.headline}")
        
    if profile.career_goals:
        lines.append("\n## Career Goals")
        lines.append(profile.career_goals)
    
    highlight_projects = [p for p in profile.projects if p.is_highlight]
    other_projects = [p for p in profile.projects if not p.is_highlight]
    
    if highlight_projects:
        lines.append("\n## Highlight Projects")
        for p in highlight_projects:
            lines.append(f"### {p.name}")
            if p.role: lines.append(f"Role: {p.role}")
            if p.date_range: lines.append(f"Dates: {p.date_range}")
            if p.tech_stack: lines.append(f"Tech Stack: {p.tech_stack}")
            if p.description: lines.append(p.description)
            for b in p.bullets:
                lines.append(f"- {b.raw_text}")
                
    if profile.experiences:
        lines.append("\n## Experiences")
        for e in profile.experiences:
            lines.append(f"### {e.title} at {e.company}")
            if e.start_date or e.end_date:
                lines.append(f"Dates: {e.start_date} - {e.end_date}")
            if e.description: lines.append(e.description)
            for b in e.bullets:
                lines.append(f"- {b.raw_text}")
                
    if other_projects:
        lines.append("\n## Other Projects")
        for p in other_projects:
            lines.append(f"### {p.name}")
            if p.tech_stack: lines.append(f"Tech Stack: {p.tech_stack}")
            for b in p.bullets:
                lines.append(f"- {b.raw_text}")
                
    if profile.skills:
        lines.append("\n## Skills")
        for s in profile.skills:
            lines.append(f"- {s.name} ({s.proficiency})")
            
    if profile.education:
        lines.append("\n## Education")
        for ed in profile.education:
            lines.append(f"- {ed.degree} at {ed.institution} ({ed.date_str})")
            
    return "\n".join(lines)
