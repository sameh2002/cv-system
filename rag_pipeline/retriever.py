# retriever.py
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from .vector_store import get_vector_store
from .config import TOP_K_RESULTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Retriever:
    """Récupérateur de chunks pertinents"""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.vector_store.create_collection()
    
    def retrieve(self, query: str, top_k: int = TOP_K_RESULTS,
                 chunk_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère les chunks les plus pertinents"""
        logger.info(f"Recherche: '{query}'")
        return self.vector_store.search(query, top_k, chunk_type)
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """Formate les résultats pour affichage"""
        if not results:
            return "❌ Aucun résultat trouvé."
        
        lines = [f"\n{'='*60}", f"📋 {len(results)} résultat(s) trouvé(s)", f"{'='*60}"]
        
        for i, r in enumerate(results, 1):
            lines.append(f"\n🔸 Résultat {i} (similarité: {r['similarity_score']:.3f})")
            lines.append(f"   📁 Fichier: {Path(r['source_file']).name}")
            lines.append(f"   🏷️  Type: {r['chunk_type']}")
            lines.append(f"   📝 Contenu: {r['content'][:200]}...")
        
        return "\n".join(lines)