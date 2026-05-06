from abc import ABC, abstractmethod
from typing import List
import httpx
from config.settings import settings

class BaseScraper(ABC):
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.timeout_seconds,
            follow_redirects=True,
            headers={
                "User-Agent": "JobAggregatorBot/1.0 (+https://github.com/yourusername/job-aggregator)"
            }
        )

    @abstractmethod
    async def scrape(self) -> List[dict]:
        """Scrape raw data from the source."""
        pass

    async def close(self):
        await self.client.aclose()
