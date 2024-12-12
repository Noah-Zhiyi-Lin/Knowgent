import sqlite3
from application.exceptions import (
    DatabaseError,
    ValidationError,
    TagError,
    TagNotFoundError,
    DuplicateTagError
)

class TagModel:
    def __init__(self, db):
        """
        Initialize the TagModel with a connection to the database
        :param db: connection to the database
        :raises ValidationError: if the database connection is invalid
        """
        if db is None:
            raise ValidationError("Database connection cannot be None")
        self.db = db

    def create_tag(self, tag_name):
        """
        Create a new tag
        :param tag_name: name of the tag
        :raises ValidationError: if the tag name is None
        :raises DuplicateTagError: if the tag already exists
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if tag_name is None:
            raise ValidationError("Tag name cannot be None")
        # Try to create the tag
        try:
            with self.db.transaction():
                sql = "INSERT INTO tags (tag_name) VALUES (?)"
                self.db.execute(sql, [tag_name])
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint" in str(e):
                raise DuplicateTagError(f"Tag name {tag_name} already exists")
            raise DatabaseError(f"Failed to create tag: {str(e)}")
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to create tag: {str(e)}")

    def get_tag_id(self, tag_name):
        """
        Retrieve a tag's ID by its name
        :param tag_name: name of the tag
        :return: ID of the tag
        """
        if tag_name is None:
            raise ValidationError("Tag name cannot be None")
        # Try to get the tag's ID
        try:
            sql = "SELECT id FROM tags WHERE tag_name = ?"
            result = self.db.fetchone(sql, [tag_name])
            if result is None:
                raise TagNotFoundError(f"Tag name {tag_name} not found")
            return result["id"]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get tag ID: {str(e)}")

    # Use get_tag_id() before using following methods
    def get_tag(self, tag_id):
        """
        Retrieve a tag by its ID
        :param tag_id: ID of the tag
        :rasies ValidationError: if the tag ID is invalid
        :raises TagNotFoundError: if the tag does not exist
        :raises DatabaseError: if database operation fails
        :return: row of the tag in database
        """
        if not isinstance(tag_id, int) or tag_id <= 0:
            raise ValidationError("Invalid tag ID")
        # Try to get the tag
        try:
            sql = "SELECT * FROM tags WHERE id = ?"
            result = self.db.fetchone(sql, [tag_id])
            if result is None:
                raise TagNotFoundError(f"Tag ID {tag_id} does not exist")
            return result
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get tag: {str(e)}")

    def update_tag(self, tag_id, new_name):
        """
        Update a tag by its ID
        :param tag_id: ID of the tag
        :param new_name: new name of the tag
        :raises ValidationError: if tag_id is invalid or new_name is None
        :raises TagNotFoundError: if the tag does not exist
        :raises DuplicateTagError: if the tag already exists
        :raises DatabseError: if database operation fails
        :return: NULL
        """
        if not isinstance(tag_id, int) or tag_id <= 0:
            raise ValidationError("Invalid tag ID")
        if new_name is None:
            raise ValidationError("New tag name must be provided to update the tag")
        # Try to update the tag
        try:
            # Check whether the tag exists
            if not self.get_tag(tag_id):
                raise TagNotFoundError(f"Tag ID {tag_id} does not exist")
            with self.db.transaction():
                sql = "UPDATE tags SET tag_name = ? WHERE id = ?"
                params = [new_name, tag_id]
                # Execute update
                self.db.execute(sql, params)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint" in str(e):
                raise DuplicateTagError(f"Tag name {new_name} already exists")
            raise DatabaseError(f"Failed to update tag: {str(e)}")
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to update tag: {str(e)}")

    def delete_tag(self, tag_id):
        """
        Delete a tag by its ID
        :param tag_id: ID of the tag
        :raises ValidationError: if the tag ID is invalid
        :raises TagNotFoundError: if the tag does not exist
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if not isinstance(tag_id, int) or tag_id <= 0:
            raise ValidationError("Invalid tag ID")
        # Try to delete the tag
        try:
            # Check whether the tag exists
            if not self.get_tag(tag_id):
                raise TagNotFoundError(f"Tag ID {tag_id} does not exist")
            with self.db.transaction():
                sql = "DELETE FROM tags WHERE id = ?"
                # Execute delete
                self.db.execute(sql, [tag_id])
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to delete tag: {str(e)}")

    def get_all_tags(self):
        """
        Retrieve all tags
        :raises DatabaseError: if database operation fails
        :return: List of all tags in the database
        """
        try:
            sql = "SELECT * FROM tags"
            return self.db.fetchall(sql)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get all tags: {str(e)}")