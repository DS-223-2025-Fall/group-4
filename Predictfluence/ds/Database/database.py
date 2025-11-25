"""
Database configuration for the DS service.
"""

import os

from dotenv import load_dotenv
import sqlalchemy as sql
import sqlalchemy.orm as orm

from .models import Base

# Load environment variables from the local .env file
load_dotenv(".env")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

engine = sql.create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Provide a database session for request handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Ensure all ORM tables exist.
    """
    from .models import Base  # Local import to avoid circular imports

    Base.metadata.create_all(bind=engine)

