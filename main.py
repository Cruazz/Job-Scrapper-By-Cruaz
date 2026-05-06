import asyncio
import logging
from datetime import datetime
from config.settings import settings
from models.database import init_db, SessionLocal, JobListing as DBJobListing, SystemSettings
from scrapers.wwr import WWRScraper, WWRParser
from scrapers.remotive import RemotiveScraper
from parsers.remotive import RemotiveParser
from filters.matcher import JobMatcher
from emailer.sender import EmailSender
import hashlib
import json
import argparse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/aggregator.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
# Ensure stdout uses utf-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logger = logging.getLogger(__name__)

def get_active_settings(user_key):
    db = SessionLocal()
    db_settings = db.query(SystemSettings).filter(SystemSettings.user_key == user_key).first()
    db.close()
    
    if db_settings:
        return {
            "keywords": json.loads(db_settings.keywords),
            "locations": json.loads(db_settings.locations),
            "min_salary": db_settings.min_salary,
            "to_email": db_settings.target_email
        }
    return {
        "keywords": settings.keywords,
        "locations": settings.locations,
        "min_salary": settings.min_salary,
        "to_email": settings.to_email
    }

async def run_pipeline(user_key="default"):
    logger.info(f"Starting job aggregation pipeline for user: {user_key}")
    
    # Initialize DB
    init_db()
    
    # Load settings
    active_settings = get_active_settings(user_key)
    
    db = SessionLocal()
    
    # Components
    scrapers = [WWRScraper(), RemotiveScraper()]
    parsers = [WWRParser(), RemotiveParser()]
    matcher = JobMatcher(
        keywords=active_settings["keywords"],
        locations=active_settings["locations"],
        min_salary=active_settings["min_salary"]
    )
    email_sender = EmailSender(to_email=active_settings["to_email"])
    
    all_new_matches = []
    
    try:
        for scraper, parser in zip(scrapers, parsers):
            logger.info(f"Running scraper: {scraper.__class__.__name__}")
            raw_data = await scraper.scrape()
            jobs = parser.parse(raw_data)
            
            for job in jobs:
                # Generate unique ID per user
                job_id = f"{user_key}_{parser.generate_id(job.title, job.company, job.location)}"
                
                # Check if exists for THIS user
                existing = db.query(DBJobListing).filter(DBJobListing.id == job_id).first()
                if existing:
                    continue
                
                # Score and Filter
                is_match, score = matcher.is_match(job)
                if is_match:
                    logger.info(f"New match found: {job.title} at {job.company} (Score: {score})")
                    
                    # Save to DB
                    db_job = DBJobListing(
                        id=job_id,
                        user_key=user_key,
                        title=job.title,
                        company=job.company,
                        location=job.location,
                        description=job.description,
                        url=job.url,
                        source=job.source,
                        scraped_at=datetime.now(),
                        match_score=score,
                        sent_in_digest=False
                    )
                    db.add(db_job)
                    all_new_matches.append(db_job)
            
            await scraper.close()
            
        db.commit()
        
        # Send Digest
        if all_new_matches:
            logger.info(f"Sending digest with {len(all_new_matches)} new matches.")
            email_sender.send_digest(all_new_matches)
            
            # Mark as sent
            for job in all_new_matches:
                job.sent_in_digest = True
            db.commit()
        else:
            logger.info("No new matches found today.")
            
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        db.rollback()
    finally:
        db.close()
        logger.info("Pipeline finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-key", type=str, default="default", help="Access key for the user")
    args = parser.parse_args()
    
    asyncio.run(run_pipeline(args.user_key))
