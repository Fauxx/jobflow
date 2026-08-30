from sqlalchemy.orm import Session
from src.models.job import Job

class DeduplicationService:
    @staticmethod
    def is_duplicate(db: Session, source: str, external_job_id: str = None, source_url: str = None) -> bool:
        if external_job_id:
            exists = db.query(Job.id).filter(Job.source == source, Job.external_job_id == external_job_id).first()
            if exists: return True
            
        if source_url:
            exists = db.query(Job.id).filter(Job.source_url == source_url).first()
            if exists: return True
            
        return False
