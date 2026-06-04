import io
import json
import logging
import os
import uuid

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, File, Query, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from models import Job, JobListResponse, ResumeProfile, ResumeUploadResponse, ScrapeResponse
from scrapers.indeed import scrape_indeed
from cache import get_cached_jobs, save_jobs

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# --- Config from .env ---
AI_API_KEY = os.getenv("OPENCODE_ZEN_API_KEY", "")
_raw_base_url = os.getenv("OPENCODE_ZEN_API_BASE_URL", "https://opencode.ai/zen/v1")
AI_BASE_URL = _raw_base_url.replace("/chat/completions", "").rstrip("/")
AI_MODEL = os.getenv("OPENCODE_ZEN_API_MODEL", "deepseek-v4-flash-free")

if not AI_API_KEY or AI_API_KEY == "***":
    logger.warning("OPENCODE_ZEN_API_KEY is not set in .env — resume parsing will fail")
else:
    logger.info("AI configured: base=%s model=%s key=%s…", AI_BASE_URL, AI_MODEL, AI_API_KEY[:12])

app = FastAPI(title="GeoHire API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _extract_text_from_pdf(content: bytes) -> str:
    from PyPDF2 import PdfReader
    reader = PdfReader(io.BytesIO(content))
    texts = []
    for p in reader.pages:
        t = p.extract_text()
        if t and t.strip():
            texts.append(t.strip())
    result = "\n".join(texts)
    logger.info("Extracted %d chars from %d PDF pages", len(result), len(reader.pages))
    if not result:
        logger.warning("PDF extraction yielded no text — file may be scanned/image-only")
    return result


def _extract_text_from_docx(content: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_text(file: UploadFile) -> str:
    content = file.file.read()
    if file.filename and file.filename.endswith(".pdf"):
        return _extract_text_from_pdf(content)
    elif file.filename and file.filename.endswith(".docx"):
        return _extract_text_from_docx(content)
    else:
        content_type = file.content_type or ""
        if "pdf" in content_type:
            return _extract_text_from_pdf(content)
        elif "word" in content_type or "docx" in content_type or "officedocument" in content_type:
            return _extract_text_from_docx(content)
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload a PDF or DOCX file.")


def _parse_resume_with_ai(text: str) -> ResumeProfile:
    if not AI_API_KEY or AI_API_KEY == "***":
        raise HTTPException(
            status_code=500,
            detail="OPENCODE_ZEN_API_KEY not configured in backend/.env. "
                   "Set it to your OpenCode Zen API key and restart the server.",
        )

    client = OpenAI(
        api_key=AI_API_KEY,
        base_url=AI_BASE_URL,
    )

    prompt = (
        "You are a resume parser. Extract structured information from the resume text below. "
        "Respond with valid JSON only (no markdown, no code fences) in this exact format:\n"
        "{\n"
        '  "skills": ["skill1", "skill2", ...],\n'
        '  "experience_years": <number or null>,\n'
        '  "job_title_keywords": ["keyword1", "keyword2", ...],\n'
        '  "summary": "brief one-line summary of the candidate profile"\n'
        "}\n\n"
        "- skills: extract technical and soft skills explicitly mentioned.\n"
        "- experience_years: total years of professional experience; use null if unclear.\n"
        "- job_title_keywords: 3-5 key job title words/phrases suitable for a job search query (e.g. 'software engineer', 'product manager', 'data scientist').\n"
        "- summary: one sentence describing the candidate's seniority and primary domain.\n\n"
        f"---RESUME TEXT (truncated to ~2048 tokens)---\n{text[:8000]}"
    )

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": "You are a precise resume parser. Output only JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=8192,
    )

    msg = response.choices[0].message
    finish = response.choices[0].finish_reason
    if not msg.content or not msg.content.strip():
        hint = " (max_tokens too low)" if finish == "length" else ""
        logger.warning("AI returned empty response (finish_reason=%s)%s", finish, hint)
        raise HTTPException(status_code=502, detail=f"AI parser returned empty response; finish_reason={finish}{hint}")

    raw = msg.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    data = None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        import re
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group())
            except json.JSONDecodeError:
                pass

    if data is None:
        logger.error("AI returned invalid JSON (finish_reason=%s): %.500s", response.choices[0].finish_reason, raw)
        raise HTTPException(status_code=502, detail="AI parser returned malformed response")

    profile = ResumeProfile(
        skills=data.get("skills", []),
        experience_years=data.get("experience_years"),
        job_title_keywords=data.get("job_title_keywords", []),
        summary=data.get("summary"),
    )
    logger.info("AI parsed resume -> %s", profile.model_dump_json())
    return profile


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scrape", response_model=ScrapeResponse)
def scrape_location(location: str = Query(..., description="City and state, e.g. 'San Francisco, CA'")):
    try:
        jobs_data = scrape_indeed(location)
    except Exception as e:
        cached = get_cached_jobs(location)
        if cached is not None:
            jobs = [Job(**j) for j in cached]
            return ScrapeResponse(
                location=location, jobs=jobs, message=f"Scraping failed, returning cached data: {e}"
            )
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


@app.post("/upload-resume", response_model=ResumeUploadResponse)
def upload_resume(file: UploadFile = File(...)):
    resume_id = str(uuid.uuid4())
    text = _extract_text(file)
    logger.info("Extracted resume text (first 500 chars): %.500s", text)
    if len(text) > 500:
        logger.info("Extracted resume text (chars 500-1000): %.500s", text[500:1000])
    profile = _parse_resume_with_ai(text)
    return ResumeUploadResponse(id=resume_id, profile=profile)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, port=8000)
