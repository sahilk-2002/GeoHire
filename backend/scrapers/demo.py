import random
import uuid
from typing import Optional

import httpx

COMPANIES_BY_INDUSTRY = {
    "tech": [
        "TechVista", "CloudNova", "DataPulse", "CodeCraft", "NeuralWorks",
        "SkyNet Solutions", "ByteBridge", "Quantum Leap", "Pixel Labs", "InnoTech",
    ],
    "finance": [
        "Apex Financial", "Pinnacle Bank", "Horizon Capital", "Meridian Trust",
        "Crestline Partners", "Summit Wealth", "BlueRock Advisory", "IronVault Finance",
    ],
    "healthcare": [
        "MediCore Health", "VitalCare", "BioGenesis Labs", "HealthFirst Group",
        "LifePath Medical", "CurePoint", "Synergy Health", "PulseMed",
    ],
    "education": [
        "EduPrime", "LearnSphere", "AcademiaNext", "SkillForge",
        "KnowledgeHub", "BrightPath Learning", "EduVantage",
    ],
    "retail": [
        "UrbanCart", "StyleCraft", "MarketMosaic", "RetailSync",
        "PrimeCart", "FreshPick", "OmniStore",
    ],
}

ROLE_TEMPLATES = {
    "tech": [
        ("Senior {role}", "{company}", "{location}", "Full-time"),
        ("{role}", "{company}", "{location}", "Full-time"),
        ("Junior {role}", "{company}", "{location}", "Full-time"),
        ("Lead {role}", "{company}", "{location}", "Full-time"),
        ("{role} Intern", "{company}", "{location}", "Internship"),
        ("Senior {role}", "{company}", "{location}", "Remote"),
        ("Principal {role}", "{company}", "{location}", "Full-time"),
        ("{role} – Contract", "{company}", "{location}", "Contract"),
    ],
    "finance": [
        ("Senior {role}", "{company}", "{location}", "Full-time"),
        ("{role}", "{company}", "{location}", "Full-time"),
        ("Associate {role}", "{company}", "{location}", "Full-time"),
        ("VP of {role}", "{company}", "{location}", "Full-time"),
        ("{role} Analyst", "{company}", "{location}", "Full-time"),
    ],
    "healthcare": [
        ("{role}", "{company}", "{location}", "Full-time"),
        ("Senior {role}", "{company}", "{location}", "Full-time"),
        ("Lead {role}", "{company}", "{location}", "Full-time"),
        ("{role} Specialist", "{company}", "{location}", "Full-time"),
    ],
    "education": [
        ("{role}", "{company}", "{location}", "Full-time"),
        ("Senior {role}", "{company}", "{location}", "Full-time"),
        ("Assistant {role}", "{company}", "{location}", "Part-time"),
        ("{role} – Adjunct", "{company}", "{location}", "Contract"),
    ],
    "retail": [
        ("{role}", "{company}", "{location}", "Full-time"),
        ("Store {role}", "{company}", "{location}", "Full-time"),
        ("Assistant {role}", "{company}", "{location}", "Part-time"),
        ("Regional {role}", "{company}", "{location}", "Full-time"),
    ],
}

TECH_ROLES = [
    "Software Engineer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "Data Engineer", "DevOps Engineer",
    "Product Manager", "UX Designer", "QA Engineer", "Mobile Developer",
    "Cloud Architect", "Security Engineer", "ML Engineer", "Data Scientist",
    "Systems Administrator", "Scrum Master", "Technical Writer",
]

FINANCE_ROLES = [
    "Financial Analyst", "Accountant", "Auditor", "Investment Banker",
    "Risk Manager", "Compliance Officer", "Financial Advisor",
    "Portfolio Manager", "Tax Specialist", "Treasury Analyst",
]

HEALTHCARE_ROLES = [
    "Registered Nurse", "Physician Assistant", "Medical Technologist",
    "Healthcare Administrator", "Clinical Researcher", "Pharmacist",
    "Physical Therapist", "Lab Technician", "Health Informatics Specialist",
]

EDUCATION_ROLES = [
    "Teacher", "Professor", "Curriculum Developer", "Academic Advisor",
    "Instructional Designer", "Education Coordinator", "Research Associate",
    "Dean of Students", "Learning Specialist",
]

RETAIL_ROLES = [
    "Sales Associate", "Store Manager", "Merchandiser", "Supply Chain Analyst",
    "E-commerce Specialist", "Customer Service Manager", "Buyer",
    "Inventory Planner", "Visual Merchandiser",
]

