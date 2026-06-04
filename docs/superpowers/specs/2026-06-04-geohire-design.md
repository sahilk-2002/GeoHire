# GeoHire — Location-Based Job Discovery Platform

## Overview

GeoHire is a web application that lets users select a geographical location, discover companies with open job roles in that area, upload their resume, and get personalized job recommendations ranked by match quality. No paid APIs are used.

## Architecture

```
frontend/ (Vue 3 + Vite) ──HTTP──▶ backend/ (FastAPI) ──scrapes──▶ Job Boards
                                       │                           (BeautifulSoup)
                                       ├── parses resumes ───▶ PDF/DOCX
                                       │    (PyMuPDF / python-docx)
                                       ├── matches jobs ───▶ TF-IDF scoring
                                       └── stores data ───▶ JSON files
```

**Backend**: FastAPI with async endpoints, background scraping, resume parsing, and TF-IDF matching.
**Frontend**: Vue 3 Composition API + Vite + Pinia + vue-leaflet + TailwindCSS.
**Data storage**: JSON files only (no database).
**Map**: Leaflet + OpenStreetMap tiles + Nominatim for free geocoding.

---

## Backend (Python / FastAPI)

### Scraping Engine (`backend/scrapers/`)
- One scraper module per job board (`indeed.py`, `linkedin.py`, `glassdoor.py`, etc.)
- Each accepts a location string, returns normalized job dicts:
  ```json
  {
    "id": "uuid",
    "title": "Senior UX Designer",
    "company": "Stripe",
    "location": "San Francisco, CA",
    "description": "...",
    "requirements": ["5+ years...", "Figma..."],
    "salary": "$140k - $180k",
    "job_type": "Full-time",
    "posted_date": "2026-06-02",
    "source": "indeed",
    "source_url": "...",
    "latitude": 37.7749,
    "longitude": -122.4194
  }
  ```
- Uses `aiohttp` + `BeautifulSoup` with rotating User-Agent headers
- Rate-limited (random 2-6s delays between requests)
- Runs as FastAPI `BackgroundTask` to avoid blocking API responses
- Cached per location in `data/jobs/<location-slug>.json`

### Resume Parser (`backend/parser/`)
- Accepts PDF (PyMuPDF) and DOCX (python-docx) via multipart upload
- Text extraction → skill extraction (predefined keyword list + frequency analysis)
- Extracts: skills, years of experience, job titles, education keywords
- Returns structured resume profile dict

### Matching Engine (`backend/matcher/`)
- TF-IDF vectorization of resume profile and all job descriptions
- Cosine similarity scoring → ranked job list with match percentage
- No paid AI APIs used; purely statistical text matching
- Stops words filtered, skills weighted higher

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/scrape?location=...` | Trigger scraping for a location, returns job list |
| GET | `/jobs?location=...` | Returns cached jobs for a location |
| GET | `/jobs/{id}` | Single job details |
| POST | `/upload-resume` | Upload and parse resume, returns profile |
| POST | `/match-jobs` | Accept resume_id + location, returns ranked jobs |
| GET | `/locations/suggest?q=...` | Location autocomplete via Nominatim |

### JSON Data Layout

```
data/
├── jobs/
│   ├── san-francisco-ca.json
│   ├── new-york-ny.json
│   └── ...
├── resumes/
│   ├── <uuid>.pdf
│   └── <uuid>.docx
├── resume-profiles.json
└── locations.json
```

---

## Frontend (Vue 3)

### Pages

1. **Job Discovery** (`/`) — Search bar (title + location inputs), list/map toggle, job card grid, filter button
2. **Job Details** (`/jobs/:id`) — Hero section, "Why You Match" percentage + matched skills, description, requirements sidebar, sticky Apply CTA
3. **Resume Upload** (`/upload`) — Drag-and-drop zone, LinkedIn import option, AI matching explanation cards
4. **Map View** (`/map`) — Full-screen Leaflet map with job pins, bottom sheet popup on pin click
5. **Profile** (`/profile`) — Saved/bookmarked jobs, uploaded resume status, settings

### Core Components

| Component | Purpose |
|-----------|---------|
| `AppNav.vue` | Bottom navigation bar (Jobs, Map, Upload, Profile) |
| `JobCard.vue` | Reusable job listing card with bookmark, salary, tags |
| `SearchBar.vue` | Job title + location inputs with autocomplete |
| `ViewToggle.vue` | List / Map toggle pill |
| `JobMap.vue` | Leaflet map wrapper with custom markers |
| `MapPin.vue` | Custom marker with salary badge popup |
| `UploadZone.vue` | Drag-and-drop file upload area |
| `MatchScore.vue` | Match percentage badge (e.g., "94%") |

### State Management (Pinia)

| Store | State |
|-------|-------|
| `useJobsStore` | Job listings, current location, search query, filters |
| `useResumeStore` | Uploaded resume file, parsed profile data |
| `useMapStore` | Map center coordinates, zoom level, selected pin |

### Design System

Follows the **Pathfinder** spec:
- **Colors**: Deep Indigo (`#3525cd`) primary, Vibrant Teal (`#006a61`) secondary, Amber (`#684000`) tertiary for urgency
- **Typography**: Inter font family, 600/700 weight for headlines, 400 for body
- **Shapes**: 12px radius for cards, 8px for buttons/inputs, 6px for chips/tags
- **Spacing**: 8px linear scale (4, 8, 16, 24, 32, 48, 64), 16px container margin
- **Elevation**: Subtle shadows at card level, stronger at nav/modal level

---

## Data Flow

1. **User searches location** → frontend calls `POST /scrape?location=...`
2. **Backend** checks cache; if stale/missing, triggers scraping in background, returns results
3. **User uploads resume** → `POST /upload-resume` → backend parses, extracts skills, returns profile
4. **User clicks "Find Matching Jobs"** → `POST /match-jobs` with resume_id + location
5. **Backend** runs TF-IDF matching, returns jobs ranked by similarity score
6. **Frontend** displays ranked jobs; user can toggle list/map view, filter, bookmark, view details

---

## Error Handling

- **Scraping failures**: Return cached data if available; show warning banner if scrape fails
- **Resume parsing**: Return partial profile if parsing encounters issues; reject unsupported formats
- **Network errors**: Retry logic with exponential backoff for scraping; timeout after 30s
- **Rate limiting**: Requests queue with delays; if IP blocked, log and notify user

---

## Testing

- **Backend**: pytest for API endpoints, scraper unit tests with mock HTML, parser tests with sample PDF/DOCX
- **Frontend**: Vitest for Vue components, Playwright for E2E flow (search → upload → match)
- **Scrapers**: Snapshot tests against known page structures; alert on structural changes

---

## Non-Goals (v1)

- No user authentication / accounts (bookmarks stored in localStorage)
- No real-time updates or live scraping streams
- No employer posting portal
- No paid APIs or external AI services
