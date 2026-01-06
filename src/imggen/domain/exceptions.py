"""Domain-level exceptions."""


class DomainException(Exception):
    """Base exception for domain errors."""
    pass


class AuthenticationError(DomainException):
    """Raised when authentication fails."""
    pass


class UserNotFoundError(DomainException):
    """Raised when user does not exist."""
    pass


class UserAlreadyExistsError(DomainException):
    """Raised when trying to create a user that already exists."""
    pass


class SessionExpiredError(DomainException):
    """Raised when session has expired."""
    pass


class SessionNotFoundError(DomainException):
    """Raised when no active session exists."""
    pass


class EncryptionError(DomainException):
    """Raised when encryption/decryption fails."""
    pass


class ImageNotFoundError(DomainException):
    """Raised when image does not exist."""
    pass


class VaultAccessError(DomainException):
    """Raised when vault access fails."""
    pass


class GenerationError(DomainException):
    """Raised when image generation fails."""
    pass

