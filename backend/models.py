from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: list[str] = []
    salary: Optional[str] = None
    job_type: Optional[str] = None
    posted_date: Optional[str] = None
    source: str = "indeed"
    source_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class JobListResponse(BaseModel):
    location: str
    jobs: list[Job]
    cached: bool = False


class ScrapeResponse(BaseModel):
    location: str
    jobs: list[Job]
    message: str = "Scraping complete"
