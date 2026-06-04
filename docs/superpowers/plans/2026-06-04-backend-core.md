# GeoHire Backend Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the FastAPI backend foundation with Indeed scraper, JSON caching, and the first two endpoints.

**Architecture:** Single FastAPI server with a function-based scraper module. Scraping runs synchronously on first request for a location, results are cached to JSON files. No database, no background tasks in v1.

**Tech Stack:** Python 3.12+, FastAPI, uvicorn, httpx, BeautifulSoup4, uv for package management

---

## File Structure

```
backend/
├── pyproject.toml          # uv project configuration
├── main.py                 # FastAPI app, routes, startup
├── scrapers/
│   ├── __init__.py
│   └── indeed.py           # Indeed scraper function
├── cache.py                # JSON file read/write helpers
├── models.py               # Pydantic models for API
└── data/
    ├── jobs/               # Cached job results per location
    └── .gitkeep
```

## Task Breakdown

### Task 1: Project Scaffolding

**Files:**
- Create: `backend/pyproject.toml`

- [ ] **Step 1: Initialize the backend project**

```bash
cd C:\Users\HP\GeoHire
mkdir -p backend\scrapers backend\data\jobs backend\tests
```

- [ ] **Step 2: Install dependencies with uv**

```bash
cd C:\Users\HP\GeoHire\backend
uv init --app
uv add "fastapi[standard]" uvicorn httpx beautifulsoup4 lxml
uv add --dev pytest pytest-asyncio httpx
```

- [ ] **Step 3: Update pyproject.toml with project metadata**

Use the Edit tool to set the project name in `backend/pyproject.toml`:

Old:
```toml
name = "backend"
```
New:
```toml
name = "geohire-backend"
version = "0.1.0"
description = "GeoHire location-based job discovery API"
```

Old *(if `[tool.uv]` section exists)* — add test config:
```toml
[tool.uv]
```

New:
```toml
[tool.uv]
dev-dependencies = ["pytest", "pytest-asyncio", "httpx"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 4: Create empty files and verify setup**

```bash
# Create __init__.py files so Python recognizes the packages
New-Item -ItemType File -Path C:\Users\HP\GeoHire\backend\scrapers\__init__.py
New-Item -ItemType File -Path C:\Users\HP\GeoHire\backend\tests\__init__.py

# Verify uv works
cd C:\Users\HP\GeoHire\backend
uv run python --version
```

Expected: `Python 3.12.x` (whatever version is installed)

- [ ] **Step 5: Commit**

```bash
cd C:\Users\HP\GeoHire
git add backend/
git commit -m "feat: scaffold backend project with uv"
```

---

### Task 2: Pydantic Models

**Files:**
- Create: `backend/models.py`

- [ ] **Step 1: Write models**

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
```

- [ ] **Step 2: Run a quick import check**

```bash
cd C:\Users\HP\GeoHire\backend
uv run python -c "from models import Job, JobListResponse, ScrapeResponse; print('models OK')"
```

Expected: `models OK`

- [ ] **Step 3: Commit**

```bash
cd C:\Users\HP\GeoHire
git add backend/models.py
git commit -m "feat: add Pydantic models for jobs API"
```

---

### Task 3: Indeed Scraper

**Files:**
- Create: `backend/scrapers/indeed.py`

- [ ] **Step 1: Write the Indeed scraper function**

