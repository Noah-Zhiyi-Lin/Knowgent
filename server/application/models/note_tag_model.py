import sqlite3
from application.exceptions import (
    ValidationError,
    DatabaseError
)

class NoteTagModel:
    def __init__(self, db):
        """
        Initialize the NoteTagModel with a connection to the database
        :param db: connection to the database
        """
        self.db = db

    def add_tag_to_note(self, note_id, tag_id):
        """
        Associate a tag with a note by adding an entry in the note_tags table
        :param note_id: ID of the note
        :param tag_id: ID of the tag
        :return: NULL
        """
        sql = """
        INSERT INTO note_tags (note_id, tag_id)
        VALUES (?, ?)
        """
        self.db.execute(sql, [note_id, tag_id])

    def remove_tag_from_note(self, note_id, tag_id):
        """
        Remove a tag from a note by deleting an entry in the note_tags table
        :param note_id: ID of the note
        :param tag_id: ID of the tag
        :return: NULL
        """
        sql = "DELETE FROM note_tags WHERE note_id = ? AND tag_id = ?"
        self.db.execute(sql, [note_id, tag_id])

    def get_tags_for_note(self, note_id):
        """
        Retrieve all tags associated a note
        :param note_id: ID of the note
        :return: List of tags associated with the note
        """
        sql = "SELECT tag_id FROM note_tags WHERE note_id = ?"
        return self.db.fetchall(sql, [note_id])

    def get_notes_for_tag(self, tag_id):
        """
        Retrieve all notes associated with a tag
        :param tag_id: ID of the tag
        :return: List of notes associated with the tag
        """
        sql = "SELECT note_id FROM note_tags WHERE tag_id = ?"
        return self.db.fetchall(sql, [tag_id])

    def remove_all_tags_for_note(self, note_id):
        """
        Remove all tags associated with a note
        :param note_id: ID of the note
        :return: NULL
        """
        sql = "DELETE FROM note_tags WHERE note_id = ?"
        self.db.execute(sql, [note_id])