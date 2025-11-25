"""
Database Configuration
"""

import os

from dotenv import load_dotenv
import sqlalchemy as sql
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm
from .models import Base

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
    # Import inside the function to avoid circular imports when FastAPI loads dependencies
    from .models import Base

    Base.metadata.create_all(bind=engine)
