from typing import List
from .base import BaseScraper
from .registry import provider_registry
from src.schemas.job import CanonicalJob
from src.core.exceptions import PlatformBlockedError

class IndeedScraper(BaseScraper):
    def discover_jobs(self, keywords: str, location: str, **kwargs) -> List[CanonicalJob]:
        raise PlatformBlockedError("Automated Indeed scraping is blocked. Please use manual URL import.")
        
    def fetch_job(self, url: str) -> CanonicalJob:
        raise PlatformBlockedError("Automated Indeed scraping is blocked. Please use manual HTML import.")
        
provider_registry.register("indeed", IndeedScraper)
