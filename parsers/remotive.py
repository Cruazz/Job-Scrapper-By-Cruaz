from typing import List
from parsers.base import BaseParser
from models.schemas import JobListingCreate
import hashlib
from datetime import datetime

class RemotiveParser(BaseParser):
    def parse(self, raw_data: List[dict]) -> List[JobListingCreate]:
        jobs = []
        for item in raw_data:
            data = item.get("data", {})
            if not data:
                continue
                
            try:
                job = JobListingCreate(
                    title=data.get("title", ""),
                    company=data.get("company_name", ""),
                    location=data.get("candidate_required_location", "Remote"),
                    description=data.get("description", ""),
                    url=data.get("url", ""),
                    source="remotive",
                    salary_range=data.get("salary", "Not specified")
                )
                jobs.append(job)
            except Exception:
                continue
        return jobs

    def generate_id(self, title: str, company: str, location: str) -> str:
        unique_str = f"{title}-{company}-remotive".lower().replace(" ", "")
        return hashlib.md5(unique_str.encode()).hexdigest()
