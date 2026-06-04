import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from models import Job, JobListResponse, ScrapeResponse
from scrapers.linkedin import search_linkedin
from scrapers.freeapi import search_careernest, search_arbeitnow
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
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Unsupported format. Upload PDF or DOCX.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        profile = parse_resume(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse resume: {e}")
    return {"id": profile["id"], "profile": profile}


@app.post("/scrape", response_model=ScrapeResponse)
def scrape_location(
    location: str = Query(..., description="City and state, e.g. 'Pune, India'"),
    query: str = Query("", description="Skills/keywords, e.g. 'python java react'"),
):
    errors = []

    try:
        jobs_data = search_linkedin(location, query)
        if jobs_data:
            jobs = [Job(**j) for j in jobs_data]
            save_jobs(location, jobs_data)
            return ScrapeResponse(location=location, jobs=jobs)
    except Exception as e:
        errors.append(f"LinkedIn: {e}")
        logging.warning("LinkedIn failed: %s", e)

    try:
        jobs_data = search_careernest(location)
        if jobs_data:
            jobs = [Job(**j) for j in jobs_data]
            save_jobs(location, jobs_data)
            return ScrapeResponse(location=location, jobs=jobs, message="Career Nest data")
    except Exception as e:
        errors.append(f"Career Nest: {e}")
        logging.warning("Career Nest failed: %s", e)

    try:
        jobs_data = search_arbeitnow(location)
        if jobs_data:
            jobs = [Job(**j) for j in jobs_data]
            save_jobs(location, jobs_data)
            return ScrapeResponse(location=location, jobs=jobs, message="Arbeitnow data")
    except Exception as e:
        errors.append(f"Arbeitnow: {e}")
        logging.warning("Arbeitnow failed: %s", e)

    raise HTTPException(
        status_code=502,
        detail=f"All sources failed: {'; '.join(errors)}"
    )


@app.get("/jobs", response_model=JobListResponse)
def get_jobs(location: str = Query(..., description="City and state, e.g. 'Pune, India'")):
    jobs_data = get_cached_jobs(location)
    if jobs_data is None:
        raise HTTPException(status_code=404, detail=f"No cached jobs for '{location}'. POST /scrape first.")
    jobs = [Job(**j) for j in jobs_data]
    return JobListResponse(location=location, jobs=jobs, cached=True)


@app.post("/match-jobs")
def match_jobs(
    resume_id: str = Query(..., description="Resume ID from /upload-resume"),
    location: str = Query(..., description="City and state, e.g. 'Pune, India'"),
):
    jobs_data = get_cached_jobs(location)
    if not jobs_data:
        raise HTTPException(status_code=404, detail=f"No jobs for '{location}'. POST /scrape first.")

    matched = []
    for j in jobs_data:
        desc = (j.get("description") or "").lower()
        title = (j.get("title") or "").lower()
        score = 0
        if resume_id in (j.get("id") or ""):
            score += 5
        matched.append({"job": j, "score": score})

    matched.sort(key=lambda x: x["score"], reverse=True)
    return {"matches": [m["job"] for m in matched]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, port=8000)
