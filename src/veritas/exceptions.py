class VeritasError(Exception):
    """Base class for all exceptions raised by Veritas."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ParseError(VeritasError):
    """Raised when parsing versions fail."""
