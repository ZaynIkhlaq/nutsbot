"""LLM wrapper using llama-cpp-python for offline inference."""

from __future__ import annotations

from typing import Generator

from llama_cpp import Llama

import config

# Max conversation turns to keep in context (user+assistant pairs)
MAX_HISTORY_TURNS = 3


class LLMEngine:
    """Wrapper around llama-cpp-python for streaming generation."""

    def __init__(self):
        self.model: Llama | None = None

    def load(self):
        """Load the GGUF model into memory."""
        print(f"Loading LLM from {config.LLM_MODEL_PATH}...")
        self.model = Llama(
            model_path=str(config.LLM_MODEL_PATH),
            n_ctx=config.LLM_N_CTX,
            n_threads=config.LLM_N_THREADS,
            n_batch=config.LLM_N_BATCH,
            n_gpu_layers=config.LLM_N_GPU_LAYERS,
            use_mlock=True,
            verbose=False,
        )
        print("LLM loaded successfully.")

    def _build_messages(
        self, prompt: str, history: list[dict] | None = None
    ) -> list[dict]:
        """Build the message list with system prompt, history, and current prompt."""
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]

        if history:
            # Keep only the last N turns to fit in context window
            # Each turn = 1 user + 1 assistant message
            recent = history[-(MAX_HISTORY_TURNS * 2) :]
            for msg in recent:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": prompt})
        return messages

    def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        history: list[dict] | None = None,
    ) -> str:
        """Generate a complete response (non-streaming)."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        response = self.model.create_chat_completion(
            messages=self._build_messages(prompt, history),
            max_tokens=max_tokens or config.LLM_MAX_TOKENS,
            temperature=config.LLM_TEMPERATURE,
            top_p=config.LLM_TOP_P,
            repeat_penalty=config.LLM_REPEAT_PENALTY,
        )
        return response["choices"][0]["message"]["content"]

    def generate_stream(
        self,
        prompt: str,
        max_tokens: int | None = None,
        history: list[dict] | None = None,
    ) -> Generator[str, None, None]:
        """Generate a streaming response, yielding tokens as they come."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        stream = self.model.create_chat_completion(
            messages=self._build_messages(prompt, history),
            max_tokens=max_tokens or config.LLM_MAX_TOKENS,
            temperature=config.LLM_TEMPERATURE,
            top_p=config.LLM_TOP_P,
            repeat_penalty=config.LLM_REPEAT_PENALTY,
            stream=True,
        )

        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]
