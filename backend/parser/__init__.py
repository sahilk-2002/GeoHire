import io
import re
import uuid
from typing import Optional

SKILL_KEYWORDS = [
    "python", "javascript", "typescript", "java", "c#", "c++", "go", "rust",
    "react", "vue", "angular", "node.js", "express", "django", "flask", "fastapi",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "git", "ci/cd", "jenkins", "github actions",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "agile", "scrum", "project management", "leadership",
    "communication", "teamwork", "problem-solving",
    "figma", "sketch", "photoshop", "ui/ux",
    "rest api", "graphql", "grpc", "microservices",
]


def extract_text_from_pdf(content: bytes) -> str:
    import fitz
    doc = fitz.open(stream=content, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def extract_text_from_docx(content: bytes) -> str:
    import docx
    doc = docx.Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs)


def _find_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = set()
    for keyword in SKILL_KEYWORDS:
        
        pattern = re.escape(keyword)
        if re.search(pattern, lowered):
            found.add(keyword)
    return sorted(found)


def _estimate_experience(text: str) -> Optional[float]:
    matches = re.findall(r"(\d+)\s*(?:\+|years?\s*(?:of\s+)?experience|yoe)", text.lower())
    if matches:
        years = [int(m) for m in matches]
        return float(max(years))
    return None


def parse_resume(filename: str, content: bytes) -> dict:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        text = extract_text_from_pdf(content)
    elif ext == "docx":
        text = extract_text_from_docx(content)
    else:
        raise ValueError(f"Unsupported format: {ext}")

    skills = _find_skills(text)
    experience_years = _estimate_experience(text)

    
    title_keywords = ["engineer", "developer", "designer", "manager", "analyst",
                      "architect", "scientist", "consultant", "intern"]
    titles_found = []
    for kw in title_keywords:
        if re.search(rf"\b{re.escape(kw)}\w*\b", text.lower()):
            titles_found.append(kw.capitalize())

    
    education_keywords = ["bachelor", "master", "phd", "ph.d", "b.s", "m.s",
                          "b.tech", "m.tech", "ba", "ma", "degree",
                          "university", "college", "institute"]
    education = []
    for kw in education_keywords:
        if re.search(rf"\b{re.escape(kw)}\w*\b", text.lower()):
            education.append(kw.capitalize())

    return {
        "id": str(uuid.uuid4()),
        "skills": skills,
        "experience_years": experience_years,
        "job_titles": list(set(titles_found)),
        "education": list(set(education)),
    }
