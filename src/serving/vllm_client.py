"""
OpenAI-compatible client for both Ollama and vLLM backends.
Switch backends via env vars — no code changes needed.

Ollama: TARGET_BASE_URL=http://localhost:11434/v1
vLLM:   TARGET_BASE_URL=http://localhost:8000/v1
"""

import os
import time
import logging
from openai import OpenAI, APIConnectionError, APITimeoutError, APIStatusError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
_RETRY_DELAY = float(os.getenv("RETRY_DELAY_S", "5"))


def _make_client(base_url: str) -> OpenAI:
    return OpenAI(
        base_url=base_url,
        api_key=os.getenv("OPENAI_API_KEY", "ollama"),
        timeout=120.0,
    )


TARGET_CLIENT = _make_client(os.getenv("TARGET_BASE_URL", "http://localhost:11434/v1"))
ATTACKER_CLIENT = _make_client(os.getenv("ATTACKER_BASE_URL", "http://localhost:11434/v1"))


def chat(
    client: OpenAI,
    model: str,
    system: str,
    user: str,
    temperature: float = 0.8,
    max_tokens: int = 2048,
) -> str:
    for attempt in range(1, _RETRY_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            return content.strip()
        except (APIConnectionError, APITimeoutError) as e:
            if attempt == _RETRY_ATTEMPTS:
                logger.warning("API unavailable after %d attempts: %s", _RETRY_ATTEMPTS, e)
                return ""
            logger.debug("Attempt %d failed (%s), retrying in %.0fs", attempt, type(e).__name__, _RETRY_DELAY)
            time.sleep(_RETRY_DELAY)
        except APIStatusError as e:
            logger.warning("API error %d: %s", e.status_code, e.message)
            return ""


def target_chat(system: str, user: str, **kwargs) -> str:
    return chat(
        TARGET_CLIENT,
        model=os.getenv("TARGET_MODEL", "gemma4:26b"),
        system=system,
        user=user,
        **kwargs,
    )


def attacker_chat(system: str, user: str, **kwargs) -> str:
    return chat(
        ATTACKER_CLIENT,
        model=os.getenv("ATTACKER_MODEL", "gemma4:e4b"),
        system=system,
        user=user,
        **kwargs,
    )


def judge_chat(system: str, user: str, **kwargs) -> str:
    return chat(
        TARGET_CLIENT,
        model=os.getenv("JUDGE_MODEL", "gemma4:26b"),
        system=system,
        user=user,
        temperature=0.0,
        **kwargs,
    )
