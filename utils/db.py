import os
import re
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. Please define DATABASE_URL in your .env file."
    )

# Normalize URL scheme for psycopg 3
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+psycopg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Configure SQLAlchemy engine with connection pooling and health check
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,
)

def _sanitize_error(error: Exception) -> str:
    """Mask any sensitive credentials from error messages."""
    msg = str(error)
    try:
        parsed = urlparse(DATABASE_URL)
        if parsed.password and parsed.password in msg:
            msg = msg.replace(parsed.password, "****")
    except Exception:
        pass
    return msg

def run_query(query, params=None):
    """Execute a SELECT query and return results as a Pandas DataFrame."""
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)
    except Exception as e:
        safe_msg = _sanitize_error(e)
        raise RuntimeError(f"Database query error: {safe_msg}") from None

def execute_query(query, params=None):
    """Execute an INSERT, UPDATE, or DDL statement within a transaction."""
    try:
        with engine.begin() as conn:
            conn.execute(text(query), params or {})
    except Exception as e:
        safe_msg = _sanitize_error(e)
        raise RuntimeError(f"Database execution error: {safe_msg}") from None