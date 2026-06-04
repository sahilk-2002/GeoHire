import logging

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from fastapi import UploadFile, File

from models import Job, JobListResponse, ScrapeResponse
from scrapers.indeed import scrape_indeed
from scrapers.demo import generate_jobs
from cache import get_cached_jobs, save_jobs
from parser import parse_resume

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


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if file.filename is None:
        raise HTTPException(status_code=400, detail="No filename")
    content = await file.read()
    try:
        profile = parse_resume(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": profile["id"], "profile": profile}


@app.post("/scrape", response_model=ScrapeResponse)
def scrape_location(location: str = Query(..., description="City and state, e.g. 'San Francisco, CA'")):
    try:
        jobs_data = scrape_indeed(location)
        if jobs_data:
            jobs = [Job(**j) for j in jobs_data]
            save_jobs(location, jobs_data)
            return ScrapeResponse(location=location, jobs=jobs)
    except Exception as e:
        logging.warning("Indeed scrape failed: %s", e)

    # Fallback: generate demo jobs for this location
    logging.info("Generating demo jobs for %s", location)
    jobs_data = generate_jobs(location)
    jobs = [Job(**j) for j in jobs_data]
    save_jobs(location, jobs_data)
    return ScrapeResponse(location=location, jobs=jobs, message="Demo data – real Indeed scraping unavailable")


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
