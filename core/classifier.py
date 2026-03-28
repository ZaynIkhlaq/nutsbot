"""Keyword-based query classifier for category-filtered retrieval."""

from __future__ import annotations

# Keyword -> category mapping
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "programs": [
        "program", "programmes", "degree", "bachelor", "master", "phd",
        "bs ", "ms ", "be ", "bba", "mba", "mbbs", "bds",
        "engineering", "computer science", "electrical", "mechanical",
        "civil", "chemical", "software", "business", "medical",
        "department", "school", "college", "seecs", "sme", "scme",
        "nice", "nbs", "s3h", "sns", "smme", "scee", "rimms", "camp",
        "rime", "iese", "igis", "rcms", "am college",
        "what can i study", "courses", "major", "discipline",
    ],
    "eligibility": [
        "eligib", "require", "criteria", "qualification", "minimum",
        "gpa", "cgpa", "marks", "percentage", "fsc", "a level",
        "a-level", "intermediate", "matric", "o level", "o-level",
        "sat", "who can apply", "can i apply", "am i eligible",
        "age limit", "domicile",
    ],
    "fees": [
        "fee", "cost", "tuition", "payment", "expense", "afford",
        "how much", "price", "charges", "semester fee", "annual fee",
        "hostel fee", "per semester", "per year",
    ],
    "net_exam": [
        "net ", "net-", "nust entry test", "entry test", "nat",
        "test date", "test pattern", "syllabus", "test prep",
        "test registration", "test score", "test result",
        "how to prepare", "passing marks", "test centers",
        "exam", "mcq",
    ],
    "deadlines": [
        "deadline", "last date", "when", "date", "schedule",
        "admission open", "admission close", "registration date",
        "important date", "timeline", "calendar",
    ],
    "merit": [
        "merit", "cutoff", "cut-off", "closing merit",
        "aggregate", "selection", "how are students selected",
        "merit list", "waiting list", "self-finance",
    ],
    "hostel": [
        "hostel", "accommodation", "residence", "dormitor",
        "room", "mess", "living", "boarding",
    ],
    "scholarships": [
        "scholarship", "financial aid", "need-based", "merit-based",
        "fee waiver", "concession", "stipend", "funding",
    ],
    "campus": [
        "campus", "location", "islamabad", "rawalpindi", "karachi",
        "lahore", "quetta", "risalpur", "facilities", "library",
        "lab", "sports", "transport",
    ],
}


def classify_query(query: str) -> str | None:
    """Classify a query into a category based on keyword matching.

    Returns the best-matching category or None if no strong match.
    """
    query_lower = query.lower()

    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[category] = score

    if not scores:
        return None

    best = max(scores, key=scores.get)
    best_score = scores[best]

    # If multiple categories matched, and the best isn't dominant, don't filter
    # This prevents misclassification when query spans multiple topics
    if len(scores) > 1:
        second_best_score = sorted(scores.values(), reverse=True)[1]
        if best_score - second_best_score <= 1:
            # Ambiguous -- let FAISS handle it without filtering
            return None

    # Only filter if there's a reasonably clear signal
    if best_score < 2:
        return None

    return best
