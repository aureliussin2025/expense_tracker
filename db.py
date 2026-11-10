from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

database_url = os.getenv("DATABASE_URL", "sqlite:///database.db")

engine = create_engine(database_url, echo=True)

Base = declarative_base()

# A factory: calling session() creates a fresh unit of database work.
session = sessionmaker(bind=engine)

def get_db():
    # FastAPI runs this dependency for each request that needs a database.
    db = session()
    try:
        # yield hands the session to the endpoint; execution resumes afterward.
        yield db
    finally:
        # Always release it, even if the endpoint raises an HTTP error.
        db.close()

