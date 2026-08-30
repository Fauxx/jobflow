import re

with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Remove legacy functions
legacy_funcs = [
    r"function launchLoginBrowser.*?\}",
    r"function openCookieModal.*?\}",
    r"function closeCookieModal.*?\}",
    r"function submitCookies.*?\}",
    r"async function checkAuthStatuses.*?\}",
    r"async function fetchAuthStatus.*?\}",
]

for func_pattern in legacy_funcs:
    js = re.sub(func_pattern, "", js, flags=re.DOTALL)

# Fix the DOMContentLoaded block
dom_loaded_pattern = re.compile(r"document\.addEventListener\('DOMContentLoaded',\s*\(\)\s*=>\s*\{.*?(?=\}\);)\}\);", re.DOTALL)

new_dom_loaded = """document.addEventListener('DOMContentLoaded', () => {
    const scraperForm = document.getElementById('scraper-form');
    const keywordsInput = document.getElementById('scrape-keywords');
    const locationInput = document.getElementById('scrape-location');
    const dateSelect = document.getElementById('scrape-date');

    if (scraperForm) {
        // Restore settings
        if (keywordsInput && localStorage.getItem('scrape-keywords')) {
            keywordsInput.value = localStorage.getItem('scrape-keywords');
        }
        if (locationInput && localStorage.getItem('scrape-location')) {
            locationInput.value = localStorage.getItem('scrape-location');
        }
        if (dateSelect && localStorage.getItem('scrape-date')) {
            dateSelect.value = localStorage.getItem('scrape-date');
        }

        // Save settings on submit and handle AJAX
        scraperForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (keywordsInput) localStorage.setItem('scrape-keywords', keywordsInput.value);
            if (locationInput) localStorage.setItem('scrape-location', locationInput.value);
            if (dateSelect) localStorage.setItem('scrape-date', dateSelect.value);
            
            const submitBtn = scraperForm.querySelector('button[type="submit"]');
            const originalText = submitBtn ? submitBtn.innerHTML : 'Scrape';
            
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
            }
            
            const formData = new FormData(scraperForm);
            
            try {
                const response = await fetch('/scrape', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert('Scraping failed with status: ' + response.status);
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while scraping.');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            }
        });
    }
});"""

if dom_loaded_pattern.search(js):
    js = dom_loaded_pattern.sub(new_dom_loaded, js)
else:
    # Append if not found
    js += "\n" + new_dom_loaded

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js)
