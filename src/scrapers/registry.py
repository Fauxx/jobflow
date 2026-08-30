from typing import Dict, Type
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
