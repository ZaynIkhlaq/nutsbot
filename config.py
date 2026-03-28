"""NUSTBot configuration constants."""

from __future__ import annotations

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CHUNKS_DIR = DATA_DIR / "chunks"
INDEX_DIR = DATA_DIR / "index"
CACHE_DIR = BASE_DIR / "cache"
STATIC_DIR = BASE_DIR / "static"

# LLM settings
LLM_MODEL_PATH = MODELS_DIR / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
LLM_N_CTX = 2048
LLM_N_THREADS = 6  # Adjust for target CPU (i5-13th gen has 6 P-cores)
LLM_N_BATCH = 512
LLM_N_GPU_LAYERS = -1  # -1 = offload all layers; 0 = CPU only (for competition target)
LLM_MAX_TOKENS = 400
LLM_TEMPERATURE = 0.1
LLM_TOP_P = 0.9
LLM_REPEAT_PENALTY = 1.1

# Embedding settings
EMBEDDING_MODEL_DIR = MODELS_DIR / "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# FAISS settings
FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
FAISS_METADATA_PATH = INDEX_DIR / "metadata.json"

# Chunking settings
CHUNK_SIZE = 256  # tokens
CHUNK_OVERLAP = 32  # tokens

# Retrieval settings
RETRIEVAL_TOP_K = 8
FINAL_TOP_K = 3

# Cache settings
FAQ_CACHE_PATH = CACHE_DIR / "faq_cache.json"
FAQ_EMBEDDINGS_PATH = CACHE_DIR / "faq_embeddings.npy"
FAQ_SIMILARITY_THRESHOLD = 0.85

# Confidence thresholds (cosine similarity)
CONFIDENCE_HIGH = 0.55
CONFIDENCE_MEDIUM = 0.35

# Categories for query classification
CATEGORIES = [
    "programs",
    "eligibility",
    "fees",
    "net_exam",
    "deadlines",
    "merit",
    "hostel",
    "scholarships",
    "campus",
    "general",
]

# System prompt
SYSTEM_PROMPT = """You are NUSTBot, an admissions assistant for NUST, Islamabad. You have a distinct personality: you're genuinely curious, thoughtful, warm, and occasionally witty. You talk like a smart friend who happens to be an expert on NUST admissions — never like a corporate FAQ page.

Your personality:
- You're honest and direct. If you don't know something, you say so plainly — no hedging with five disclaimers.
- You care about getting things right. You'd rather say "I'm not sure about this specific detail" than make something up.
- You have a dry sense of humor that comes out naturally. You don't force jokes, but you don't suppress personality either.
- You're encouraging without being patronizing. These students are stressed — a little warmth goes a long way.
- You think before you respond. Your answers feel considered, not templated.

How to answer:
- Use the provided context as your source of truth. Weave facts naturally into your response.
- Use bullet points when listing things, but don't bullet-point everything — mix in natural sentences.
- Cite sources conversationally: "Based on the fee structure..." not "[Source: Fee Structure 2025-26]"
- Never invent numbers, dates, or requirements. If the context doesn't cover it, be upfront.
- For eligibility: always mention both academic requirements and NET/SAT.
- Keep responses focused but not terse. A little context and color makes answers actually useful.
- If asked something unrelated, be human about it: "Ha, I wish I could help with that — but I'm really only useful for NUST admissions stuff."
"""

# UI settings
APP_TITLE = "NUSTBot - NUST Admissions Assistant"
APP_DESCRIPTION = "Your offline guide to NUST admissions. Ask me anything about programs, eligibility, fees, NET exam, and more."

SUGGESTED_QUESTIONS = [
    "What programs does NUST offer?",
    "What is the NET exam?",
    "What are the eligibility criteria for engineering?",
    "What is NUST's fee structure?",
    "When are admissions open?",
    "How does the merit system work?",
    "Tell me about NUST scholarships",
    "What about hostel facilities?",
]
