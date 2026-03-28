# Nutsbot

Offline admissions chatbot for NUST, Islamabad. Built for the NUST Local Chatbot Competition 2026.

100% offline. CPU only. 8GB RAM. Data from [nust.edu.pk/faqs](https://nust.edu.pk/faqs/).

---

## Setup

**You need:** Python 3.9+ and ~2GB free disk space.

```bash
git clone https://github.com/ZaynIkhlaq/nutsbot
cd nutsbot
python setup.py
```

> Use `python3` if `python` doesn't work. Windows users may need [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (select "Desktop development with C++").

Setup takes ~5-10 minutes. It downloads models (~1.1GB), builds the knowledge base, and pre-computes FAQ answers.

---

## Run

**macOS / Linux:**
```bash
source .venv/bin/activate
python app.py
```

**Windows:**
```cmd
.venv\Scripts\activate
python app.py
```

Open [http://127.0.0.1:7860](http://127.0.0.1:7860).

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  LAYER 1: CHITCHAT                          (0ms)   │
│  Regex matches greetings, thanks, small talk.       │
│  Instant personality-driven response.               │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│  LAYER 2: FAQ CACHE                        (~10ms)  │
│  30 pre-computed answers. Semantic similarity match. │
│  Score > 0.85 → instant cached answer.              │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│  LAYER 3: RAG PIPELINE                   (5-10s)    │
│                                                     │
│  Classify → Embed → FAISS search → Confidence score │
│  → Build prompt (system + 3-turn history + context) │
│  → Qwen 2.5 1.5B streaming generation              │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│  GRADIO UI                                          │
│  Dark theme, streaming, confidence + timer display  │
└─────────────────────────────────────────────────────┘
```

### Data Pipeline (runs once during setup)

```
nust.edu.pk/faqs (HTML) → parse → 73 Q&A pairs
    ├─→ chunk → embed → FAISS index (73 × 384 dims)
    └─→ generate 30 cached FAQ answers
```

### Memory at Runtime

| Component | RAM |
|-----------|-----|
| Qwen 2.5 1.5B (Q4_K_M) | ~1,800 MB |
| OS + Python + Gradio | ~650 MB |
| Embeddings (ONNX) | ~130 MB |
| FAISS + cache | ~2 MB |
| **Total** | **~2,600 MB** |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Qwen 2.5 1.5B Instruct (Q4_K_M GGUF) via llama-cpp-python |
| Embeddings | all-MiniLM-L6-v2 via ONNX Runtime |
| Vector search | FAISS (IndexFlatIP) |
| UI | Gradio |
| Data | 73 FAQs from nust.edu.pk/faqs |

---

## Project Structure

```
nutsbot/
├── app.py              # Gradio web UI
├── config.py           # All settings
├── setup.py            # Cross-platform setup script
├── core/
│   ├── pipeline.py     # Orchestrator: chitchat → cache → RAG → LLM
│   ├── llm.py          # LLM wrapper with conversation history
│   ├── embedder.py     # ONNX embedding engine
│   ├── retriever.py    # FAISS search + category filtering
│   ├── cache.py        # Semantic FAQ cache
│   ├── chitchat.py     # Personality-driven instant responses
│   └── classifier.py   # Keyword query categorizer
├── scripts/            # Setup scripts (model download, indexing)
├── data/raw/           # Source FAQs from nust.edu.pk
├── models/             # Downloaded during setup (~1.1GB)
└── cache/              # Pre-computed answers (built during setup)
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Module not found" | Activate venv: `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows) |
| Models not found | Run `python scripts/download_models.py` |
| Port 7860 in use | macOS/Linux: `lsof -ti:7860 \| xargs kill -9`. Windows: `taskkill /F /PID <pid>` |
| PowerShell scripts disabled | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Windows `setup.py` opens wrong program | Run `python setup.py` explicitly |

---

## Design Tradeoffs

See [TRADEOFFS.md](TRADEOFFS.md).

