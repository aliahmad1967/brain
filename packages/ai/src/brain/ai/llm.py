"""Ollama LLM client implementation."""

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

import httpx
from brain.shared.exceptions import AIError
from brain.shared.models import ChatMessage

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM interactions."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a single response for a prompt."""
        pass

    @abstractmethod
    async def chat(self, messages: list[ChatMessage]) -> ChatMessage:
        """Run a chat completion for a list of messages."""
        pass

    @abstractmethod
    async def chat_stream(self, messages: list[ChatMessage]) -> AsyncGenerator[str]:
        """Stream chat completion tokens as they are generated."""
        yield ""


class OllamaLLMClient(LLMClient):
    """Local LLM client using Ollama's HTTP API."""

    def __init__(self, base_url: str, model_name: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return str(data["response"])
        except Exception as e:
            logger.error("Ollama generate request failed: %s", e)
            raise AIError(f"Ollama generation failure: {e}") from e

    async def chat(self, messages: list[ChatMessage]) -> ChatMessage:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                role = data["message"]["role"]
                content = data["message"]["content"]
                return ChatMessage(role=role, content=content)
        except Exception as e:
            logger.error("Ollama chat request failed: %s", e)
            raise AIError(f"Ollama chat failure: {e}") from e

    async def chat_stream(self, messages: list[ChatMessage]) -> AsyncGenerator[str]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
        except Exception as e:
            logger.error("Ollama streaming chat request failed: %s", e)
            raise AIError(f"Ollama stream failure: {e}") from e
