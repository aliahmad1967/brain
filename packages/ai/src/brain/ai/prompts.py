"""Prompt templates and prompt management for local AI inference."""


class PromptManager:
    """Manages system and user prompt templates for local AI generation."""

    DEFAULT_RAG_SYSTEM = (
        "You are Brain, a secure, local-first AI knowledge assistant.\n"
        "Answer the user's question using only the context retrieved below. "
        "If the context does not contain enough information to answer, state clearly that you do not "
        "have that information (do not make up facts).\n\n"
        "--- START RETRIEVED CONTEXT ---\n"
        "{context}\n"
        "--- END RETRIEVED CONTEXT ---"
    )

    DEFAULT_RAG_USER = "Question: {question}"

    DEFAULT_SUMMARY_SYSTEM = (
        "You are an expert summarizer. Provide a concise summary of the following document. "
        "Focus on key insights, major themes, and actionable points."
    )

    DEFAULT_SUMMARY_USER = "Document Content:\n\n{content}\n\nSummary:"

    @classmethod
    def format_rag_system(cls, context: str) -> str:
        """Format the system prompt for retrieval-augmented generation with context."""
        return cls.DEFAULT_RAG_SYSTEM.format(context=context)

    @classmethod
    def format_rag_user(cls, question: str) -> str:
        """Format the user prompt for RAG with the specific question."""
        return cls.DEFAULT_RAG_USER.format(question=question)

    @classmethod
    def format_summary_system(cls) -> str:
        """Get the system prompt for document summarization."""
        return cls.DEFAULT_SUMMARY_SYSTEM

    @classmethod
    def format_summary_user(cls, content: str) -> str:
        """Format the user prompt for document summarization with content."""
        return cls.DEFAULT_SUMMARY_USER.format(content=content)
