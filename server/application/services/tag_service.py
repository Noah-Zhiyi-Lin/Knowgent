from server.application.models.tag_model import TagModel
from server.application.exceptions import (
    ValidationError,
    DatabaseError,
    TagNotFoundError,
    DuplicateTagError,
    TagError
)

class TagService:
    def __init__(self, db):
        """
        Initialize the TagService with a connection to the database
        :param db: connection to the database
        :raises TagError: if service initialization fails
        """
        try:
            self.__tag_model = TagModel(db)
        except ValidationError as e:
            raise TagError(f"Failed to initialize TagService: {str(e)}")
        except Exception as e:
            raise TagError(f"Unexpected error during TagService initialization: {str(e)}")
        
    def create_tag(self, tag_name):
        """
        Create a new tag
        :param tag_name: name of the new tag
        :raises TagError: if tag creation fails
        :return: True if the tag is created successfully, False otherwise
        """
        try:
            self.__tag_model.create_tag(tag_name)
            return True
        except (ValidationError, DuplicateTagError, DatabaseError, Exception) as e:
            raise TagError(f"Failed to create tag {tag_name}: {str(e)}")
        
    def get_tag(self, tag_name):
        """
        Get a tag by its name
        :param tag_name: name of the tag
        :raises TagError: if retrieval fails
        :return: tag details or None if not found
        """
        try:
            tag_id = self.__tag_model.get_tag_id(tag_name)
            return self.__tag_model.get_tag(tag_id)
        except (ValidationError, TagNotFoundError, DatabaseError, Exception) as e:
            raise TagError(f"Failed to get tag {tag_name}: {str(e)}")

    def update_tag(self, tag_name, new_name):
        """
        Update a tag's name
        :param tag_name: current name of the tag
        :param new_name: new name of the tag
        :raises TagError: if update fails
        :return: True if the tag is updated successfully, False otherwise
        """
        try:
            tag_id = self.__tag_model.get_tag_id(tag_name)
            # Update the tag
            self.__tag_model.update_tag(tag_id, new_name)
            return True
        except (ValidationError, TagNotFoundError, DuplicateTagError, DatabaseError, Exception) as e:
            raise TagError(f"Failed to update tag {tag_name}: {str(e)}")

    def delete_tag(self, tag_name):
        """
        Delete a tag
        :param tag_name: name of the tag
        :raises TagError: if deletion fails
        :return: True if the tag is deleted successfully, False otherwise
        """
        try:
            tag_id = self.__tag_model.get_tag_id(tag_name)
            # Delete the tag (in database)
            self.__tag_model.delete_tag(tag_id)
            return True
        except (ValidationError, TagNotFoundError, DatabaseError, Exception) as e:
            raise TagError(f"Failed to delete tag {tag_name}: {str(e)}")
        
    def get_all_tags(self):
        """
        Get all tags
        :raises TagError: if retrieval fails
        :return: list of all tag names
        """
        try:
            tags = self.__tag_model.get_all_tags()
            return [tag["tag_name"] for tag in tags]
        except (DatabaseError, Exception) as e:
            raise TagError(f"Failed to get all tags: {str(e)}")