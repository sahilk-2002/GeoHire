# GeoHire Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a location-based job discovery platform with resume matching, free APIs only, following the design spec.

**Architecture:** FastAPI backend (scrapers, resume parser, TF-IDF matcher) + Vue 3 frontend (Pinia, Leaflet, TailwindCSS). JSON file storage. No database.

**Tech Stack:** Python 3.11+, FastAPI, BeautifulSoup/aiohttp, PyMuPDF, scikit-learn (TF-IDF); Vue 3, Vite, Pinia, vue-leaflet, TailwindCSS.

---

## File Structure

```
D:\GeoHire\
├── backend\
│   ├── main.py                 # FastAPI app, CORS, startup
│   ├── models.py               # Pydantic data models
│   ├── scrapers\
│   │   ├── __init__.py
│   │   ├── base.py             # Base scraper with rate limiting
│   │   ├── indeed.py           # Indeed scraper
│   │   └── utils.py            # User-agent rotation, slug helpers
│   ├── parser\
│   │   ├── __init__.py
│   │   ├── resume_parser.py    # PDF/DOCX text + skill extraction
│   │   └── skills_db.py        # Skill keyword list
│   ├── matcher\
│   │   ├── __init__.py
│   │   └── matcher.py          # TF-IDF cosine similarity matcher
│   ├── routes\
│   │   ├── __init__.py
│   │   ├── jobs.py             # GET /jobs, GET /jobs/{id}, POST /scrape
│   │   ├── resume.py           # POST /upload-resume
│   │   ├── match.py            # POST /match-jobs
│   │   └── locations.py        # GET /locations/suggest
│   └── data\
│       ├── jobs\               # Per-location job JSON cache
│       └── resumes\            # Uploaded resume files
├── frontend\
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src\
│       ├── main.js
│       ├── App.vue
│       ├── style.css
│       ├── router\index.js
│       ├── stores\
│       │   ├── jobs.js
│       │   ├── resume.js
│       │   └── map.js
│       ├── components\
│       │   ├── AppNav.vue
│       │   ├── JobCard.vue
│       │   ├── SearchBar.vue
│       │   ├── ViewToggle.vue
│       │   ├── JobMap.vue
│       │   ├── MapPin.vue
│       │   ├── UploadZone.vue
│       │   └── MatchScore.vue
│       └── views\
│           ├── JobDiscovery.vue
│           ├── JobDetails.vue
│           ├── ResumeUpload.vue
│           ├── MapView.vue
│           └── Profile.vue
├── docs\superpowers\specs\2026-06-04-geohire-design.md
└── requirements.txt
```

---

### Task 1: Backend Project Setup + Data Models

**Files:**
- Create: `backend/__init__.py` (empty)
- Create: `backend/main.py`
- Create: `backend/models.py`
- Create: `requirements.txt`
- Create: `backend/data/__init__.py` (empty)
- Modify: `README.md`

- [ ] **Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
aiohttp==3.10.0
beautifulsoup4==4.12.0
PyMuPDF==1.24.0
python-docx==1.1.0
scikit-learn==1.5.0
python-multipart==0.0.9
```

- [ ] **Step 2: Create Pydantic models in backend/models.py**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: list[str]
    salary: Optional[str] = None
    job_type: Optional[str] = None
    posted_date: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ResumeProfile(BaseModel):
    id: str
    skills: list[str]
    experience_years: Optional[float] = None
    job_titles: list[str]
    education: list[str]
    raw_text: str

class MatchResult(BaseModel):
    job: Job
    score: float

class ScrapeRequest(BaseModel):
    location: str

class ScrapeResponse(BaseModel):
    location: str
    jobs: list[Job]
    cached: bool
```

- [ ] **Step 3: Create FastAPI app in backend/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import jobs, resume, match, locations

app = FastAPI(title="GeoHire API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(resume.router, prefix="/api", tags=["resume"])
app.include_router(match.router, prefix="/api", tags=["match"])
app.include_router(locations.router, prefix="/api", tags=["locations"])

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Create route __init__.py files**

```python
# backend/routes/__init__.py (empty)
# backend/scrapers/__init__.py (empty)
# backend/parser/__init__.py (empty)
# backend/matcher/__init__.py (empty)
```

- [ ] **Step 5: Verify backend starts**

Run:
```powershell
cd D:\GeoHire
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Expected: Server starts at http://localhost:8000, `GET /api/health` returns `{"status": "ok"}`

- [ ] **Step 6: Commit**

```bash
git add backend/ requirements.txt README.md
git commit -m "feat: backend project setup with FastAPI and data models"
```

---

### Task 2: JSON Storage Helpers

**Files:**
- Create: `backend/storage.py`

This centralizes all file I/O so scrapers/routes don't touch filesystem directly.

- [ ] **Step 1: Create backend/storage.py**

```python
import json
import os
import uuid
from pathlib import Path
from typing import Optional
from backend.models import Job, ResumeProfile

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
JOBS_DIR = DATA_DIR / "jobs"
RESUMES_DIR = DATA_DIR / "resumes"
PROFILES_PATH = DATA_DIR / "resume-profiles.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
JOBS_DIR.mkdir(parents=True, exist_ok=True)
RESUMES_DIR.mkdir(parents=True, exist_ok=True)

def location_slug(location: str) -> str:
    return location.lower().replace(", ", "-").replace(" ", "-")

def save_jobs(location: str, jobs: list[Job]):
    path = JOBS_DIR / f"{location_slug(location)}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump([j.model_dump() for j in jobs], f, indent=2, ensure_ascii=False)

def load_jobs(location: str) -> Optional[list[Job]]:
    path = JOBS_DIR / f"{location_slug(location)}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return [Job(**j) for j in json.load(f)]

def save_resume_file(filename: str, content: bytes) -> str:
    file_id = str(uuid.uuid4())
    ext = Path(filename).suffix
    dest = RESUMES_DIR / f"{file_id}{ext}"
    with open(dest, "wb") as f:
        f.write(content)
    return file_id

def get_resume_path(file_id: str) -> Optional[Path]:
    for ext in [".pdf", ".docx"]:
        p = RESUMES_DIR / f"{file_id}{ext}"
        if p.exists():
            return p
    return None

def save_resume_profile(profile: ResumeProfile):
    profiles = {}
    if PROFILES_PATH.exists():
        with open(PROFILES_PATH, "r", encoding="utf-8") as f:
            profiles = json.load(f)
    profiles[profile.id] = profile.model_dump()
    with open(PROFILES_PATH, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)

def load_resume_profile(resume_id: str) -> Optional[ResumeProfile]:
    if not PROFILES_PATH.exists():
        return None
    with open(PROFILES_PATH, "r", encoding="utf-8") as f:
        profiles = json.load(f)
    data = profiles.get(resume_id)
    return ResumeProfile(**data) if data else None
```

- [ ] **Step 2: Commit**

```bash
git add backend/storage.py
git commit -m "feat: JSON storage helpers for jobs, resumes, profiles"
```

---

### Task 3: Scraper Utilities and Base Class

**Files:**
- Create: `backend/scrapers/__init__.py` (empty)
- Create: `backend/scrapers/utils.py`
- Create: `backend/scrapers/base.py`

- [ ] **Step 1: Create backend/scrapers/utils.py**

```python
import random
import asyncio

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

def random_user_agent() -> str:
    return random.choice(USER_AGENTS)

async def rate_limit_delay(min_sec=2, max_sec=6):
    await asyncio.sleep(random.uniform(min_sec, max_sec))
```

- [ ] **Step 2: Create backend/scrapers/base.py**

```python
from abc import ABC, abstractmethod
from backend.models import Job

class BaseScraper(ABC):
    source_name: str = ""

    @abstractmethod
    async def scrape_location(self, location: str) -> list[Job]:
        pass
```

- [ ] **Step 3: Commit**

```bash
git add backend/scrapers/
git commit -m "feat: scraper base class and utilities"
```

---

### Task 4: Indeed Scraper

**Files:**
- Create: `backend/scrapers/indeed.py`

- [ ] **Step 1: Create backend/scrapers/indeed.py**

```python
import re
import uuid
from bs4 import BeautifulSoup
import aiohttp
from backend.scrapers.base import BaseScraper
from backend.scrapers.utils import random_user_agent, rate_limit_delay
from backend.models import Job

class IndeedScraper(BaseScraper):
    source_name = "indeed"

    async def scrape_location(self, location: str) -> list[Job]:
        query = location.replace(" ", "+")
        url = f"https://www.indeed.com/jobs?q=&l={query}"
        headers = {"User-Agent": random_user_agent()}
        jobs = []

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=30) as resp:
                    if resp.status != 200:
                        return jobs
                    html = await resp.text()
            except Exception:
                return jobs

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("[class*='job_seen_beacon'], [class*='resultContent'], .jobCard")
        for card in cards[:25]:
            title_el = card.select_one("h2 a, [class*='jobTitle'], [data-testid='job-title']")
            company_el = card.select_one("[class*='companyName'], [data-testid='company-name'], .companyName")
            location_el = card.select_one("[class*='companyLocation'], [data-testid='company-location']")
            salary_el = card.select_one("[class*='salary-snippet'], [class*='estimated-salary']")
            desc_el = card.select_one("[class*='job-snippet'], li")
            url_el = card.select_one("h2 a")

            title = title_el.get_text(strip=True) if title_el else "Unknown"
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            loc = location_el.get_text(strip=True) if location_el else location
            salary = salary_el.get_text(strip=True) if salary_el else None
            desc = desc_el.get_text(strip=True) if desc_el else ""
            job_url = "https://www.indeed.com" + url_el["href"] if url_el and url_el.get("href") else url

            if title == "Unknown":
                continue

            jobs.append(Job(
                id=str(uuid.uuid4()),
                title=title,
                company=company,
                location=loc,
                description=desc,
                requirements=[],
                salary=salary,
                source=self.source_name,
                source_url=job_url,
            ))

            await rate_limit_delay()

        return jobs
