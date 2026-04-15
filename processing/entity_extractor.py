import re
import spacy

nlp_en = spacy.load("en_core_web_sm")
nlp_fr = spacy.load("fr_core_news_sm")

# ---------------------------
# NAME DETECTION
# ---------------------------
def detect_name(text):
    lines = text.split("\n")[:10]

    blacklist = [
        "experience", "education", "skills", "profile",
        "summary", "cv", "resume", "technicienne",
        "technicien", "ingenieur", "engineer",
        "developer", "manager"
    ]

    for line in lines:
        line = line.strip()

        if not line or "@" in line:
            continue

        if any(b in line.lower() for b in blacklist):
            continue

        # Nettoyer caractères parasites
        line = re.sub(r"[^A-Za-zÀ-ÿ\s]", "", line)

        words = line.split()

        if 2 <= len(words) <= 4:
            if all(w[0].isupper() for w in words if len(w) > 1):
                return " ".join(words[:3])

    return None


# ---------------------------
# SKILLS EXTRACTION
# ---------------------------
def extract_skills(text):
    skills_list = [
        "python", "java", "sql", "html", "css",
        "javascript", "react", "node.js", "nodejs",
        "php", "angular", "docker", "mysql",
        "pl/sql", "plsql", "git", "linux",
        "scrum", "aws", "tensorflow", "pytorch"
    ]

    text_lower = text.lower()

    found = set()

    for skill in skills_list:
        if skill in text_lower:
            found.add(skill.replace(".js", "").replace("/", "").strip())

    return list(found)


# ---------------------------
# EXPERIENCE EXTRACTION (IMPROVED)
# ---------------------------
def extract_experience(text):
    experiences = []
    lines = text.split("\n")

    buffer = []
    in_section = False

    keywords = ["experience", "stage", "internship", "work", "expérience"]
    stop_keywords = ["education", "skills", "compétences", "certificat", "langues"]

    for line in lines:
        l = line.strip()
        if not l:
            continue

        l_lower = l.lower()

        if any(k in l_lower for k in keywords) and len(l.split()) < 6:
            in_section = True
            continue

        if any(k in l_lower for k in stop_keywords):
            if buffer:
                experiences.append({"text": clean_text(" ".join(buffer))})
                buffer = []
            in_section = False

        if in_section:
            # Nouvelle expérience si date détectée
            if re.search(r"\b(20\d{2}|19\d{2})\b", l) and buffer:
                experiences.append({"text": clean_text(" ".join(buffer))})
                buffer = []

            buffer.append(l)

    if buffer:
        experiences.append({"text": clean_text(" ".join(buffer))})

    return experiences


# ---------------------------
# EDUCATION EXTRACTION (IMPROVED)
# ---------------------------
def extract_education(text):
    education = []
    lines = text.split("\n")

    buffer = []
    in_section = False

    keywords = ["education", "bachelor", "master", "licence", "baccalauréat", "formation"]
    stop_keywords = ["experience", "skills", "compétences", "certificat"]

    for line in lines:
        l = line.strip()
        if not l:
            continue

        l_lower = l.lower()

        if any(k in l_lower for k in keywords) and len(l.split()) < 6:
            in_section = True
            continue

        if any(k in l_lower for k in stop_keywords):
            if buffer:
                education.append({"text": clean_text(" ".join(buffer))})
                buffer = []
            in_section = False

        if in_section:
            buffer.append(l)

    if buffer:
        education.append({"text": clean_text(" ".join(buffer))})

    return education


# ---------------------------
# CLEAN TEXT (IMPORTANT)
# ---------------------------
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'http\S+', '', text)  # remove links
    text = re.sub(r'\S+@\S+', '', text)  # remove emails
    return text.strip()


# ---------------------------
# MAIN FUNCTION
# ---------------------------
def extract_entities(text):
    entities = {
        "name": detect_name(text),
        "email": None,
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text)
    }

    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if email:
        entities["email"] = email.group()

    return entities