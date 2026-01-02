"""
Utils Module
"""

from datetime import datetime, timezone, timedelta


def format_context(context_chunks: list[str]) -> str:
    """
    Formats context chunks into a single string.

    Args:
        context_chunks: List of retrieved chunk texts

    Returns:
        str: Formatted context text
    """
    if not context_chunks:
        return "No relevant context found."

    return "\n\n".join(context_chunks)


def extract_response_text(response) -> str:
    """
    Robustly extracts text from LLM responses.
    Accepts: BaseMessage, dict, list or str.
    """

    content = getattr(response, "content", response)

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        textos = []
        for part in content:
            if isinstance(part, dict):
                if "text" in part:
                    textos.append(part["text"])
                elif "content" in part:
                    textos.append(part["content"])
            elif isinstance(part, str):
                textos.append(part)

        if textos:
            return "\n".join(textos).strip()

    return str(content) if content is not None else ""


def now() -> datetime:
    """
    Returns the current date and time
    """
    return datetime.now(timezone(timedelta(hours=-3)))
