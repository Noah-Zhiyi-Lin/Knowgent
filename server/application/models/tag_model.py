class TagModel:
    def __init__(self, db):
        """
        Initialize the TagModel with a connection to the database
        :param db: connection to the database
        """
        self.db = db

    def create_tag(self, tag_name):
        """
        Create a new tag
        :param tag_name: name of the tag
        :return: NULL
        """
        sql = "INSERT INTO tags (tag_name) VALUES (?)"
        self.db.execute(sql, [tag_name])

    def get_tag_id(self, tag_name):
        """
        Retrieve a tag's ID by its name
        :param tag_name: name of the tag
        :return: ID of the tag
        """
        sql = "SELECT id FROM tags WHERE tag_name = ?"
        result = self.db.fetchone(sql, [tag_name])
        return result["id"] if result else None

    # Use get_tag_id() before using following methods
    def get_tag(self, tag_id):
        """
        Retrieve a tag by its ID
        :param tag_id: ID of the tag
        :return: row of the tag in database
        """
        sql = "SELECT * FROM tags WHERE id = ?"
        return self.db.fetchone(sql, [tag_id])

    def update_tag(self, tag_id, new_name):
        """
        Update a tag by its ID
        :param tag_id: ID of the tag
        :param new_name: new name of the tag
        :return: NULL
        """
        sql = "UPDATE tags SET tag_name = ? WHERE id = ?"
        params = [new_name, tag_id]
        # Execute update
        self.db.execute(sql, params)

    def delete_tag(self, tag_id):
        """
        Delete a tag by its ID
        :param tag_id: ID of the tag
        :return: NULL
        """
        sql = "DELETE FROM tags WHERE id = ?"
        self.db.execute(sql, [tag_id])

    def get_all_tags(self):
        """
        Retrieve all tags
        :return: List of all tags in the database
        """
        sql = "SELECT * FROM tags"
        return self.db.fetchall(sql)