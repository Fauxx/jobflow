from bs4 import BeautifulSoup
import os

with open('templates/dashboard_stripped.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

os.makedirs('templates/partials', exist_ok=True)

# Find sidebar
aside = soup.find('aside')
if aside:
    with open('templates/partials/sidebar.html', 'w', encoding='utf-8') as f:
        f.write(str(aside))
    aside.extract() # Remove from main soup

# The header also needs removing since it's in base.html
header = soup.find('header')
if header:
    header.extract()

# The modal needs to be moved to block modals
modal = soup.find(id='jobModal')
if modal:
    with open('templates/partials/job_modal.html', 'w', encoding='utf-8') as f:
        f.write(str(modal))
    modal.extract()

resume_modal = soup.find(id='resumeTailorModal')
if resume_modal:
    with open('templates/partials/resume_modal.html', 'w', encoding='utf-8') as f:
        f.write(str(resume_modal))
    resume_modal.extract()

apply_modal = soup.find(id='applyModal')
if apply_modal:
    with open('templates/partials/apply_modal.html', 'w', encoding='utf-8') as f:
        f.write(str(apply_modal))
    apply_modal.extract()

# The rest is the content
main_content = soup.find('main')
if main_content:
    content_inner = main_content.decode_contents()
else:
    content_inner = str(soup.body.decode_contents() if soup.body else soup)

final_dashboard = f"""{{% extends "base.html" %}}

{{% block content %}}
{content_inner}
{{% endblock %}}

{{% block modals %}}
{{% include "partials/job_modal.html" ignore missing %}}
{{% include "partials/resume_modal.html" ignore missing %}}
{{% include "partials/apply_modal.html" ignore missing %}}
{{% endblock %}}
"""

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(final_dashboard)

