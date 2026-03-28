"""Build the FAQ cache with pre-computed answers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

import config
from core.embedder import Embedder
from core.llm import LLMEngine
from core.retriever import Retriever

# Common FAQ questions with expected categories
FAQ_QUESTIONS = [
    "What programs does NUST offer?",
    "What is the NET exam?",
    "How do I prepare for the NET exam?",
    "What are the eligibility criteria for engineering at NUST?",
    "What is the eligibility for computer science at NUST?",
    "What is the eligibility for BBA at NUST?",
    "What is the eligibility for MBBS at NUST?",
    "What is the fee structure at NUST?",
    "How much does it cost to study engineering at NUST?",
    "How much is the hostel fee at NUST?",
    "When do admissions open at NUST?",
    "What are the important admission deadlines?",
    "How does the merit system work at NUST?",
    "What is the aggregate formula for NUST?",
    "What scholarships does NUST offer?",
    "How to apply for financial aid at NUST?",
    "Tell me about NUST hostel facilities",
    "Where is NUST located?",
    "How do I apply to NUST?",
    "What documents are required for NUST admission?",
    "Can international students apply to NUST?",
    "What is SEECS at NUST?",
    "What schools and colleges does NUST have?",
    "Is SAT accepted at NUST?",
    "What is the NUST aggregate cutoff for CS?",
    "Tell me about NUST campus facilities",
    "What is the NET exam pattern?",
    "How many times can I take the NET exam?",
    "What is NBS at NUST?",
    "Does NUST have a medical college?",
]


def main():
    print("=== Building FAQ Cache ===\n")

    # Load components
    embedder = Embedder()
    embedder.load()

    llm = LLMEngine()
    llm.load()

    retriever = Retriever(embedder)
    retriever.load()

    # Build cache
    cache_entries = []

    for i, question in enumerate(FAQ_QUESTIONS):
        print(f"\n[{i + 1}/{len(FAQ_QUESTIONS)}] {question}")

        # Retrieve context
        chunks = retriever.search(question, top_k=config.RETRIEVAL_TOP_K)
        chunks = chunks[: config.FINAL_TOP_K]

        sources = list(set(c.source for c in chunks))

        # Build context
        context_parts = []
        for j, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"--- Document {j}: {chunk.title} ---\n"
                f"{chunk.text}\n"
                f"[Source: {chunk.source}]"
            )
        context = "\n\n".join(context_parts)

        prompt = f"Context:\n{context}\n\n---\n\nQuestion: {question}"

        # Generate answer
        answer = llm.generate(prompt)
        print(f"  Answer: {answer[:100]}...")

        cache_entries.append({
            "question": question,
            "answer": answer,
            "sources": sources,
        })

    # Save cache
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.FAQ_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache_entries, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(cache_entries)} FAQ entries to {config.FAQ_CACHE_PATH}")

    # Build and save embeddings
    questions = [e["question"] for e in cache_entries]
    embeddings = embedder.embed_batch(questions)
    np.save(str(config.FAQ_EMBEDDINGS_PATH), embeddings)
    print(f"Saved FAQ embeddings to {config.FAQ_EMBEDDINGS_PATH}")

    print("\nFAQ cache built successfully!")


if __name__ == "__main__":
    main()