```

- [ ] **Step 2: Add Indeed scraper to a scrapers registry**

Create `backend/scrapers/__init__.py`:
```python
from backend.scrapers.indeed import IndeedScraper

SCRAPERS = {
    "indeed": IndeedScraper(),
}
```

- [ ] **Step 3: Commit**

```bash
git add backend/scrapers/
git commit -m "feat: Indeed job scraper"
```

---

### Task 5: Resume Parser

**Files:**
- Create: `backend/parser/skills_db.py`
- Create: `backend/parser/resume_parser.py`

- [ ] **Step 1: Create backend/parser/skills_db.py**

```python
SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "react", "vue", "angular",
    "node", "express", "django", "flask", "fastapi", "sql", "nosql", "postgresql",
    "mysql", "mongodb", "redis", "docker", "kubernetes", "aws", "azure", "gcp",
    "git", "ci/cd", "jenkins", "terraform", "html", "css", "sass", "tailwind",
    "figma", "sketch", "photoshop", "ui/ux", "agile", "scrum", "jira",
    "rest", "graphql", "api", "microservices", "machine learning", "data science",
    "tensorflow", "pytorch", "pandas", "numpy", "pytest", "jest", "cypress",
    "leadership", "product management", "project management", "communication",
    "c++", "c#", "go", "rust", "swift", "kotlin", "ruby", "php", "scala",
    "tableau", "power bi", "excel", "analytics", "a/b testing",
]
```

- [ ] **Step 2: Create backend/parser/resume_parser.py**

```python
import re
import uuid
from pathlib import Path
from backend.models import ResumeProfile
from backend.parser.skills_db import SKILL_KEYWORDS

def extract_text_from_pdf(path: Path) -> str:
    import fitz
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_text_from_docx(path: Path) -> str:
    from docx import Document
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = set()
    for skill in SKILL_KEYWORDS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found.add(skill)
    return sorted(found)

def estimate_experience_years(text: str) -> float:
    years = re.findall(r'(\d+)\+?\s*years?', text.lower())
    if years:
        return max(int(y) for y in years)
    return 0.0

def extract_job_titles(text: str) -> list[str]:
    title_patterns = [
        r'(?:^|\n)\s*(senior|lead|principal|junior|associate)?\s*(software engineer|developer|designer|manager|analyst|architect|consultant|director|engineer|scientist)',
    ]
    titles = []
    for pattern in title_patterns:
        titles.extend(m.group(0).strip() for m in re.finditer(pattern, text, re.IGNORECASE))
    return titles[:10]

def extract_education(text: str) -> list[str]:
    degrees = re.findall(
        r'(bachelor|master|phd|b\.?s\.?|m\.?s\.?|ph\.?d\.?|bachelor\'s|master\'s|b\.tech|m\.tech)'
        r'(?:\s+(?:of|in|of science in|of arts in))?\s*([^,\n]*)',
        text, re.IGNORECASE
    )
    return [f"{d[0]} {d[1]}".strip() for d in degrees if d[1].strip()]

def parse_resume(file_path: Path) -> ResumeProfile:
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported format: {ext}")

    return ResumeProfile(
        id=str(uuid.uuid4()),
        skills=extract_skills(text),
        experience_years=estimate_experience_years(text),
        job_titles=extract_job_titles(text),
        education=extract_education(text),
        raw_text=text,
    )
```

- [ ] **Step 3: Commit**

```bash
git add backend/parser/
git commit -m "feat: resume parser (PDF/DOCX) with skill extraction"
```

---

### Task 6: Matching Engine

**Files:**
- Create: `backend/matcher/matcher.py`

- [ ] **Step 1: Create backend/matcher/matcher.py**

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.models import Job, ResumeProfile, MatchResult

def preprocess(text: str) -> str:
    return text.lower()

def match_resume_to_jobs(resume: ResumeProfile, jobs: list[Job]) -> list[MatchResult]:
    if not jobs:
        return []

    resume_text = preprocess(" ".join(resume.skills * 3 + resume.job_titles * 2 + resume.education))

    job_docs = []
    for job in jobs:
        doc = f"{job.title} {job.company} {job.description} {' '.join(job.requirements)}"
        job_docs.append(preprocess(doc))

    documents = [resume_text] + job_docs
    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(documents)
    resume_vec = tfidf_matrix[0:1]
    job_vecs = tfidf_matrix[1:]

    scores = cosine_similarity(resume_vec, job_vecs)[0]
    results = [MatchResult(job=job, score=round(float(scores[i]) * 100, 1))
               for i, job in enumerate(jobs)]
    results.sort(key=lambda r: r.score, reverse=True)
    return results
```

