import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove styles
style_pattern = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
html = style_pattern.sub('', html)

# Remove scripts EXCEPT tailwind and fontawesome
script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
def script_replacer(match):
    content = match.group(1)
    if content.strip() and '__NEXT_DATA__' not in content:
        return ''
    return match.group(0)

html = script_pattern.sub(script_replacer, html)

# Add links back (assuming they aren't already there from git checkout)
if '<link href="/static/css/main.css" rel="stylesheet">' not in html:
    html = html.replace('</head>', '    <link href="/static/css/main.css" rel="stylesheet">\n</head>')
if '<script src="/static/js/main.js"></script>' not in html:
    html = html.replace('</body>', '    <script src="/static/js/main.js"></script>\n</body>')

# Replace the aside with the include partial (because we git checkout'd it!)
html = re.sub(r'<aside.*?</aside>', '{% include "partials/sidebar.html" %}', html, flags=re.DOTALL)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
