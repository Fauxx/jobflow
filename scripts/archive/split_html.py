from bs4 import BeautifulSoup
import os

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Extract styles
styles = soup.find_all('style')
css_content = ""
for style in styles:
    css_content += style.string or ""
    style.extract()

# Extract scripts
scripts = soup.find_all('script')
js_content = ""
for script in scripts:
    if script.string: # Inline scripts
        if "__NEXT_DATA__" not in script.string: # exclude next data if any exist
            js_content += script.string + "\n"
        script.extract()
    else:
        # keep external scripts like Tailwind/FontAwesome
        pass

os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

with open('static/css/main.css', 'w', encoding='utf-8') as f:
    f.write(css_content.strip())

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js_content.strip())

with open('templates/dashboard_stripped.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
