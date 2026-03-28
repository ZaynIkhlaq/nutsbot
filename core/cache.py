"""FAQ cache for instant responses to common questions."""

from __future__ import annotations

import json

import numpy as np

import config
from core.embedder import Embedder


class FAQCache:
    """Cache of pre-computed answers for common admissions questions."""

    def __init__(self, embedder: Embedder):
        self.embedder = embedder
        self.questions: list[str] = []
        self.answers: list[str] = []
        self.sources: list[list[str]] = []
        self.embeddings: np.ndarray | None = None

    def load(self):
        """Load FAQ cache from disk."""
        if not config.FAQ_CACHE_PATH.exists():
            print("No FAQ cache found. Skipping.")
            return

        print("Loading FAQ cache...")
        with open(config.FAQ_CACHE_PATH, "r") as f:
            cache_data = json.load(f)

        self.questions = [item["question"] for item in cache_data]
        self.answers = [item["answer"] for item in cache_data]
        self.sources = [item.get("sources", []) for item in cache_data]

        if config.FAQ_EMBEDDINGS_PATH.exists():
            self.embeddings = np.load(str(config.FAQ_EMBEDDINGS_PATH))
        elif self.questions:
            # Compute embeddings on the fly
            self.embeddings = self.embedder.embed_batch(self.questions)
            np.save(str(config.FAQ_EMBEDDINGS_PATH), self.embeddings)

        print(f"Loaded {len(self.questions)} FAQ entries.")

    def lookup(self, query: str) -> tuple[str, list[str], float] | None:
        """Look up a query in the FAQ cache.

        Returns (answer, sources, similarity) if match found, else None.
        """
        if self.embeddings is None or len(self.questions) == 0:
            return None

        query_vec = self.embedder.embed(query).reshape(1, -1)

        # Cosine similarity (embeddings are already normalized)
        similarities = (self.embeddings @ query_vec.T).flatten()
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score >= config.FAQ_SIMILARITY_THRESHOLD:
            return self.answers[best_idx], self.sources[best_idx], best_score

        return None
