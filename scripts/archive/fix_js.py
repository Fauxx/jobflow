import re

with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the current submit listener
old_submit = """scraperForm.addEventListener('submit', () => {
                    localStorage.setItem('scrape-keywords', keywordsInput.value);
                    localStorage.setItem('scrape-location', locationInput.value);
                    localStorage.setItem('scrape-date', dateSelect.value);
                    localStorage.setItem('scrape-use-auth', useAuthCheckbox.checked);
                });"""

new_submit = """scraperForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    localStorage.setItem('scrape-keywords', keywordsInput.value);
                    localStorage.setItem('scrape-location', locationInput.value);
                    
                    const submitBtn = scraperForm.querySelector('button[type="submit"]');
                    const originalText = submitBtn.innerHTML;
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
                    
                    const formData = new FormData(scraperForm);
                    
                    try {
                        const response = await fetch('/scrape', {
                            method: 'POST',
                            body: formData
                        });
                        if (response.ok) {
                            window.location.reload();
                        } else {
                            alert('Scraping failed.');
                            submitBtn.disabled = false;
                            submitBtn.innerHTML = originalText;
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        alert('Scraping error.');
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }
                });"""

if old_submit in js:
    js = js.replace(old_submit, new_submit)
else:
    # Just append it or find a looser match
    # Since we can't be 100% sure of whitespace, let's use regex
    pattern = re.compile(r"scraperForm\.addEventListener\('submit', \(\) => \{.*?\}\);", re.DOTALL)
    js = pattern.sub(new_submit, js)

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js)
