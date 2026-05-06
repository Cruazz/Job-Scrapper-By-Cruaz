from sqlalchemy import create_engine, Column, String, Float, DateTime, Date, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config.settings import settings
import os

# Ensure data directory exists
os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///./{settings.database_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class JobListing(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    user_key = Column(String, index=True, default="default")
    title = Column(String)
    company = Column(String)
    location = Column(String)
    salary_range = Column(String, nullable=True)
    description = Column(String)
    url = Column(String)
    source = Column(String)
    posted_date = Column(Date, nullable=True)
    scraped_at = Column(DateTime)
    sent_in_digest = Column(Boolean, default=False)
    match_score = Column(Float, default=0.0)
    status = Column(String, default="New") # New, Applied, Interviewing, Rejected, Offer

class SystemSettings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    user_key = Column(String, unique=True, index=True)
    keywords = Column(String) # JSON string
    locations = Column(String) # JSON string
    min_salary = Column(Integer, default=0)
    target_email = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
