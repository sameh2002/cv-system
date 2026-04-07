# main_rag.py
"""
Interface principale du système RAG
"""

import sys
from pathlib import Path

from rag_pipeline.retriever import Retriever
from rag_ingestion import load_and_store


def interactive_mode():
    """Mode interactif pour poser des questions"""
    
    print("\n" + "🎯 SYSTÈME RAG - QUESTIONS SUR LES CVs".center(60, "="))
    print("\n💡 Commandes:")
    print("   • tapez votre question normalement")
    print("   • 'exit' ou 'quit' pour quitter")
    print("   • 'skills' pour chercher par compétence")
    print("   • 'index' pour réindexer les CVs")
    print("="*60 + "\n")
    
    retriever = Retriever()
    
    # Vérifier que la base n'est pas vide
    count = retriever.vector_store.get_count()
    if count == 0:
        print("⚠️  Base vide! Indexation automatique...")
        load_and_store()
        retriever = Retriever()
        count = retriever.vector_store.get_count()
    
    print(f"✅ Base prête: {count} documents dans ChromaDB\n")
    
    while True:
        try:
            user_input = input("\n❓ Votre question: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 Au revoir!")
                break
            
            if user_input.lower() == 'index':
                load_and_store()
                retriever = Retriever()
                continue
            
            if user_input.lower().startswith('skills'):
                skill = user_input.replace('skills', '').strip()
                if skill:
                    results = retriever.retrieve(f"compétences en {skill}", top_k=5, chunk_type="SKILLS")
                else:
                    results = retriever.retrieve("compétences techniques", top_k=5, chunk_type="SKILLS")
            else:
                results = retriever.retrieve(user_input, top_k=5)
            
            print(retriever.format_results(results))
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    interactive_mode()