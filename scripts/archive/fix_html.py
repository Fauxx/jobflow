with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

# Add CSS link
html = html.replace('</head>', '    <link href="/static/css/main.css" rel="stylesheet">\n</head>')

# Add JS link
html = html.replace('</body>', '    <script src="/static/js/main.js"></script>\n</body>')

# Note: The dashboard HTML might have been reverted entirely, so it STILL has the styles and scripts.
# Wait, my split_regex.py did not OVERWRITE dashboard.html! It only wrote static assets.
# I need to overwrite it.

import re

# Remove styles
style_pattern = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
html = style_pattern.sub('', html)

# Remove scripts
script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
def script_replacer(match):
    content = match.group(1)
    if content.strip() and '__NEXT_DATA__' not in content:
        return ''
    return match.group(0)

html = script_pattern.sub(script_replacer, html)

# Add links back
html = html.replace('</head>', '    <link href="/static/css/main.css" rel="stylesheet">\n</head>')
html = html.replace('</body>', '    <script src="/static/js/main.js"></script>\n</body>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
