import os
import sqlite3
import urllib.parse
import threading
from playwright.sync_api import sync_playwright
from src.config import DB_PATH, SERPAPI_API_KEY

# Global thread lock to prevent profile directory collisions
profile_lock = threading.Lock()

def scrape_jobs(keywords=None, location="Philippines", date_range="week", platforms=None, use_auth=True):
    if SERPAPI_API_KEY:
        print("Using configured SerpAPI for job scraping...")
        # Clear out all unprocessed "NEW" listings to keep leads fresh per run
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs WHERE status = 'NEW'")
        conn.commit()
        conn.close()
        
        if not keywords:
            keywords = ["new grad devops", "junior devops"]
        return scrape_serpapi(keywords, location, date_range)
        
    with profile_lock:
        return _scrape_jobs_impl(keywords, location, date_range, platforms, use_auth)

def _scrape_jobs_impl(keywords=None, location="Philippines", date_range="week", platforms=None, use_auth=True):
    """
    Scrapes jobs directly from JobStreet and Indeed PH using a Playwright browser context.
    Falls back to mock data if the scraper fails.
    """
    if not keywords:
        keywords = ["new grad devops", "junior devops"]
    if not platforms:
        platforms = ["linkedin", "indeed", "jobstreet"]

    # Clear out all unprocessed "NEW" listings to keep leads fresh per run
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE status = 'NEW'")
    conn.commit()
    conn.close()
    print("Cleared old unprocessed 'NEW' job listings from database.")

    profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "playwright_profile"))
    
    # Check if user has authenticated first if using auth
    has_auth_profile = os.path.exists(profile_dir) and os.listdir(profile_dir)
    if use_auth and not has_auth_profile:
        print("Playwright profile directory is empty. Falling back to unauthenticated public search...")
        use_auth = False

    print(f"Starting browser scraper (Authenticated: {use_auth})...")
    new_jobs_count = 0

    # Map date range to Indeed's fromage parameter
    fromage_map = {"day": "1", "week": "3", "month": "7"}
    fromage = fromage_map.get(date_range, "3")

    with sync_playwright() as p:
        try:
            browser = None
            if use_auth:
                # Open browser in headless mode using saved profile session
                context = p.firefox.launch_persistent_context(
                    user_data_dir=profile_dir,
                    headless=True,
                    viewport={"width": 1280, "height": 800},
                    firefox_user_prefs={
                        "dom.webdriver.enabled": False,
                        "media.peerconnection.enabled": False
                    }
                )
                page = context.new_page()
            else:
                # Launch a clean, incognito Firefox session
                browser = p.firefox.launch(
                    headless=True,
                    firefox_user_prefs={
                        "dom.webdriver.enabled": False,
                        "media.peerconnection.enabled": False
                    }
                )
                context = browser.new_context(viewport={"width": 1280, "height": 800})
                page = context.new_page()

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # -------------------------------------------------------------
            # SCRAPE LINKEDIN (Authenticated search)
            # -------------------------------------------------------------
            if "linkedin" in platforms:
                for kw in keywords:
                    query_esc = urllib.parse.quote_plus(kw)
                    loc_esc = urllib.parse.quote_plus(location)
                    url = f"https://www.linkedin.com/jobs/search/?keywords={query_esc}&location={loc_esc}"
                    
                    print(f"Navigating LinkedIn: {url}")
                    try:
                        page.goto(url, timeout=45000)
                        page.wait_for_timeout(3500)
                        
                        # Locate LinkedIn job links
                        cards = page.query_selector_all('a.job-card-list__title, .job-card-list__title')
                        print(f"Found {len(cards)} job cards on LinkedIn.")
                        
                        for card in cards[:6]:  # Limit to top 6
                            try:
                                title = card.inner_text().strip()
                                link = card.get_attribute("href")
                                if link and "?" in link:
                                    link = link.split("?")[0]
                                    
                                card.click()
                                page.wait_for_timeout(2500)
                                
                                # Extract details
                                comp_elem = page.query_selector('.jobs-unified-top-card__company-name, .job-card-container__company-name')
                                company = comp_elem.inner_text().strip() if comp_elem else "Unknown Company"
                                
                                loc_elem = page.query_selector('.jobs-unified-top-card__bullet, .job-card-container__metadata-item')
                                loc = loc_elem.inner_text().strip() if loc_elem else "Philippines"
                                
                                desc_elem = page.query_selector('#job-details, .jobs-description-content__text, .jobs-box__html-content')
                                description = desc_elem.inner_text().strip() if desc_elem else "See posting details on platform."
                                
                                # Extract date posted
                                date_elem = page.query_selector('.jobs-unified-top-card__posted-date, time')
                                posted_time = date_elem.inner_text().strip() if date_elem else "Recently"
                                
                                cursor.execute("SELECT id FROM jobs WHERE title = ? AND company = ?", (title, company))
                                if not cursor.fetchone():
                                    cursor.execute("""
                                        INSERT INTO jobs (title, company, location, description, description_url, contact_email, source, status, posted_time)
                                        VALUES (?, ?, ?, ?, ?, 'recruitment@example.com', 'LinkedIn', 'NEW', ?)
                                    """, (title, company, loc, description, link, posted_time))
                                    new_jobs_count += 1
                            except Exception as card_err:
                                print(f"Error parsing LinkedIn card: {card_err}")
                                continue
                    except Exception as page_err:
                        print(f"LinkedIn page navigation failed: {page_err}")
                        continue

            # -------------------------------------------------------------
            # SCRAPE INDEED PH
            # -------------------------------------------------------------
            if "indeed" in platforms:
                for kw in keywords:
                    query_esc = urllib.parse.quote_plus(kw)
                    loc_esc = urllib.parse.quote_plus(location)
                    url = f"https://ph.indeed.com/jobs?q={query_esc}&l={loc_esc}&fromage={fromage}"
                    
                    print(f"Navigating Indeed: {url}")
                    page.goto(url, timeout=40000)
                    page.wait_for_timeout(3000) # Wait to resolve dynamic JS

                    # Locate Indeed job cards
                    cards = page.query_selector_all("a.jcs-JobTitle")
                    print(f"Found {len(cards)} job cards on Indeed page.")
                    
                    for card in cards[:8]:  # Limit to top 8 results per keyword
                        try:
                            title = card.inner_text().strip()
                            link = card.get_attribute("href")
                            if link and link.startswith("/"):
                                link = "https://ph.indeed.com" + link

                            # Click card to load description panel on the right
                            card.click()
                            page.wait_for_timeout(2000)

                            # Extract company and description details
                            company_elem = page.query_selector('[data-testid="inlineHeader-companyName"]')
                            company = company_elem.inner_text().strip() if company_elem else "Unknown Company"
                            
                            loc_elem = page.query_selector('[data-testid="inlineHeader-companyLocation"]')
                            loc = loc_elem.inner_text().strip() if loc_elem else "Philippines"

                            desc_elem = page.query_selector("#jobDescriptionText")
                            description = desc_elem.inner_text().strip() if desc_elem else "See posting details on platform."

                            # Extract date posted
                            parent_beacon = card.locator("xpath=ancestor::div[contains(@class, 'job_seen_beacon')]")
                            date_elem = parent_beacon.locator("span.date") if parent_beacon else None
                            posted_time = "Recently"
                            if date_elem and date_elem.count() > 0:
                                posted_time = date_elem.first.inner_text().strip()
                                if "Posted" in posted_time:
                                    posted_time = posted_time.replace("Posted", "").strip()

                            # Check duplicate
                            cursor.execute("SELECT id FROM jobs WHERE title = ? AND company = ?", (title, company))
                            if not cursor.fetchone():
                                cursor.execute("""
                                    INSERT INTO jobs (title, company, location, description, description_url, contact_email, source, status, posted_time)
                                    VALUES (?, ?, ?, ?, ?, 'recruitment@example.com', 'Indeed', 'NEW', ?)
                                """, (title, company, loc, description, link, posted_time))
                                new_jobs_count += 1
                        except Exception as e:
                            print(f"Error parsing Indeed card: {e}")
                            continue

            # -------------------------------------------------------------
            # SCRAPE JOBSTREET PH
            # -------------------------------------------------------------
            if "jobstreet" in platforms:
                for kw in keywords:
                    query_esc = urllib.parse.quote_plus(kw)
                    # JobStreet search format: /en/job-search/devops-jobs/
                    url = f"https://www.jobstreet.com.ph/en/job-search/{query_esc}-jobs/"
                    
                    print(f"Navigating JobStreet: {url}")
                    page.goto(url, timeout=40000)
                    page.wait_for_timeout(3000)

                    # Locate job links/headers
                    cards = page.query_selector_all('a[data-automation="jobTitle"]')
                    print(f"Found {len(cards)} job cards on JobStreet.")

                    for card in cards[:8]:
                        try:
                            title = card.inner_text().strip()
                            link = card.get_attribute("href")
                            if link and link.startswith("/"):
                                link = "https://www.jobstreet.com.ph" + link

                            # Click to open/view description or navigate
                            # For JobStreet, we can navigate directly to the job link to parse the full description
                            detail_page = context.new_page()
                            detail_page.goto(link, timeout=25000)
                            detail_page.wait_for_timeout(2000)

                            # Extract company details with fallbacks
                            comp_elem = detail_page.query_selector('[data-automation="advertiser-name"]')
                            if not comp_elem:
                                comp_elem = detail_page.query_selector('span[class*="advertiser"]')
                            company = comp_elem.inner_text().strip() if comp_elem else "Unknown Company"

                            # Extract location with fallbacks
                            loc_elem = detail_page.query_selector('[data-automation="job-detail-location"]')
                            if not loc_elem:
                                loc_elem = detail_page.query_selector('span[class*="location"]')
                            loc = loc_elem.inner_text().strip() if loc_elem else "Philippines"

                            # Extract job description with fallbacks
                            desc_elem = detail_page.query_selector('[data-automation="jobAdDetails"]')
                            if not desc_elem:
                                desc_elem = detail_page.query_selector('[data-automation="jobDescription"]')
                            if not desc_elem:
                                desc_elem = detail_page.query_selector('[data-automation="job-details"]')
                            if not desc_elem:
                                desc_elem = detail_page.query_selector('.job-details, .jobDescription')
                            if not desc_elem:
                                desc_elem = detail_page.query_selector('div[class*="jobDescription"]')
                            if not desc_elem:
                                desc_elem = detail_page.query_selector('div[class*="jobDetail"]')
                            description = desc_elem.inner_text().strip() if desc_elem else "See posting details on platform."

                            # Extract date posted
                            date_elem = detail_page.query_selector('span[data-automation="jobListingDate"]')
                            if not date_elem:
                                date_elem = detail_page.query_selector('span:has-text("Posted"), span:has-text("ago")')
                            posted_time = date_elem.inner_text().strip() if date_elem else "Recently"
                            if "Posted" in posted_time:
                                posted_time = posted_time.replace("Posted", "").strip()

                            detail_page.close()

                            cursor.execute("SELECT id FROM jobs WHERE title = ? AND company = ?", (title, company))
                            if not cursor.fetchone():
                                cursor.execute("""
                                    INSERT INTO jobs (title, company, location, description, description_url, contact_email, source, status, posted_time)
                                    VALUES (?, ?, ?, ?, ?, 'recruitment@example.com', 'JobStreet', 'NEW', ?)
                                """, (title, company, loc, description, link, posted_time))
                                new_jobs_count += 1
                        except Exception as e:
                            print(f"Error parsing JobStreet card: {e}")
                            continue

            conn.commit()
            conn.close()
            context.close()
            if browser:
                browser.close()
        except Exception as e:
            print(f"Browser scraping hit an error: {e}")
    print(f"Scraping completed. Added {new_jobs_count} new postings.")
    return new_jobs_count

