with open("src/services/profile_service.py", "r") as f:
    content = f.read()

import re
content = content.replace("db.add(ProfileBullet(project_id=proj.id", "import uuid\n                db.add(ProfileBullet(id=str(uuid.uuid4()), project_id=proj.id")
content = content.replace("db.add(ProfileBullet(experience_id=exp.id", "db.add(ProfileBullet(id=str(uuid.uuid4()), experience_id=exp.id")

# Fix trailing commas introduced by my previous replace logic:
content = content.replace(",\n        )", "\n        )")

with open("src/services/profile_service.py", "w") as f:
    f.write(content)
