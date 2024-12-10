from .base import BaseError

class DatabaseError(BaseError):
    """
    Raised when database operations fail (e.g., connection errors, query failures)
    """
    pass

class ValidationError(BaseError):
    """
    Raised when data validation fails (e.g., invalid input, missing required fields)
    """
    pass