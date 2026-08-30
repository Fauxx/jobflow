from abc import ABC, abstractmethod
from typing import List
from src.schemas.job import CanonicalJob

class BaseScraper(ABC):
    @abstractmethod
    def discover_jobs(self, keywords: str, location: str, **kwargs) -> List[CanonicalJob]:
        pass
        
    @abstractmethod
    def fetch_job(self, url: str) -> CanonicalJob:
        pass
