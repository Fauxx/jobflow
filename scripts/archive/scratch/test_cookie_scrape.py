import sys, asyncio
sys.path.append('/home/zett/RiderProjects/jobflow')
from src.services.ingestion import UniversalScraperService

async def main():
    print("Initializing scraper...")
    scraper = UniversalScraperService()
    try:
        print("Attempting to scrape LinkedIn...")
        result = await scraper.scrape_job('https://www.linkedin.com/jobs/view/4006155913')
        print("Scrape Result Title:", result.get('title'))
        print("Scrape Result Company:", result.get('company'))
    except Exception as e:
        print("Scrape Error:", e)

asyncio.run(main())
