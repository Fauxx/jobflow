import os

# Schemas
with open('src/schemas/job.py', 'w') as f:
    f.write("""from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CanonicalJob(BaseModel):
    external_job_id: str
    source: str
    source_url: str
    title: str
    company: str
    location: Optional[str] = None
    description: str
    date_posted: Optional[datetime] = None
    employment_type: Optional[str] = None
    salary_display: Optional[str] = None
    workplace_type: Optional[str] = None
    experience_level: Optional[str] = None
""")

with open('src/scrapers/__init__.py', 'w') as f:
    f.write("""from .registry import provider_registry

# Register adapters
import src.scrapers.linkedin
import src.scrapers.jobstreet
import src.scrapers.kalibrr
import src.scrapers.indeed
""")

with open('src/scrapers/base.py', 'w') as f:
    f.write("""from abc import ABC, abstractmethod
from typing import List
from src.schemas.job import CanonicalJob

class BaseScraper(ABC):
    @abstractmethod
    def discover_jobs(self, keywords: str, location: str, **kwargs) -> List[CanonicalJob]:
        pass
        
    @abstractmethod
    def fetch_job(self, url: str) -> CanonicalJob:
        pass
""")

with open('src/scrapers/registry.py', 'w') as f:
    f.write("""from typing import Dict, Type
from .base import BaseScraper

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, Type[BaseScraper]] = {}
        
    def register(self, name: str, scraper_class: Type[BaseScraper]):
        self._providers[name] = scraper_class
        
    def get(self, name: str) -> Type[BaseScraper]:
        if name not in self._providers:
            raise ValueError(f"Provider {name} not found")
        return self._providers[name]
        
    def get_all(self) -> Dict[str, Type[BaseScraper]]:
        return self._providers

provider_registry = ProviderRegistry()
""")

with open('src/scrapers/linkedin.py', 'w') as f:
    f.write("""from .base import BaseScraper
from .registry import provider_registry
from src.schemas.job import CanonicalJob
from typing import List

class LinkedInScraper(BaseScraper):
    def discover_jobs(self, keywords: str, location: str, **kwargs) -> List[CanonicalJob]:
        # TODO: Implement guest API scraping
        return []
        
    def fetch_job(self, url: str) -> CanonicalJob:
        # TODO: Implement detail fetch
        pass

provider_registry.register("linkedin", LinkedInScraper)
""")

with open('src/scrapers/jobstreet.py', 'w') as f:
    f.write("""from .base import BaseScraper
from .registry import provider_registry
from src.schemas.job import CanonicalJob
from typing import List

class JobStreetScraper(BaseScraper):
    def discover_jobs(self, keywords: str, location: str, **kwargs) -> List[CanonicalJob]:
        # TODO: Implement SEEK v5 API
        return []
        
    def fetch_job(self, url: str) -> CanonicalJob:
        pass

provider_registry.register("jobstreet", JobStreetScraper)
""")

with open('src/scrapers/kalibrr.py', 'w') as f:
    f.write("""from .base import BaseScraper
from .registry import provider_registry
from src.schemas.job import CanonicalJob
from typing import List

class KalibrrScraper(BaseScraper):
    def discover_jobs(self, keywords: str, location: str, **kwargs) -> List[CanonicalJob]:
        # TODO: Implement Next.js SSR parsing
        return []
        
    def fetch_job(self, url: str) -> CanonicalJob:
        pass

provider_registry.register("kalibrr", KalibrrScraper)
""")

with open('src/scrapers/indeed.py', 'w') as f:
    f.write("""from .base import BaseScraper
from .registry import provider_registry
from src.schemas.job import CanonicalJob
from src.core.exceptions import PlatformBlockedError
from typing import List

class IndeedScraper(BaseScraper):
    def discover_jobs(self, keywords: str, location: str, **kwargs) -> List[CanonicalJob]:
        raise PlatformBlockedError("Automated Indeed scraping is blocked. Use manual URL import.")
        
    def fetch_job(self, url: str) -> CanonicalJob:
        raise PlatformBlockedError("Automated Indeed scraping is blocked. Provide HTML manually.")

provider_registry.register("indeed", IndeedScraper)
""")