ROLES_BY_INDUSTRY = {
    "tech": TECH_ROLES,
    "finance": FINANCE_ROLES,
    "healthcare": HEALTHCARE_ROLES,
    "education": EDUCATION_ROLES,
    "retail": RETAIL_ROLES,
}

SALARY_RANGES = {
    "tech": ["$80k – $120k", "$100k – $150k", "$120k – $180k", "$150k – $220k", "$60k – $90k"],
    "finance": ["$70k – $100k", "$90k – $140k", "$120k – $180k", "$150k – $250k"],
    "healthcare": ["$60k – $90k", "$80k – $120k", "$100k – $160k", "$130k – $200k"],
    "education": ["$40k – $60k", "$50k – $75k", "$65k – $95k", "$80k – $120k"],
    "retail": ["$35k – $50k", "$45k – $65k", "$55k – $85k", "$70k – $110k"],
}

DESCRIPTION_TEMPLATES = [
    "We are looking for a talented professional to join our growing team in {location}. You will work on cutting-edge projects that impact millions of users.",
    "Join our innovative team in {location} and help shape the future of our industry. We offer competitive compensation and a collaborative work environment.",
    "An exciting opportunity has opened at {company} in {location}. We're seeking someone passionate about delivering exceptional results.",
    "{company} is expanding its {location} office and needs a skilled professional to drive key initiatives. Excellent growth potential.",
    "Be part of something big. {company} is hiring for our {location} team. You'll work with industry leaders on meaningful projects.",
]

REQUIREMENTS_POOL = {
    "tech": [
        "Bachelor's in Computer Science or related field",
        "3+ years of relevant experience",
        "Strong problem-solving skills",
        "Experience with agile methodologies",
        "Excellent communication skills",
        "Proficiency in relevant programming languages",
        "Experience with cloud platforms (AWS/GCP/Azure)",
        "Knowledge of CI/CD pipelines",
        "Strong understanding of data structures and algorithms",
        "Experience with version control (Git)",
    ],
}


def _geocode_location(location: str) -> Optional[tuple[float, float]]:
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


def _infer_industry(location: str) -> str:
    loc_lower = location.lower()
    tech_hubs = ["san francisco", "san jose", "palo alto", "seattle", "new york",
                 "austin", "boston", "bangalore", "bengaluru", "hyderabad", "pune",
                 "london", "berlin", "dublin", "tokyo", "singapore", "tel aviv",
                 "chennai", "mumbai", "gurgaon", "noida", "delhi"]
    finance_hubs = ["new york", "london", "hong kong", "singapore", "zurich",
                    "frankfurt", "chicago", "mumbai", "tokyo"]
    for hub in tech_hubs:
        if hub in loc_lower:
            return "tech"
    for hub in finance_hubs:
        if hub in loc_lower:
            return random.choice(["tech", "finance"])
    weights = ["tech"] * 40 + ["finance"] * 20 + ["healthcare"] * 15 + ["education"] * 15 + ["retail"] * 10
    return random.choice(weights)


def generate_jobs(location: str, count: int = 15) -> list[dict]:
    coords = _geocode_location(location)
    lat, lng = coords if coords else (20.0, 0.0)

    industry = _infer_industry(location)
    companies = COMPANIES_BY_INDUSTRY[industry]
    roles = ROLES_BY_INDUSTRY[industry]
    templates = ROLE_TEMPLATES[industry]
    salaries = SALARY_RANGES[industry]
    requirements = REQUIREMENTS_POOL["tech"]

    jobs = []
    for _ in range(count):
        role = random.choice(roles)
        company = random.choice(companies)
        template = random.choice(templates)
        salary = random.choice(salaries)

        title = template[0].format(role=role, company=company, location=location)
        desc = random.choice(DESCRIPTION_TEMPLATES).format(company=company, location=location)
        reqs = random.sample(requirements, min(random.randint(3, 6), len(requirements)))

        job_lat = lat + random.uniform(-0.05, 0.05)
        job_lng = lng + random.uniform(-0.05, 0.05)

        jobs.append({
            "id": str(uuid.uuid4()),
            "title": title,
            "company": company,
            "location": location,
            "description": desc,
            "requirements": reqs,
            "salary": salary,
            "job_type": template[3],
            "posted_date": "Posted today",
            "source": "demo",
            "source_url": "",
            "latitude": round(job_lat, 6),
            "longitude": round(job_lng, 6),
        })

    return jobs