def check_platform_auth(platform):
    with profile_lock:
        return _check_platform_auth_impl(platform)

def _check_platform_auth_impl(platform):
    """
    Launches a quick headless session and checks if we are logged in to the target platform.
    Returns: CONNECTED, EXPIRED, or DISCONNECTED.
    """
    profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "playwright_profile"))
    if not os.path.exists(profile_dir) or not os.listdir(profile_dir):
        return "DISCONNECTED"

    with sync_playwright() as p:
        try:
            context = p.firefox.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=True,
                firefox_user_prefs={
                    "dom.webdriver.enabled": False,
                    "media.peerconnection.enabled": False
                }
            )
            cookies = context.cookies()
            context.close()
            
            # Filter cookies by domain
            platform_cookies = [c for c in cookies if platform in c.get("domain", "")]
            if not platform_cookies:
                return "DISCONNECTED"
                
            # Check for primary session tokens
            if platform == "linkedin":
                has_session = any(c["name"] == "li_at" for c in platform_cookies)
                return "CONNECTED" if has_session else "EXPIRED"
            elif platform == "indeed":
                # Indeed session cookies are CTK, SURF, INDEED_USER_TOKEN, or JSESSIONID
                has_session = any(c["name"] in ["SURF", "CTK", "JSESSIONID", "INDEED_USER_TOKEN", "cf_chl_rc_ni"] for c in platform_cookies)
                return "CONNECTED" if has_session else "EXPIRED"
            elif platform == "jobstreet":
                # JobStreet/SEEK uses SEEKUSER, userToken, seekSession, etc.
                has_session = any(c["name"] in ["SEEKUSER", "userToken", "seekSession"] or "seek" in c["name"].lower() for c in platform_cookies)
                return "CONNECTED" if has_session else "EXPIRED"
                
            return "CONNECTED"
        except Exception as e:
            print(f"Error checking auth status for {platform}: {e}")
            return "DISCONNECTED"

