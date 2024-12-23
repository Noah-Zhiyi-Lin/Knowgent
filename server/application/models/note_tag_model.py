import sqlite3
from server.application.exceptions import (
    ValidationError,
    DatabaseError,
    NoteNotFoundError,
    TagNotFoundError,
    DuplicateNoteTagError
)

class NoteTagModel:
    def __init__(self, db):
        """
        Initialize the NoteTagModel with a connection to the database
        :param db: connection to the database
        """
        if db is None:
            raise ValidationError("Database connection cannot be None")
        self.db = db
        
    def __is_note_exists(self, note_id):
        """
        Check whether a note exists
        :param note_id: ID of the note
        :return: True if the note exists, False otherwise
        """
        if not isinstance(note_id, int) or note_id <= 0:
            return False
        check_sql = "SELECT id FROM notes WHERE id = ?"
        result = self.db.fetchone(check_sql, [note_id])
        if result is None:
            return False
        return True
        
    def __is_tag_exists(self, tag_id):
        """
        Check whether a tag exists
        :param tag_id: ID of the tag
        :return: True if the tag exists, False otherwise
        """
        if not isinstance(tag_id, int) or tag_id <= 0:
            return False
        check_sql = "SELECT id FROM tags WHERE id = ?"
        result = self.db.fetchone(check_sql, [tag_id])
        if result is None:
            return False
        return True


    def add_tag_to_note(self, note_id, tag_id):
        """
        Associate a tag with a note by adding an entry in the note_tags table
        :param note_id: ID of the note
        :param tag_id: ID of the tag
        :raises ValidationError: if note_id or tag_id is invalid
        :raises DuplicateNoteTagError: if the note-tag association already exists
        :raises NoteNotFoundError: if the note does not exist
        :raises TagNotFoundError: if the tag does not exist
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValidationError("Invalid note ID")
        if not isinstance(tag_id, int) or tag_id <= 0:
            raise ValidationError("Invalid tag ID")
        # Check if the note and tag exist
        if not self.__is_note_exists(note_id):
            raise NoteNotFoundError(f"Note with ID {note_id} does not exist")
        if not self.__is_tag_exists(tag_id):
            raise TagNotFoundError(f"Tag with ID {tag_id} does not exist")
        # Try to associate the tag with the note
        try:
            with self.db.transaction():
                sql = """
                INSERT INTO note_tags (note_id, tag_id)
                VALUES (?, ?)
                """
                self.db.execute(sql, [note_id, tag_id])
        except sqlite3.IntegrityError as e:
            err_info = str(e)
            if "UNIQUE constraint failed" in err_info:
                raise DuplicateNoteTagError(
                    f"Note with id {note_id} is already associated with tag with id {tag_id}"
                )
            raise DatabaseError(f"Failed to associate tag with note: {err_info}")
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to associate tag with note: {str(e)}")

    def get_tags_for_note(self, note_id):
        """
        Retrieve all tags associated a note
        :param note_id: ID of the note
        :raises ValidationError: if note_id is invalid
        :raises NoteNotFoundError: if the note does not exist
        :raises DatabaseError: if database operation fails
        :return: List of tag names associated with the note
        """
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValidationError("Invalid note ID")
        if not self.__is_note_exists(note_id):
            raise NoteNotFoundError(f"Note with ID {note_id} does not exist")
        # Try to get the tags associated with the note
        try:
            sql = """
            SELECT tags.tag_name
            FROM tags
            JOIN note_tags ON tags.id = note_tags.tag_id
            WHERE note_tags.note_id = ?
            """
            results = self.db.fetchall(sql, [note_id])
            return [result["tag_name"] for result in results]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get tags for note: {str(e)}")

    def get_notes_for_tag(self, tag_id):
        """
        Retrieve all notes associated with a tag
        :param tag_id: ID of the tag
        :raises ValidationError: if tag_id is invalid
        :raises TagNotFoundError: if the tag does not exist
        :raises DatabaseError: if database operation fails
        :return: List of note ids associated with the tag
        """
        if not isinstance(tag_id, int) or tag_id <= 0:
            raise ValidationError("Invalid tag ID")
        if not self.__is_tag_exists(tag_id):
            raise TagNotFoundError(f"Tag with ID {tag_id} does not exist")
        # Try to get the notes associated with the tag
        try:
            sql = """
            SELECT notes.id
            FROM notes
            JOIN note_tags ON notes.id = note_tags.note_id
            WHERE note_tags.tag_id = ?
            """
            results = self.db.fetchall(sql, [tag_id])
            return [result["id"] for result in results]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get notes for tag: {str(e)}")

    def remove_tag_from_note(self, note_id, tag_id):
        """
        Remove a tag from a note by deleting an entry in the note_tags table
        :param note_id: ID of the note
        :param tag_id: ID of the tag
        :raises ValidationError: if note_id or tag_id is invalid
        :raises NoteNotFoundError: if the note does not exist
        :raises TagNotFoundError: if the tag does not exist
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValidationError("Invalid note ID")
        if not isinstance(tag_id, int) or tag_id <= 0:
            raise ValidationError("Invalid tag ID")
        # Check if the note and tag exist
        if not self.__is_note_exists(note_id):
            raise NoteNotFoundError(f"Note with ID {note_id} does not exist")
        if not self.__is_tag_exists(tag_id):
            raise TagNotFoundError(f"Tag with ID {tag_id} does not exist")
        # Try to remove the tag from the note
        try:
            with self.db.transaction():
                sql = "DELETE FROM note_tags WHERE note_id = ? AND tag_id = ?"
                self.db.execute(sql, [note_id, tag_id])
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to remove tag from note: {str(e)}")

    def remove_all_tags_for_note(self, note_id):
        """
        Remove all tags associated with a note
        :param note_id: ID of the note
        :raises ValidationError: if note_id is invalid
        :raises NoteNotFoundError: if the note does not exist
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValidationError("Invalid note ID")
        if not self.__is_note_exists(note_id):
            raise NoteNotFoundError(f"Note with ID {note_id} does not exist")
        # Try to remove all tags associated with the note
        try:
            with self.db.transaction():
                sql = "DELETE FROM note_tags WHERE note_id = ?"
                self.db.execute(sql, [note_id])
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to remove all tags for note: {str(e)}")

    def remove_all_notes_for_tag(self, tag_id):
        """
        Remove all notes associated with a tag
        :param tag_id: ID of the tag
        :raises ValidationError: if tag_id is invalid
        :raises TagNotFoundError: if the tag does not exist
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if not isinstance(tag_id, int) or tag_id <= 0:
            raise ValidationError("Invalid tag ID")
        if not self.__is_tag_exists(tag_id):
            raise TagNotFoundError(f"Tag with ID {tag_id} does not exist")
        # Try to remove all notes associated with the tag
        try:
            with self.db.transaction():
                sql = "DELETE FROM note_tags WHERE tag_id = ?"
                self.db.execute(sql, [tag_id])
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to remove all notes for tag: {str(e)}")