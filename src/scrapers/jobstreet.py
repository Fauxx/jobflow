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
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Upgrade-Insecure-Requests': '1', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Cache-Control': 'max-age=0'})
        
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

    def fetch_job(self, url: str):
        import urllib.request, re, json
        from bs4 import BeautifulSoup
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        desc = ""
        title = "Unknown"
        company = "Unknown"
        location = None
        job_id = url.split('/')[-1].split('?')[0]
        
        match = re.search(r'window\.SEEK_REDUX_DATA\s*=\s*(\{.*?\});\n', html)
        if match:
            try:
                data = json.loads(match.group(1))
                job = data.get('jobdetails', {}).get('result', {}).get('job', {})
                if job:
                    raw_content = job.get('content', '')
                    if raw_content:
                        desc = BeautifulSoup(raw_content, 'html.parser').get_text(separator='\n').strip()
                    title = job.get('title', 'Unknown')
                    if job.get('advertiser'):
                        company = job['advertiser'].get('name', 'Unknown')
                    if job.get('location'):
                        location = job['location'].get('name') if isinstance(job['location'], dict) else str(job['location'])
            except Exception as e:
                print(f"Error parsing SEEK_REDUX_DATA: {e}")
                
        if not desc:
            soup = BeautifulSoup(html, 'html.parser')
            desc_div = soup.find(attrs={'data-automation': re.compile('.*description.*', re.I)})
            if desc_div:
                desc = desc_div.get_text(separator='\n').strip()

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
