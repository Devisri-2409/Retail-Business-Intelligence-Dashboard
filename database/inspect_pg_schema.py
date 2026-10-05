import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.db import run_query

print("=== 1. ROW COUNTS ===")
for tbl in ["products", "customers", "sales"]:
    df = run_query(f"SELECT COUNT(*) AS count FROM {tbl}")
    print(f"{tbl}: {df.iloc[0]['count']} rows")

print("\n=== 2. TABLE STRUCTURES ===")
for tbl in ["products", "customers", "sales"]:
    df = run_query(f"""
        SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = '{tbl}'
        ORDER BY ordinal_position;
    """)
    print(f"-- {tbl} --")
    for _, r in df.iterrows():
        dtype = r['data_type']
        if r['character_maximum_length'] is not None and str(r['character_maximum_length']) != '<NA>' and str(r['character_maximum_length']) != 'nan':
            dtype += f"({int(r['character_maximum_length'])})"
        elif r['numeric_precision'] is not None and str(r['numeric_precision']) != '<NA>' and str(r['numeric_precision']) != 'nan':
            dtype += f"({int(r['numeric_precision'])},{int(r['numeric_scale'])})"
        print(f"  {r['column_name']}: {dtype} (Nullable: {r['is_nullable']})")

print("\n=== 3. FOREIGN KEYS ===")
df_fk = run_query("""
    SELECT
        tc.table_name, kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name,
        rc.delete_rule
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
    JOIN information_schema.referential_constraints AS rc
      ON rc.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema='public';
""")
for _, r in df_fk.iterrows():
    print(f"{r['table_name']}.{r['column_name']} -> {r['foreign_table_name']}.{r['foreign_column_name']} (ON DELETE {r['delete_rule']})")

print("\n=== 4. INDEXES ===")
df_idx = run_query("""
    SELECT tablename, indexname, indexdef
    FROM pg_indexes
    WHERE schemaname = 'public'
    ORDER BY tablename, indexname;
""")
for _, r in df_idx.iterrows():
    print(f"{r['tablename']} | {r['indexname']} | {r['indexdef']}")
