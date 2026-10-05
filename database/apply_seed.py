import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("ERROR: DATABASE_URL not set in .env")
    sys.exit(1)

seed_file = os.path.join(os.path.dirname(__file__), "seed_data.sql")
with open(seed_file, "r", encoding="utf-8") as f:
    sql_content = f.read()

try:
    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(text(sql_content))
    print("Seed data applied successfully!")
except Exception as e:
    print("Error applying seed data:", e)
    sys.exit(1)
