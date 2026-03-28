#!/bin/bash
# NUSTBot - One-command setup
# Usage: bash setup.sh

set -e

echo "==============================="
echo "  NUSTBot Setup"
echo "==============================="
echo ""

# 1. Check Python version
PYTHON=""
for cmd in python3.13 python3.12 python3.11 python3; do
    if command -v "$cmd" &>/dev/null; then
        version=$($cmd --version 2>&1 | grep -oP '\d+\.\d+')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.9+ is required."
    echo "Install it with: brew install python@3.13  (macOS)"
    echo "                 sudo apt install python3   (Ubuntu)"
    exit 1
fi

echo "Using: $($PYTHON --version)"

# 2. Create virtual environment
if [ ! -d ".venv" ]; then
    echo ""
    echo "[1/4] Creating virtual environment..."
    $PYTHON -m venv .venv
else
    echo ""
    echo "[1/4] Virtual environment exists."
fi

source .venv/bin/activate

# 3. Install dependencies
echo "[2/4] Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 4. Download models (if not present)
echo "[3/4] Checking models..."
if [ ! -f "models/qwen2.5-1.5b-instruct-q4_k_m.gguf" ]; then
    echo "  Downloading LLM model (~1GB)..."
    python scripts/download_models.py
else
    echo "  Models already downloaded."
fi

# 5. Build index (if not present)
echo "[4/4] Checking knowledge base..."
if [ ! -f "data/index/faiss.index" ]; then
    echo "  Building knowledge base..."
    python scripts/parse_official_faqs.py
    python scripts/build_chunks.py
    python scripts/build_index.py
    python scripts/build_faq_cache.py
else
    echo "  Knowledge base ready."
fi

echo ""
echo "==============================="
echo "  Setup complete!"
echo "  Run:  source .venv/bin/activate && python app.py"
echo "  Open: http://127.0.0.1:7860"
echo "==============================="
