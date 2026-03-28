"""Parse the official NUST FAQs page HTML and rebuild the knowledge base.

This is the ONLY authorized data source for the competition.
Source: https://nust.edu.pk/faqs/
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup
import config


# The FAQ page HTML (categories visible in sidebar):
# - UG Admissions FAQs
# - MBBS Admissions FAQs
# - BSHND Admissions FAQs

# Category detection based on question content
def categorize_faq(question: str, answer: str) -> str:
    q = question.lower()
    a = answer.lower()
    combined = q + " " + a

    if any(w in combined for w in ["mbbs", "nshs", "medical", "mdcat", "health sciences"]):
        return "mbbs"
    if any(w in combined for w in ["bshnd", "nutrition", "dietetics", "allied"]):
        return "bshnd"
    if any(w in combined for w in ["fee", "tuition", "payment", "installment", "charges", "refund"]):
        return "fees"
    if any(w in combined for w in ["entry test", "net ", "mcq", "test venue", "test result", "negative marking", "duration of test", "syllabus", "sample test"]):
        return "net_exam"
    if any(w in combined for w in ["eligib", "criteria", "fsc", "a level", "o level", "ics", "dae", "qualification", "60%"]):
        return "eligibility"
    if any(w in combined for w in ["sat", "act"]):
        return "sat_act"
    if any(w in combined for w in ["merit", "selection"]):
        return "merit"
    if any(w in combined for w in ["scholarship", "financial"]):
        return "scholarships"
    if any(w in combined for w in ["hostel", "pick and drop", "transport"]):
        return "hostel"
    if any(w in combined for w in ["programme", "program"]):
        return "programs"
    if any(w in combined for w in ["migration", "transfer"]):
        return "general"
    if any(w in combined for w in ["document", "cnic", "equivalence", "ibcc"]):
        return "eligibility"
    if any(w in combined for w in ["contact", "phone", "email"]):
        return "general"
    return "general"


def parse_faqs_from_html(html: str) -> list[dict]:
    """Extract all Q&A pairs from the NUST FAQs page HTML."""
    soup = BeautifulSoup(html, "html.parser")

    faqs = []
    cards = soup.find_all("div", class_="card")

    for card in cards:
        btn = card.find("button")
        if not btn:
            continue

        # Get question text (first span child)
        spans = btn.find_all("span")
        if not spans:
            continue
        question = spans[0].get_text(strip=True)

        # Get answer from card-body
        body = card.find("div", class_="card-body")
        if not body:
            continue

        # Get answer text, preserving structure
        answer = body.get_text(separator="\n", strip=True)
        # Clean up excessive whitespace but keep newlines
        answer = re.sub(r"[ \t]+", " ", answer)
        answer = re.sub(r"\n\s*\n+", "\n", answer)
        answer = answer.strip()

        if question and answer:
            category = categorize_faq(question, answer)
            faqs.append({
                "question": question,
                "answer": answer,
                "category": category,
                "source": "NUST Official FAQs (nust.edu.pk/faqs/)",
            })

    return faqs


def build_curated_from_faqs(faqs: list[dict]) -> list[dict]:
    """Convert FAQ pairs into curated data entries for the RAG pipeline."""
    entries = []
    for faq in faqs:
        entries.append({
            "title": faq["question"],
            "category": faq["category"],
            "source": faq["source"],
            "text": f"Q: {faq['question']}\nA: {faq['answer']}",
        })
    return entries


def main():
    # Read HTML from stdin or file
    html_path = config.RAW_DIR / "nust_faqs_page.html"

    if not html_path.exists():
        print(f"ERROR: {html_path} not found.")
        print("Save the NUST FAQs page HTML to data/raw/nust_faqs_page.html first.")
        sys.exit(1)

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    print("=== Parsing Official NUST FAQs ===\n")

    faqs = parse_faqs_from_html(html)
    print(f"Extracted {len(faqs)} FAQ pairs.\n")

    # Print all FAQs
    for i, faq in enumerate(faqs, 1):
        print(f"  {i}. [{faq['category']}] {faq['question'][:80]}")

    # Save raw FAQs
    faqs_path = config.RAW_DIR / "nust_official_faqs.json"
    with open(faqs_path, "w", encoding="utf-8") as f:
        json.dump(faqs, f, indent=2, ensure_ascii=False)
    print(f"\nSaved FAQs to {faqs_path}")

    # Build curated data (REPLACE existing, don't append)
    entries = build_curated_from_faqs(faqs)
    curated_path = config.RAW_DIR / "curated.json"
    with open(curated_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    print(f"Rebuilt curated.json with {len(entries)} entries (official FAQs only)")

    # Category distribution
    from collections import Counter
    cats = Counter(faq["category"] for faq in faqs)
    print("\nCategory distribution:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
