class NoteModel:
    def __init__(self, db):
        """
        Initialize the NoteModel with a connection to the database
        :param db: connection to the database
        """
        self.db = db
    def create_note(self, title, file_path, notebook_id):
        """
        Create a new note
        :param title: title of the note
        :param file_path: path of the note
        :param notebook_id: ID of the notebook which the note belongs to
        :return: NULL
        """
        sql = """
        INSERT INTO notes (title, file_path, notebook_id)
        VALUES (?, ?, ?)
        """
        params = [title, file_path, notebook_id]
        self.db.execute(sql, params)

    def get_note_id(self, title):
        """
        Retrieve a note's ID by title
        :param title: title of the note
        :return: ID of the note in database
        """
        sql = "SELECT id FROM notes WHERE title = ?"
        result = self.db.fetchone(sql, [title])
        return result["id"] if result else None

    # Use get_note_id() before using following methods
    def get_note(self, note_id):
        """
        Retrieve a note's details by ID
        :param note_id: ID of the note
        :return: row of the note in database
        """
        sql = "SELECT * FROM notes WHERE id = ?"
        self.db.execute(sql, [note_id])
        return self.db.fetchone()

    def update_note(self, note_id, new_title=None, new_path=None, new_notebook_id=None):
        """
        Update a note by ID
        :param note_id: ID of the note
        :param new_title: new title of the note
        :param new_path: new path of the note
        :param new_notebook_id: new notebook id of the note
        :return: NULL
        """
        sql = "UPDATE notes SET"
        params = []
        # Add conditions for fields that need to be updated
        if new_title:
            sql += " title = ?,"
            params.append(new_title)
        if new_path:
            sql += " path = ?,"
            params.append(new_path)
        # Use get_id_by_name() in NotebookModel to get id of a notebook
        if new_notebook_id:
            sql += " notebook_id = ?,"
            params.append(new_notebook_id)
        # Set update time by CURRENT_TIMESTAMP
        sql += " updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        params.append(note_id)
        # Execute update
        self.db.execute(sql, params)

    def delete_note(self, note_id):
        """
        Delete a note by ID
        :param note_id: ID of the note
        :return: NULL
        """
        sql = "DELETE FROM notes WHERE id = ?"
        # Execute delete
        self.db.execute(sql, [id])

    def get_all_notes(self):
        """
        Retrieve all notes
        :return: List of all notes in database
        """
        sql = "SELECT * FROM notes"
        return self.db.fetchall(sql)