- [ ] **Step 2: Commit**

```bash
git add backend/matcher/
git commit -m "feat: TF-IDF job matching engine"
```

---

### Task 7: Backend API Routes

**Files:**
- Create: `backend/routes/jobs.py`
- Create: `backend/routes/resume.py`
- Create: `backend/routes/match.py`
- Create: `backend/routes/locations.py`

- [ ] **Step 1: Create backend/routes/jobs.py**

```python
from fastapi import APIRouter, BackgroundTasks, Query
from backend.models import Job, ScrapeResponse
from backend.storage import save_jobs, load_jobs
from backend.scrapers import SCRAPERS
import asyncio

router = APIRouter()

async def run_scrapers(location: str):
    all_jobs = []
    for name, scraper in SCRAPERS.items():
        try:
            jobs = await scraper.scrape_location(location)
            all_jobs.extend(jobs)
        except Exception:
            pass
    save_jobs(location, all_jobs)
    return all_jobs

@router.get("/jobs")
async def get_jobs(location: str = Query(...)):
    cached = load_jobs(location)
    if cached:
        return ScrapeResponse(location=location, jobs=cached, cached=True)
    return ScrapeResponse(location=location, jobs=[], cached=False)

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, location: str = Query(...)):
    jobs = load_jobs(location)
    if not jobs:
        return None
    for job in jobs:
        if job.id == job_id:
            return job
    return None

@router.post("/scrape")
async def scrape_jobs(location: str = Query(...), background_tasks: BackgroundTasks = None):
    background_tasks.add_task(run_scrapers, location)
    return {"message": "Scraping started", "location": location}
```

- [ ] **Step 2: Create backend/routes/resume.py**

```python
from fastapi import APIRouter, UploadFile, File
from backend.storage import save_resume_file, get_resume_path, save_resume_profile
from backend.parser.resume_parser import parse_resume

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf", "docx"]:
        return {"error": "Only PDF and DOCX files are supported"}, 400

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        return {"error": "File too large (max 10MB)"}, 400

    file_id = save_resume_file(file.filename, content)
    file_path = get_resume_path(file_id)
    profile = parse_resume(file_path)
    save_resume_profile(profile)
    return {"resume_id": file_id, "profile": profile.model_dump()}
```

- [ ] **Step 3: Create backend/routes/match.py**

```python
from fastapi import APIRouter, Query
from backend.storage import load_resume_profile, load_jobs
from backend.matcher.matcher import match_resume_to_jobs

router = APIRouter()

@router.post("/match-jobs")
async def match_jobs(resume_id: str = Query(...), location: str = Query(...)):
    profile = load_resume_profile(resume_id)
    if not profile:
        return {"error": "Resume not found"}, 404

    jobs = load_jobs(location)
    if not jobs:
        return {"error": "No jobs found for location. Try scraping first."}, 404

    results = match_resume_to_jobs(profile, jobs)
    return {"location": location, "matches": [r.model_dump() for r in results]}
```

- [ ] **Step 4: Create backend/routes/locations.py**

```python
from fastapi import APIRouter, Query
import aiohttp

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

router = APIRouter()

@router.get("/locations/suggest")
async def suggest_locations(q: str = Query(...)):
    params = {"q": q, "format": "json", "limit": 5}
    headers = {"User-Agent": "GeoHire/1.0"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(NOMINATIM_URL, params=params, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                return [{"display_name": r["display_name"], "lat": r["lat"], "lon": r["lon"]} for r in data]
        except Exception:
            return []
```

- [ ] **Step 5: Commit**

```bash
git add backend/routes/
git commit -m "feat: API routes for jobs, resume, matching, and locations"
```

---

### Task 8: Frontend Project Setup

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/style.css`
- Create: `frontend/src/router/index.js`

- [ ] **Step 1: Create frontend/package.json**

```json
{
  "name": "geohire-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.0",
    "leaflet": "^1.9.4",
    "vue-leaflet": "^0.10.1",
    "@tailwindcss/vite": "^4.0.0",
    "tailwindcss": "^4.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.4.0"
  }
}
```

- [ ] **Step 2: Create frontend/vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: { port: 5173, proxy: { '/api': 'http://localhost:8000' } }
})
```

- [ ] **Step 3: Create frontend/index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
  <title>GeoHire</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: Create frontend/src/main.js**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 5: Create frontend/src/style.css**

```css
@import "tailwindcss";

@theme {
  --color-background: #f8f9ff;
  --color-surface: #f8f9ff;
  --color-surface-dim: #cbdbf5;
  --color-surface-container-lowest: #ffffff;
  --color-surface-container-low: #eff4ff;
  --color-surface-container: #e5eeff;
  --color-surface-container-high: #dce9ff;
  --color-surface-container-highest: #d3e4fe;
  --color-on-surface: #0b1c30;
  --color-on-surface-variant: #464555;
  --color-primary: #3525cd;
  --color-on-primary: #ffffff;
  --color-primary-container: #4f46e5;
  --color-on-primary-container: #dad7ff;
  --color-secondary: #006a61;
  --color-on-secondary: #ffffff;
  --color-secondary-container: #86f2e4;
  --color-on-secondary-container: #006f66;
  --color-tertiary: #684000;
  --color-error: #ba1a1a;
  --color-outline: #777587;
  --color-outline-variant: #c7c4d8;
  --font-family-sans: Inter, sans-serif;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
}

body {
  font-family: Inter, sans-serif;
  background-color: var(--color-background);
  color: var(--color-on-surface);
  -webkit-font-smoothing: antialiased;
}
```

- [ ] **Step 6: Create frontend/src/App.vue**

```vue
<template>
  <div class="min-h-screen bg-background">
    <router-view />
    <AppNav />
  </div>
</template>

<script setup>
import AppNav from './components/AppNav.vue'
</script>
```

- [ ] **Step 7: Create frontend/src/router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'JobDiscovery', component: () => import('../views/JobDiscovery.vue') },
  { path: '/jobs/:id', name: 'JobDetails', component: () => import('../views/JobDetails.vue') },
  { path: '/upload', name: 'ResumeUpload', component: () => import('../views/ResumeUpload.vue') },
  { path: '/map', name: 'MapView', component: () => import('../views/MapView.vue') },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
```

- [ ] **Step 8: Install dependencies and verify**

```powershell
cd D:\GeoHire\frontend
npm install
npx vite --port 5173
```
Expected: Dev server starts at http://localhost:5173

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat: frontend project setup with Vue 3, Pinia, router, Tailwind"
```

---

### Task 9: Pinia Stores

