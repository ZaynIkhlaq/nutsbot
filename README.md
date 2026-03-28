# nutsbot

An offline admissions chatbot for NUST (National University of Sciences and Technology), Islamabad.

Built for the NUST Islamabad Local Chatbot Competition 2026. Runs entirely on your machine -- no internet, no cloud APIs, no GPU required. All answers are grounded in the official NUST FAQs at [nust.edu.pk/faqs](https://nust.edu.pk/faqs/).

---

## Prerequisites

Before you start, make sure you have:

- **Python 3.9 or higher** (3.11+ recommended)
- **8 GB RAM** (runs in ~2.6 GB, but the OS needs room too)
- **~2 GB free disk space** (for models and dependencies)
- **macOS, Linux, or Windows** (tested on macOS and Linux)

Check your Python version:

```bash
python3 --version
```

If you don't have Python 3.9+:
- **macOS:** `brew install python@3.13`
- **Ubuntu/Debian:** `sudo apt install python3`
- **Windows:** Download from [python.org](https://www.python.org/downloads/)

**Windows only:** You also need C++ build tools for `llama-cpp-python`. Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and select "Desktop development with C++" during installation. Alternatively, install a pre-built wheel:
```cmd
pip install llama-cpp-python --prefer-binary
```

---

## Setup

Clone the repo and run the setup script. Works on **Windows, macOS, and Linux**. It handles everything -- virtual environment, dependencies, model downloads, and knowledge base indexing.

```bash
git clone <repo-url>
cd nutsbot
python setup.py
```

> On some systems you may need to use `python3` instead of `python`.

This will:
1. Create a Python virtual environment (`.venv/`)
2. Install all dependencies
3. Download the LLM and embedding models (~1.1 GB, requires internet)
4. Build the FAQ index and response cache (~5 minutes)

After setup finishes, it tells you exactly what to run next.

---

## Running nutsbot

**macOS / Linux:**
```bash
source .venv/bin/activate
python app.py
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate
python app.py
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
python app.py
```

Then open [http://127.0.0.1:7860](http://127.0.0.1:7860) in your browser. That's it.

---

## Usage Tips

- **Type naturally** -- "Is there negative marking in NET?", "How much is the application fee?", "Can I apply with A Levels?"
- **Greet it** -- Say "hello", "salam", "hey" and it responds with personality
- **Ask follow-ups** -- It remembers the last 3 turns of conversation
- **Look at the status bar** -- After each response, you'll see a confidence indicator (Verified / Partial / Low) and response time

---

## Running on Competition Hardware (Intel i5, No GPU)

By default, nutsbot uses GPU acceleration on Apple Silicon Macs. For the competition target (Intel Core i5 13th Gen, 8GB RAM, no GPU):

Open `config.py` and change:

```python
LLM_N_GPU_LAYERS = 0    # CPU only
```

Expected response times on CPU:
- Cached/chitchat responses: instant
- RAG queries: 5-10 seconds (streamed, so first words appear in ~1s)

---

## Project Structure

```
nutsbot/
├── app.py                     # Web UI (Gradio, dark theme)
├── config.py                  # All settings in one place
├── setup.sh                   # One-command setup script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── TRADEOFFS.md               # Design decisions and rationale
│
├── core/                      # Application logic
│   ├── pipeline.py            # Main orchestrator (chitchat -> cache -> RAG -> LLM)
│   ├── llm.py                 # LLM wrapper (Qwen 2.5 1.5B via llama-cpp-python)
│   ├── embedder.py            # Text embeddings (all-MiniLM-L6-v2 via ONNX)
│   ├── retriever.py           # FAISS vector search with category filtering
│   ├── cache.py               # Semantic FAQ cache for instant answers
│   ├── chitchat.py            # Personality-driven greeting/smalltalk handler
│   └── classifier.py          # Keyword-based query categorizer
│
├── scripts/                   # Setup and data processing
│   ├── download_models.py     # Downloads LLM + embedding models
│   ├── parse_official_faqs.py # Extracts Q&A from nust.edu.pk/faqs HTML
│   ├── build_chunks.py        # Splits FAQs into chunks for embedding
│   ├── build_index.py         # Builds FAISS vector index
│   └── build_faq_cache.py     # Pre-computes answers for common questions
│
├── data/                      # Knowledge base (built from official FAQs)
│   ├── raw/                   # Source HTML and parsed JSON
│   ├── chunks/                # Chunked text for embedding
│   └── index/                 # FAISS index + metadata
│
├── cache/                     # Pre-computed FAQ answers + embeddings
│
└── models/                    # ML models (downloaded during setup)
    ├── qwen2.5-1.5b-instruct-q4_k_m.gguf   # LLM (1.0 GB)
    └── all-MiniLM-L6-v2/                     # Embedding model (86 MB)
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        User Query                            │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  LAYER 1: CHITCHAT DETECTOR                        (0ms)    │
│                                                              │
│  Regex patterns match greetings ("hello", "salam"),          │
│  thanks, stress, meta-questions, jokes, goodbyes.            │
│  Returns hand-crafted personality-driven responses.          │
│  Not a match? ↓                                              │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  LAYER 2: FOLLOW-UP DETECTOR                                │
│                                                              │
│  Keyword scan for "what about...", "tell me more",           │
│  "what did I ask", etc. If detected, skips FAQ cache         │
│  so the LLM receives full conversation history.              │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  LAYER 3: FAQ CACHE                               (~10ms)   │
│                                                              │
│  30 pre-computed answers for common questions.               │
│  Embeds the query → cosine similarity vs cached questions.   │
│  Score > 0.85? → returns cached answer instantly.            │
│  No match? ↓                                                 │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  LAYER 4: RAG PIPELINE                      (0.6-2s GPU /   │
│                                              5-10s CPU)      │
│                                                              │
│  4a. CLASSIFY QUERY                                          │
│      Keyword rules → category (mbbs/net_exam/fees/...)       │
│      Ambiguous? → no filter, let FAISS handle it             │
│                                                              │
│  4b. EMBED QUERY                                    <50ms    │
│      all-MiniLM-L6-v2 via ONNX Runtime                      │
│      Query → 384-dimensional normalized vector               │
│                                                              │
│  4c. FAISS RETRIEVAL                                 <1ms    │
│      IndexFlatIP (cosine similarity on normalized vectors)   │
│      73 chunks from nust.edu.pk/faqs                         │
│      Search top-8 → filter by category → take top-3          │
│      Low scores? → fallback to unfiltered search             │
│                                                              │
│  4d. CONFIDENCE SCORING                                      │
│      Top-1 retrieval similarity:                             │
│        > 0.55 → "Verified" (green)                           │
│        > 0.35 → "Partial match" (yellow)                     │
│        ≤ 0.35 → "Low confidence" (red)                       │
│                                                              │
│  4e. PROMPT CONSTRUCTION                                     │
│      System prompt (personality + rules)                     │
│      + Last 3 conversation turns (memory)                    │
│      + Top-3 retrieved FAQ chunks (context)                  │
│      + Current user question                                 │
│                                                              │
│  4f. LLM GENERATION (streaming)                              │
│      Qwen 2.5 1.5B Instruct (Q4_K_M GGUF)                   │
│      llama-cpp-python, Metal on Mac / CPU on Intel           │
│      n_ctx=2048, max_tokens=400                              │
│      Tokens stream to UI in real-time                        │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  GRADIO UI                                                   │
│                                                              │
│  Dark theme (ChatGPT-style)                                  │
│  Streaming chat with rounded input bar                       │
│  Status bar: confidence pill + response timer                │
│  User messages: dark pills | Bot messages: plain text        │
└──────────────────────────────────────────────────────────────┘
```

### Data Pipeline (runs once during setup)

```
nust.edu.pk/faqs (HTML)
        │
        ▼
  parse_official_faqs.py → 73 Q&A pairs (JSON)
        │
        ├──→ build_chunks.py → 73 text chunks (JSONL)
        │         │
        │         ▼
        │    build_index.py → FAISS index (73 vectors × 384 dims)
        │
        └──→ build_faq_cache.py → 30 pre-computed answers + embeddings
```

### Memory Layout at Runtime

```
Component                          RAM
──────────────────────────────────────────
OS + Python runtime                ~500 MB
Qwen 2.5 1.5B Q4_K_M              ~1,800 MB
all-MiniLM-L6-v2 (ONNX)           ~80 MB
ONNX Runtime                       ~50 MB
FAISS index (73 × 384)            ~0.1 MB
Gradio + app code                  ~150 MB
FAQ cache + embeddings             ~1 MB
──────────────────────────────────────────
TOTAL                              ~2,600 MB (of 8,192 MB limit)
```

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| LLM | Qwen 2.5 1.5B (Q4_K_M GGUF) | Best instruction-following at this size, fast on CPU |
| Inference | llama-cpp-python | Direct bindings, no HTTP overhead, streaming |
| Embeddings | all-MiniLM-L6-v2 (ONNX) | 86MB, <50ms/query, no PyTorch needed |
| Vector Store | FAISS (IndexFlatIP) | Sub-millisecond exact search |
| UI | Gradio | Dark theme, streaming, minimal |
| Data Source | nust.edu.pk/faqs | 73 official FAQ pairs |

Total RAM: ~2.6 GB. Well within the 8 GB competition limit.

---

## Troubleshooting

**"Module not found" errors:**
Make sure the virtual environment is activated:
- macOS/Linux: `source .venv/bin/activate`
- Windows CMD: `.venv\Scripts\activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

**Models not found:**
Run `python scripts/download_models.py` (requires internet).

**Port 7860 already in use:**
- macOS/Linux: `lsof -ti:7860 | xargs kill -9`
- Windows: `netstat -ano | findstr :7860` then `taskkill /PID <pid> /F`

**Slow responses on CPU:**
Expected without GPU. Responses stream token-by-token so you see the first words quickly even if the full response takes a few seconds.

**Windows: `setup.py` opens the wrong program:**
Run `python setup.py` explicitly, not by double-clicking the file.

**PowerShell: "cannot be loaded because running scripts is disabled":**
Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` then try again.

---

## Design Tradeoffs

See [TRADEOFFS.md](TRADEOFFS.md) for detailed rationale behind every design decision.

---

## Data Source

All answers are grounded exclusively in the official NUST FAQs at [nust.edu.pk/faqs](https://nust.edu.pk/faqs/). No other data sources are used.

For the latest admissions information, contact NUST directly:
- Phone: +92-51-90856878
- Email: admissions@nust.edu.pk
- Web: [nust.edu.pk/admissions](https://nust.edu.pk/admissions/)
