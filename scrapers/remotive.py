from typing import List
from scrapers.base import BaseScraper
import logging

logger = logging.getLogger(__name__)

class RemotiveScraper(BaseScraper):
    """
    Scraper for Remotive.com using their public JSON API.
    """
    API_URL = "https://remotive.com/api/remote-jobs?category=software-dev&limit=50"

    async def scrape(self) -> List[dict]:
        try:
            logger.info("Fetching jobs from Remotive API...")
            response = await self.client.get(self.API_URL)
            response.raise_for_status()
            data = response.json()
            
            # Remotive returns a list of jobs in the 'jobs' key
            return [{"data": job, "source": "remotive"} for job in data.get("jobs", [])]
        except Exception as e:
            logger.error(f"Remotive API error: {e}")
            return []