**Files:**
- Create: `frontend/src/stores/jobs.js`
- Create: `frontend/src/stores/resume.js`
- Create: `frontend/src/stores/map.js`

- [ ] **Step 1: Create frontend/src/stores/jobs.js**

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useJobsStore = defineStore('jobs', () => {
  const jobs = ref([])
  const matches = ref([])
  const location = ref('')
  const loading = ref(false)

  async function fetchJobs(loc) {
    loading.value = true
    location.value = loc
    try {
      const res = await fetch(`/api/jobs?location=${encodeURIComponent(loc)}`)
      const data = await res.json()
      jobs.value = data.jobs || []
    } catch (e) {
      jobs.value = []
    } finally {
      loading.value = false
    }
  }

  async function scrapeJobs(loc) {
    loading.value = true
    try {
      await fetch(`/api/scrape?location=${encodeURIComponent(loc)}`, { method: 'POST' })
      setTimeout(() => fetchJobs(loc), 3000)
    } catch (e) {
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function matchJobs(resumeId, loc) {
    loading.value = true
    try {
      const res = await fetch(`/api/match-jobs?resume_id=${resumeId}&location=${encodeURIComponent(loc)}`, { method: 'POST' })
      const data = await res.json()
      matches.value = data.matches || []
    } catch (e) {
      matches.value = []
    } finally {
      loading.value = false
    }
  }

  return { jobs, matches, location, loading, fetchJobs, scrapeJobs, matchJobs }
})
```

- [ ] **Step 2: Create frontend/src/stores/resume.js**

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useResumeStore = defineStore('resume', () => {
  const resumeId = ref(null)
  const profile = ref(null)
  const uploading = ref(false)

  async function uploadResume(file) {
    uploading.value = true
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await fetch('/api/upload-resume', { method: 'POST', body: form })
      const data = await res.json()
      if (data.resume_id) {
        resumeId.value = data.resume_id
        profile.value = data.profile
      }
    } catch (e) {
      console.error(e)
    } finally {
      uploading.value = false
    }
  }

  function clear() {
    resumeId.value = null
    profile.value = null
  }

  return { resumeId, profile, uploading, uploadResume, clear }
})
```

- [ ] **Step 3: Create frontend/src/stores/map.js**

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMapStore = defineStore('map', () => {
  const center = ref([20, 0])
  const zoom = ref(2)
  const selectedJob = ref(null)

  function setCenter(lat, lon) {
    center.value = [lat, lon]
    zoom.value = 11
  }

  function selectJob(job) {
    selectedJob.value = job
  }

  function clearSelection() {
    selectedJob.value = null
  }

  return { center, zoom, selectedJob, setCenter, selectJob, clearSelection }
})
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/stores/
git commit -m "feat: Pinia stores for jobs, resume, and map state"
```

---

### Task 10: Core Frontend Components

**Files:**
- Create: `frontend/src/components/AppNav.vue`
- Create: `frontend/src/components/JobCard.vue`
- Create: `frontend/src/components/SearchBar.vue`
- Create: `frontend/src/components/ViewToggle.vue`
- Create: `frontend/src/components/MatchScore.vue`

- [ ] **Step 1: Create frontend/src/components/AppNav.vue**

```vue
<template>
  <nav class="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-4 pt-2 bg-surface shadow-lg rounded-t-xl">
    <router-link v-for="item in items" :key="item.path" :to="item.path"
      class="flex flex-col items-center justify-center px-4 py-1 rounded-full transition-all duration-150 active:scale-90"
      :class="$route.path === item.path
        ? 'bg-secondary-container text-on-secondary-container'
        : 'text-on-surface-variant hover:bg-surface-container-high'">
      <span class="material-symbols-outlined text-sm">{{ item.icon }}</span>
      <span class="font-label-sm text-label-sm">{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
const items = [
  { path: '/', icon: 'work', label: 'Jobs' },
  { path: '/map', icon: 'map', label: 'Map' },
  { path: '/upload', icon: 'upload_file', label: 'Upload' },
  { path: '/profile', icon: 'person', label: 'Profile' },
]
</script>
```

- [ ] **Step 2: Create frontend/src/components/JobCard.vue**

```vue
<template>
  <div @click="$router.push(`/jobs/${job.id}`)"
    class="bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm hover:shadow-md hover:border-primary/30 transition-all cursor-pointer group">
    <div class="flex justify-between items-start mb-4">
      <div class="w-12 h-12 rounded-lg bg-surface-container p-2 flex items-center justify-center text-primary font-bold text-lg">
        {{ job.company.charAt(0) }}
      </div>
      <span @click.stop="toggleBookmark"
        class="material-symbols-outlined text-outline group-hover:text-primary transition-colors cursor-pointer"
        :style="bookmarked ? { fontVariationSettings: \"'FILL' 1\" } : {}">
        bookmark
      </span>
    </div>
    <h3 class="font-headline-sm text-headline-sm text-primary mb-1">{{ job.title }}</h3>
    <p class="font-body-md text-on-surface-variant mb-4">{{ job.company }}</p>
    <div class="flex flex-wrap gap-2 mb-6">
      <span v-if="matchScore !== undefined"
        class="px-2 py-1 bg-secondary-container/50 text-on-secondary-container text-[10px] font-bold rounded uppercase tracking-wider">
        {{ matchScore }}% Match
      </span>
      <span v-if="job.job_type"
        class="px-2 py-1 bg-surface-container text-on-surface-variant text-[10px] font-bold rounded uppercase tracking-wider">
        {{ job.job_type }}
      </span>
    </div>
    <div class="flex items-center justify-between pt-4 border-t border-outline-variant">
      <div class="flex items-center gap-1 text-on-surface-variant">
        <span class="material-symbols-outlined text-sm">location_on</span>
        <span class="text-label-sm">{{ job.location }}</span>
      </div>
      <p v-if="job.salary" class="text-label-sm font-semibold text-secondary">{{ job.salary }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  job: Object,
  matchScore: Number
})

const bookmarks = JSON.parse(localStorage.getItem('geohire_bookmarks') || '[]')
const bookmarked = computed(() => bookmarks.includes(props.job.id))

function toggleBookmark() {
  const idx = bookmarks.indexOf(props.job.id)
  if (idx > -1) bookmarks.splice(idx, 1)
  else bookmarks.push(props.job.id)
  localStorage.setItem('geohire_bookmarks', JSON.stringify(bookmarks))
}
</script>
```

- [ ] **Step 3: Create frontend/src/components/SearchBar.vue**

```vue
<template>
  <section class="mb-lg">
    <div class="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant p-4 flex flex-col md:flex-row gap-4">
      <div class="flex-1 flex items-center gap-3 bg-surface-container-low px-4 py-3 rounded-lg border border-transparent focus-within:border-primary transition-colors">
        <span class="material-symbols-outlined text-outline">work</span>
        <input v-model="titleQuery" @keyup.enter="$emit('search', titleQuery, locationQuery)"
          class="bg-transparent border-none focus:ring-0 w-full font-body-md text-on-surface placeholder:text-outline p-0 outline-none"
          placeholder="Job title or keywords" type="text" />
      </div>
      <div class="flex-1 flex items-center gap-3 bg-surface-container-low px-4 py-3 rounded-lg border border-transparent focus-within:border-primary transition-colors">
        <span class="material-symbols-outlined text-outline">location_on</span>
        <input v-model="locationQuery" @keyup.enter="$emit('search', titleQuery, locationQuery)"
          class="bg-transparent border-none focus:ring-0 w-full font-body-md text-on-surface placeholder:text-outline p-0 outline-none"
          placeholder="Location" type="text" />
      </div>
      <button @click="$emit('search', titleQuery, locationQuery)"
        class="bg-primary hover:opacity-90 text-on-primary px-8 py-3 rounded-lg font-label-md transition-all active:scale-95">
        Search
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

defineEmits(['search'])
const titleQuery = ref('')
const locationQuery = ref('')
</script>
```

- [ ] **Step 4: Create frontend/src/components/ViewToggle.vue**

```vue
<template>
  <div class="bg-surface-container-high p-1 rounded-full flex items-center">
    <button @click="$emit('toggle', 'list')"
      class="px-6 py-1.5 rounded-full font-label-sm transition-all duration-200"
      :class="view === 'list'
        ? 'bg-secondary-container text-on-secondary-container shadow-sm'
        : 'text-on-surface-variant hover:bg-surface-variant'">
      List View
    </button>
    <button @click="$emit('toggle', 'map')"
      class="px-6 py-1.5 rounded-full font-label-sm transition-all duration-200"
      :class="view === 'map'
        ? 'bg-secondary-container text-on-secondary-container shadow-sm'
        : 'text-on-surface-variant hover:bg-surface-variant'">
      Map View
    </button>
  </div>
</template>

<script setup>
defineProps({ view: { type: String, default: 'list' } })
defineEmits(['toggle'])
</script>
```

- [ ] **Step 5: Create frontend/src/components/MatchScore.vue**

```vue
<template>
  <div class="bg-primary-container text-on-primary-container p-lg rounded-xl shadow-lg relative overflow-hidden">
    <div class="absolute -right-12 -top-12 w-48 h-48 bg-white/10 rounded-full blur-3xl"></div>
    <div class="relative z-10">
      <div class="flex items-center gap-sm mb-md">
        <span class="material-symbols-outlined" style="fontVariationSettings: \"'FILL' 1\"">auto_awesome</span>
        <h2 class="font-headline-sm">Why you match</h2>
      </div>
      <p class="font-body-md text-body-md text-on-primary-container/90 mb-lg">
        Based on your uploaded resume, you have a <strong>{{ score }}%</strong> compatibility score for this role.
      </p>
      <div class="flex flex-wrap gap-sm">
        <div v-for="skill in skills" :key="skill"
          class="bg-white/20 backdrop-blur-sm border border-white/30 px-md py-2 rounded-lg flex items-center gap-sm">
          <span class="material-symbols-outlined text-[20px]" style="fontVariationSettings: \"'FILL' 1\"">check_circle</span>
          <span class="font-label-md text-label-md">{{ skill }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  score: { type: Number, default: 0 },
  skills: { type: Array, default: () => [] }
})
</script>
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/
git commit -m "feat: core UI components (AppNav, JobCard, SearchBar, ViewToggle, MatchScore)"
```

---

### Task 11: Map Components (Leaflet)

**Files:**
- Create: `frontend/src/components/JobMap.vue`
- Create: `frontend/src/components/MapPin.vue`

- [ ] **Step 1: Create frontend/src/components/JobMap.vue**

```vue
<template>
  <div class="h-[600px] w-full rounded-2xl overflow-hidden shadow-lg border border-outline-variant relative">
    <l-map :zoom="zoom" :center="center" @update:center="updateCenter" @update:zoom="updateZoom">
      <l-tile-layer :url="tileUrl" :attribution="attribution" />
      <MapPin v-for="job in jobs" :key="job.id" :job="job" @click="selectJob(job)" />
    </l-map>
  </div>
</template>

<script setup>
import { LMap, LTileLayer } from 'vue-leaflet'
import MapPin from './MapPin.vue'
import { useMapStore } from '../stores/map'

const props = defineProps({
  jobs: Array,
  center: { type: Array, default: () => [20, 0] },
  zoom: { type: Number, default: 2 }
})

const emit = defineEmits(['update:center', 'update:zoom'])
const mapStore = useMapStore()

const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'

function updateCenter(center) { emit('update:center', center) }
function updateZoom(zoom) { emit('update:zoom', zoom) }
function selectJob(job) { mapStore.selectJob(job) }
</script>
```

- [ ] **Step 2: Create frontend/src/components/MapPin.vue**

```vue
<template>
  <l-marker :lat-lng="[job.latitude || 0, job.longitude || 0]">
    <l-icon :icon-size="[36, 36]" :icon-anchor="[18, 36]">
      <div class="relative flex flex-col items-center">
        <span v-if="job.salary" class="bg-primary text-on-primary px-2 py-0.5 rounded-full text-xs font-bold shadow-md mb-0.5 whitespace-nowrap">
          {{ job.salary }}
        </span>
        <span class="material-symbols-outlined text-primary text-3xl drop-shadow-md" style="fontVariationSettings: \"'FILL' 1\"">location_on</span>
      </div>
    </l-icon>
  </l-marker>
</template>

<script setup>
import { LMarker, LIcon } from 'vue-leaflet'

defineProps({ job: Object })
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/JobMap.vue frontend/src/components/MapPin.vue
git commit -m "feat: Leaflet map components with job pins"
```

---

### Task 12: Job Discovery Page

**Files:**
- Create: `frontend/src/views/JobDiscovery.vue`

- [ ] **Step 1: Create frontend/src/views/JobDiscovery.vue**

```vue
<template>
  <div class="pb-24">
    <!-- Header -->
    <header class="bg-background w-full top-0 sticky z-40">
      <div class="flex items-center justify-between px-md py-sm max-w-5xl mx-auto">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-primary">explore</span>
          <h1 class="font-headline-md text-headline-md font-bold text-primary tracking-tight">GeoHire</h1>
        </div>
        <button class="hover:opacity-80 transition-opacity active:scale-95 p-2">
          <span class="material-symbols-outlined text-on-surface-variant">notifications</span>
        </button>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-container-margin pt-sm">
      <SearchBar @search="handleSearch" />

      <div v-if="jobsStore.jobs.length || jobsStore.matches.length" class="flex items-center justify-between mb-md">
        <ViewToggle :view="currentView" @toggle="currentView = $event" />
        <button class="flex items-center gap-2 px-4 py-2 border border-outline-variant rounded-full font-label-sm hover:bg-surface-container-high transition-colors">
          <span class="material-symbols-outlined text-sm">tune</span>
          Filters
        </button>
      </div>

      <!-- Loading -->
      <div v-if="jobsStore.loading" class="flex items-center justify-center py-20">
        <span class="material-symbols-outlined text-primary text-4xl animate-spin">progress_activity</span>
      </div>

      <!-- List View -->
      <div v-if="currentView === 'list' && !jobsStore.loading">
        <div v-if="displayJobs.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
          <JobCard v-for="item in displayJobs" :key="item.job?.id || item.id"
            :job="item.job || item" :match-score="item.score" />
        </div>
        <div v-else-if="jobsStore.location" class="text-center py-20 text-on-surface-variant">
          <span class="material-symbols-outlined text-5xl mb-4 block">search_off</span>
          <p>No jobs found for this location. Try searching a different area.</p>
        </div>
      </div>

      <!-- Map View -->
      <div v-if="currentView === 'map' && !jobsStore.loading" class="relative">
        <JobMap :jobs="displayJobs.map(d => d.job || d)" :center="mapCenter" :zoom="11" />
        <div v-if="mapStore.selectedJob"
          class="absolute bottom-4 left-4 right-4 z-40 bg-surface-container-lowest p-md rounded-xl shadow-xl border border-outline-variant flex items-center gap-md cursor-pointer"
          @click="$router.push(`/jobs/${mapStore.selectedJob.id}`)">
          <div class="w-14 h-14 rounded-lg bg-surface-container flex items-center justify-center text-primary font-bold text-xl shrink-0">
            {{ mapStore.selectedJob.company.charAt(0) }}
          </div>
          <div class="flex-grow min-w-0">
            <h3 class="font-headline-sm text-headline-sm text-on-surface truncate">{{ mapStore.selectedJob.title }}</h3>
            <p class="text-body-sm text-on-surface-variant">{{ mapStore.selectedJob.company }}</p>
            <span v-if="mapStore.selectedJob.salary" class="text-label-md text-primary">{{ mapStore.selectedJob.salary }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useJobsStore } from '../stores/jobs'
import { useMapStore } from '../stores/map'
import { useResumeStore } from '../stores/resume'
import SearchBar from '../components/SearchBar.vue'
import ViewToggle from '../components/ViewToggle.vue'
import JobCard from '../components/JobCard.vue'
import JobMap from '../components/JobMap.vue'

const jobsStore = useJobsStore()
const mapStore = useMapStore()
const resumeStore = useResumeStore()
const currentView = ref('list')

const displayJobs = computed(() => {
  if (jobsStore.matches.length) return jobsStore.matches
  return jobsStore.jobs.map(j => ({ job: j }))
})

const mapCenter = computed(() => {
  if (mapStore.center[0] !== 20 || mapStore.center[1] !== 0) return mapStore.center
  return [37.7749, -122.4194]
})

async function handleSearch(title, location) {
  if (!location) return
  await jobsStore.fetchJobs(location)
  if (!jobsStore.jobs.length) {
    await jobsStore.scrapeJobs(location)
  }
  if (resumeStore.resumeId) {
    await jobsStore.matchJobs(resumeStore.resumeId, location)
  }
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/JobDiscovery.vue
git commit -m "feat: job discovery page with list/map toggle, search, and matching"
```

---

### Task 13: Job Details Page + Upload Page + Map View + Profile Page

**Files:**
- Create: `frontend/src/views/JobDetails.vue`
- Create: `frontend/src/views/ResumeUpload.vue`
- Create: `frontend/src/views/MapView.vue`
- Create: `frontend/src/views/Profile.vue`

- [ ] **Step 1: Create frontend/src/views/JobDetails.vue**

```vue
<template>
  <div class="pb-32">
    <header class="w-full top-0 sticky z-40 bg-background/80 backdrop-blur-md flex items-center justify-between px-md py-sm">
      <button @click="$router.back()"
        class="w-11 h-11 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors active:scale-95 text-on-surface-variant">
        <span class="material-symbols-outlined">arrow_back</span>
      </button>
      <div class="flex gap-2">
        <button class="w-11 h-11 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors active:scale-95 text-on-surface-variant">
          <span class="material-symbols-outlined">share</span>
        </button>
        <button class="w-11 h-11 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors active:scale-95 text-on-surface-variant">
          <span class="material-symbols-outlined">bookmark</span>
        </button>
      </div>
    </header>

    <main v-if="job" class="max-w-screen-md mx-auto px-container-margin">
      <section class="mt-lg mb-xl text-center">
        <div class="w-24 h-24 rounded-2xl overflow-hidden bg-white shadow-md border border-outline-variant p-4 flex items-center justify-center mx-auto mb-md">
          <span class="text-primary text-3xl font-bold">{{ job.company.charAt(0) }}</span>
        </div>
        <h1 class="font-headline-lg-mobile text-headline-lg-mobile md:font-headline-lg md:text-headline-lg text-on-background mb-xs">{{ job.title }}</h1>
        <p class="font-headline-sm text-headline-sm text-primary mb-md">{{ job.company }}</p>
        <div class="flex flex-wrap justify-center gap-sm">
          <div class="bg-surface-container-high px-md py-1.5 rounded-full flex items-center gap-xs">
            <span class="material-symbols-outlined text-[18px] text-on-surface-variant">location_on</span>
            <span class="font-label-md text-label-md text-on-surface-variant">{{ job.location }}</span>
          </div>
          <div v-if="job.job_type" class="bg-surface-container-high px-md py-1.5 rounded-full flex items-center gap-xs">
            <span class="material-symbols-outlined text-[18px] text-on-surface-variant">schedule</span>
            <span class="font-label-md text-label-md text-on-surface-variant">{{ job.job_type }}</span>
          </div>
          <div v-if="job.salary" class="bg-surface-container-high px-md py-1.5 rounded-full flex items-center gap-xs">
            <span class="material-symbols-outlined text-[18px] text-on-surface-variant">payments</span>
            <span class="font-label-md text-label-md text-on-surface-variant">{{ job.salary }}</span>
          </div>
        </div>
      </section>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-md">
        <MatchScore v-if="matchScore !== undefined" :score="matchScore" :skills="matchedSkills" class="md:col-span-3" />

        <div class="md:col-span-2 space-y-md">
          <article class="bg-white border border-outline-variant p-lg rounded-xl shadow-sm">
            <h2 class="font-headline-sm text-headline-sm mb-md text-on-background border-l-4 border-primary pl-md">Job Description</h2>
            <p class="text-on-surface-variant leading-relaxed">{{ job.description }}</p>
          </article>

          <article v-if="job.requirements?.length" class="bg-white border border-outline-variant p-lg rounded-xl shadow-sm">
            <h2 class="font-headline-sm text-headline-sm mb-md text-on-background border-l-4 border-primary pl-md">Requirements</h2>
            <ul class="space-y-sm">
              <li v-for="req in job.requirements" :key="req" class="flex items-start gap-md text-on-surface-variant">
                <div class="w-1.5 h-1.5 rounded-full bg-primary mt-2.5 shrink-0"></div>
                <span>{{ req }}</span>
              </li>
            </ul>
          </article>
        </div>

        <aside class="space-y-md">
          <div class="bg-surface-container-low border border-outline-variant p-md rounded-xl">
            <h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wider mb-sm">Source</h3>
            <p class="text-on-surface-variant">{{ job.source }}</p>
          </div>
          <div class="bg-surface-container-low border border-outline-variant p-md rounded-xl">
            <h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wider mb-sm">Company</h3>
            <p class="text-on-surface-variant">{{ job.company }}</p>
          </div>
        </aside>
      </div>
    </main>

    <div v-if="job" class="fixed bottom-0 left-0 w-full z-50 px-container-margin pb-lg pt-md bg-white/80 backdrop-blur-xl border-t border-outline-variant/30 flex justify-center items-center">
      <div class="max-w-screen-md w-full flex gap-md">
        <button class="w-14 h-14 border border-outline-variant rounded-xl flex items-center justify-center bg-white hover:bg-surface-container-high transition-colors active:scale-90">
          <span class="material-symbols-outlined text-on-surface-variant">favorite</span>
        </button>
        <a :href="job.source_url" target="_blank"
          class="flex-1 bg-primary text-on-primary font-headline-sm text-headline-sm py-md rounded-xl shadow-lg shadow-primary/20 hover:bg-primary-container hover:text-on-primary-container transition-all active:scale-[0.98] flex items-center justify-center gap-sm">
          Apply Now
          <span class="material-symbols-outlined">arrow_forward</span>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useJobsStore } from '../stores/jobs'
import { useResumeStore } from '../stores/resume'
import MatchScore from '../components/MatchScore.vue'

const route = useRoute()
const jobsStore = useJobsStore()
const resumeStore = useResumeStore()

const job = computed(() => jobsStore.jobs.find(j => j.id === route.params.id))
const match = computed(() => jobsStore.matches.find(m => m.job?.id === route.params.id || m.job.id === route.params.id))
const matchScore = computed(() => match.value?.score)
const matchedSkills = computed(() => resumeStore.profile?.skills?.slice(0, 4) || [])
</script>
```

- [ ] **Step 2: Create frontend/src/views/ResumeUpload.vue**

```vue
<template>
  <div class="pb-32">
    <header class="w-full top-0 sticky bg-background z-40 flex items-center justify-between px-md py-sm">
      <div class="flex items-center gap-sm">
        <span class="material-symbols-outlined text-primary">explore</span>
        <span class="font-headline-md text-headline-md font-bold text-primary">GeoHire</span>
      </div>
      <button class="p-2 active:scale-95 transition-transform">
        <span class="material-symbols-outlined text-on-surface-variant">notifications</span>
      </button>
    </header>

    <main class="px-container-margin md:max-w-4xl md:mx-auto">
      <section class="mt-xl text-center">
        <h1 class="font-headline-lg-mobile text-headline-lg-mobile md:font-headline-lg md:text-headline-lg text-on-background mb-sm">Ready for Your Next Move?</h1>
        <p class="font-body-md text-body-md text-on-surface-variant max-w-md mx-auto">Upload your resume to see matching jobs and get personalized career insights.</p>
      </section>

      <section class="mt-xl">
        <div @click="triggerUpload" @dragover.prevent @drop.prevent="handleDrop"
          class="relative overflow-hidden border-2 border-dashed border-outline-variant bg-surface-container-lowest rounded-xl p-xl flex flex-col items-center justify-center transition-all duration-300 hover:border-primary cursor-pointer active:scale-[0.98]">
          <div class="w-20 h-20 rounded-full bg-surface-container flex items-center justify-center mb-md relative">
            <div class="absolute inset-0 rounded-full bg-primary opacity-10"></div>
            <span class="material-symbols-outlined text-primary text-[40px]">upload_file</span>
          </div>
          <h2 class="font-headline-sm text-headline-sm text-on-surface mb-xs">Drop your resume here</h2>
          <p class="font-body-sm text-body-sm text-on-surface-variant mb-lg">PDF, DOCX up to 10MB</p>
          <button class="bg-primary text-on-primary px-lg py-sm rounded-lg font-label-md text-label-md shadow-lg active:scale-95 transition-transform">
            Browse Files
          </button>
          <input ref="fileInput" type="file" accept=".pdf,.docx" class="hidden" @change="handleFileChange" />
        </div>

        <div v-if="resumeStore.uploading" class="mt-md text-center text-on-surface-variant">
          <span class="material-symbols-outlined animate-spin inline-block mr-2">progress_activity</span>
          Parsing your resume...
        </div>

        <div v-if="resumeStore.profile" class="mt-md p-md bg-surface-container-lowest border border-outline-variant rounded-xl">
          <h3 class="font-headline-sm text-headline-sm text-primary mb-sm">Resume Parsed</h3>
          <p class="text-body-sm text-on-surface-variant mb-sm">Skills: {{ resumeStore.profile.skills?.join(', ') }}</p>
          <p v-if="resumeStore.profile.experience_years" class="text-body-sm text-on-surface-variant mb-sm">Experience: {{ resumeStore.profile.experience_years }} years</p>
          <router-link to="/"
            class="inline-block bg-primary text-on-primary px-lg py-sm rounded-lg font-label-md mt-sm active:scale-95 transition-transform">
            Find Matching Jobs
          </router-link>
        </div>
      </section>

      <section class="mt-xl pb-12">
        <h3 class="font-headline-sm text-headline-sm text-on-background mb-md">How AI Matching Works</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-md">
          <div class="bg-white border border-outline-variant p-md rounded-xl shadow-sm">
            <div class="w-10 h-10 rounded-lg bg-secondary-container flex items-center justify-center mb-sm">
              <span class="material-symbols-outlined text-on-secondary-container">psychology</span>
            </div>
            <h4 class="font-headline-sm text-[18px] text-on-surface mb-xs">Skills Analysis</h4>
            <p class="font-body-sm text-body-sm text-on-surface-variant">Our engine parses your experience to identify strengths and technical proficiencies.</p>
          </div>
          <div class="bg-white border border-outline-variant p-md rounded-xl shadow-sm">
            <div class="w-10 h-10 rounded-lg bg-primary-container/10 flex items-center justify-center mb-sm">
              <span class="material-symbols-outlined text-primary">analytics</span>
            </div>
            <h4 class="font-headline-sm text-[18px] text-on-surface mb-xs">Industry Fit</h4>
            <p class="font-body-sm text-body-sm text-on-surface-variant">We map your trajectory against market demands to find roles where you'll have the highest impact.</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useResumeStore } from '../stores/resume'

const resumeStore = useResumeStore()
const fileInput = ref(null)

function triggerUpload() { fileInput.value?.click() }

async function handleFileChange(e) {
  const file = e.target.files?.[0]
  if (file) await resumeStore.uploadResume(file)
}

async function handleDrop(e) {
  const file = e.dataTransfer?.files?.[0]
  if (file) await resumeStore.uploadResume(file)
}
</script>
```

- [ ] **Step 3: Create frontend/src/views/MapView.vue**

```vue
<template>
  <div class="h-screen w-full overflow-hidden">
    <header class="w-full top-0 sticky bg-background z-40">
      <div class="flex items-center justify-between px-md py-sm">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-primary">explore</span>
          <span class="font-headline-md text-headline-md font-bold text-primary">GeoHire</span>
        </div>
      </div>
      <div class="px-md pb-sm">
        <div class="relative flex items-center">
          <span class="material-symbols-outlined absolute left-3 text-on-surface-variant">search</span>
          <input v-model="searchQuery" @keyup.enter="searchLocation"
            class="w-full h-11 pl-10 pr-4 bg-surface-container border border-outline-variant rounded-full text-body-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
            placeholder="Search location..." type="text" />
          <span class="material-symbols-outlined absolute right-3 text-primary">my_location</span>
        </div>
      </div>
    </header>

    <main class="h-[calc(100vh-140px)] w-full">
      <JobMap :jobs="mapJobs" :center="mapStore.center" :zoom="mapStore.zoom"
        @update:center="mapStore.setCenter" @update:zoom="mapStore.zoom = $event" />
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMapStore } from '../stores/map'
import { useJobsStore } from '../stores/jobs'
import JobMap from '../components/JobMap.vue'

