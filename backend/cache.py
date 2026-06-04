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
