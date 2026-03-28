"""Build the FAISS index from chunks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import faiss
import numpy as np

import config
from core.embedder import Embedder


def main():
    print("=== Building FAISS Index ===\n")

    # Load chunks
    chunks_path = config.CHUNKS_DIR / "chunks.jsonl"
    if not chunks_path.exists():
        print("No chunks found. Run build_chunks.py first.")
        return

    chunks = []
    with open(chunks_path, "r") as f:
        for line in f:
            chunks.append(json.loads(line))

    print(f"Loaded {len(chunks)} chunks.")

    # Initialize embedder
    embedder = Embedder()
    embedder.load()

    # Embed all chunks in batches
    batch_size = 32
    all_embeddings = []
    texts = [c["text"] for c in chunks]

    print("Embedding chunks...")
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        embs = embedder.embed_batch(batch)
        all_embeddings.append(embs)
        print(f"  Embedded {min(i + batch_size, len(texts))}/{len(texts)}")

    embeddings = np.vstack(all_embeddings).astype(np.float32)
    print(f"Embeddings shape: {embeddings.shape}")

    # Build FAISS index (Inner Product for cosine similarity on normalized vectors)
    index = faiss.IndexFlatIP(config.EMBEDDING_DIM)
    index.add(embeddings)
    print(f"FAISS index built with {index.ntotal} vectors.")

    # Save index
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(config.FAISS_INDEX_PATH))
    print(f"Index saved to {config.FAISS_INDEX_PATH}")

    # Save metadata
    metadata = []
    for chunk in chunks:
        metadata.append({
            "id": chunk["id"],
            "text": chunk["text"],
            "title": chunk["title"],
            "category": chunk["category"],
            "source": chunk["source"],
        })

    with open(config.FAISS_METADATA_PATH, "w") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Metadata saved to {config.FAISS_METADATA_PATH}")

    print("\nDone!")


if __name__ == "__main__":
    main()
