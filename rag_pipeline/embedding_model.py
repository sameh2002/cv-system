# embedding_model.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import logging

from .config import EMBEDDING_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Générateur d'embeddings vectoriels"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        logger.info(f"Chargement du modèle: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Dimension des vecteurs: {self.dimension}")
    
    def encode_chunks_batch(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Encode plusieurs chunks en batch"""
        enhanced_texts = [f"[{c['type']}] {c['content']}" for c in chunks]
        embeddings = self.model.encode(enhanced_texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def encode_query(self, query: str) -> List[float]:
        """Encode une requête utilisateur"""
        return self.model.encode(query, convert_to_numpy=True).tolist()


# Singleton
_embedding_generator = None

def get_embedding_generator():
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator