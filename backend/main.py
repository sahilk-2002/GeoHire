from fastapi import FastAPI, Query, HTTPException
from models import Job, JobListResponse, ScrapeResponse
from scrapers.indeed import scrape_indeed
from cache import get_cached_jobs, save_jobs

app = FastAPI(title="GeoHire API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scrape", response_model=ScrapeResponse)
def scrape_location(location: str = Query(..., description="City and state, e.g. 'San Francisco, CA'")):
    try:
        jobs_data = scrape_indeed(location)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Scraping failed: {str(e)}")

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
