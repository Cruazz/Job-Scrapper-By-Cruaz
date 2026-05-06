from bs4 import BeautifulSoup
from typing import List
from scrapers.base import BaseScraper
from parsers.base import BaseParser
from models.schemas import JobListingCreate
import asyncio
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class WWRScraper(BaseScraper):
    URL = "https://weworkremotely.com/categories/remote-back-end-programming-jobs"

    async def scrape(self) -> List[dict]:
        try:
            response = await self.client.get(self.URL)
            response.raise_for_status()
            return [{"html": response.text, "source": "wwr"}]
        except Exception as e:
            logger.error(f"Error scraping WWR: {e}")
            return []

class WWRParser(BaseParser):
    def parse(self, raw_data: List[dict]) -> List[JobListingCreate]:
        jobs = []
        for item in raw_data:
            soup = BeautifulSoup(item["html"], "lxml")
            sections = soup.find_all("section", class_="jobs")
            for section in sections:
                list_items = section.find_all("li")
                for li in list_items:
                    link_tag = li.find("a")
                    if not link_tag or "href" not in link_tag.attrs:
                        continue
                    
                    url = link_tag["href"]
                    if url.startswith("/"):
                        url = "https://weworkremotely.com" + url
                    
                    title_tag = li.find("span", class_="new-listing__header__title__text")
                    company_tag = li.find("p", class_="new-listing__company-name")
                    region_tag = li.find("span", class_="new-listing__region") # Best guess or check again
                    
                    if not title_tag or not company_tag:
                        # Fallback for old structure or ads
                        title_tag = title_tag or li.find("span", class_="title")
                        company_tag = company_tag or li.find("span", class_="company")
                        region_tag = region_tag or li.find("span", class_="region")

                    if not title_tag or not company_tag:
                        continue
                        
                    title = title_tag.text.strip()
                    company = company_tag.text.strip()
                    location = region_tag.text.strip() if region_tag else "Remote"
                    
                    # Log for debugging
                    logger.debug(f"Parsed job: {title} at {company}")
                    
                    # Description might require another request, but for now we'll use a placeholder or summary
                    description = f"Job at {company} for {title} in {location}"
                    
                    jobs.append(JobListingCreate(
                        title=title,
                        company=company,
                        location=location,
                        description=description,
                        url=url,
                        source="wwr"
                    ))
        return jobs
