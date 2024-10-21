from deepgram.errors import DeepgramApiKeyError
from typing import Any, Callable, TypeVar
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


def handle_deepgram_api_error(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle common Deepgram API errors.
    """

    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except DeepgramApiKeyError as e:
            if e.status_code == 401:
                logger.error(f"Authentication error: {e}")
            elif e.status_code == 403:
                logger.error(f"Permission denied: {e}")
            elif e.status_code == 429:
                logger.error(f"Rate limit exceeded: {e}")
            elif e.status_code >= 500:
                logger.error(f"Deepgram server error: {e}")
            else:
                logger.error(f"Deepgram API error: {e}")
        except ConnectionError as e:
            logger.error(f"Network error: {e}")
        except TimeoutError as e:
            logger.error(f"Request timed out: {e}")
        except ValueError as e:
            logger.error(f"Invalid request: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return None  # type: ignore

    return wrapper
