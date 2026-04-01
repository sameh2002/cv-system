import re

SECTION_KEYWORDS = {
    "EXPERIENCE": [
        "experience", "work experience", "professional experience",
        "stage", "internship", "emploi"
    ],
    "EDUCATION": [
        "education", "academic", "bachelor", "master",
        "licence", "degree"
    ],
    "SKILLS": [
        "skills", "competences", "compétences", "technical skills"
    ],
    "CERTIFICATIONS": [
        "certification", "certificates", "certificats"
    ]
}


def detect_type(text: str):
    t = text.lower()

    for section, keywords in SECTION_KEYWORDS.items():
        if any(k in t for k in keywords):
            return section

    return None


def create_chunks(text: str, max_chars: int = 600):

    lines = text.split("\n")

    chunks = []
    buffer = []
    current_type = "GENERAL"

    def flush():
        nonlocal buffer, current_type

        if not buffer:
            return

        content = " ".join(buffer).strip()

        if len(content) < 20:
            buffer.clear()
            return

        # filtrer langues
        if current_type == "SKILLS":
            if any(x in content.lower() for x in ["langue", "language", "arabe", "français", "anglais"]):
                buffer.clear()
                return

        #  éviter chunks trop longs
        if len(content.split()) > 80:
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

        detected = detect_type(line)

        if detected:
            flush()
            current_type = detected
            continue

        buffer.append(line)

        if len(" ".join(buffer)) > max_chars:
            flush()

    flush()

    return chunks