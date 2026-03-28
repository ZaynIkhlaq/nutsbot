# Design Tradeoffs

## Qwen 2.5 1.5B over larger models

A 1.5B model generates ~15-25 tok/s on CPU vs ~5-10 tok/s for 3B models. Since we use RAG (the model paraphrases retrieved context, not recall from parameters), a smaller model with strong instruction-following is sufficient. Qwen 2.5 1.5B is best-in-class at this size.

**Tradeoff:** Less fluent long-form responses. Mitigated by max_tokens=400 and structured prompts.

## ONNX Runtime over PyTorch for embeddings

PyTorch adds ~2GB to memory. ONNX Runtime is ~40MB and inference is faster on CPU. Same model weights, same quality.

## FAISS Flat over approximate search

Our corpus is 73 chunks. Exact search on 73 vectors is sub-millisecond. Approximate search adds complexity for zero benefit at this scale.

## Three-tier response system

1. **Chitchat** (regex, 0ms) -- handles greetings, thanks, meta-questions
2. **FAQ Cache** (embedding similarity, ~10ms) -- pre-computed answers for common questions
3. **RAG Pipeline** (embed + search + generate, 0.6-2s) -- full retrieval-augmented generation

This means ~60% of queries get instant responses. Judges notice speed.

## 3 turns of conversation history

We keep the last 3 user-assistant pairs in context. More turns = more tokens = slower inference. 3 turns is enough to follow a thread without blowing the 2048 context window.

## Official FAQs as sole data source

The competition requires nust.edu.pk/faqs as the data source. All 73 Q&A pairs are extracted and indexed. No external data.

## llama-cpp-python over Ollama

Direct Python bindings give fine-grained control over n_threads, n_ctx, n_batch, streaming, and memory. No separate server process, no HTTP overhead.

## Gradio over terminal UI

Competition judges evaluate UX. A web UI with streaming, dark theme, and confidence indicators provides a better experience than a terminal chatbot. Adds ~100MB RAM, well within budget.
