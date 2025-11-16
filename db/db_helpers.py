# db_helpers.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import dotenv
import pandas as pd

# ----------------------------
# Load environment variables
# ----------------------------
dotenv.load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "influencer_db")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


class DBHelper:
    def __init__(self):
        """Initialize the DBHelper and connect to PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            print("Connected to PostgreSQL successfully")
        except Exception as e:
            print("Error connecting to PostgreSQL:", e)
            raise

    def query(self, sql: str, params: tuple = None) -> list:
        """
        Execute a SELECT query and return results as list of dicts.
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            results = cur.fetchall()
        return results

    def query_df(self, sql: str, params: tuple = None) -> pd.DataFrame:
        """
        Execute a SELECT query and return results as a pandas DataFrame.
        """
        return pd.read_sql_query(sql, self.conn, params=params)

    def execute(self, sql: str, params: tuple = None):
        """
        Execute INSERT, UPDATE, DELETE, or DDL commands.
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            self.conn.commit()

    def execute_many(self, sql: str, data: list):
        """
        Execute many commands with data list (e.g., batch insert).
        """
        with self.conn.cursor() as cur:
            cur.executemany(sql, data)
            self.conn.commit()

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Connection closed")


# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    db = DBHelper()

    # Fetch top 5 influencers
    influencers = db.query("SELECT * FROM influencers ORDER BY follower_count DESC LIMIT 5;")
    print(influencers)

    # Fetch as DataFrame
    df = db.query_df("SELECT * FROM fact_influencer_performance LIMIT 5;")
    print(df)

    db.close()
