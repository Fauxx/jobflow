from sqlalchemy.orm import Session
from src.models.profile import (
    UserProfile, ProfileSkill, ProfileProject, ProfileExperience,
    ProfileBullet, ProfileEducation, ProfileAchievement, ProfileStatus
)

def get_full_profile(db: Session, user_id: int) -> dict:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        return {}
        
    return {
        "id": profile.id,
        "name": profile.name,
        "title": profile.title,
        "headline": profile.headline,
        "phone": profile.phone,
        "linkedin_url": profile.linkedin_url,
        "github_url": profile.github_url,
        "portfolio_url": profile.portfolio_url,
        "location": profile.location,
        "status": profile.status.value if profile.status else None,
        "career_goals": profile.career_goals,
        "target_roles": profile.target_roles,
        "target_industries": profile.target_industries,
        "location_prefs": profile.location_prefs,
        "personalization_prefs": profile.personalization_prefs,
        "skills": [
            {
                "id": s.id,
                "category": s.category,
                "name": s.name,
                "proficiency": s.proficiency
            } for s in profile.skills
        ],
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "role": p.role,
                "url": p.url,
                "tech_stack": p.tech_stack,
                "date_range": p.date_range,
                "is_highlight": p.is_highlight,
                "order": p.order,
                "bullets": [{"id": b.id, "raw_text": b.raw_text, "order": b.order} for b in p.bullets]
            } for p in profile.projects
        ],
        "experiences": [
            {
                "id": e.id,
                "company": e.company,
                "title": e.title,
                "location": e.location,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "description": e.description,
                "achievements": e.achievements,
                "order": e.order,
                "bullets": [{"id": b.id, "raw_text": b.raw_text, "order": b.order} for b in e.bullets]
            } for e in profile.experiences
        ],
        "education": [
            {
                "id": ed.id,
                "institution": ed.institution,
                "degree": ed.degree,
                "date_str": ed.date_str,
                "location": ed.location
            } for ed in profile.education
        ],
        "achievements": [
            {
                "id": a.id,
                "title": a.title,
                "description": a.description
            } for a in profile.achievements
        ]
    }

def save_full_profile(db: Session, user_id: int, profile_data: dict):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.flush()
        
    profile.name = profile_data.get("name")
    profile.title = profile_data.get("title")
    profile.headline = profile_data.get("headline")
    profile.phone = profile_data.get("phone")
    profile.linkedin_url = profile_data.get("linkedin_url")
    profile.github_url = profile_data.get("github_url")
    profile.portfolio_url = profile_data.get("portfolio_url")
    profile.location = profile_data.get("location")
    
    if "status" in profile_data:
        profile.status = profile_data["status"]
    
    profile.career_goals = profile_data.get("career_goals")
    profile.target_roles = profile_data.get("target_roles")
    profile.target_industries = profile_data.get("target_industries")
    profile.location_prefs = profile_data.get("location_prefs")
    profile.personalization_prefs = profile_data.get("personalization_prefs")
    
    db.query(ProfileSkill).filter(ProfileSkill.profile_id == profile.id).delete()
    db.query(ProfileProject).filter(ProfileProject.profile_id == profile.id).delete()
    db.query(ProfileExperience).filter(ProfileExperience.profile_id == profile.id).delete()
    db.query(ProfileEducation).filter(ProfileEducation.profile_id == profile.id).delete()
    db.query(ProfileAchievement).filter(ProfileAchievement.profile_id == profile.id).delete()
    
    db.flush()
    
    for s_data in profile_data.get("skills", []):
        skill = ProfileSkill(
            profile_id=profile.id,
            category=s_data.get("category"),
            name=s_data.get("name") or s_data.get("items") or "",
            proficiency=s_data.get("proficiency")
        )
        db.add(skill)
        
    for p_data in profile_data.get("projects", []):
        proj = ProfileProject(
            profile_id=profile.id,
            name=p_data.get("name") or p_data.get("title") or "",
            description=p_data.get("description"),
            role=p_data.get("role"),
            url=p_data.get("url"),
            tech_stack=p_data.get("tech_stack"),
            date_range=p_data.get("date_range") or p_data.get("date") or "",
            is_highlight=p_data.get("is_highlight", False),
            order=p_data.get("order", 0)
        )
        db.add(proj)
        db.flush()
        for b_idx, b_data in enumerate(p_data.get("bullets", [])):
            if isinstance(b_data, str):
                text = b_data
            else:
                text = b_data.get("raw_text", "")
            if text:
                db.add(ProfileBullet(project_id=proj.id, raw_text=text, order=b_idx))
                
    for e_data in profile_data.get("experiences", []):
        exp = ProfileExperience(
            profile_id=profile.id,
            company=e_data.get("company") or "",
            title=e_data.get("title") or e_data.get("role") or "",
            location=e_data.get("location"),
            start_date=e_data.get("start_date"),
            end_date=e_data.get("end_date") or e_data.get("date"),
            description=e_data.get("description"),
            achievements=e_data.get("achievements"),
            order=e_data.get("order", 0)
        )
        db.add(exp)
        db.flush()
        for b_idx, b_data in enumerate(e_data.get("bullets", [])):
            if isinstance(b_data, str):
                text = b_data
            else:
                text = b_data.get("raw_text", "")
            if text:
                db.add(ProfileBullet(experience_id=exp.id, raw_text=text, order=b_idx))
                
    for ed_data in profile_data.get("education", []):
        ed = ProfileEducation(
            profile_id=profile.id,
            institution=ed_data.get("institution") or ed_data.get("school") or "",
            degree=ed_data.get("degree") or "",
            date_str=ed_data.get("date_str") or ed_data.get("date"),
            location=ed_data.get("location")
        )
        db.add(ed)
        
    for a_data in profile_data.get("achievements", []):
        ach = ProfileAchievement(
            profile_id=profile.id,
            title=a_data.get("title") or "",
            description=a_data.get("description")
        )
        db.add(ach)
        
    db.commit()
