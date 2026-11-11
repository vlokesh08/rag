class DomainError(Exception):
    """Base class for service-layer errors that map to HTTP responses."""


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class AuthError(DomainError):
    pass