```python
import time
import random
import uuid
from typing import Optional

import httpx
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]


def _build_url(location: str, query: str = "") -> str:
    query_part = f"&q={query}" if query else ""
    return f"https://www.indeed.com/jobs?l={location}{query_part}&sort=date"


def _parse_salary(salary_text: Optional[str]) -> Optional[str]:
    if not salary_text:
        return None
    return salary_text.strip()


def _parse_job_type(job_type_text: Optional[str]) -> Optional[str]:
    if not job_type_text:
        return None
    text = job_type_text.strip().lower()
    if "full-time" in text or "full time" in text:
        return "Full-time"
    if "part-time" in text or "part time" in text:
        return "Part-time"
    if "contract" in text:
        return "Contract"
    if "temporary" in text:
        return "Temporary"
    if "internship" in text:
        return "Internship"
    return job_type_text.strip()


def scrape_indeed(location: str, query: str = "") -> list[dict]:
    url = _build_url(location, query)
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    time.sleep(random.uniform(2, 6))

    response = httpx.get(url, headers=headers, follow_redirects=True, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    job_cards = soup.select("div.job_seen_beacon, div[data-testid='slider_item']")
    jobs = []

    for card in job_cards:
        try:
            title_el = card.select_one("h2.jobTitle a, a[data-jk]")
            title = title_el.get_text(strip=True) if title_el else "Unknown"

            company_el = card.select_one(
                "span[data-testid='company-name'], span.companyName"
            )
            company = company_el.get_text(strip=True) if company_el else "Unknown"

            location_el = card.select_one(
                "div[data-testid='text-location'], div.companyLocation"
            )
            job_location = location_el.get_text(strip=True) if location_el else location

            desc_el = card.select_one("div.job-snippet, ul li")
            description = desc_el.get_text(strip=True) if desc_el else ""

            salary_el = card.select_one(
                "div[data-testid='attribute_snippet_testid'], span.salary-snippet"
            )
            salary = _parse_salary(salary_el.get_text(strip=True) if salary_el else None)

            job_type_el = card.select_one(
                "div[data-testid='attribute_snippet_testid'] + div, span.job-type"
            )
            job_type = _parse_job_type(
                job_type_el.get_text(strip=True) if job_type_el else None
            )

            footer_el = card.select_one("table.jobCard_footer")
            posted_date = None
            if footer_el:
                date_el = footer_el.select_one("span.date")
                posted_date = date_el.get_text(strip=True) if date_el else None

            jobs.append(
                {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "company": company,
                    "location": job_location,
                    "description": description,
                    "requirements": [],
                    "salary": salary,
                    "job_type": job_type,
                    "posted_date": posted_date,
                    "source": "indeed",
                    "source_url": url,
                    "latitude": None,
                    "longitude": None,
                }
            )
        except Exception:
            continue

    return jobs
```

- [ ] **Step 2: Verify the scraper module loads**

```bash
cd C:\Users\HP\GeoHire\backend
uv run python -c "from scrapers.indeed import scrape_indeed; print('scraper OK')"
```

Expected: `scraper OK`

- [ ] **Step 3: Commit**

```bash
cd C:\Users\HP\GeoHire
git add backend/scrapers/
git commit -m "feat: add Indeed scraper with rate limiting"
```

---

### Task 4: JSON Cache Layer

**Files:**
- Create: `backend/cache.py`

- [ ] **Step 1: Write cache helpers**

```python
import json
import os
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
JOBS_DIR = os.path.join(DATA_DIR, "jobs")


def _ensure_dirs():
    os.makedirs(JOBS_DIR, exist_ok=True)


def _slugify(location: str) -> str:
    return location.lower().replace(" ", "-").replace(",", "")


def get_cached_jobs(location: str) -> Optional[list[dict]]:
    _ensure_dirs()
    path = os.path.join(JOBS_DIR, f"{_slugify(location)}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_jobs(location: str, jobs: list[dict]):
    _ensure_dirs()
    path = os.path.join(JOBS_DIR, f"{_slugify(location)}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
```

- [ ] **Step 2: Test cache module loads**

```bash
cd C:\Users\HP\GeoHire\backend
uv run python -c "from cache import get_cached_jobs, save_jobs; print('cache OK')"
```

Expected: `cache OK`

- [ ] **Step 3: Commit**

```bash
cd C:\Users\HP\GeoHire
git add backend/cache.py
git commit -m "feat: add JSON cache helpers"
```

---

### Task 5: FastAPI Application

**Files:**
- Create: `backend/main.py`

- [ ] **Step 1: Write the FastAPI app**

```python
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
```

- [ ] **Step 2: Start the server and verify health endpoint**

```bash
cd C:\Users\HP\GeoHire\backend
uv run uvicorn main:app --port 8000 &
# Wait a moment for startup
Start-Sleep -Seconds 2
uv run python -c "import httpx; r = httpx.get('http://localhost:8000/health'); print(r.json())"
```

