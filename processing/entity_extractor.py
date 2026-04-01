import re
import spacy

nlp_en = spacy.load("en_core_web_sm")
nlp_fr = spacy.load("fr_core_news_sm")



def detect_name(text):
    lines = text.split("\n")[:15]

    for line in lines:
        line = line.strip()

        if not line or "@" in line:
            continue

        if line.lower() in ["developer", "engineer", "manager"]:
            continue

        if line.isupper() and len(line.split()) <= 4:
            return line.title()

        clean = re.sub(r"[0-9]", "", line)
        words = clean.split()

        words = [w for w in words if re.match(r"^[A-Za-zÀ-ÿ\-]+$", w)]

        blacklist = [
            "experience", "education", "skills", "profile",
            "summary", "cv", "resume"
        ]

        if len(words) >= 2 and not any(b in line.lower() for b in blacklist):

            # éviter job titles
            job_words = ["developer", "engineer", "manager", "intern"]
            if any(w.lower() in job_words for w in words):
                continue

            return words[0].capitalize() + " " + words[1].capitalize()

    return None



def extract_experience(text):

    experiences = []
    buffer = []
    in_section = False

    keywords = ["experience", "stage", "internship", "work", "expérience"]
    stop_keywords = ["education", "skills", "compétences", "certificat"]

    for line in text.split("\n"):
        l = line.strip()
        if not l:
            continue

        l_lower = l.lower()

        if any(k in l_lower for k in keywords) and len(l.split()) < 6:
            in_section = True
            continue

        if any(k in l_lower for k in stop_keywords):
            if buffer:
                experiences.append({"text": " ".join(buffer)})
                buffer = []
            in_section = False

        if in_section:

            #  séparation par date
            if re.search(r"\d{4}", l) and buffer:
                experiences.append({"text": " ".join(buffer)})
                buffer = []

            buffer.append(l)

    if buffer:
        experiences.append({"text": " ".join(buffer)})

    return experiences



def extract_education(text):

    education = []
    buffer = []
    in_section = False

    keywords = ["education", "bachelor", "master", "licence", "baccalauréat"]
    stop_keywords = ["experience", "skills", "compétences"]

    for line in text.split("\n"):
        l = line.strip()
        if not l:
            continue

        l_lower = l.lower()

        if any(k in l_lower for k in keywords) and len(l.split()) < 6:
            in_section = True
            continue

        # éviter mélange certificats
        if any(k in l_lower for k in stop_keywords) or "certificat" in l_lower:
            if buffer:
                education.append({"text": " ".join(buffer)})
                buffer = []
            in_section = False

        if in_section:
            buffer.append(l)

    if buffer:
        education.append({"text": " ".join(buffer)})

    return education



def extract_skills(text):

    skills_list = [
        "python", "java", "sql", "html", "css",
        "javascript", "react", "node.js", "php",
        "angular", "docker", "mysql", "pl/sql",
        "git", "linux",
        "machine learning", "deep learning",
        "seo", "marketing", "data analysis",
        "power bi", "excel",
        "google analytics", "semrush", "sem",
        "social media", "content marketing"
    ]

    text_lower = text.lower()

    found = [skill for skill in skills_list if skill in text_lower]

    return list(set(found))



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