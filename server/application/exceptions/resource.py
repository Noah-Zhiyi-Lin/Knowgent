from .base import BaseError

class ResourceNotFoundError(BaseError):
    """
    Base class for resource not found errors
    """
    pass

class NotebookNotFoundError(ResourceNotFoundError):
    """
    Raised when a notebook cannot be found
    """
    pass

class NoteNotFoundError(ResourceNotFoundError):
    """
    Raised when a note cannot be found
    """
    pass

class TagNotFoundError(ResourceNotFoundError):
    """
    Raised when a tag cannot be found
    """
    pass

class DuplicateResourceError(BaseError):
    """
    Base class for duplicate resource errors
    """
    pass

class DuplicateNotebookError(DuplicateResourceError):
    """
    Raised when attempting to create a duplicate notebook
    """
    pass

class DuplicateNoteError(DuplicateResourceError):
    """
    Raised when attempting to create a duplicate note
    """
    pass

class DuplicateTagError(DuplicateResourceError):
    """
    Raised when attempting to create a duplicate tag
    """
    pass

class DuplicateNoteTagError(DuplicateResourceError):
    """
    Raised when attempting to create a duplicate note-tag association
    """
    pass