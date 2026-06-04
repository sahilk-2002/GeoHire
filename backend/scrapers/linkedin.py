import logging
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

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

_geocode_cache: dict[str, tuple[float, float]] = {}


def _geocode(location: str) -> Optional[tuple[float, float]]:
    if location in _geocode_cache:
        return _geocode_cache[location]
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json", "limit": 1}
        headers = {"User-Agent": "GeoHire/1.0"}
        resp = httpx.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        if data and len(data) > 0:
            coords = (float(data[0]["lat"]), float(data[0]["lon"]))
            _geocode_cache[location] = coords
            return coords
    except Exception:
        pass
    return None


def _jitter(base_lat: float, base_lng: float) -> tuple[float, float]:
    lat = base_lat + random.uniform(-0.02, 0.02)
    lng = base_lng + random.uniform(-0.02, 0.02)
    return (lat, lng)


def _extract_job_id(card) -> Optional[str]:
    entity_urn = card.get("data-entity-urn", "")
    if entity_urn:
        parts = entity_urn.split(":")
        if len(parts) >= 4:
            return parts[-1]
    return str(uuid.uuid4())


def _extract_text(el, selector: str, default: str = "") -> str:
    found = el.select_one(selector)
    return found.get_text(strip=True) if found else default


def _fetch_descriptions(urls: list[str]) -> dict[str, str]:
    result = {}
    if not urls:
        return result
    import concurrent.futures

    def _fetch_one(url: str) -> tuple[str, str]:
        if not url:
            return (url, "")
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            resp = httpx.get(url, headers=headers, follow_redirects=True, timeout=8)
            soup = BeautifulSoup(resp.text, "lxml")
            desc = soup.select_one("div.description, article.description, div[class*='description']")
            if desc:
                return (url, desc.get_text(strip=True)[:2000])
            meta = soup.select_one("meta[name='description']")
            if meta:
                return (url, meta.get("content", "")[:2000])
        except Exception:
            pass
        return (url, "")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for url, desc in pool.map(_fetch_one, urls):
            result[url] = desc
    return result


def search_linkedin(location: str, query: str = "", start: int = 0) -> Optional[list[dict]]:
    keywords = quote(query) if query else "software"
    loc_encoded = quote(location)
    url = f"{BASE_URL}?keywords={keywords}&location={loc_encoded}&start={start}"

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        resp = httpx.get(url, headers=headers, follow_redirects=True, timeout=30)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.warning("LinkedIn API HTTP %s for %s", e.response.status_code, location)
        return None
    except Exception as e:
        logger.warning("LinkedIn API request failed: %s", e)
        return None

    soup = BeautifulSoup(resp.text, "lxml")
    cards = soup.select("li[data-entity-urn]")
    if not cards:
        cards = soup.select("div.base-search-card, div.job-search-card")

    if not cards:
        logger.warning("No job cards found for %s", location)
        return None

    fallback_coords = _geocode(location)

    raw_cards = []
    for card in cards:
        try:
            raw_cards.append({
                "id": _extract_job_id(card),
                "title": _extract_text(card, "h3.base-search-card__title, [class*='search-card__title']") or _extract_text(card, "a[data-tracking-will-navigate] span") or "Unknown",
                "company": _extract_text(card, "h4.base-search-card__subtitle, a[class*='subtitle']") or _extract_text(card, "[class*='search-card__subtitle']") or "Unknown",
                "location": _extract_text(card, "span.job-search-card__location, [class*='search-card__location']") or location,
                "date": (card.select_one("time").get("datetime", "") if card.select_one("time") else ""),
                "url": (card.select_one("a.base-card__full-link").get("href", "") if card.select_one("a.base-card__full-link") else ""),
            })
        except Exception:
            continue

    desc_map = _fetch_descriptions([c["url"] for c in raw_cards])

    used_coords: set[tuple[float, float]] = set()
    jobs = []
    for c in raw_cards:
        try:
            coords = _geocode(c["location"])
            if coords is None and fallback_coords is not None:
                coords = _jitter(fallback_coords[0], fallback_coords[1])
            lat, lng = coords if coords else (None, None)
            if lat is not None and lng is not None:
                while (round(lat, 4), round(lng, 4)) in used_coords:
                    lat, lng = _jitter(lat, lng)
                used_coords.add((round(lat, 4), round(lng, 4)))

            jobs.append({
                "id": c["id"],
                "title": c["title"],
                "company": c["company"],
                "location": c["location"],
                "description": desc_map.get(c["url"], ""),
                "requirements": [],
                "salary": None,
                "job_type": "",
                "posted_date": c["date"],
                "source": "linkedin",
                "source_url": c["url"],
                "latitude": lat,
                "longitude": lng,
            })
        except Exception:
            continue

    return jobs
