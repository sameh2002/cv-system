import json
from pathlib import Path
from rag_pipeline.vector_store import get_vector_store


def load_and_store(json_path="output/structured_cvs.json"):
    print("\n📚 INDEXING CVs...")

    with open(json_path, "r", encoding="utf-8") as f:
        cvs_data = json.load(f)

    vs = get_vector_store()
    vs.create_collection()

    total = 0

    for cv in cvs_data:
        chunks = cv.get("chunks", [])
        entities = cv.get("entities", {})

        # 🔥 SAFE NAME HANDLING
        candidate_name = entities.get("name") or "unknown"
        candidate_name = str(candidate_name).strip().lower()

        enriched = []

        for c in chunks:
            enriched.append({
                "type": c["type"],
                "content": c["content"],
                "candidate_name": candidate_name
            })

        vs.add_chunks(enriched, cv["file"])
        total += len(enriched)

        print(f"✔ {candidate_name}: {len(enriched)} chunks")

    print(f"\n✅ DONE: {total} chunks indexed")
    return True


if __name__ == "__main__":
    load_and_store()