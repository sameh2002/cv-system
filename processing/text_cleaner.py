import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    # garder les sauts de ligne
    text = re.sub(r'[ \t]+', ' ', text)

    # enlever caractères bizarres
    text = re.sub(r'[^a-zA-ZÀ-ÿ0-9@%:.,+/#()\-\n\' ]', ' ', text)

    # nettoyer espaces multiples (sans toucher aux \n)
    text = re.sub(r' +', ' ', text)

    return text.strip()