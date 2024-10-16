import openai
from typing import Any, Callable, TypeVar
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


def handle_openai_api_error(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle common API errors.
    """

    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
        except openai.APIConnectionError as e:
            logger.error(f"Network error: {e}")
        except openai.APITimeoutError as e:
            logger.error(f"Request timed out: {e}")
        except openai.AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
        except openai.PermissionDeniedError as e:
            logger.error(f"Permission denied: {e}")
        except openai.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return None  # type: ignore

    return wrapper