Expected: `{'status': 'ok'}`

- [ ] **Step 3: Kill the test server**

```bash
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
```

- [ ] **Step 4: Commit**

```bash
cd C:\Users\HP\GeoHire
git add backend/main.py
git commit -m "feat: add FastAPI app with /health, /scrape, /jobs endpoints"
```

---

### Task 6: Tests

**Files:**
- Create: `backend/tests/test_api.py`

- [ ] **Step 1: Write the API tests**

```python
import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_jobs_no_cache(client):
    response = await client.get("/jobs", params={"location": "Nowhere, XX"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_scrape_invalid_location(client):
    response = await client.post("/scrape", params={"location": "Xyzzzzzzzz"})
    # Should return an error, but not crash
    assert response.status_code in (200, 502)
```

- [ ] **Step 2: Write scraper unit tests**

```python
# backend/tests/test_indeed.py
from scrapers.indeed import _parse_salary, _parse_job_type


def test_parse_salary_none():
    assert _parse_salary(None) is None


def test_parse_salary_value():
    assert _parse_salary("  $50k - $70k  ") == "$50k - $70k"


def test_parse_job_type_full_time():
    assert _parse_job_type("Full-time") == "Full-time"


def test_parse_job_type_none():
    assert _parse_job_type(None) is None


def test_parse_job_type_part_time():
    assert _parse_job_type("Part-time") == "Part-time"


def test_parse_job_type_contract():
    assert _parse_job_type("Contract") == "Contract"
```

- [ ] **Step 3: Write cache tests**

```python
# backend/tests/test_cache.py
import os
import tempfile
from cache import _slugify


def test_slugify():
    assert _slugify("San Francisco, CA") == "san-francisco-ca"


def test_slugify_simple():
    assert _slugify("New York") == "new-york"
```

- [ ] **Step 4: Run all tests**

```bash
cd C:\Users\HP\GeoHire\backend
uv run pytest tests/ -v
```

Expected: All tests pass (7+ tests)

- [ ] **Step 5: Commit**

```bash
cd C:\Users\HP\GeoHire
git add backend/tests/
git commit -m "test: add API endpoint, scraper, and cache tests"
```

---

### Task 7: Clean Up and Verify

- [ ] **Step 1: Final full test run**

```bash
cd C:\Users\HP\GeoHire\backend
uv run pytest tests/ -v
```

- [ ] **Step 2: Remove any test files created in data/**

```bash
Remove-Item -Recurse -Force C:\Users\HP\GeoHire\backend\data\jobs\*.json -ErrorAction SilentlyContinue
```

- [ ] **Step 3: Start server and do a quick manual smoke test**

```bash
cd C:\Users\HP\GeoHire\backend
uv run uvicorn main:app --port 8000 &
Start-Sleep -Seconds 3
uv run python -c "
import httpx
r = httpx.get('http://localhost:8000/health')
print('health:', r.json())
r = httpx.post('http://localhost:8000/scrape', params={'location': 'Austin, TX'})
print('scrape status:', r.status_code)
if r.status_code == 200:
    data = r.json()
    print(f'got {len(data[\"jobs\"])} jobs')
"
```

- [ ] **Step 4: Kill server**

```bash
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

## Spec Coverage

| Spec Requirement | Task |
|---|---|
| POST /scrape?location=... triggers scraping, returns jobs | Task 5 |
| GET /jobs?location=... returns cached jobs | Task 5 |
| Indeed scraper with normalized job dict format | Task 3 |
| Rate-limited scraping (2-6s delays) | Task 3 |
| JSON file caching per location | Task 4 |
| Backend: FastAPI with async endpoints | Task 5 |
| pytest for API endpoints | Task 6 |
| Scraper unit tests with mock HTML | Task 6 |
| Data layout: data/jobs/<slug>.json | Task 4 |

**Not included in this plan** (future phases):
- GET /jobs/{id} — single job details
- POST /upload-resume — resume parsing
- POST /match-jobs — TF-IDF matching
- GET /locations/suggest — Nominatim autocomplete
- Other scrapers (LinkedIn, Glassdoor)
- Background task scraping (currently synchronous)
