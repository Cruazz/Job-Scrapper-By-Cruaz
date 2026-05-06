from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class JobListingBase(BaseModel):
    title: str
    company: str
    location: str
    salary_range: Optional[str] = None
    description: str
    url: str
    source: str
    posted_date: Optional[date] = None

class JobListingCreate(JobListingBase):
    pass

class JobListing(JobListingBase):
    id: str  # Hash based ID
    scraped_at: datetime
    sent_in_digest: bool = False
    match_score: float = 0.0

    class Config:
        from_attributes = True

class UserPreferences(BaseModel):
    keywords: List[str]
    locations: List[str]
    excluded_companies: List[str] = []
    min_salary: Optional[int] = None
    seniority_levels: List[str] = []
    email_address: str
