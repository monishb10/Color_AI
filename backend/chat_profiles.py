"""
Chat Profiles Manager for Jerryy's AI
Safely loads system prompts based on a strict whitelist of supported profiles.
"""

from pathlib import Path
import logging

logger = logging.getLogger("jerryys_ai.profiles")

# Base directory for prompts (d:\Animations\prompts)
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

# Strict whitelist mapping profile name -> prompt filename
SUPPORTED_PROFILES = {
    "default": "default.txt",
    "exam": "exam.txt",
    "dbms": "dbms.txt",
    "programming": "programming.txt",
    "study_support": "study_support.txt"
}

# Cache prompt contents in memory to avoid disk reads on every chat message
_PROMPT_CACHE = {}


def get_chat_profile(profile_name: str) -> str:
    """
    Safely loads the matching system prompt for the given profile.
    Falls back to 'default' if profile_name is unknown or invalid.
    Strictly prevents directory traversal or arbitrary filesystem paths.
    """
    normalized = (profile_name or "").strip().lower()
    filename = SUPPORTED_PROFILES.get(normalized, SUPPORTED_PROFILES["default"])

    if filename in _PROMPT_CACHE:
        return _PROMPT_CACHE[filename]

    prompt_path = PROMPTS_DIR / filename
    try:
        if prompt_path.is_file():
            content = prompt_path.read_text(encoding="utf-8").strip()
            _PROMPT_CACHE[filename] = content
            return content
        else:
            logger.warning(f"Prompt file {prompt_path} not found. Using fallback text.")
    except Exception as e:
        logger.error(f"Error reading prompt file {prompt_path}: {e}")

    fallback_default = "You are Jerryy's AI. Answer the user's questions clearly, concisely, and helpfully."
    return fallback_default
