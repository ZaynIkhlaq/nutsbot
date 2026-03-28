"""Process raw data into chunks for the RAG pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config


def chunk_text(text: str, max_tokens: int = 256, overlap: int = 32) -> list[str]:
    """Split text into overlapping chunks by approximate token count.

    Uses a simple word-based approximation (1 token ~ 0.75 words).
    """
    words = text.split()
    # Approximate tokens per word ratio
    words_per_chunk = int(max_tokens * 0.75)
    words_overlap = int(overlap * 0.75)

    if len(words) <= words_per_chunk:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + words_per_chunk
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += words_per_chunk - words_overlap

    return chunks


def process_curated_data() -> list[dict]:
    """Process curated data into chunks."""
    curated_path = config.RAW_DIR / "curated.json"
    if not curated_path.exists():
        print("  No curated data found. Run scrape_nust.py first.")
        return []

    with open(curated_path, "r") as f:
        curated = json.load(f)

    chunks = []
    for item in curated:
        text = item["text"]
        title = item.get("title", "")
        category = item.get("category", "general")
        source = item.get("source", "Unknown")

        text_chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        for i, chunk_text_str in enumerate(text_chunks):
            chunk_title = f"{title}" if len(text_chunks) == 1 else f"{title} (Part {i + 1})"
            chunks.append({
                "id": f"curated_{category}_{len(chunks)}",
                "text": chunk_text_str,
                "title": chunk_title,
                "category": category,
                "source": source,
            })

    return chunks


def process_scraped_data() -> list[dict]:
    """Process scraped web data into chunks."""
    scraped_path = config.RAW_DIR / "scraped.json"
    if not scraped_path.exists():
        print("  No scraped data found. Using curated data only.")
        return []

    with open(scraped_path, "r") as f:
        scraped = json.load(f)

    chunks = []
    for item in scraped:
        text = item.get("text", "")
        if not text or len(text) < 50:
            continue

        name = item.get("name", "unknown")
        source = item.get("source", "NUST Website")

        # Determine category from name
        category = "general"
        if "program" in name.lower():
            category = "programs"
        elif "net" in name.lower() or "entry" in name.lower():
            category = "net_exam"
        elif "fee" in name.lower():
            category = "fees"
        elif "eligib" in name.lower():
            category = "eligibility"

        text_chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        for i, chunk_text_str in enumerate(text_chunks):
            if len(chunk_text_str.strip()) < 30:
                continue
            chunks.append({
                "id": f"scraped_{name}_{len(chunks)}",
                "text": chunk_text_str,
                "title": f"NUST Website - {name} (Part {i + 1})",
                "category": category,
                "source": source,
            })

    return chunks


def main():
    print("=== Building Chunks ===\n")

    all_chunks = []

    print("Processing curated data...")
    all_chunks.extend(process_curated_data())
    print(f"  {len(all_chunks)} chunks from curated data.")

    print("Processing scraped data...")
    scraped_chunks = process_scraped_data()
    all_chunks.extend(scraped_chunks)
    print(f"  {len(scraped_chunks)} chunks from scraped data.")

    print(f"\nTotal chunks: {len(all_chunks)}")

    # Save chunks
    config.CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    chunks_path = config.CHUNKS_DIR / "chunks.jsonl"
    with open(chunks_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"Saved to {chunks_path}")

    # Print category distribution
    from collections import Counter
    cats = Counter(c["category"] for c in all_chunks)
    print("\nCategory distribution:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
