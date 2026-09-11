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
        "headline": profile.headline,
        "summary": profile.summary,
        "phone": profile.phone,
        "linkedin_url": profile.linkedin_url,
        "github_url": profile.github_url,
        "portfolio_url": profile.portfolio_url,
        "location": profile.location,
        "skills": [
            {
                "id": s.id,
                "category": s.category,
                "name": s.items
            } for s in profile.skills
        ],
        "projects": [
            {
                "id": p.id,
                "name": p.title,
                "role": p.role,
                "date_range": p.date_range,
                "detailed_context": p.detailed_context,
                "order": p.order,
                "bullets": [{"id": b.id, "text": b.text, "order": b.order} for b in p.bullets]
            } for p in profile.projects
        ],
        "experiences": [
            {
                "id": e.id,
                "company": e.company,
                "title": e.role,
                "location": e.location,
                "date_range": e.date_range,
                "detailed_context": e.detailed_context,
                "order": e.order,
                "bullets": [{"id": b.id, "text": b.text, "order": b.order} for b in e.bullets]
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
        ]
    }

def save_full_profile(db: Session, user_id: int, profile_data: dict):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.flush()
        
    profile.name = profile_data.get("name")
    profile.headline = profile_data.get("headline") or profile_data.get("title")
    profile.summary = profile_data.get("summary")
    profile.phone = profile_data.get("phone")
    profile.linkedin_url = profile_data.get("linkedin_url")
    profile.github_url = profile_data.get("github_url")
    profile.portfolio_url = profile_data.get("portfolio_url")
    profile.location = profile_data.get("location")
    

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
            items=s_data.get("items") or s_data.get("name") or "",
            
        )
        db.add(skill)
        
    for p_data in profile_data.get("projects", []):
        proj = ProfileProject(
            profile_id=profile.id,
            title=p_data.get("title") or p_data.get("name") or "",
            detailed_context=p_data.get("description") or p_data.get("detailed_context"),
            role=p_data.get("role"),
            date_range=p_data.get("date_range") or p_data.get("date") or "",
            order=p_data.get("order", 0)
        )
        db.add(proj)
        db.flush()
        for b_idx, b_data in enumerate(p_data.get("bullets", [])):
            if isinstance(b_data, str):
                text = b_data
            else:
                text = b_data.get("text", "")
            if text:
                import uuid
                db.add(ProfileBullet(id=str(uuid.uuid4()), project_id=proj.id, text=text, order=b_idx))
                
    for e_data in profile_data.get("experiences", []):
        exp = ProfileExperience(
            profile_id=profile.id,
            company=e_data.get("company") or "",
            role=e_data.get("role") or e_data.get("title") or "",
            location=e_data.get("location"),
            date_range=e_data.get("date_range") or e_data.get("start_date"),
            
            detailed_context=e_data.get("description") or e_data.get("detailed_context"),
            
            order=e_data.get("order", 0)
        )
        db.add(exp)
        db.flush()
        for b_idx, b_data in enumerate(e_data.get("bullets", [])):
            if isinstance(b_data, str):
                text = b_data
            else:
                text = b_data.get("text", "")
            if text:
                db.add(ProfileBullet(id=str(uuid.uuid4()), experience_id=exp.id, text=text, order=b_idx))
                
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
