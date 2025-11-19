import os
import psycopg2
from psycopg2.extras import RealDictCursor
import dotenv
import pandas as pd

dotenv.load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "influencer_db")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def create_database_if_not_exists():
    """Create the database if it doesn't exist yet."""
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Database {DB_NAME} created")
    cur.close()
    conn.close()


class DBHelper:
    def __init__(self):
        # ensure DB exists
        create_database_if_not_exists()

        # connect to the target database
        self.conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

    def query(self, sql: str, params: tuple = None) -> list:
        """Return list of dicts."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def query_df(self, sql: str, params: tuple = None) -> pd.DataFrame:
        """Return DataFrame."""
        return pd.read_sql_query(sql, self.conn, params=params)

    def execute(self, sql: str, params: tuple = None):
        """Execute single query."""
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            self.conn.commit()

    def execute_many(self, sql: str, data: list):
        """Execute multiple queries at once."""
        with self.conn.cursor() as cur:
            cur.executemany(sql, data)
            self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
