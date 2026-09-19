"""
Ollama Client for Jerryy's AI
Handles asynchronous communication with local Ollama instance.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import httpx
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("jerryys_ai.ollama")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "jerryys-ai")
TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT", "600.0"))


class OllamaConnectionError(Exception):
    """Raised when cannot connect to local Ollama server."""
    pass


class OllamaModelNotFoundError(Exception):
    """Raised when the specified model is not available in Ollama."""
    pass


class OllamaResponseError(Exception):
    """Raised when Ollama returns an invalid or empty response."""
    pass


async def check_ollama_health() -> Dict[str, Any]:
    """
    Checks if Ollama is running and verifies model availability.
    Returns status dict with connectivity and model presence.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Check for either 'jerryys-ai', 'jerryys-ai:latest', or matching model name
                model_found = any(
                    OLLAMA_MODEL == m or m.startswith(f"{OLLAMA_MODEL}:") or m == f"{OLLAMA_MODEL}:latest"
                    for m in models
                )
                return {
                    "online": True,
                    "model_found": model_found,
                    "available_models": models
                }
            return {
                "online": False,
                "model_found": False,
                "error": f"Ollama HTTP {resp.status_code}"
            }
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")
        return {
            "online": False,
            "model_found": False,
            "error": str(e)
        }


async def chat_with_ollama(messages: List[Dict[str, str]]) -> str:
    """
    Sends conversation messages to Ollama /api/chat endpoint.
    - model: jerryys-ai
    - stream: false
    - think: false (never expose internal reasoning)
    - timeout: 180s (local CPU execution)
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "think": False
    }

    url = f"{OLLAMA_URL}/api/chat"

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=payload)
    except httpx.ConnectError as e:
        logger.error(f"Cannot connect to Ollama at {url}: {e}")
        raise OllamaConnectionError(
            "Jerryy's AI could not connect to the local model. Make sure Ollama is running."
        ) from e
    except httpx.TimeoutException as e:
        logger.error(f"Ollama request timed out after {TIMEOUT_SECONDS}s: {e}")
        raise OllamaResponseError(
            "The model response timed out. Please try again with a shorter prompt."
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error communicating with Ollama: {e}")
        raise OllamaConnectionError(
            f"Error communicating with local Ollama: {e}"
        ) from e

    if response.status_code == 404:
        logger.error(f"Model '{OLLAMA_MODEL}' not found in Ollama.")
        raise OllamaModelNotFoundError(
            f"The {OLLAMA_MODEL} model is not available in Ollama."
        )

    if response.status_code != 200:
        logger.error(f"Ollama returned HTTP {response.status_code}: {response.text}")
        raise OllamaResponseError(
            f"Ollama returned error status {response.status_code}."
        )

    try:
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to parse Ollama JSON response: {e}")
        raise OllamaResponseError("Invalid JSON received from Ollama.") from e

    # Extract message content
    message_obj = data.get("message", {})
    content = message_obj.get("content", "")

    if not content or not content.strip():
        logger.warning("Ollama returned an empty response content.")
        raise OllamaResponseError("The model returned an empty response.")

    return content.strip()
