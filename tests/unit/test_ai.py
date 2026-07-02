"""Unit tests for the AI package prompts."""

from brain.ai.prompts import PromptManager


def test_prompt_manager_rag_formatting() -> None:
    context = "Retrieved document chunk contents."
    sys_prompt = PromptManager.format_rag_system(context)
    assert context in sys_prompt
    assert "local-first AI knowledge assistant" in sys_prompt

    question = "Who is the lead software engineer?"
    user_prompt = PromptManager.format_rag_user(question)
    assert question in user_prompt
    assert "Question:" in user_prompt


def test_prompt_manager_summary_formatting() -> None:
    content = "Some document body text to summarize."
    sys_prompt = PromptManager.format_summary_system()
    user_prompt = PromptManager.format_summary_user(content)

    assert "expert summarizer" in sys_prompt
    assert content in user_prompt
