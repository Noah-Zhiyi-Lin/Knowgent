from .base import BaseError

class FileSystemError(BaseError):
    """
    Raised when file system operations fail (e.g., creating/deleting directories)
    """
    pass