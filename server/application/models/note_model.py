import sqlite3
from application.exceptions import (
    DatabaseError,
    ValidationError,
    NoteNotFoundError,
    NotebookNotFoundError,
    DuplicateNoteError
)

class NoteModel:
    def __init__(self, db):
        """
        Initialize the NoteModel with a connection to the database
        :param db: connection to the database
        :raises ValidationError: if the database connection is invalid
        """
        if db is None:
            raise ValidationError("Database connection cannot be None")
        self.db = db
    
    def __is_notebook_exists(self, notebook_id):
        """
        Check whether a notebook exists
        :param notebook_id: ID of the notebook
        :return: True if the notebook exists, False otherwise
        """
        if not isinstance(notebook_id, int) or notebook_id <= 0:
            return False
        check_sql = "SELECT id FROM notebooks WHERE id = ?"
        result = self.db.fetchone(check_sql, [notebook_id])
        if result is None:
            return False
        return True
        
    def create_note(self, title, file_path, notebook_id):
        """
        Create a new note
        :param title: title of the note
        :param file_path: path of the note
        :param notebook_id: ID of the notebook which the note belongs to
        :raises ValidationError: if the title or file path is None, or notebook ID is invalid
        :raises DuplicateNoteError: if the note already exists
        :raises DatabaseError: if database operation fails
        :raises NotebookNotFoundError: if the notebook does not exist
        :return: NULL
        """
        if title is None:
            raise ValidationError("Note title cannot be None")
        if file_path is None:
            raise ValidationError("Note path cannot be None")
        if not isinstance(notebook_id, int) or notebook_id <= 0:
            raise ValidationError("Invalid notebook ID")
        # Check if the notebook exists
        if not self.__is_notebook_exists(notebook_id):
            raise NotebookNotFoundError(f"Notebook with ID {notebook_id} does not exist")
        try:
            with self.db.transaction():
                # Create the note
                sql = """
                INSERT INTO notes (title, file_path, notebook_id)
                VALUES (?, ?, ?)
                """
                params = [title, file_path, notebook_id]
                self.db.execute(sql, params)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint" in str(e):
                raise DuplicateNoteError(f"Note with title {title} already exists")
            raise DatabaseError(f"Failed to create note: {str(e)}")
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to create note: {str(e)}")
        
    def get_note_id(self, title, notebook_id):
        """
        Retrieve a note's ID by title
        :param title: title of the note
        :param notebook_id: ID of the notebook which the note belongs to
        :raises ValidationError: if the title is None, or notebook_id is invalid
        :raises NoteNotFoundError: if the note does not exist
        :raises NotebookNotFoundError: if the notebook does not exist
        :raises DatabaseError: if database operation fails
        :return: ID of the note in database
        """
        if title is None:
            raise ValidationError("Note title cannote be None")
        if not isinstance(notebook_id, int) or notebook_id <= 0:
            raise ValidationError("Invalid notebook ID")
        # Check if the notebook exists
        if not self.__is_notebook_exists(notebook_id):
            raise NotebookNotFoundError(f"Notebook with ID {notebook_id} does not exist")
        # Try to get the note's ID
        try:
            sql = "SELECT id FROM notes WHERE title = ? AND notebook_id = ?"
            result = self.db.fetchone(sql, [title, notebook_id])
            if result is None:
                raise NoteNotFoundError(f"Note with title {title} does not exist")
            return result["id"]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get note ID: {str(e)}")

    # Use get_note_id() before using following methods
    def get_note(self, note_id):
        """
        Retrieve a note's details by ID
        :param note_id: ID of the note
        :raises ValidationError: if the note ID is invalid
        :raises NoteNotFoundError: if the note does not exist
        :raises DatabaseError: if database operation fails
        :return: row of the note in database
        """
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValidationError("Invalid note ID")
        try:
            sql = "SELECT * FROM notes WHERE id = ?"
            result = self.db.fetchone(sql, [note_id])
            if result is None:
                raise NoteNotFoundError(f"Note with ID {note_id} does not exist")
            return result
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get note: {str(e)}")

    def update_note(self, note_id, new_title=None, new_path=None, new_notebook_id=None):
        """
        Update a note by ID
        :param note_id: ID of the note
        :param new_title: new title of the note
        :param new_path: new path of the note
        :param new_notebook_id: new notebook id of the note
        :raises ValidationError: if the note ID or new notebook ID is invalid, or no update parameter is provided
        :raises NoteNotFoundError: if the note does not exist
        :raises NotebookNotFoundError: if the notebook does not exist
        :raises DuplicateNoteError: if the note already exists
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValidationError("Invalid note ID")
        if not any([new_title, new_path, new_notebook_id]):
            raise ValidationError("At least one update parameter must be provided")
        # If new notebook_id is provided, check if the notebook id is valid and if the notebook exists
        if new_notebook_id:
            if not isinstance(new_notebook_id, int) or new_notebook_id <= 0:
                raise ValidationError("Invalid notebook ID")
            check_sql = "SELECT id FROM notebooks WHERE id = ?"
            if self.db.fetchone(check_sql, [new_notebook_id]) is None:
                raise NotebookNotFoundError(f"Notebook with ID {new_notebook_id} does not exist")
        # Try to update the note
        try:
            # Check whether the note exists
            if not self.get_note(note_id):
                raise NoteNotFoundError(f"Note with ID {note_id} does not exist")
            with self.db.transaction():
                sql = "UPDATE notes SET"
                updates = [] # Fileds need to be updated
                params = [] # Parameters for the SQL query
                # Add conditions for fields that need to be updated
                if new_title:
                    updates.append(" title = ?")
                    params.append(new_title)
                if new_path:
                    updates.append(" path = ?")
                    params.append(new_path)
                # Use get_id_by_name() in NotebookModel to get id of a notebook
                if new_notebook_id:
                    updates.append(" notebook_id = ?")
                    params.append(new_notebook_id)
                # Set update time by CURRENT_TIMESTAMP
                updates.append(" updated_at = CURRENT_TIMESTAMP")
                # Join updates
                sql += ", ".join(updates)
                sql += " WHERE id = ?"
                params.append(note_id)
                # Execute update
                self.db.execute(sql, params)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint" in str(e):
                raise DuplicateNoteError(f"Note with title {new_title} already exists")
            raise DatabaseError(f"Failed to update note: {str(e)}")
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to update note: {str(e)}")

    def delete_note(self, note_id):
        """
        Delete a note by ID
        :param note_id: ID of the note
        :raises ValidationError: if the note ID is invalid
        :raises NoteNotFoundError: if the note does not exist
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValidationError("Invalid note ID")
        try:
            # Check whether the note exists
            if not self.get_note(note_id):
                raise NoteNotFoundError(f"Note with ID {note_id} does not exist")
            with self.db.transaction():
                sql = "DELETE FROM notes WHERE id = ?"
                # Execute delete
                self.db.execute(sql, [note_id])
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to delete note: {str(e)}")
        
    def get_all_notes_in_notebook(self, notebook_id):
        """
        Retrieve all notes in a notebook
        :param notebook_id: ID of the notebook
        :raises: ValidationError: if the notebook ID is invalid
        :raises: NotebookNotFoundError: if the notebook does not exist
        :raises: DatabaseError: if database operation fails
        :return: List of all notes in the notebook
        """
        if not isinstance(notebook_id, int) or notebook_id <= 0:
            raise ValidationError("Invalid notebook ID")
        # Check whether the notebook exists
        if not self.__is_notebook_exists(notebook_id):
            raise NotebookNotFoundError(f"Notebook with ID {notebook_id} does not exist")
        try:
            sql = "SELECT * FROM notes WHERE notebook_id = ?"
            return self.db.fetchall(sql, [notebook_id])
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get all notes in notebook with ID {notebook_id}: {str(e)}")
        
    def get_all_notes(self):
        """
        Retrieve all notes
        :raises DatabaseError: if database operation fails
        :return: List of all notes in database
        """
        try:
            sql = "SELECT * FROM notes"
            return self.db.fetchall(sql)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get all notes: {str(e)}")