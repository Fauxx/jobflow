from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.scrapers import provider_registry
from src.schemas.job import CanonicalJob
from src.models.job import Job
from src.services.deduplication import DeduplicationService
from src.core.exceptions import JobflowException

class IngestionService:
    @staticmethod
    def ingest_from_provider(db: Session, provider_name: str, keywords: str, location: str, fetch_details: bool = True) -> List[Dict[str, Any]]:
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
                
            # Optionally fetch full details if missing from discover payload
            if fetch_details and not cj.description:
                try:
                    full_cj = scraper.fetch_job(cj.source_url)
                    # Merge description
                    cj.description = full_cj.description
                    if not cj.company or cj.company == "Unknown":
                        cj.company = full_cj.company
                except Exception as e:
                    print(f"Failed to fetch details for {cj.source_url}: {e}")
            
            # Add to ephemeral list
            ephemeral_jobs.append({
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
    def ingest_all(db: Session, keywords: str, location: str) -> dict:
        results = {"status": "success", "counts": {}, "jobs": []}
        for provider_name in provider_registry.get_all().keys():
            jobs_from_provider = IngestionService.ingest_from_provider(db, provider_name, keywords, location)
            results["counts"][provider_name] = len(jobs_from_provider)
            results["jobs"].extend(jobs_from_provider)
        return results
