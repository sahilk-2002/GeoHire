import logging
import uuid

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import Job, JobListResponse, ScrapeResponse
from scrapers.linkedin import scrape_linkedin
from cache import get_cached_jobs, save_jobs


MOCK_JOBS = [
    {
        "title": "Senior Software Engineer",
        "company": "Microsoft", "location": "{loc}",
        "description": "Build and maintain cloud infrastructure services for millions of users worldwide.",
        "requirements": ["5+ years experience", "Distributed systems", "Azure/AWS", "C# or Python"],
        "salary": "$150k – $220k", "job_type": "Full-time",
        "source": "linkedin", "latitude": 18.5204, "longitude": 73.8567,
    },
    {
        "title": "Full Stack Developer",
        "company": "Amazon", "location": "{loc}",
        "description": "Design and implement scalable web applications for e-commerce platforms.",
        "requirements": ["React", "Node.js", "TypeScript", "PostgreSQL"],
        "salary": "$130k – $190k", "job_type": "Full-time",
        "source": "linkedin", "latitude": 18.5204, "longitude": 73.8567,
    },
    {
        "title": "Data Analyst",
        "company": "Deloitte", "location": "{loc}",
        "description": "Analyze business data to provide actionable insights for client decision-making.",
        "requirements": ["SQL", "Python", "Tableau", "Statistics"],
        "salary": "$90k – $130k", "job_type": "Full-time",
        "source": "linkedin", "latitude": 18.5204, "longitude": 73.8567,
    },
    {
        "title": "UX Designer",
        "company": "Adobe", "location": "{loc}",
        "description": "Create intuitive user experiences for creative cloud products.",
        "requirements": ["Figma", "User research", "Prototyping", "Design systems"],
        "salary": "$120k – $170k", "job_type": "Remote",
        "source": "linkedin", "latitude": 18.5204, "longitude": 73.8567,
    },
    {
        "title": "DevOps Engineer",
        "company": "Netflix", "location": "{loc}",
        "description": "Ensure reliability and scalability of streaming infrastructure.",
        "requirements": ["Kubernetes", "Terraform", "CI/CD", "Monitoring"],
        "salary": "$160k – $230k", "job_type": "Full-time",
        "source": "linkedin", "latitude": 18.5204, "longitude": 73.8567,
    },
]


def get_mock_jobs(location: str) -> list[dict]:
    return [{**job, "id": str(uuid.uuid4())[:8], "location": location} for job in MOCK_JOBS]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="GeoHire API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scrape", response_model=ScrapeResponse)
def scrape_location(location: str = Query(..., description="City and state, e.g. 'San Francisco, CA'")):
    try:
        jobs_data = scrape_linkedin(location)
    except Exception as e:
        cached = get_cached_jobs(location)
        if cached is not None:
            jobs = [Job(**j) for j in cached]
            return ScrapeResponse(
                location=location, jobs=jobs, message=f"Scraping failed, returning cached data: {e}"
            )
        logging.warning("Scrape failed and no cache — returning mock data for '%s': %s", location, e)
        mock_data = get_mock_jobs(location)
        save_jobs(location, mock_data)
        jobs = [Job(**j) for j in mock_data]
        return ScrapeResponse(location=location, jobs=jobs, message=f"Scraping failed, returning sample data: {e}")

    jobs = [Job(**j) for j in jobs_data]
    save_jobs(location, jobs_data)
    return ScrapeResponse(location=location, jobs=jobs)


@app.get("/jobs", response_model=JobListResponse)
def get_jobs(location: str = Query(..., description="City and state, e.g. 'San Francisco, CA'")):
    jobs_data = get_cached_jobs(location)
    if jobs_data is None:
        raise HTTPException(status_code=404, detail=f"No cached jobs for '{location}'. POST /scrape first.")
    jobs = [Job(**j) for j in jobs_data]
    return JobListResponse(location=location, jobs=jobs, cached=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, port=8000)
