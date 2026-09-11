with open("src/services/profile_service.py", "r") as f:
    content = f.read()

import re

# Remove "is_highlight": p.is_highlight,
content = re.sub(r'\s*"is_highlight": p\.is_highlight,', '', content)
# Remove "tech_stack": p.tech_stack,
content = re.sub(r'\s*"tech_stack": p\.tech_stack,', '', content)
# Remove "url": p.url,
content = re.sub(r'\s*"url": p\.url,', '', content)
# Remove "proficiency": s.proficiency
content = re.sub(r',\s*"proficiency": s\.proficiency', '', content)

# In save_full_profile
content = re.sub(r'\s*url=p_data\.get\("url"\),', '', content)
content = re.sub(r'\s*tech_stack=p_data\.get\("tech_stack"\),', '', content)
content = re.sub(r'\s*is_highlight=p_data\.get\("is_highlight", False\),', '', content)

with open("src/services/profile_service.py", "w") as f:
    f.write(content)
