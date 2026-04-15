# rag_pipeline/retriever.py

from typing import List, Dict, Any, Optional
import logging
import re
from pathlib import Path

from .vector_store import get_vector_store
from .config import TOP_K_RESULTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Retriever:
    """ULTRA PRO Retriever corrigé et stable"""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.vector_store.create_collection()

    # =========================================================
    # 🔍 DETECT CANDIDATE
    # =========================================================
    def detect_candidate(self, query: str) -> Optional[str]:
        query_lower = query.lower()

        known_names = [
            "sameh", "mbarki",
            "faten", "chaabani",
            "malek", "abbes",
            "achref", "smari",
            "michael", "harris"
        ]

        for name in known_names:
            if name in query_lower:
                return name

        return None

    # =========================================================
    # 🎯 DETECT INTENT
    # =========================================================
    def detect_intent(self, query: str) -> Optional[str]:
        q = query.lower()

        if any(x in q for x in ["skill", "compétence", "competence", "technologie"]):
            return "SKILLS"

        if any(x in q for x in ["experience", "expérience", "stage", "work"]):
            return "EXPERIENCE"

        if any(x in q for x in ["education", "formation", "diplome"]):
            return "EDUCATION"

        return None

    # =========================================================
    # 🔎 RETRIEVE (FIX CHROMADB FILTER)
    # =========================================================
    def retrieve(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict[str, Any]]:
        logger.info(f"Query: {query}")

        candidate = self.detect_candidate(query)
        intent = self.detect_intent(query)

        filters = []

        # ✅ SAFE FILTERS
        if candidate:
            filters.append({"candidate_name": candidate})

        if intent:
            filters.append({"chunk_type": intent})

        # Build ChromaDB where
        where = None
        if len(filters) == 1:
            where = filters[0]
        elif len(filters) > 1:
            where = {"$and": filters}

        logger.info(f"Where filter: {where}")

        # 🔥 QUERY CHROMA
        results = self.vector_store.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        output = []

        for i in range(len(docs)):
            meta = metas[i] if i < len(metas) else {}

            output.append({
                "content": docs[i],
                "chunk_type": meta.get("chunk_type", "UNKNOWN"),
                "source_file": meta.get("source_file", "unknown"),
                "candidate_name": meta.get("candidate", "unknown"),
                "similarity_score": 1.0
            })

        return output

    # =========================================================
    # 🧠 ANSWER GENERATION
    # =========================================================
    def generate_answer(self, query: str, results: List[Dict[str, Any]]) -> str:
        if not results:
            return "❌ Aucun résultat trouvé."

        candidate = self.detect_candidate(query)
        intent = self.detect_intent(query)

        # 🔥 SKILLS
        if intent == "SKILLS":
            skills_text = " ".join([r["content"] for r in results])

            skills = re.findall(r'\b[A-Za-z\+#\.]+\b', skills_text)
            skills = list(set(skills))[:15]

            if candidate:
                return f"✅ Skills de {candidate.title()} : {', '.join(skills)}"

            return f"✅ Skills : {', '.join(skills)}"

        # 🔥 EXPERIENCE
        if intent == "EXPERIENCE":
            exp = [r["content"] for r in results[:3]]

            if candidate:
                return f"💼 Expérience de {candidate.title()}:\n- " + "\n- ".join(exp)

            return "💼 Expérience:\n- " + "\n- ".join(exp)

        # 🔥 EDUCATION
        if intent == "EDUCATION":
            edu = [r["content"] for r in results[:3]]

            if candidate:
                return f"🎓 Formation de {candidate.title()}:\n- " + "\n- ".join(edu)

            return "🎓 Formation:\n- " + "\n- ".join(edu)

        # 🔥 DEFAULT
        return self.format_results(results)

    # =========================================================
    # 📋 FORMAT DEBUG
    # =========================================================
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        if not results:
            return "❌ Aucun résultat trouvé."

        lines = [
            "\n" + "=" * 60,
            f"📋 {len(results)} résultats",
            "=" * 60
        ]

        for i, r in enumerate(results, 1):
            lines.append(f"\n🔹 Résultat {i}")
            lines.append(f"📁 {r['source_file']}")
            lines.append(f"🏷️ {r['chunk_type']}")
            lines.append(f"📝 {r['content'][:150]}...")

        return "\n".join(lines)