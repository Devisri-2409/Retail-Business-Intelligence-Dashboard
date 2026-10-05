import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("ERROR: DATABASE_URL not found in .env")
    sys.exit(1)

# Mask URL for safe printing
parsed = urlparse(db_url)
masked_url = db_url.replace(parsed.password, "****") if parsed.password else db_url
print(f"Connecting with host: {parsed.hostname}, port: {parsed.port}, target db: {parsed.path.lstrip('/')}")

# Connect to maintenance db 'postgres' first to verify auth and ensure target db exists
maint_url = db_url.rsplit("/", 1)[0] + "/postgres"
target_db = parsed.path.lstrip("/") or "retail_dashboard"

try:
    engine = create_engine(maint_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT version()")).scalar()
        print("PostgreSQL authentication SUCCESSFUL!")
        print("PostgreSQL Version:", res.split(",")[0])
        
        # Check if target db exists
        db_exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :d"), {"d": target_db}
        ).scalar()
        if not db_exists:
            print(f"Creating database: {target_db}...")
            conn.execute(text(f'CREATE DATABASE "{target_db}"'))
            print(f"Database {target_db} created successfully.")
        else:
            print(f"Database {target_db} already exists.")
except Exception as e:
    err_str = str(e)
    if parsed.password and parsed.password in err_str:
        err_str = err_str.replace(parsed.password, "****")
    print("CONNECTION/AUTH FAILED:", err_str)
    sys.exit(1)
