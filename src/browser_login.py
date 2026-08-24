import os
import sys
import time
from playwright.sync_api import sync_playwright

def run():
    profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "playwright_profile"))
    os.makedirs(profile_dir, exist_ok=True)
    
    # Determine which platform login to launch
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    
    print("\n" + "="*60)
    print(f"LAUNCHING PERSISTENT CHROMIUM BROWSER (Target: {target.upper()})")
    print(f"Profile Directory: {profile_dir}")
    print("="*60)
    print(f"1. A browser window will open on your screen to {target.upper()} login page.")
    print("2. Log in to your account.")
    print("3. Once finished, CLOSE the browser window.")
    print("Your login sessions and cookies will be saved in your project folder.")
    print("="*60 + "\n")
    
    with sync_playwright() as p:
        try:
            context = p.firefox.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                viewport=None,
                args=["--start-maximized"],
                firefox_user_prefs={
                    "dom.webdriver.enabled": False,
                    "media.peerconnection.enabled": False
                }
            )
            
            # Open selected login page
            if target in ["linkedin", "all"]:
                page1 = context.new_page()
                page1.goto("https://www.linkedin.com/login")
            
            if target in ["indeed", "all"]:
                page2 = context.new_page()
                page2.goto("https://ph.indeed.com/")
            
            if target in ["jobstreet", "all"]:
                page3 = context.new_page()
                page3.goto("https://www.jobstreet.com.ph/")
            
            # Keep python process alive while pages are open
            while True:
                # If all pages are closed by user, exit
                if not context.pages:
                    break
                time.sleep(1)
                
            context.close()
            print("Browser closed. Login sessions saved successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run()
