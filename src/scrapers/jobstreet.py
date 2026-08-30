import urllib.request
import json
import urllib.parse
from typing import List
from datetime import datetime
from dateutil.parser import parse as parse_date
from bs4 import BeautifulSoup

from .base import BaseScraper
from .registry import provider_registry
from src.schemas.job import CanonicalJob
from src.core.exceptions import ParsingError

class JobStreetScraper(BaseScraper):
    def discover_jobs(self, keywords: str, location: str, **kwargs) -> List[CanonicalJob]:
        encoded_kw = urllib.parse.quote(keywords)
        encoded_loc = urllib.parse.quote(location)
        url = f"https://jobsearch-api.cloud.seek.com.au/v5/search?keywords={encoded_kw}&where={encoded_loc}&pageSize=30"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"JobStreet API error: {e}")
            return []
            
        jobs = []
        for j in data.get('data', []):
            job_id = str(j.get('id'))
            source_url = f"https://www.jobstreet.com.ph/job/{job_id}"
            
            loc = None
            if j.get('locations'):
                loc = j['locations'][0].get('label')
                
            workplace = None
            if j.get('workArrangements') and 'displayText' in j['workArrangements']:
                workplace = j['workArrangements']['displayText']
                
            employment_type = None
            if j.get('workTypes'):
                employment_type = j['workTypes'][0]
                
            date_posted = None
            if j.get('listingDate'):
                try:
                    date_posted = parse_date(j['listingDate'])
                except:
                    pass
            
            company = "Unknown"
            if j.get('companyName'):
                company = j['companyName']
            elif j.get('employer'):
                company = j['employer'].get('name', 'Unknown')
                
            job = CanonicalJob(
                external_job_id=job_id,
                source="jobstreet",
                source_url=source_url,
                title=j.get('title', 'Unknown'),
                company=company,
                location=loc,
                description=j.get('teaser', ''), # Temporary until fetch_job
                date_posted=date_posted,
                employment_type=employment_type,
                salary_display=j.get('salaryLabel'),
                workplace_type=workplace,
                experience_level=None
            )
            jobs.append(job)
            
        return jobs

    def fetch_job(self, url: str) -> CanonicalJob:
        # Extract full description from HTML detail page
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        soup = BeautifulSoup(html, 'html.parser')
        desc_div = soup.find('div', attrs={'data-automation': 'jobAdDetails'})
        desc = desc_div.decode_contents() if desc_div else ''
        
        # We need a basic canonical job return here. Normally we'd merge this with search data.
        # For simplicity, returning a partial job with just the description and URL.
        # The ingestion service should handle merging.
        
        # Attempt to parse title and company if accessed directly
        title_tag = soup.find(attrs={'data-automation': 'job-detail-title'})
        title = title_tag.get_text(strip=True) if title_tag else "Unknown"
        
        comp_tag = soup.find(attrs={'data-automation': 'advertiser-name'})
        company = comp_tag.get_text(strip=True) if comp_tag else "Unknown"
        
        loc_tag = soup.find(attrs={'data-automation': 'job-detail-location'})
        location = loc_tag.get_text(strip=True) if loc_tag else None
        
        job_id = url.split('/')[-1].split('?')[0]
        
        return CanonicalJob(
            external_job_id=job_id,
            source="jobstreet",
            source_url=url,
            title=title,
            company=company,
            location=location,
            description=desc,
        )

provider_registry.register("jobstreet", JobStreetScraper)
