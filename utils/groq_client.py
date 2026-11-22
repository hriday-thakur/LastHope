"""
Groq API client wrapper for LastHope.
Provides secure credential management from .env, structured exception handling,
timeouts, and reusable chat completion calls.
"""

import os
from typing import Optional
from dotenv import load_dotenv
import groq

# Ensure .env is loaded
load_dotenv()


class GroqClientError(Exception):
    """Base exception for all Groq client errors."""
    pass


class MissingAPIKeyError(GroqClientError):
    """Raised when the GROQ_API_KEY is missing or empty in .env."""
    pass


class AuthenticationError(GroqClientError):
    """Raised when the Groq API rejects the provided credentials."""
    pass


class ModelNotFoundError(GroqClientError):
    """Raised when the requested model is invalid or unavailable."""
    pass


class RateLimitExceededError(GroqClientError):
    """Raised when API rate limits are exceeded."""
    pass


class NetworkConnectionError(GroqClientError):
    """Raised when a network or DNS failure occurs."""
    pass


class APIRequestTimeoutError(GroqClientError):
    """Raised when an API request times out."""
    pass


def get_configured_model() -> str:
    """Returns the model configured in .env, falling back to openai/gpt-oss-120b."""
    load_dotenv(override=True)
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    return model.strip() if model else "openai/gpt-oss-120b"


def get_groq_client(timeout: float = 60.0, max_retries: int = 1) -> groq.Groq:
    """
    Initializes and returns an authenticated Groq client instance.
    Never exposes or logs the API key.
    """
    load_dotenv(override=True)
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or not api_key.strip() or "your_groq_api_key_here" in api_key:
        raise MissingAPIKeyError(
            "GROQ_API_KEY is missing or unconfigured. Please add your Groq API key to the local .env file."
        )

    return groq.Groq(
        api_key=api_key.strip(),
        timeout=timeout,
        max_retries=max_retries,
    )


def generate_response(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
    timeout: float = 60.0,
) -> str:
    """
    Sends a system and user prompt to Groq and returns the generated text response.

    Args:
        system_prompt: Instructions defining the model's persona, rules, and output schema.
        user_prompt: The actual content or material to process.
        model: Optional model override. Defaults to GROQ_MODEL in .env.
        temperature: Sampling temperature (lower = more deterministic/factual).
        max_tokens: Maximum tokens in response completion (optional).
        timeout: Request timeout in seconds.

    Returns:
        Cleaned string response from the model.
    """
    if not user_prompt or not user_prompt.strip():
        raise ValueError("User prompt cannot be empty.")

    target_model = model.strip() if model else get_configured_model()
    client = get_groq_client(timeout=timeout)

    messages = []
    if system_prompt and system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt.strip()})
    messages.append({"role": "user", "content": user_prompt.strip()})

    try:
        kwargs = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None and max_tokens > 0:
            kwargs["max_tokens"] = max_tokens

        completion = client.chat.completions.create(**kwargs)

        if not completion.choices or len(completion.choices) == 0:
            raise GroqClientError("Groq API returned an empty response with no completion choices.")

        content = completion.choices[0].message.content
        if content is None:
            return ""

        return content.strip()

    except groq.AuthenticationError as e:
        raise AuthenticationError("Authentication failed: Invalid Groq API key in .env.") from e
    except groq.NotFoundError as e:
        raise ModelNotFoundError(
            f"Model '{target_model}' was not found or is not accessible on your Groq account."
        ) from e
    except groq.RateLimitError as e:
        raise RateLimitExceededError(
            f"Rate limit exceeded for model '{target_model}'. Please wait a moment before trying again."
        ) from e
    except groq.APITimeoutError as e:
        raise APIRequestTimeoutError(
            f"Request timed out after {timeout} seconds while communicating with Groq."
        ) from e
    except groq.APIConnectionError as e:
        raise NetworkConnectionError(
            "Network connection failed: Unable to reach the Groq API server."
        ) from e
    except groq.APIStatusError as e:
        raise GroqClientError(f"Groq API returned status {e.status_code}: {e.message}") from e
    except Exception as e:
        raise GroqClientError(f"Failed to generate response from Groq: {type(e).__name__} - {e}") from e
