import re

SECTION_KEYWORDS = {
    "EXPERIENCE": [
        "experience", "work experience", "professional experience",
        "stage", "internship", "emploi", "expérience"
    ],
    "EDUCATION": [
        "education", "academic", "bachelor", "master",
        "licence", "degree", "formation", "études"
    ],
    "SKILLS": [
        "skills", "competences", "compétences",
        "technical skills"
    ],
    "CERTIFICATIONS": [
        "certification", "certificates", "certificat"
    ]
}


# ---------------------------
# DETECT SECTION TYPE
# ---------------------------
def detect_type(text: str):
    t = text.lower()

    # ignorer langues
    if any(x in t for x in ["langue", "language", "arabe", "français", "anglais"]):
        return None

    for section, keywords in SECTION_KEYWORDS.items():
        if any(k in t for k in keywords):
            return section

    return None


# ---------------------------
# CLEAN TEXT
# ---------------------------
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    return text.strip()


# ---------------------------
# CREATE CHUNKS (FINAL VERSION)
# ---------------------------
def create_chunks(text: str, max_chars: int = 500):
    lines = text.split("\n")

    chunks = []
    buffer = []
    current_type = "GENERAL"

    def flush():
        nonlocal buffer, current_type

        if not buffer:
            return

        content = clean_text(" ".join(buffer))

        # ❌ filtrer contenu trop court
        if len(content) < 30:
            buffer.clear()
            return

        # ❌ filtrer soft skills inutiles
        if any(x in content.lower() for x in [
            "self-motivated", "hard working", "team environment",
            "working well under pressure"
        ]):
            buffer.clear()
            return

        chunks.append({
            "type": current_type,
            "content": content
        })

        buffer.clear()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        line_lower = line.lower()

        # ❌ FILTRE CONTACT / BRUIT
        if any(x in line_lower for x in [
            "linkedin", "+216", "phone", "contact", "email", "github"
        ]):
            continue

        # ❌ FILTRE LANGUES
        if any(x in line_lower for x in [
            "languages", "langues", "arabic", "english", "french"
        ]):
            continue

        detected = detect_type(line)

        if detected:
            flush()
            current_type = detected
            continue

        # ignorer lignes trop courtes
        if len(line) < 3:
            continue

        buffer.append(line)

        # flush si chunk trop long
        if len(" ".join(buffer)) > max_chars:
            flush()

    flush()

    # ---------------------------
    # REMOVE DUPLICATES
    # ---------------------------
    unique_chunks = []
    seen = set()

    for chunk in chunks:
        if chunk["content"] not in seen:
            seen.add(chunk["content"])
            unique_chunks.append(chunk)

    return unique_chunks