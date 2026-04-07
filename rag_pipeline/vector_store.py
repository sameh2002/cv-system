# vector_store.py
import chromadb
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from .config import CHROMA_DIR
from .embedding_model import get_embedding_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store basé sur ChromaDB"""
    
    def __init__(self):
        self.embedding_gen = get_embedding_generator()
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = None
    
    def create_collection(self, collection_name: str = "cv_chunks"):
        """Crée ou récupère une collection"""
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Collection prête - {self.collection.count()} documents")
    
    def add_chunks(self, chunks: List[Dict[str, Any]], source_file: str):
        """Ajoute des chunks à la base"""
        if not chunks:
            return
        
        if self.collection is None:
            self.create_collection()
        
        # Générer les embeddings
        embeddings = self.embedding_gen.encode_chunks_batch(chunks)
        
        # Préparer les données
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{Path(source_file).stem}_{i}_{hash(chunk['content']) % 10000}"
            ids.append(chunk_id)
            documents.append(chunk['content'])
            metadatas.append({
                "source_file": source_file,
                "chunk_type": chunk['type'],
                "file_name": Path(source_file).name
            })
        
        # Ajouter à ChromaDB
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        logger.info(f"Ajouté {len(chunks)} chunks de {Path(source_file).name}")
    
    def search(self, query: str, top_k: int = 5, 
               chunk_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Recherche les chunks pertinents"""
        if self.collection is None:
            self.create_collection()
        
        if self.collection.count() == 0:
            return []
        
        query_embedding = self.embedding_gen.encode_query(query)
        
        where_filter = {"chunk_type": chunk_type} if chunk_type else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        
        formatted_results = []
        if results and results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                distance = results['distances'][0][i] if results.get('distances') else 0
                similarity = 1 - distance
                
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "source_file": results['metadatas'][0][i]['source_file'],
                    "chunk_type": results['metadatas'][0][i]['chunk_type'],
                    "similarity_score": round(similarity, 4),
                    "id": results['ids'][0][i]
                })
        
        return formatted_results
    
    def get_count(self) -> int:
        if self.collection is None:
            return 0
        return self.collection.count()


# Singleton
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store