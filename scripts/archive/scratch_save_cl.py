from pydantic import BaseModel
class CoverLetterSaveRequest(BaseModel):
    content: str

@router.put("/{job_id}/cover-letter")
async def save_cover_letter(job_id: int, req: CoverLetterSaveRequest, db: Session = Depends(get_db)):
    user = get_current_user(db)
    app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    app.cover_letter = req.content
    db.commit()
    return {"status": "ok"}
