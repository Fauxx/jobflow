import json
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from src.models.job import Job
from src.services.job_analysis import call_gemini
from urllib.parse import urlparse

class UniversalScraperService:
    @staticmethod
    def extract_text_and_title_from_url(url: str) -> dict:
        """
        Uses Playwright to fully render the page, bypass basic bot checks, 
        and extract the raw visible text + page title.
        """
        from playwright.sync_api import sync_playwright
        import os
        
        # Use persistent profile to reuse cookies and bypass login walls
        profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "playwright_profile"))
        os.makedirs(profile_dir, exist_ok=True)
        
        with sync_playwright() as p:
            # Using persistent context to keep sessions alive
            context = p.firefox.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=True,
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                firefox_user_prefs={
                    "dom.webdriver.enabled": False,
                    "media.peerconnection.enabled": False
                }
            )
            
            # Try to seamlessly inject cookies from the user's actual local browser!
            try:
                import browser_cookie3
                domain_name = urlparse(url).netloc.replace('www.', '')
                
                # .load() has a known bug crashing on NoneType for missing browsers.
                # Safe fallback chain: try Firefox first, then Chrome, etc.
                cj = None
                for browser_fn in [browser_cookie3.firefox, browser_cookie3.chrome, browser_cookie3.edge, browser_cookie3.safari, browser_cookie3.brave]:
                    try:
                        cj = browser_fn(domain_name=domain_name)
                        # We have to consume the iterator to test if it worked without erroring
                        cj_list = list(cj)
                        if len(cj_list) > 0:
                            cj = cj_list
                            break
                    except Exception:
                        continue
                        
                pw_cookies = []
                if cj:
                    for c in cj:
                        if domain_name in c.domain:
                            pw_cookies.append({
                                'name': c.name,
                                'value': c.value,
                                'domain': c.domain,
                                'path': c.path
                            })
                if pw_cookies:
                    context.add_cookies(pw_cookies)
                    print(f"Loaded {len(pw_cookies)} native Firefox cookies for {domain_name}")
            except Exception as e:
                print(f"Could not load native browser cookies: {e}")

            page = context.new_page()
            
            try:
                page.goto(url, timeout=30000)
                # Wait for network idle or a short timeout to let SPAs load
                page.wait_for_timeout(3000)
                
                title = page.title()
                
                # Get the HTML and pass to BeautifulSoup to strip noise
                html_content = page.content()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                for script in soup(["script", "style", "noscript", "meta", "link", "header", "footer"]):
                    script.decompose()
                    
                text = soup.get_text(separator=' ')
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return {
                    "title": title.strip() if title else "Unknown Title",
                    "text": clean_text[:50000] # Increased limit since we bypass AI here
                }
            except Exception as e:
                raise ValueError(f"Playwright failed to fetch webpage: {str(e)}")
            finally:
                context.close()

    @staticmethod
    def import_job(url: str, db: Session) -> Job:
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Check if job already exists
        existing_job = db.query(Job).filter(Job.source_url == url).first()
        if existing_job:
            return existing_job
            
        # 1. Fetch raw text instantly (No AI)
        data = UniversalScraperService.extract_text_and_title_from_url(url)
        raw_text = data["text"]
        page_title = data["title"]
        
        if not raw_text or len(raw_text) < 100:
            raise ValueError("Could not extract enough text from the URL. The page might be heavily blocked.")
            
        # 2. Extract basic info without AI for temporary display
        # We can try to guess the company from the domain or title
        guessed_company = domain.split('.')[0].capitalize()
        
        # 3. Save to Database instantly
        new_job = Job(
            title=page_title, # Temporary title
            company=guessed_company, # Temporary company
            location="Unspecified",
            description="[AI Extraction Pending] Click 'Approve & Tailor' to process this job.",
            raw_scraped_text=raw_text,
            source=domain,
            source_url=url
        )
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        return new_job

    @staticmethod
    def hydrate_job(db: Session, job: Job):
        # Deprecated: Hydration will happen dynamically during the "Approve" phase
        pass
