from src.core.database import SessionLocal
from src.services.ingestion import IngestionService
from src.models.job import Job

def test():
    db = SessionLocal()
    print("Testing Kalibrr ingestion for 'Python Developer'...")
    try:
        count = IngestionService.ingest_from_provider(db, "kalibrr", "Python Developer", "Philippines")
        print(f"Ingested {count} jobs from Kalibrr.")
        
        jobs = db.query(Job).all()
        print(f"Total jobs in DB: {len(jobs)}")
        if jobs:
            print(f"First job: {jobs[0].title} at {jobs[0].company} ({jobs[0].source_url})")
    finally:
        db.close()

if __name__ == "__main__":
    test()
