"""Download all required model files."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config

def download_gguf():
    """Download the Qwen 2.5 1.5B Instruct GGUF model."""
    from huggingface_hub import hf_hub_download

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if config.LLM_MODEL_PATH.exists():
        print(f"LLM model already exists at {config.LLM_MODEL_PATH}")
        return

    print("Downloading Qwen 2.5 1.5B Instruct Q4_K_M GGUF...")
    hf_hub_download(
        repo_id="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        filename="qwen2.5-1.5b-instruct-q4_k_m.gguf",
        local_dir=str(config.MODELS_DIR),
    )
    print("LLM model downloaded successfully.")


def download_embedding_model():
    """Download the all-MiniLM-L6-v2 ONNX model."""
    from huggingface_hub import hf_hub_download

    model_dir = config.EMBEDDING_MODEL_DIR
    model_dir.mkdir(parents=True, exist_ok=True)

    files_to_download = [
        ("sentence-transformers/all-MiniLM-L6-v2", "tokenizer.json"),
        ("sentence-transformers/all-MiniLM-L6-v2", "tokenizer_config.json"),
    ]

    # Download ONNX model from the ONNX-specific repo
    onnx_files = [
        ("xenova/all-MiniLM-L6-v2", "onnx/model.onnx"),
    ]

    for repo_id, filename in files_to_download:
        target = model_dir / Path(filename).name
        if target.exists():
            print(f"  {filename} already exists")
            continue
        print(f"  Downloading {filename} from {repo_id}...")
        downloaded = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=str(model_dir),
        )
        # Move file to model_dir root if it's in a subdirectory
        downloaded_path = Path(downloaded)
        if downloaded_path.parent != model_dir:
            downloaded_path.rename(target)

    for repo_id, filename in onnx_files:
        target = model_dir / "model.onnx"
        if target.exists():
            print(f"  model.onnx already exists")
            continue
        print(f"  Downloading {filename} from {repo_id}...")
        downloaded = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=str(model_dir),
        )
        downloaded_path = Path(downloaded)
        if downloaded_path != target:
            downloaded_path.rename(target)

    print("Embedding model downloaded successfully.")


if __name__ == "__main__":
    download_gguf()
    download_embedding_model()
    print("\nAll models downloaded!")
