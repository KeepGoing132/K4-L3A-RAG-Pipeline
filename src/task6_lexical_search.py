"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""


CORPUS: list[dict] = []


def get_corpus() -> list[dict]:
    global CORPUS
    if not CORPUS:
        try:
            from .task4_chunking_indexing import chunk_documents, load_documents
            CORPUS = chunk_documents(load_documents())
        except Exception:
            CORPUS = []
    return CORPUS


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    from rank_bm25 import BM25Plus
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Plus(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    import numpy as np

    corpus = CORPUS if CORPUS else get_corpus()
    if not corpus:
        return []

    bm25 = build_bm25_index(corpus)
    scores = bm25.get_scores(query.lower().split())
    indices = np.argsort(scores)[::-1]

    results = []
    for index in indices:
        if len(results) >= top_k:
            break
        score_val = float(scores[index])
        if score_val <= 0:
            continue
        item = corpus[index]
        clean_meta = dict(item["metadata"])
        if "chunk_index" in clean_meta:
            clean_meta["chunk_index"] = int(clean_meta["chunk_index"])
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": score_val,
            "metadata": clean_meta,
            "retrieval_method": "bm25",
        })
    return results[:top_k]


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    for result in lexical_search("hộ kinh doanh", top_k=3):
        print(f"[{result['score']:.4f}] {result['id']} - {result['metadata'].get('title', '')}")
