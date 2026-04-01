import chromadb
from chromadb.config import Settings

# créer client local
client = chromadb.Client(Settings(persist_directory="./chroma_db"))

# créer collection
collection = client.get_or_create_collection(name="cv_collection")


def add_documents(chunks, ids):
    collection.add(
        documents=chunks,
        ids=ids
    )


def query_documents(query, n_results=3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results