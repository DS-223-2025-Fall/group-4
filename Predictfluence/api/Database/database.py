"""
Database Configuration Module

This module sets up the connection to the database for the influencer marketing
project using SQLAlchemy. It provides the engine, session factory, and helper
functions for creating tables and obtaining database sessions.

Key Components:
- engine: SQLAlchemy Engine bound to DATABASE_URL from environment variables.
- SessionLocal: SQLAlchemy session factory for request-scoped sessions.
- get_db(): Dependency generator for FastAPI routes to provide a session.
- create_tables(): Utility function to create all tables defined in models.py.

Usage:
1. Ensure the DATABASE_URL environment variable is set in a .env file or system environment.
2. Import SessionLocal or use get_db() in your API endpoints.
3. Call create_tables() at application startup if tables need to be created.

Example:
    from Database.database import get_db, create_tables

    create_tables()  # create tables if they don't exist

    with next(get_db()) as db:
        # perform database operations
        pass
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
    Yield a SQLAlchemy database session.

    This function provides a database session for use in FastAPI endpoints.
    The session is automatically closed after use, ensuring proper
    resource management.

    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables defined in the SQLAlchemy ORM models.

    This function initializes the database schema by creating all tables
    defined in the `Base` metadata. Importing `Base` inside the function
    avoids circular imports when FastAPI loads dependencies.

    Usage:
        create_tables()
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)

