from sqlalchemy import create_engine, text
engine = create_engine('postgresql://jobflow:password@localhost:5432/jobflow')
with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE applications ADD COLUMN cover_letter TEXT;'))
        conn.commit()
        print("Successfully added cover_letter to applications.")
    except Exception as e:
        print("Error (might already exist):", e)