const mapStore = useMapStore()
const jobsStore = useJobsStore()
const searchQuery = ref('')

const mapJobs = computed(() => jobsStore.jobs.filter(j => j.latitude && j.longitude))

function searchLocation() {
  if (searchQuery.value) {
    jobsStore.fetchJobs(searchQuery.value)
  }
}
</script>
```

- [ ] **Step 4: Create frontend/src/views/Profile.vue**

```vue
<template>
  <div class="pb-32 px-container-margin max-w-2xl mx-auto">
    <header class="w-full top-0 sticky bg-background z-40 flex items-center justify-between px-0 py-sm">
      <h1 class="font-headline-md text-headline-md font-bold text-primary">Profile</h1>
    </header>

    <section class="mt-lg">
      <h2 class="font-headline-sm text-headline-sm mb-md">Your Resume</h2>
      <div v-if="resumeStore.profile" class="bg-white border border-outline-variant p-md rounded-xl shadow-sm">
        <p class="text-body-sm text-on-surface-variant mb-sm">Skills: {{ resumeStore.profile.skills?.join(', ') }}</p>
        <p v-if="resumeStore.profile.experience_years" class="text-body-sm text-on-surface-variant mb-sm">Experience: {{ resumeStore.profile.experience_years }} years</p>
        <button @click="resumeStore.clear()" class="text-error text-label-sm mt-sm">Remove Resume</button>
      </div>
      <div v-else class="bg-white border border-outline-variant p-md rounded-xl shadow-sm text-center text-on-surface-variant">
        <p>No resume uploaded yet.</p>
        <router-link to="/upload" class="text-primary font-label-md mt-sm inline-block">Upload Resume</router-link>
      </div>
    </section>

    <section class="mt-lg">
      <h2 class="font-headline-sm text-headline-sm mb-md">Bookmarked Jobs</h2>
      <div v-if="bookmarkedJobs.length" class="space-y-md">
        <div v-for="job in bookmarkedJobs" :key="job.id"
          class="bg-white border border-outline-variant p-md rounded-xl shadow-sm cursor-pointer"
          @click="$router.push(`/jobs/${job.id}`)">
          <h3 class="font-headline-sm text-headline-sm text-primary">{{ job.title }}</h3>
          <p class="text-body-sm text-on-surface-variant">{{ job.company }} · {{ job.location }}</p>
        </div>
      </div>
      <div v-else class="text-center text-on-surface-variant py-8">
        <p>No bookmarked jobs.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useResumeStore } from '../stores/resume'
