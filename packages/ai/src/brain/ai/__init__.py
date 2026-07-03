"""AI clients (LLM, embeddings) and prompt templates."""

from brain.ai.embeddings import (
    EmbeddingsClient,
    EmbeddingService,
    OllamaEmbeddingsClient,
    create_ollama_client_from_settings,
)
from brain.ai.llm import LLMClient, OllamaLLMClient
from brain.ai.prompts import PromptManager

__all__ = [
    "EmbeddingsClient",
    "EmbeddingService",
    "create_ollama_client_from_settings",
    "LLMClient",
    "OllamaEmbeddingsClient",
    "OllamaLLMClient",
    "PromptManager",
]
