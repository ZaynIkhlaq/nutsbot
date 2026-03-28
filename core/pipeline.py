"""Main RAG pipeline orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generator

import config
from core.cache import FAQCache
from core.chitchat import match_chitchat
from core.classifier import classify_query
from core.embedder import Embedder
from core.llm import LLMEngine
from core.retriever import Chunk, Retriever


@dataclass
class PipelineResponse:
    """Response from the pipeline with metadata."""
    answer: str = ""
    sources: list[str] = field(default_factory=list)
    confidence: str = "low"  # "high", "medium", "low"
    from_cache: bool = False
    category: str | None = None


class Pipeline:
    """Full RAG pipeline: query -> classify -> cache/retrieve -> generate."""

    def __init__(self):
        self.embedder = Embedder()
        self.llm = LLMEngine()
        self.retriever = Retriever(self.embedder)
        self.faq_cache = FAQCache(self.embedder)

    def load_all(self):
        """Load all components."""
        self.embedder.load()
        self.llm.load()
        self.retriever.load()
        self.faq_cache.load()
        print("\nAll components loaded. NUSTBot is ready!\n")

    def _get_confidence(self, score: float) -> str:
        """Map retrieval score to confidence level."""
        if score >= config.CONFIDENCE_HIGH:
            return "high"
        elif score >= config.CONFIDENCE_MEDIUM:
            return "medium"
        return "low"

    def _build_context(self, chunks: list[Chunk]) -> str:
        """Format retrieved chunks into context for the LLM."""
        if not chunks:
            return "No relevant information found in the knowledge base."

        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"--- Document {i}: {chunk.title} ---\n"
                f"{chunk.text}\n"
                f"[Source: {chunk.source}]"
            )
        return "\n\n".join(parts)

    def _build_prompt(self, query: str, context: str) -> str:
        """Build the full user prompt with context."""
        return (
            f"Context:\n{context}\n\n"
            f"---\n\n"
            f"Question: {query}"
        )

    def query(
        self, user_query: str, history: list[dict] | None = None
    ) -> PipelineResponse:
        """Process a query and return a complete response."""
        response = PipelineResponse()

        # Step 0: Check chitchat (greetings, thanks, etc.)
        chitchat_reply = match_chitchat(user_query)
        if chitchat_reply:
            response.answer = chitchat_reply
            response.confidence = "high"
            response.from_cache = True
            return response

        # Step 1: Check FAQ cache (skip if this looks like a follow-up)
        if not self._is_followup(user_query):
            cache_hit = self.faq_cache.lookup(user_query)
            if cache_hit:
                answer, sources, score = cache_hit
                response.answer = answer
                response.sources = sources
                response.confidence = "high"
                response.from_cache = True
                return response

        # Step 2: Classify query
        category = classify_query(user_query)
        response.category = category

        # Step 3: Retrieve relevant chunks
        chunks = self.retriever.search(
            user_query,
            top_k=config.RETRIEVAL_TOP_K,
            category_filter=category,
        )

        # Fallback: if filtered results have low scores, try unfiltered
        top_score = self.retriever.get_top_score(chunks)
        if category and top_score < config.CONFIDENCE_MEDIUM:
            unfiltered = self.retriever.search(
                user_query, top_k=config.RETRIEVAL_TOP_K, category_filter=None
            )
            if self.retriever.get_top_score(unfiltered) > top_score:
                chunks = unfiltered

        # Take the final top-K
        chunks = chunks[: config.FINAL_TOP_K]

        # Step 4: Determine confidence
        top_score = self.retriever.get_top_score(chunks)
        response.confidence = self._get_confidence(top_score)
        response.sources = list(set(c.source for c in chunks))

        # Step 5: Build prompt and generate
        context = self._build_context(chunks)
        prompt = self._build_prompt(user_query, context)
        response.answer = self.llm.generate(prompt, history=history)

        return response

    def query_stream(
        self, user_query: str, history: list[dict] | None = None
    ) -> Generator[tuple[str, PipelineResponse], None, None]:
        """Process a query with streaming response.

        Yields (token, partial_response) tuples. The PipelineResponse
        metadata is available from the first yield.
        """
        response = PipelineResponse()

        # Step 0: Check chitchat
        chitchat_reply = match_chitchat(user_query)
        if chitchat_reply:
            response.answer = chitchat_reply
            response.confidence = "high"
            response.from_cache = True
            yield chitchat_reply, response
            return

        # Step 1: Check FAQ cache (skip if this looks like a follow-up)
        if not self._is_followup(user_query):
            cache_hit = self.faq_cache.lookup(user_query)
            if cache_hit:
                answer, sources, score = cache_hit
                response.answer = answer
                response.sources = sources
                response.confidence = "high"
                response.from_cache = True
                yield answer, response
                return

        # Step 2: Classify query
        category = classify_query(user_query)
        response.category = category

        # Step 3: Retrieve relevant chunks
        chunks = self.retriever.search(
            user_query,
            top_k=config.RETRIEVAL_TOP_K,
            category_filter=category,
        )

        # Fallback: if filtered results have low scores, try unfiltered
        top_score = self.retriever.get_top_score(chunks)
        if category and top_score < config.CONFIDENCE_MEDIUM:
            unfiltered = self.retriever.search(
                user_query, top_k=config.RETRIEVAL_TOP_K, category_filter=None
            )
            if self.retriever.get_top_score(unfiltered) > top_score:
                chunks = unfiltered

        chunks = chunks[: config.FINAL_TOP_K]

        # Step 4: Determine confidence
        top_score = self.retriever.get_top_score(chunks)
        response.confidence = self._get_confidence(top_score)
        response.sources = list(set(c.source for c in chunks))

        # Step 5: Build prompt and stream
        context = self._build_context(chunks)
        prompt = self._build_prompt(user_query, context)

        full_answer = ""
        for token in self.llm.generate_stream(prompt, history=history):
            full_answer += token
            response.answer = full_answer
            yield token, response

    @staticmethod
    def _is_followup(query: str) -> bool:
        """Detect if a query is a follow-up that needs conversation context."""
        q = query.lower().strip()
        followup_signals = [
            "what did i", "what was", "you just", "you said",
            "remember", "earlier", "last question", "previous",
            "more about", "tell me more", "elaborate", "explain more",
            "what about", "and the", "how about", "also",
            "can you repeat", "say that again", "what else",
            "go on", "continue", "keep going",
        ]
        return any(signal in q for signal in followup_signals)
