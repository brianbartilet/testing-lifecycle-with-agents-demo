"""
Prompt loader utility.

Reads system prompts from markdown files in apps/prompts/.
Each .md file embeds the literal prompt between HTML comment markers:

    <!-- BEGIN_PROMPT -->
    ...prompt text...
    <!-- END_PROMPT -->

Everything outside those markers is human-readable documentation and is
ignored at runtime.
"""
import re
from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent
_BEGIN = "<!-- BEGIN_PROMPT -->"
_END   = "<!-- END_PROMPT -->"


def load(filename: str) -> str:
    """
    Load and return the system prompt from a markdown file.

    Args:
        filename: Filename relative to apps/prompts/ (e.g. "requirements_analysis.md").

    Returns:
        The prompt text stripped of leading/trailing whitespace.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If BEGIN_PROMPT / END_PROMPT markers are missing.
    """
    path = _PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    content = path.read_text(encoding="utf-8")

    start = content.find(_BEGIN)
    end   = content.find(_END)

    if start == -1 or end == -1:
        raise ValueError(
            f"Prompt markers not found in {filename}. "
            f"Expected '<!-- BEGIN_PROMPT -->' and '<!-- END_PROMPT -->'."
        )

    prompt = content[start + len(_BEGIN): end]
    return prompt.strip()
