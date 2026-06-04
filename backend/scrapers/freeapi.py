import logging
import uuid
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

CAREER_NEST_URL = "https://careernest.cloud/api/feed"
ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"


def _geocode(location: str) -> Optional[tuple[float, float]]:
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json", "limit": 1}
        headers = {"User-Agent": "GeoHire/1.0"}
        resp = httpx.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        if data and len(data) > 0:
            return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception:
        pass
    return None


def _match_location(job_location: str, query_location: str) -> bool:
    """Check if job_location matches the query_location."""
    jl = job_location.lower().strip()
    ql = query_location.lower().strip()
    if ql in jl or jl in ql:
        return True
    ql_parts = [p.strip() for p in ql.replace(",", " ").split()]
    return any(part in jl for part in ql_parts if len(part) > 2)


def _normalize(jobs: list[dict], source: str, location: str) -> list[dict]:
    coords = _geocode(location)
    lat, lng = coords if coords else (None, None)
    geocoded = {}
    results = []
    for job in jobs:
        jloc = job.get("location") or location
        if not _match_location(jloc, location):
            continue

        raw_lat = job.get("latitude") or job.get("lat")
        raw_lng = job.get("longitude") or job.get("lng")
        if raw_lat and raw_lng:
            pass
        elif lat and lng:
            if jloc not in geocoded:
                c = _geocode(jloc)
                geocoded[jloc] = c if c else (lat, lng)
            raw_lat, raw_lng = geocoded[jloc]
        else:
            raw_lat, raw_lng = (None, None)

        results.append({
            "id": str(uuid.uuid4()),
            "title": job.get("title") or "Unknown",
            "company": job.get("company") or job.get("company_name") or "Unknown",
            "location": jloc,
            "description": (job.get("description") or "")[:2000],
            "requirements": [],
            "salary": job.get("salary"),
            "job_type": job.get("job_type") or (job.get("job_types") or [None])[0] or "",
            "posted_date": str(job.get("posted_at") or job.get("created_at") or ""),
            "source": source,
            "source_url": job.get("url") or job.get("job_url") or "",
            "latitude": raw_lat,
            "longitude": raw_lng,
        })
    return results


def search_careernest(location: str, limit: int = 100) -> Optional[list[dict]]:
    try:
        resp = httpx.get(CAREER_NEST_URL, params={"limit": limit}, timeout=15)
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])
        return _normalize(jobs, "careernest", location)
    except Exception as e:
        logger.warning("Career Nest failed: %s", e)
        return None


def search_arbeitnow(location: str, limit: int = 25) -> Optional[list[dict]]:
    try:
        resp = httpx.get(ARBEITNOW_URL, params={"page": 1, "per_page": limit}, timeout=15)
        resp.raise_for_status()
        jobs = resp.json().get("data", [])
        return _normalize(jobs, "arbeitnow", location)
    except Exception as e:
        logger.warning("Arbeitnow failed: %s", e)
        return None
