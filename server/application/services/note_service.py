from pathlib import Path
from application.models.note_model import NoteModel
from application.exceptions import (
    ValidationError,
    DatabaseError,
    NoteError,
    NoteNotFoundError,
    NotebookNotFoundError,
    DuplicateNoteError,
    FileSystemError
)
