from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Scraping
    request_delay: float = 1.5
    max_retries: int = 3
    timeout_seconds: int = 30

    # Sources
    scrape_indeed: bool = True
    scrape_linkedin: bool = True
    scrape_wwr: bool = True

    # Filtering
    keywords: List[str] = ["python", "backend", "api"]
    locations: List[str] = ["remote"]
    min_salary: Optional[int] = None
    seniority: List[str] = ["mid", "senior"]

    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    to_email: Optional[str] = None

    # System
    log_level: str = "INFO"
    database_path: str = "data/jobs.db"

settings = Settings()
