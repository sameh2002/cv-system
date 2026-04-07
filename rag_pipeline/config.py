# config.py
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
CHROMA_DIR = OUTPUT_DIR / "chroma_db"

# Modèle d'embeddings (multilingue français/anglais)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Paramètres de recherche
TOP_K_RESULTS = 5

# Créer le dossier
CHROMA_DIR.mkdir(parents=True, exist_ok=True)