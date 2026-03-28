"""nutsbot setup - works on Windows, macOS, and Linux."""

import os
import sys
import subprocess
import platform

VENV_DIR = ".venv"
IS_WINDOWS = platform.system() == "Windows"
PYTHON_IN_VENV = os.path.join(VENV_DIR, "Scripts" if IS_WINDOWS else "bin", "python")
PIP_IN_VENV = os.path.join(VENV_DIR, "Scripts" if IS_WINDOWS else "bin", "pip")


def run(cmd, desc=None):
    if desc:
        print(f"  {desc}...")
    result = subprocess.run(cmd, shell=isinstance(cmd, str))
    if result.returncode != 0:
        print(f"\n  ERROR: Command failed: {cmd}")
        sys.exit(1)


def main():
    print()
    print("=" * 40)
    print("  nutsbot setup")
    print("=" * 40)
    print()

    # Check Python version
    major, minor = sys.version_info[:2]
    print(f"  Python {major}.{minor} ({platform.system()})")
    if major < 3 or minor < 9:
        print("\n  ERROR: Python 3.9+ is required.")
        print("  Download from https://python.org/downloads/")
        sys.exit(1)

    # Step 1: Create venv
    print()
    print("[1/5] Virtual environment")
    if not os.path.exists(VENV_DIR):
        run([sys.executable, "-m", "venv", VENV_DIR], "Creating .venv")
    else:
        print("  Already exists.")

    # Step 2: Install dependencies
    print()
    print("[2/5] Installing dependencies")
    run([PIP_IN_VENV, "install", "-q", "--upgrade", "pip"])
    # Use --prefer-binary for llama-cpp-python to avoid C++ compilation issues on Windows
    run([PIP_IN_VENV, "install", "-q", "--prefer-binary", "-r", "requirements.txt"], "Installing packages")

    # Step 3: Download models
    print()
    print("[3/5] Models")
    gguf = os.path.join("models", "qwen2.5-1.5b-instruct-q4_k_m.gguf")
    onnx = os.path.join("models", "all-MiniLM-L6-v2", "model.onnx")
    if os.path.exists(gguf) and os.path.exists(onnx):
        print("  Already downloaded.")
    else:
        run([PYTHON_IN_VENV, "scripts/download_models.py"], "Downloading models (~1.1 GB)")

    # Step 4: Parse FAQs + build chunks + build index
    print()
    print("[4/5] Knowledge base")
    index_path = os.path.join("data", "index", "faiss.index")
    if os.path.exists(index_path):
        print("  Already built.")
    else:
        run([PYTHON_IN_VENV, "scripts/parse_official_faqs.py"], "Parsing FAQs")
        run([PYTHON_IN_VENV, "scripts/build_chunks.py"], "Building chunks")
        run([PYTHON_IN_VENV, "scripts/build_index.py"], "Building FAISS index")

    # Step 5: Build FAQ cache
    print()
    print("[5/5] FAQ cache")
    cache_path = os.path.join("cache", "faq_cache.json")
    if os.path.exists(cache_path):
        print("  Already built.")
    else:
        print("  Generating pre-computed answers (this takes ~5 minutes)...")
        run([PYTHON_IN_VENV, "scripts/build_faq_cache.py"])

    # Done
    activate = ".venv\\Scripts\\activate" if IS_WINDOWS else "source .venv/bin/activate"
    print()
    print("=" * 40)
    print("  Setup complete!")
    print()
    print(f"  Run these commands:")
    print(f"    {activate}")
    print(f"    python app.py")
    print()
    print(f"  Then open: http://127.0.0.1:7860")
    print("=" * 40)
    print()


if __name__ == "__main__":
    main()
