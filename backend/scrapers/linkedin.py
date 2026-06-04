"""Scraper for LinkedIn job listings via the public guest API."""
import logging
import time
import random
import uuid
from urllib.parse import urlencode
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"


def _build_search_url(location: str, query: str = "", start: int = 0) -> str:
    params = urlencode({"keywords": query, "location": location, "start": start})
    return f"{SEARCH_URL}?{params}"


def _parse_search_results(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.find_all("li", class_="jobs-search-results__list-item")
    jobs = []
    for card in cards:
        try:
            link = card.find("a", class_="base-card__full-link")
            if not link or not link.get("href"):
                continue
            href = link["href"]
            job_id = None
            if "/jobs/view/" in href:
                job_id = href.split("/jobs/view/")[1].split("/")[0]
            if not job_id:
                continue
            title_el = card.find("h3", class_="base-search-card--title")
            title = title_el.get_text(strip=True) if title_el else "Unknown"
            company_el = card.find("h4", class_="base-search-card--subtitle")
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            location_el = card.find("span", class_="job-search-card__location")
            job_location = location_el.get_text(strip=True) if location_el else ""
            time_el = card.find("time")
            posted_date = time_el.get("datetime") if time_el else None
            jobs.append({
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": job_location,
                "posted_date": posted_date,
            })
        except Exception:
            logger.exception("Failed to parse search result card")
            continue
    return jobs


def _fetch_job_detail(job_id: str, client: httpx.Client) -> dict:
    url = DETAIL_URL.format(job_id=job_id)
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    response = client.get(url, headers=headers, follow_redirects=True, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    desc_el = soup.find("div", class_="description__text")
    description = desc_el.get_text(strip=True) if desc_el else ""
    seniority_el = soup.find("span", class_="job-criteria__text--seniority")
    seniority = seniority_el.get_text(strip=True) if seniority_el else None
    employment_el = soup.find("span", class_="job-criteria__text--employment-type")
    job_type = employment_el.get_text(strip=True) if employment_el else "Full-time"
    salary_el = soup.find("span", class_="job-criteria__text--salary")
    salary = salary_el.get_text(strip=True) if salary_el else None
    return {
        "description": description,
        "seniority": seniority,
        "job_type": job_type,
        "salary": salary,
    }


def _geocode_location(location: str, client: httpx.Client) -> tuple[Optional[float], Optional[float]]:
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json", "limit": 1}
        headers = {"User-Agent": "GeoHire/1.0"}
        response = client.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        logger.warning("Geocoding failed for '%s'", location)
    return None, None


def scrape_linkedin(
    location: str,
    query: str = "",
    max_jobs: int = 25,
) -> list[dict]:
    if not location.strip():
        return []
    jobs_data = []
    with httpx.Client() as client:
        search_url = _build_search_url(location, query, 0)
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        time.sleep(random.uniform(2, 6))
        response = client.get(search_url, headers=headers, follow_redirects=True, timeout=30)
        if response.status_code != 200:
            logger.warning("LinkedIn search returned %s", response.status_code)
            return []
        search_results = _parse_search_results(response.text)
        for result in search_results[:max_jobs]:
            try:
                time.sleep(random.uniform(1, 3))
                detail = _fetch_job_detail(result["job_id"], client)
                lat, lng = _geocode_location(result["location"], client)
                jobs_data.append({
                    "id": str(uuid.uuid4()),
                    "title": result["title"],
                    "company": result["company"],
                    "location": result["location"],
                    "description": detail.get("description", ""),
                    "requirements": [],
                    "salary": detail.get("salary"),
                    "job_type": detail.get("job_type", "Full-time"),
                    "posted_date": result.get("posted_date"),
                    "source": "linkedin",
                    "source_url": f"https://www.linkedin.com/jobs/view/{result['job_id']}/",
                    "latitude": lat,
                    "longitude": lng,
                })
            except Exception:
                logger.exception("Failed to fetch detail for job %s", result["job_id"])
                continue
    return jobs_data
