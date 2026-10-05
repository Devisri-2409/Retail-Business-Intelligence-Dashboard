import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("ERROR: DATABASE_URL not found in .env")
    sys.exit(1)

schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
with open(schema_file, "r", encoding="utf-8") as f:
    schema_sql = f.read()

try:
    engine = create_engine(db_url)
    with engine.begin() as conn:
        # Split statements by semicolon or execute directly
        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
    print("Schema applied successfully!")
    
    # Verify tables
    with engine.connect() as conn:
        tables = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)).fetchall()
        print("Tables in retail_dashboard:")
        for t in tables:
            print(f" - {t[0]}")
            
        # Verify columns in each table
        for table_name in ["products", "customers", "sales"]:
            cols = conn.execute(text(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)).fetchall()
            print(f"\nColumns for {table_name}:")
            for c in cols:
                print(f"   {c[0]} ({c[1]}, nullable={c[2]})")
                
        # Verify indexes
        indexes = conn.execute(text("""
            SELECT indexname, tablename
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """)).fetchall()
        print("\nIndexes created:")
        for idx in indexes:
            print(f" - {idx[0]} on {idx[1]}")
            
except Exception as e:
    print("Failed to apply schema:", e)
    sys.exit(1)
