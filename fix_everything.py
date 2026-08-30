import re
import os

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Extract the raw original Javascript
script_pattern = re.compile(r'<script>(.*?)</script>', re.DOTALL | re.IGNORECASE)
scripts = script_pattern.findall(html)
original_js = scripts[0] if scripts else ""

# 2. Modify the JS to fix the AJAX form and remove auth junk, but KEEP EVERYTHING ELSE
# Replace the form submit block
old_submit_block = """scraperForm.addEventListener('submit', () => {
                    localStorage.setItem('scrape-keywords', keywordsInput.value);
                    localStorage.setItem('scrape-location', locationInput.value);
                    localStorage.setItem('scrape-date', dateSelect.value);
                    localStorage.setItem('scrape-use-auth', useAuthCheckbox.checked);
                });"""

new_submit_block = """scraperForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    if(keywordsInput) localStorage.setItem('scrape-keywords', keywordsInput.value);
                    if(locationInput) localStorage.setItem('scrape-location', locationInput.value);
                    if(dateSelect) localStorage.setItem('scrape-date', dateSelect.value);
                    
                    const submitBtn = scraperForm.querySelector('button[type="submit"]');
                    const originalText = submitBtn.innerHTML;
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
                    
                    const formData = new FormData(scraperForm);
                    try {
                        const response = await fetch('/scrape', { method: 'POST', body: formData });
                        if (response.ok) { window.location.reload(); }
                        else { alert('Scraping failed.'); submitBtn.disabled = false; submitBtn.innerHTML = originalText; }
                    } catch (error) {
                        console.error('Error:', error);
                        alert('Scraping error.');
                        submitBtn.disabled = false; submitBtn.innerHTML = originalText;
                    }
                });"""

fixed_js = original_js.replace(old_submit_block, new_submit_block)

# Remove the useAuthCheckbox from DOMContentLoaded safely
fixed_js = fixed_js.replace("const useAuthCheckbox = document.getElementById('scrape-use-auth');", "")
fixed_js = fixed_js.replace("""if (localStorage.getItem('scrape-use-auth') !== null) {
                    useAuthCheckbox.checked = localStorage.getItem('scrape-use-auth') === 'true';
                }""", "")

# Remove checkAuthStatuses call
fixed_js = fixed_js.replace("checkAuthStatuses();", "")

# 3. Write fixed JS to static/js/main.js
os.makedirs('static/js', exist_ok=True)
with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(fixed_js.strip())

# 4. Now fix sidebar.html by removing the Auth sections
with open('templates/partials/sidebar.html', 'r', encoding='utf-8') as f:
    sidebar = f.read()

# Using regex to remove the Sources block entirely
sidebar = re.sub(r'<div class="flex justify-between items-center mb-1\.5">.*?<label class="block text-xs text-gray-400 font-bold">Sources</label>.*?</div>.*?</div>', '', sidebar, flags=re.DOTALL)

# And remove Use Auth block
sidebar = re.sub(r'<div class="border-t border-gray-700 pt-3">.*?<label class="flex items-center space-x-2 cursor-pointer text-xs font-semibold text-gray-300">.*?Use Authenticated Session.*?</div>', '', sidebar, flags=re.DOTALL)

with open('templates/partials/sidebar.html', 'w', encoding='utf-8') as f:
    f.write(sidebar)

