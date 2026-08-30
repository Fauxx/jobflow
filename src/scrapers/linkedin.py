import urllib.request
import urllib.parse
from typing import List
from bs4 import BeautifulSoup
from datetime import datetime

from .base import BaseScraper
from .registry import provider_registry
from src.schemas.job import CanonicalJob

class LinkedInScraper(BaseScraper):
    def discover_jobs(self, keywords: str, location: str, **kwargs) -> List[CanonicalJob]:
        encoded_kw = urllib.parse.quote(keywords)
        encoded_loc = urllib.parse.quote(location)
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={encoded_kw}&location={encoded_loc}&start=0"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
        except Exception as e:
            print(f"LinkedIn Search error: {e}")
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        for card in soup.find_all('div', class_='base-card'):
            link_tag = card.find('a', class_='base-card__full-link')
            if not link_tag:
                continue
                
            source_url = link_tag.get('href', '').split('?')[0]
            job_id_match = source_url.split('-')[-1]
            try:
                job_id = "".join(filter(str.isdigit, job_id_match))
                if not job_id:
                    continue
            except:
                continue
                
            title_tag = card.find('h3', class_='base-search-card__title')
            title = title_tag.get_text(strip=True) if title_tag else "Unknown"
            
            comp_tag = card.find('h4', class_='base-search-card__subtitle')
            company = comp_tag.get_text(strip=True) if comp_tag else "Unknown"
            
            loc_tag = card.find('span', class_='job-search-card__location')
            location_text = loc_tag.get_text(strip=True) if loc_tag else None
            
            job = CanonicalJob(
                external_job_id=job_id,
                source="linkedin",
                source_url=source_url,
                title=title,
                company=company,
                location=location_text,
                description="" # Must be fetched
            )
            jobs.append(job)
            
        return jobs

    def fetch_job(self, url: str) -> CanonicalJob:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        soup = BeautifulSoup(html, 'html.parser')
        
        title_tag = soup.find('h1', class_='top-card-layout__title')
        title = title_tag.get_text(strip=True) if title_tag else "Unknown"
        
        comp_tag = soup.find('a', class_='topcard__org-name-link')
        company = comp_tag.get_text(strip=True) if comp_tag else "Unknown"
        
        loc_tag = soup.find('span', class_='topcard__flavor--bullet')
        location = loc_tag.get_text(strip=True) if loc_tag else None
        
        desc_div = soup.find('div', class_='show-more-less-html__markup')
        desc = desc_div.decode_contents() if desc_div else ''
        
        job_id = url.split('/')[-1].split('?')[0]
        
        # Criteria (employment type, seniority)
        criteria = soup.find_all('span', class_='description__job-criteria-text')
        emp_type = criteria[1].get_text(strip=True) if len(criteria) > 1 else None
        seniority = criteria[0].get_text(strip=True) if len(criteria) > 0 else None
        
        return CanonicalJob(
            external_job_id=job_id,
            source="linkedin",
            source_url=url,
            title=title,
            company=company,
            location=location,
            description=desc,
            employment_type=emp_type,
            experience_level=seniority
        )

provider_registry.register("linkedin", LinkedInScraper)
