class NoteModel:
    def __init__(self, db):
        # Database connection
        self.db = db
    def create_note(self, title, file_path, notebook_id):
        """
        Create a new note
        :param title: title of the note
        :param file_path: path of the note
        :param notebook_id: ID of the notebook which the note belongs to
        :return: None
        """
        sql = """
        INSERT INTO notes (title, file_path, notebook_id)
        VALUES (?, ?, ?)
        """
        params = [title, file_path, notebook_id]
        self.db.execute(sql, params)

    def get_note_by_title(self, title):
        """
        Retrieve a note's details by title
        :param title: title of the note
        :return: row of the note in database
        """
        sql = "SELECT * FROM notes WHERE title = ?"
        self.db.execute(sql, [title])
        return self.db.fetchone()

    def get_id_by_title(self, title):
        """
        Retrieve a note's ID by title
        :param title: title of the note
        :return: ID of the note in database
        """
        sql = "SELECT id FROM notes WHERE title = ?"
        result = self.db.fetchone(sql, [title])
        return result["id"] if result else None

    def update_note_by_title(self, title, new_title=None, new_path=None, new_notebook_id=None):
        """
        Update a note by current title
        :param title: current title of the note
        :param new_title: new title of the note
        :param new_path: new path of the note
        :param new_notebook_id: new notebook id of the note
        :return: None
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
        sql += " updated_at = CURRENT_TIMESTAMP WHERE title = ?"
        params.append(title)
        # Execute update
        self.db.execute(sql, params)

    def delete_note_by_title(self, title):
        """
        Delete a note by title
        :param title: title of the note
        :return: None
        """
        sql = "DELETE FROM notes WHERE title = ?"
        # Execute delete
        self.db.execute(sql, [title])

    def get_all_notes(self):
        """
        Retrieve all notes
        :return: rows of all notes in database
        """
        sql = "SELECT * FROM notes"
        return self.db.fetchall(sql)