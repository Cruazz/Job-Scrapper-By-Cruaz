from abc import ABC, abstractmethod
from typing import List
from models.schemas import JobListingCreate
import hashlib

class BaseParser(ABC):
    @abstractmethod
    def parse(self, raw_data: any) -> List[JobListingCreate]:
        """Parse raw data into JobListingCreate models."""
        pass

    def generate_id(self, title: str, company: str, location: str) -> str:
        """Generate a unique hash for a job listing."""
        content = f"{title.lower()}|{company.lower()}|{location.lower()}"
        return hashlib.sha256(content.encode()).hexdigest()
