"""Embedding engine using ONNX Runtime for CPU-efficient inference."""

from __future__ import annotations

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

import config


class Embedder:
    """Embeds text using all-MiniLM-L6-v2 via ONNX Runtime."""

    def __init__(self):
        self.session: ort.InferenceSession | None = None
        self.tokenizer: Tokenizer | None = None

    def load(self):
        """Load the ONNX model and tokenizer."""
        model_dir = config.EMBEDDING_MODEL_DIR
        print(f"Loading embedding model from {model_dir}...")

        self.tokenizer = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
        self.tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=128)
        self.tokenizer.enable_truncation(max_length=128)

        # ONNX model may be in onnx/ subdirectory
        onnx_path = model_dir / "onnx" / "model.onnx"
        if not onnx_path.exists():
            onnx_path = model_dir / "model.onnx"

        self.session = ort.InferenceSession(
            str(onnx_path),
            providers=["CPUExecutionProvider"],
        )
        print("Embedding model loaded successfully.")

    def embed(self, text: str) -> np.ndarray:
        """Embed a single text string. Returns a 1D float32 array."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Embed a batch of texts. Returns (N, dim) float32 array."""
        if self.session is None or self.tokenizer is None:
            raise RuntimeError("Embedder not loaded. Call load() first.")

        encoded = self.tokenizer.encode_batch(texts)

        input_ids = np.array([e.ids for e in encoded], dtype=np.int64)
        attention_mask = np.array([e.attention_mask for e in encoded], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

        outputs = self.session.run(
            None,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "token_type_ids": token_type_ids,
            },
        )

        # Mean pooling over token embeddings, masked by attention
        token_embeddings = outputs[0]  # (batch, seq_len, dim)
        mask_expanded = attention_mask[:, :, np.newaxis].astype(np.float32)
        sum_embeddings = np.sum(token_embeddings * mask_expanded, axis=1)
        sum_mask = np.clip(mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
        embeddings = sum_embeddings / sum_mask

        # L2 normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.clip(norms, a_min=1e-9, a_max=None)
        embeddings = embeddings / norms

        return embeddings.astype(np.float32)