import { useJobsStore } from '../stores/jobs'

const resumeStore = useResumeStore()
const jobsStore = useJobsStore()

const bookmarkedJobs = computed(() => {
  const bookmarks = JSON.parse(localStorage.getItem('geohire_bookmarks') || '[]')
  return jobsStore.jobs.filter(j => bookmarks.includes(j.id))
})
</script>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/
git commit -m "feat: all pages (JobDetails, ResumeUpload, MapView, Profile)"
```

---

### Task 14: Upload Zone Component + Final Integration

**Files:**
- Create: `frontend/src/components/UploadZone.vue`

- [ ] **Step 1: Create frontend/src/components/UploadZone.vue**

```vue
<template>
  <div @click="$refs.input.click()" @dragover.prevent @drop.prevent="handleDrop"
    class="border-2 border-dashed border-outline-variant bg-surface-container-lowest rounded-xl p-xl flex flex-col items-center justify-center transition-all duration-300 hover:border-primary cursor-pointer active:scale-[0.98]"
    :class="{ 'border-primary bg-surface-container': isDragging }">
    <div class="w-20 h-20 rounded-full bg-surface-container flex items-center justify-center mb-md">
      <span class="material-symbols-outlined text-primary text-[40px]">upload_file</span>
    </div>
    <h2 class="font-headline-sm text-headline-sm text-on-surface mb-xs">Drop your resume here</h2>
    <p class="font-body-sm text-body-sm text-on-surface-variant mb-lg">PDF, DOCX up to 10MB</p>
    <button type="button" class="bg-primary text-on-primary px-lg py-sm rounded-lg font-label-md text-label-md shadow-lg active:scale-95 transition-transform">
      Browse Files
    </button>
    <input ref="input" type="file" accept=".pdf,.docx" class="hidden" @change="handleFile" />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['file-selected'])
