import sys
import json
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.models.resume import MasterResume
from src.models.application import Application

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("Starting migration...")
mrs = db.query(MasterResume).all()
bullet_text_to_id = {}

for mr in mrs:
    if not mr.content: continue
    try:
        data = json.loads(mr.content)
    except json.JSONDecodeError:
        continue
    
    # Update projects
    for p in data.get('projects', []):
        new_bullets = []
        for b in p.get('bullets', []):
            if isinstance(b, str):
                bid = str(uuid.uuid4())
                bullet_text_to_id[b.strip()] = bid
                new_bullets.append({"id": bid, "text": b})
            else:
                new_bullets.append(b)
        p['bullets'] = new_bullets
        
    # Update experiences
    for e in data.get('experience', []):
        new_bullets = []
        for b in e.get('bullets', []):
            if isinstance(b, str):
                bid = str(uuid.uuid4())
                bullet_text_to_id[b.strip()] = bid
                new_bullets.append({"id": bid, "text": b})
            else:
                new_bullets.append(b)
        e['bullets'] = new_bullets
        
    mr.content = json.dumps(data)

# Update Applications
apps = db.query(Application).filter(Application.ai_draft_json != None).all()
for app in apps:
    try:
        draft = json.loads(app.ai_draft_json)
    except json.JSONDecodeError:
        continue
        
    # Update drafted projects
    for p in draft.get('projects', []):
        for b in p.get('bullets', []):
            orig_text = b.get('original_text', '').strip()
            if orig_text in bullet_text_to_id:
                b['id'] = bullet_text_to_id[orig_text]
            elif 'id' not in b:
                b['id'] = str(uuid.uuid4())
                
    # Update drafted experiences
    for e in draft.get('experiences', []):
        for b in e.get('bullets', []):
            orig_text = b.get('original_text', '').strip()
            if orig_text in bullet_text_to_id:
                b['id'] = bullet_text_to_id[orig_text]
            elif 'id' not in b:
                b['id'] = str(uuid.uuid4())
                
    app.ai_draft_json = json.dumps(draft)

db.commit()
print("Migration successful")
