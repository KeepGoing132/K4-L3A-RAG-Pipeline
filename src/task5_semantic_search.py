"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    query_vector = embed_texts([query])[0]
    response = get_collection().query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    results = []
    if response and response.get("ids") and response["ids"][0]:
        for item_id, content, metadata, distance in zip(
            response["ids"][0],
            response["documents"][0],
            response["metadatas"][0],
            response["distances"][0],
        ):
            score = max(0.0, 1.0 - float(distance))
            clean_meta = dict(metadata) if metadata else {}
            if "chunk_index" in clean_meta:
                clean_meta["chunk_index"] = int(clean_meta["chunk_index"])
            if clean_meta.get("url") == "":
                clean_meta["url"] = None

            results.append({
                "id": item_id,
                "content": content,
                "score": score,
                "metadata": clean_meta,
                "retrieval_method": "dense",
            })
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    for result in semantic_search("thuế hộ kinh doanh", top_k=3):
        print(f"[{result['score']:.4f}] {result['id']} - {result['metadata'].get('title', '')}")
