from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.scrapers import provider_registry
from src.schemas.job import CanonicalJob
from src.models.job import Job
from src.services.deduplication import DeduplicationService
from src.core.exceptions import JobflowException
from datetime import datetime, timedelta, timezone

class IngestionService:
    @staticmethod
    def ingest_from_provider(db: Session, provider_name: str, keywords: str, location: str, fetch_details: bool = False) -> List[Dict[str, Any]]:
        scraper_class = provider_registry.get(provider_name)
        scraper = scraper_class()
        
        try:
            jobs = scraper.discover_jobs(keywords=keywords, location=location)
        except JobflowException as e:
            print(f"Skipping {provider_name}: {e}")
            return []
            
        ephemeral_jobs = []
        for cj in jobs:
            # Check duplicates (if it's in the DB, skip it)
            if DeduplicationService.is_duplicate(db, cj.source, cj.external_job_id, cj.source_url):
                continue
                

            
            # Add to ephemeral list
            
            # Save to database immediately so it gets an ID
            new_job = Job(
                external_job_id=cj.external_job_id,
                source=cj.source,
                source_url=cj.source_url,
                title=cj.title,
                company=cj.company,
                location=cj.location,
                description=cj.description,
                date_posted=cj.date_posted,
                employment_type=cj.employment_type,
                salary_display=cj.salary_display,
                workplace_type=cj.workplace_type,
                experience_level=cj.experience_level
            )
            db.add(new_job)
            db.commit()
            db.refresh(new_job)
            
            # Also create a NEW application status for the current user (if user context was available, 
            # but we can do that in dashboard.py instead by fetching jobs with no application)
            
            ephemeral_jobs.append({
                "id": new_job.id,
                "external_job_id": cj.external_job_id,
                "source": cj.source,
                "source_url": cj.source_url,
                "title": cj.title,
                "company": cj.company,
                "location": cj.location,
                "description": cj.description,
                "date_posted": cj.date_posted.isoformat() if cj.date_posted else None,
                "employment_type": cj.employment_type,
                "salary_display": cj.salary_display,
                "workplace_type": cj.workplace_type,
                "experience_level": cj.experience_level
            })
            
        return ephemeral_jobs
        

    @staticmethod
    def hydrate_job(db: Session, job: Job) -> Job:
        """Just-In-Time (JIT) hydration for full job descriptions."""
        if job.description and len(job.description) > 1500:
            return job
            
        scraper_class = provider_registry.get(job.source)
        if not scraper_class:
            return job
            
        scraper = scraper_class()
        try:
            full_cj = scraper.fetch_job(job.source_url)
            if full_cj and full_cj.description:
                job.description = full_cj.description
            if full_cj and full_cj.company and full_cj.company != "Unknown":
                job.company = full_cj.company
                
            db.commit()
            db.refresh(job)
        except Exception as e:
            print(f"Hydration failed for job {job.id} from {job.source}: {e}")
            
        return job

    @staticmethod
    def ingest_all(db: Session, keywords: str, location: str) -> dict:
        results = {"status": "success", "counts": {}, "jobs": []}
        for provider_name in provider_registry.get_all().keys():
            jobs_from_provider = IngestionService.ingest_from_provider(db, provider_name, keywords, location)
            results["counts"][provider_name] = len(jobs_from_provider)
            results["jobs"].extend(jobs_from_provider)
        return results
