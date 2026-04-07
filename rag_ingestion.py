# rag_ingestion.py
"""
Script d'indexation des CVs dans ChromaDB
À exécuter UNE SEULE FOIS après avoir généré structured_cvs.json
"""

import json
import sys
from pathlib import Path

from rag_pipeline.vector_store import get_vector_store


def load_and_store(json_path: str = "output/structured_cvs.json"):
    """Charge les CVs parsés et les indexe dans ChromaDB"""
    
    print("\n" + "="*60)
    print("📚 INDEXATION DES CVs DANS CHROMADB".center(60))
    print("="*60)
    
    # Vérifier que le fichier existe
    json_file = Path(json_path)
    if not json_file.exists():
        print(f"❌ Fichier {json_path} non trouvé!")
        print("   Veuillez d'abord exécuter: python main.py")
        return False
    
    # Charger les CVs
    print(f"\n📂 Chargement: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        cvs_data = json.load(f)
    
    print(f"✅ {len(cvs_data)} CVs chargés")
    
    # Initialiser ChromaDB
    print("\n🔧 Initialisation de ChromaDB...")
    vector_store = get_vector_store()
    vector_store.create_collection()
    
    # Vérifier si déjà des données
    current_count = vector_store.get_count()
    if current_count > 0:
        print(f"⚠️  La base contient déjà {current_count} documents")
        response = input("   Voulez-vous les remplacer? (o/N): ")
        if response.lower() == 'o':
            # Supprimer l'ancienne collection
            vector_store.client.delete_collection("cv_chunks")
            vector_store.create_collection()
            print("   ✅ Ancienne collection supprimée")
    
    # Indexer chaque CV
    print("\n📤 Indexation...")
    total_chunks = 0
    
    for cv in cvs_data:
        chunks = cv.get("chunks", [])
        if chunks:
            vector_store.add_chunks(chunks, cv["file"])
            total_chunks += len(chunks)
            print(f"   ✅ {Path(cv['file']).name}: {len(chunks)} chunks")
        else:
            print(f"   ⚠️  {Path(cv['file']).name}: aucun chunk")
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ".center(60))
    print("="*60)
    print(f"   CVs traités: {len(cvs_data)}")
    print(f"   Chunks indexés: {total_chunks}")
    print(f"   Base ChromaDB: {vector_store.get_count()} documents")
    
    print("\n✨ Indexation terminée!")
    return True


if __name__ == "__main__":
    load_and_store()