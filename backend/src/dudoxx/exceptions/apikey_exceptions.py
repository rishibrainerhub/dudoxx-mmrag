class APIKeyError(Exception):
    """Base exception class for API key related errors."""


class APIKeyCreationError(APIKeyError):
    """Raised when there's an error creating an API key."""


class APIKeyValidationError(APIKeyError):
    """Raised when there's an error validating an API key."""


class APIKeyRevocationError(APIKeyError):
    """Raised when there's an error revoking an API key."""


class ApiKeyNotFound(APIKeyError):
    """Raised when an API key is not found."""

    def __init__(self):
        super().__init__("API key not found")
