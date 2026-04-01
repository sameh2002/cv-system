import json
from rag.vector_store import add_documents
from rag.retriever import retrieve


def index_cvs(json_file):

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_chunks = []
    all_ids = []

    for i, cv in enumerate(data):
        for j, chunk in enumerate(cv["chunks"]):
            all_chunks.append(chunk)
            all_ids.append(f"cv_{i}_chunk_{j}")

    add_documents(all_chunks, all_ids)

    print(" Indexing done!")


def ask_question(query):

    docs = retrieve(query)

    print("\n🔍 Top results:\n")

    for i, d in enumerate(docs):
        print(f"{i+1}. {d}\n")