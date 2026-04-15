from rag_pipeline.retriever import Retriever
from rag_ingestion import load_and_store


def interactive_mode():
    print("\n🎯 RAG CV SYSTEM")
    print("=" * 50)
    print("Commands:")
    print("- index  → rebuild database")
    print("- exit   → quit")
    print("=" * 50)

    retriever = Retriever()

    # 🔥 auto index si vide
    if retriever.vector_store.get_count() == 0:
        print("📦 Base vide → indexing...")
        load_and_store()
        retriever = Retriever()

    print(f"✅ Ready: {retriever.vector_store.get_count()} documents\n")

    while True:
        query = input("\n❓ Question: ").strip()

        if not query:
            continue

        if query.lower() in ["exit", "quit"]:
            break

        # 🔥 INDEX MODE
        if query.lower() == "index":
            print("\n📚 Re-indexing database...")
            load_and_store()
            retriever = Retriever()
            continue

        # 🔥 SEARCH
        results = retriever.retrieve(query, top_k=5)

        print(retriever.format_results(results))


if __name__ == "__main__":
    interactive_mode()