with open("src/services/profile_service.py", "r") as f:
    content = f.read()

# Fix the dictionary mapping in get_full_profile
content = content.replace("s.name", "s.items")
content = content.replace("p.name", "p.title")
content = content.replace("p.description", "p.detailed_context")
content = content.replace("b.raw_text", "b.text")
content = content.replace("e.title", "e.role")
content = content.replace("e.start_date", "e.date_range")
content = content.replace("e.end_date", "''")
content = content.replace("e.description", "e.detailed_context")
content = content.replace("e.achievements", "''")

# Now fix save_full_profile column assignments
content = content.replace('name=s_data.get("name") or s_data.get("items") or ""', 'items=s_data.get("items") or s_data.get("name") or ""')
content = content.replace('name=p_data.get("name") or p_data.get("title") or ""', 'title=p_data.get("title") or p_data.get("name") or ""')
content = content.replace('description=p_data.get("description")', 'detailed_context=p_data.get("description") or p_data.get("detailed_context")')
content = content.replace('raw_text=text', 'text=text')
content = content.replace('title=e_data.get("title") or e_data.get("role") or ""', 'role=e_data.get("role") or e_data.get("title") or ""')
content = content.replace('start_date=e_data.get("start_date")', 'date_range=e_data.get("date_range") or e_data.get("start_date")')
content = content.replace('description=e_data.get("description")', 'detailed_context=e_data.get("description") or e_data.get("detailed_context")')

# Drop proficiency, end_date, achievements in assignments
content = content.replace("proficiency=s_data.get(\"proficiency\")", "")
content = content.replace("end_date=e_data.get(\"end_date\") or e_data.get(\"date\"),", "")
content = content.replace("achievements=e_data.get(\"achievements\"),", "")

with open("src/services/profile_service.py", "w") as f:
    f.write(content)
