"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

from pathlib import Path


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Dispatch theo EMBEDDING_PROVIDER trong .env hoặc dùng HashingVectorizer / SentenceTransformer."""
    import os
    provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()

    if provider == "sentence_transformers":
        try:
            from sentence_transformers import SentenceTransformer
            model_name = os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL)
            model = SentenceTransformer(model_name)
            return model.encode(texts, convert_to_numpy=True).tolist()
        except Exception as exc:
            print(f"Warning: sentence_transformers fallback: {exc}")

    from sklearn.feature_extraction.text import HashingVectorizer
    vectorizer = HashingVectorizer(n_features=EMBEDDING_DIM, norm="l2", alternate_sign=True)
    embeddings = vectorizer.transform(texts).toarray()
    return embeddings.tolist()


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        doc_type = "legal" if "legal" in path.parts else "news"
        raw_text = path.read_text(encoding="utf-8")
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        title = path.stem
        url = None
        for line in lines[:5]:
            if line.startswith("# "):
                title = line.lstrip("# ").strip()
            elif line.startswith("**Source:**"):
                url_candidate = line.replace("**Source:**", "").strip()
                if url_candidate.startswith("http"):
                    url = url_candidate

        documents.append({
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": raw_text,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    separators = ["\n\n", "\n", ". ", " "]

    def _split(t: str, seps: list[str]) -> list[str]:
        if not t:
            return []
        if len(t) <= CHUNK_SIZE:
            return [t]
        if not seps:
            chunks = []
            start = 0
            step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)
            while start < len(t):
                chunks.append(t[start : start + CHUNK_SIZE])
                start += step
            return chunks
        sep = seps[0]
        parts = t.split(sep)
        if len(parts) <= 1:
            return _split(t, seps[1:])
        chunks = []
        current = ""
        for part in parts:
            candidate = f"{current}{sep}{part}" if current else part
            if len(candidate) <= CHUNK_SIZE:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                if len(part) <= CHUNK_SIZE:
                    current = part
                else:
                    sub = _split(part, seps[1:])
                    if sub:
                        chunks.extend(sub[:-1])
                        current = sub[-1]
                    else:
                        current = ""
        if current:
            chunks.append(current)
        return chunks

    result_chunks = []
    for document in documents:
        splits = _split(document["content"], separators)
        for index, text in enumerate(splits):
            meta = dict(document["metadata"])
            meta["chunk_index"] = index
            result_chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": meta,
            })
    return result_chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return
    collection = get_collection()
    cleaned_metadatas = []
    for chunk in chunks:
        meta = {}
        for k, v in chunk["metadata"].items():
            meta[k] = "" if v is None else v
        cleaned_metadatas.append(meta)

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=cleaned_metadatas,
    )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
