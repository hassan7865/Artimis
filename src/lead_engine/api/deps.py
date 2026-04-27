from __future__ import annotations
import psycopg
from psycopg.rows import dict_row
from lead_engine.config import CONFIG

def get_db_conn():
    with psycopg.connect(CONFIG["DATABASE_URL"], row_factory=dict_row) as conn:
        yield conn
