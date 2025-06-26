import re
import logging

logger = logging.getLogger(__name__)


def wash_json(text: str) -> str:
    """Extract JSON string from possible Markdown code blocks."""
    if text is None:
        return text
    text = text.strip()
    # Find JSON inside triple backticks
    match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Remove leading/trailing fences if present
    if text.startswith('```') and text.endswith('```'):
        text = re.sub(r'^```[^\n]*\n', '', text)
        text = re.sub(r'\n```$', '', text)

    logger.debug("Washed text: %s", text)
    return text.strip()
