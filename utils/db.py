import pandas as pd
from sqlalchemy import create_engine, text
from config import *

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

def run_query(query, params=None):
    return pd.read_sql(text(query), engine, params=params)

def execute_query(query, params=None):
    with engine.begin() as conn:
        conn.execute(text(query), params or {})