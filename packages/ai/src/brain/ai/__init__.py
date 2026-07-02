"""AI clients (LLM, embeddings) and prompt templates."""

from brain.ai.embeddings import EmbeddingsClient, OllamaEmbeddingsClient
from brain.ai.llm import LLMClient, OllamaLLMClient
from brain.ai.prompts import PromptManager

__all__ = [
    "EmbeddingsClient",
    "LLMClient",
    "OllamaEmbeddingsClient",
    "OllamaLLMClient",
    "PromptManager",
]
