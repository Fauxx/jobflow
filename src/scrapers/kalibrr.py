import json
import urllib.request
import re
from typing import List, Optional
from datetime import datetime
from dateutil.parser import parse as parse_date
from .base import BaseScraper
from .registry import provider_registry
from src.schemas.job import CanonicalJob

class KalibrrScraper(BaseScraper):
    def discover_jobs(self, keywords: str, location: str, **kwargs) -> List[CanonicalJob]:
        # URL encode keywords and location
        import urllib.parse
        encoded_kw = urllib.parse.quote(keywords.replace(' ', '-'))
        encoded_loc = urllib.parse.quote(location)
        
        # e.g., https://www.kalibrr.com/home/te/devops-engineer/co/Philippines
        url = f"https://www.kalibrr.com/home/te/{encoded_kw}/co/{encoded_loc}"
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
        except Exception as e:
            print(f"Error fetching Kalibrr: {e}")
            return []
            
        return self._extract_jobs_from_html(html)

    def fetch_job(self, url: str) -> CanonicalJob:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        jobs = self._extract_jobs_from_html(html)
        if jobs:
            return jobs[0]
        raise ValueError(f"Could not extract job from {url}")

    def _extract_jobs_from_html(self, html: str) -> List[CanonicalJob]:
        next_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
        if not next_match:
            return []
            
        try:
            data = json.loads(next_match.group(1))
        except json.JSONDecodeError:
            return []
            
        page_props = data.get('props', {}).get('pageProps', {})
        
        # Determine if we are on a search page (jobs list) or detail page (single job)
        raw_jobs = []
        if 'jobs' in page_props:
            raw_jobs = page_props['jobs']
        elif 'job' in page_props:
            raw_jobs = [page_props['job']]
            
        canonical_jobs = []
        for j in raw_jobs:
            # Parse date
            date_posted = None
            if j.get('activationDate'):
                try:
                    date_posted = parse_date(j.get('activationDate'))
                except:
                    pass
                    
            # Workplace type
            workplace = None
            if j.get('isWorkFromHome'):
                workplace = "Remote"
            elif j.get('isHybrid'):
                workplace = "Hybrid"
            else:
                workplace = "On-site"
                
            # Salary
            salary_display = None
            if j.get('baseSalary') and j.get('maximumSalary'):
                curr = j.get('salaryCurrency', 'PHP')
                interval = j.get('salaryInterval', 'month')
                salary_display = f"{curr} {j.get('baseSalary')} - {j.get('maximumSalary')} / {interval}"
                
            # Company
            company_name = "Unknown"
            if isinstance(j.get('company'), dict):
                company_name = j.get('company').get('name', 'Unknown')
            elif isinstance(j.get('companyInfo'), dict):
                company_name = j.get('companyInfo').get('name', 'Unknown')
                
            # Location
            loc = None
            if isinstance(j.get('googleLocation'), dict):
                loc = j.get('googleLocation').get('formattedAddress')
                if not loc and 'addressComponents' in j.get('googleLocation'):
                    ac = j.get('googleLocation')['addressComponents']
                    loc = f"{ac.get('city', '')}, {ac.get('country', '')}".strip(', ')
            
            job_id = str(j.get('id'))
            
            # Construct URL if missing
            url = j.get('applyRedirectUrl')
            if not url:
                company_code = j.get('company', {}).get('code', 'unknown')
                slug = j.get('slug', 'job')
                url = f"https://www.kalibrr.com/c/{company_code}/jobs/{job_id}/{slug}"

            job = CanonicalJob(
                external_job_id=job_id,
                source="kalibrr",
                source_url=url,
                title=j.get('name', 'Unknown Title'),
                company=company_name,
                location=loc,
                description=j.get('description', ''),
                date_posted=date_posted,
                employment_type=j.get('tenure'),
                salary_display=salary_display,
                workplace_type=workplace,
                experience_level=str(j.get('workExperience')) if j.get('workExperience') else None
            )
            canonical_jobs.append(job)
            
        return canonical_jobs

provider_registry.register("kalibrr", KalibrrScraper)
