import chromadb
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from .config import CHROMA_DIR
from .embedding_model import get_embedding_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:

    def __init__(self):
        self.embedding_gen = get_embedding_generator()
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = None

    def create_collection(self, name="cv_chunks"):
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )

    # ======================================================
    # ADD CHUNKS (CORRIGÉ + candidate_name)
    # ======================================================
    def add_chunks(self, chunks: List[Dict[str, Any]], source_file: str):

        if not chunks:
            return

        if self.collection is None:
            self.create_collection()

        embeddings = self.embedding_gen.encode_chunks_batch(chunks)

        ids, docs, metas = [], [], []

        for i, chunk in enumerate(chunks):

            candidate = chunk.get("candidate_name", "unknown")

            chunk_id = f"{Path(source_file).stem}_{i}_{hash(chunk['content']) % 10000}"

            ids.append(chunk_id)
            docs.append(chunk["content"])

            metas.append({
                "source_file": source_file,
                "chunk_type": chunk["type"],
                "file_name": Path(source_file).name,
                "candidate_name": candidate.lower().strip()
            })

        self.collection.add(
            ids=ids,
            documents=docs,
            metadatas=metas,
            embeddings=embeddings
        )

    # ======================================================
    # SEARCH SIMPLE
    # ======================================================
    def search(self, query: str, top_k: int = 5):

        if self.collection is None:
            self.create_collection()

        query_embedding = self.embedding_gen.encode_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        output = []

        if results["ids"]:

            for i in range(len(results["ids"][0])):

                distance = results["distances"][0][i]
                similarity = 1 - distance

                meta = results["metadatas"][0][i]

                output.append({
                    "content": results["documents"][0][i],
                    "source_file": meta["source_file"],
                    "chunk_type": meta["chunk_type"],
                    "candidate_name": meta.get("candidate_name", "unknown"),
                    "similarity_score": round(similarity, 4)
                })

        return output

    def get_count(self):
        return self.collection.count() if self.collection else 0


# SINGLETON
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store