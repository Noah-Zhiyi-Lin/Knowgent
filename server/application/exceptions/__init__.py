"""
Application-wide exceptions for handling various error cases in the notebook application.
"""

from .base import BaseError
from .database import (
    DatabaseError,
    ValidationError
)
from .resource import (
    ResourceNotFoundError,
    NotebookNotFoundError,
    NoteNotFoundError,
    TagNotFoundError,
    DuplicateResourceError,
    DuplicateNotebookError,
    DuplicateNoteError,
    DuplicateTagError
)
from .filesystem import FileSystemError
from .operation import (
    NotebookError,
    NoteError,
    TagError,
    NoteTagError
)

__all__ = [
    'BaseError',
    'DatabaseError',
    'ValidationError',
    'ResourceNotFoundError',
    'NotebookNotFoundError',
    'NoteNotFoundError',
    'TagNotFoundError',
    'FileSystemError',
    'NotebookError',
    'NoteError',
    'TagError',
    'NoteTagError',
    'DuplicateResourceError',
    'DuplicateNotebookError',
    'DuplicateNoteError',
    'DuplicateTagError'
]