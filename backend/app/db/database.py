from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# In a production environment, use environment variables for these settings
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost/quantumnest"

# For development, we can use SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./quantumnest.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
