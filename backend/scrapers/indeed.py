import logging
import time
import random
import uuid
from typing import Optional
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]


def _build_url(location: str, query: str = "") -> str:
    encoded_location = quote(location)
    query_part = f"&q={quote(query)}" if query else ""
    return f"https://www.indeed.com/jobs?l={encoded_location}{query_part}&sort=date"


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


def _extract_source_url(card, base_url: str) -> str:
    link = card.select_one("h2.jobTitle a, a[data-jk]")
    if link and link.get("href"):
        href = link["href"]
        if href.startswith("/"):
            return f"https://www.indeed.com{href}"
        return href
    return base_url


def scrape_indeed(
    location: str, query: str = "", client: Optional[httpx.Client] = None
) -> list[dict]:
    if not location.strip():
        raise ValueError("location must not be empty")

    url = _build_url(location, query)
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    time.sleep(random.uniform(2, 6))

    if client is None:
        with httpx.Client() as client:
            response = client.get(url, headers=headers, follow_redirects=True, timeout=30)
    else:
        response = client.get(url, headers=headers, follow_redirects=True, timeout=30)
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

            source_url = _extract_source_url(card, url)

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
                    "source_url": source_url,
                    "latitude": None,
                    "longitude": None,
                }
            )
        except Exception:
            logger.exception("Failed to parse job card")
            continue

    return jobs
