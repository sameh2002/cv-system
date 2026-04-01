from rag.vector_store import query_documents


def retrieve(query, top_k=3):
    results = query_documents(query, n_results=top_k)

    documents = results["documents"][0]

    return documents