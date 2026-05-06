from typing import List, Tuple
from models.schemas import JobListingCreate
from config.settings import settings

class JobMatcher:
    def __init__(self, keywords: List[str], locations: List[str], min_salary: int = None):
        self.keywords = [k.lower() for k in keywords]
        self.locations = [l.lower() for l in locations]
        self.min_salary = min_salary

    def score_job(self, job: JobListingCreate) -> float:
        score = 0.0
        
        # Title match
        title_lower = job.title.lower()
        if any(k in title_lower for k in self.keywords):
            score += 0.4
            
        # Description match
        desc_lower = job.description.lower()
        if any(k in desc_lower for k in self.keywords):
            score += 0.2
            
        # Location match
        loc_lower = job.location.lower()
        if any(l in loc_lower for l in self.locations) or "remote" in loc_lower:
            score += 0.2
            
        # Salary match (if available)
        # This is simplified; real salary parsing would be needed
        if self.min_salary and job.salary_range:
            # Assume salary_range contains a number we can extract
            # For MVP, we'll just give a small boost if salary is present
            score += 0.1
            
        return round(min(score, 1.0), 2)

    def is_match(self, job: JobListingCreate, threshold: float = 0.5) -> Tuple[bool, float]:
        score = self.score_job(job)
        return score >= threshold, score
