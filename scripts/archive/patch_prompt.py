import re

with open('src/services/resume_tailor.py', 'r') as f:
    content = f.read()

old_rules = """STRICT RULES:
1. You ONLY use information from the Candidate Knowledge Base below. 
2. NEVER invent skills, tools, metrics, companies, dates, or achievements.
3. DO NOT REWRITE OR REPHRASE BULLETS. Your job is to SELECT the most relevant existing bullets verbatim from the candidate's master profile.
4. IMPORTANT: When selecting a bullet, you MUST provide its exact ID and its exact original text.
5. If the JD requires a skill the candidate does NOT have, list it under "missing_skills" — do NOT pretend the candidate has it.
6. Provide a brief explanation for why each verbatim bullet was selected and whether it is highly recommended based on the JD."""

new_rules = """STRICT RULES:
1. FACTUAL ANCHORING: You ONLY use information from the Candidate Knowledge Base below. NEVER invent skills, tools, metrics, companies, dates, or achievements.
2. VERBATIM SELECTION: DO NOT REWRITE OR REPHRASE BULLETS. Your job is to SELECT the most relevant existing bullets verbatim from the candidate's master profile.
3. EXACT MAPPING: When selecting a bullet, you MUST provide its exact ID and its exact original text.
4. ARCHITECTURAL COHESION: Ensure the selected bullets make sense architecturally based on the JD. Do not blindly keyword-match (e.g., do not pick a Python ETL bullet if the JD specifically asks for frontend UI work). Select bullets that demonstrate systems-level architecture aligned with the role.
5. HIGH-IMPACT ALIGNMENT: Prioritize bullets that demonstrate measurable business impact, scale, or advanced technical patterns (like Zero-Trust or multi-cloud) IF they match the JD requirements.
6. MISSING SKILLS GAP: If the JD requires a skill the candidate does NOT have, list it under "missing_skills" — do NOT pretend the candidate has it.
7. TECHNICAL JUSTIFICATION: Provide a brief architectural explanation for why each verbatim bullet was selected and how it specifically solves a requirement in the JD."""

content = content.replace(old_rules, new_rules)

with open('src/services/resume_tailor.py', 'w') as f:
    f.write(content)

print("Prompt patched successfully!")