def scrape_serpapi(keywords, location, date_range):
    import requests
    new_jobs_count = 0
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Map date range to SerpAPI chip
    chip_map = {"day": "date_posted:today", "week": "date_posted:3days", "month": "date_posted:week"}
    chip = chip_map.get(date_range, "date_posted:3days")

    for kw in keywords:
        query = f"{kw} {location}"
        print(f"Querying SerpAPI for: {query}")
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_jobs",
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "chips": chip
        }
        try:
            response = requests.get(url, params=params, timeout=20)
            if response.status_code == 200:
                data = response.json()
                job_results = data.get("jobs_results", [])
                print(f"SerpAPI returned {len(job_results)} jobs.")
                for job in job_results:
                    title = job.get("title")
                    company = job.get("company_name", "Unknown Company")
                    loc = job.get("location", "Philippines")
                    description = job.get("description", "")
                    
                    via = job.get("via", "")
                    source = "Google Jobs"
                    if "indeed" in via.lower():
                        source = "Indeed"
                    elif "linkedin" in via.lower():
                        source = "LinkedIn"
                    elif "jobstreet" in via.lower():
                        source = "JobStreet"
                    elif via:
                        source = via.replace("via", "").strip()

                    job_url = ""
                    related_links = job.get("related_links", [])
                    if related_links:
                        job_url = related_links[0].get("link", "")
                    
                    posted_time = job.get("detected_extensions", {}).get("posted_at", "Recently")

                    cursor.execute("SELECT id FROM jobs WHERE title = ? AND company = ?", (title, company))
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO jobs (title, company, location, description, description_url, contact_email, source, status, posted_time)
                            VALUES (?, ?, ?, ?, ?, 'recruitment@example.com', ?, 'NEW', ?)
                        """, (title, company, loc, description, job_url, source, posted_time))
                        new_jobs_count += 1
            else:
                print(f"SerpAPI returned status code: {response.status_code}")
        except Exception as e:
            print(f"Error querying SerpAPI: {e}")
            
    conn.commit()
    conn.close()
    print(f"SerpAPI scraping completed. Added {new_jobs_count} new postings.")
    return new_jobs_count

if __name__ == "__main__":
    scrape_jobs()
