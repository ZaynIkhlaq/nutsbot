"""FAISS-based retriever with category filtering."""

from __future__ import annotations

import json

import faiss
import numpy as np

import config
from core.embedder import Embedder


class Chunk:
    """A retrieved chunk with metadata."""

    def __init__(self, text: str, source: str, category: str, title: str, score: float):
        self.text = text
        self.source = source
        self.category = category
        self.title = title
        self.score = score  # cosine similarity (higher = better)

    def __repr__(self):
        return f"Chunk(title={self.title!r}, score={self.score:.3f})"


class Retriever:
    """FAISS-based document retriever."""

    def __init__(self, embedder: Embedder):
        self.embedder = embedder
        self.index: faiss.IndexFlatIP | None = None
        self.metadata: list[dict] = []

    def load(self):
        """Load the FAISS index and metadata from disk."""
        print("Loading FAISS index...")
        self.index = faiss.read_index(str(config.FAISS_INDEX_PATH))
        with open(config.FAISS_METADATA_PATH, "r") as f:
            self.metadata = json.load(f)
        print(f"Loaded {self.index.ntotal} vectors.")

    def search(
        self,
        query: str,
        top_k: int | None = None,
        category_filter: str | None = None,
    ) -> list[Chunk]:
        """Search for the most relevant chunks given a query."""
        if self.index is None:
            raise RuntimeError("Index not loaded. Call load() first.")

        top_k = top_k or config.RETRIEVAL_TOP_K

        query_vec = self.embedder.embed(query).reshape(1, -1)

        # Search more if filtering by category
        search_k = top_k * 4 if category_filter else top_k
        search_k = min(search_k, self.index.ntotal)

        scores, indices = self.index.search(query_vec, search_k)
        scores = scores[0]
        indices = indices[0]

        chunks = []
        for score, idx in zip(scores, indices):
            if idx == -1:
                continue
            meta = self.metadata[idx]

            if category_filter and meta.get("category") != category_filter:
                continue

            chunks.append(
                Chunk(
                    text=meta["text"],
                    source=meta.get("source", "Unknown"),
                    category=meta.get("category", "general"),
                    title=meta.get("title", ""),
                    score=float(score),
                )
            )

            if len(chunks) >= (top_k or config.FINAL_TOP_K):
                break

        return chunks

    def get_top_score(self, chunks: list[Chunk]) -> float:
        """Get the highest similarity score from retrieved chunks."""
        if not chunks:
            return 0.0
        return max(c.score for c in chunks)
