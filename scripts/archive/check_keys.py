import json

with open("jobflow_backup.json", "r") as f:
    backup = json.load(f)

for mr in backup.get("master_resumes", []):
    content = json.loads(mr["content"])
    print(list(content.keys()))

