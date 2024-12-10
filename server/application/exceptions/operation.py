from .base import BaseError

class NotebookError(BaseError):
    """
    Raised when notebook operations fail
    """
    pass

class NoteError(BaseError):
    """
    Raised when note operations fail
    """
    pass

class TagError(BaseError):
    """
    Raised when tag operations fail
    """
    pass

class NoteTagError(BaseError):
    """
    Raised when note-tag relationship operations fail
    """
    pass