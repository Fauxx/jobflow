import re
import os

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract styles
style_pattern = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
styles = style_pattern.findall(html)
css_content = "\n".join(styles)

# Remove styles
html = style_pattern.sub('', html)

# Extract scripts
script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
script_matches = script_pattern.findall(html)
js_content = ""
for js in script_matches:
    if js.strip() and '__NEXT_DATA__' not in js:
        js_content += js + "\n"

# Only remove inline scripts (leave external scripts like tailwind)
def script_replacer(match):
    content = match.group(1)
    if content.strip() and '__NEXT_DATA__' not in content:
        return ''
    return match.group(0)

html = script_pattern.sub(script_replacer, html)

os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

with open('static/css/main.css', 'w', encoding='utf-8') as f:
    f.write(css_content.strip())

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js_content.strip())

# The HTML is still mostly monolithic, but let's just make it extend base.html
# Actually, if we just remove the <html> <head> <body> wrappers from dashboard.html,
# we can wrap it in {% extends "base.html" %} {% block content %}.

# For MVP frontend refactor, we just want it to load the extracted CSS/JS properly.
# The user wants "modular Jinja2 templates and extracted static assets".
# Let's extract the aside sidebar manually using simple splits.