const isDragging = ref(false)

function handleFile(e) {
  const file = e.target.files?.[0]
  if (file) emit('file-selected', file)
}

function handleDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) emit('file-selected', file)
}
</script>
```

- [ ] **Step 2: Verify full app starts and works end-to-end**

Start backend:
```powershell
cd D:\GeoHire
uvicorn backend.main:app --reload
```

Start frontend (separate terminal):
```powershell
cd D:\GeoHire\frontend
npx vite --port 5173
```

**Test manually:**
1. Open http://localhost:5173
2. Search a location in the search bar (e.g., "San Francisco, CA")
3. Click Search — should fetch/scrape jobs
4. Navigate to /upload — upload a PDF/DOCX resume
5. Go back to home — matching jobs should appear with scores
6. Toggle to Map View — pins should show on map
7. Click a job card — details page should show
8. Bookmark a job — should persist in localStorage
9. Check /profile — should show resume and bookmarks

- [ ] **Step 3: Final commit**

```bash
git add frontend/src/components/UploadZone.vue
git commit -m "feat: UploadZone component and final integration"
```

---

## Self-Review Checklist

**1. Spec coverage:**
- Location selection → SearchBar + `/scrape` + `/jobs` endpoints
- Companies with open jobs → Indeed scraper, JSON cache, JobCard display
- Resume upload → UploadZone + `/upload-resume` + parser
- Resume-based job matching → `/match-jobs` + TF-IDF matcher + MatchScore display
- No paid APIs → BeautifulSoup (free), PyMuPDF (free), scikit-learn (free), Leaflet/OSM (free), Nominatim (free)
- Map view → Leaflet + vue-leaflet + MapView page + MapPin component

**2. Placeholder scan:** No TBD, TODOs, or vague requirements. Code is complete in every step.

**3. Type consistency:** Model field names are consistent across backend models, storage, scraper output, frontend components.

**4. Ambiguity check:** Every step has exact file paths, code blocks, and commands.
