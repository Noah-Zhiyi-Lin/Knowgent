from server.application.models.note_tag_model import NoteTagModel
from server.application.models.note_model import NoteModel
from server.application.exceptions import (
    ValidationError,
    DatabaseError,
    NoteNotFoundError,
    TagNotFoundError,
    DuplicateNoteTagError,
    NoteError,
    TagError,
    NoteTagError
)

class NoteTagService:
    def __init__(self, db):
        """
        Initialize the NoteTagService with a connection to the database
        :param db: connection to the database
        :raises NoteTagError: if service initialization fails
        """
        try:
            self.__note_tag_model = NoteTagModel(db)
            self.__note_service = None
            self.__tag_service = None
            self.__note_model = NoteModel(db)
        except (ValidationError, NoteError, TagError) as e:
            raise NoteTagError(f"Failed to initialize NoteTagService: {str(e)}")
        except Exception as e:
            raise NoteTagError(f"Unexpected error during NoteTagService initialization: {str(e)}")
        
    # Inject dependencies
    @property
    def note_service(self):
        if not self.__note_service:
            raise NoteError("NoteService not set")
        return self.__note_service
    
    @note_service.setter
    def note_service(self, service):
        self.__note_service = service
        
    @property
    def tag_service(self):
        if not self.__tag_service:
            raise TagError("TagService not set")
        return self.__tag_service

    @tag_service.setter
    def tag_service(self, service):
        self.__tag_service = service

    def add_tag_to_note(self, title, notebook_name, tag_name):
        """
        Add a tag to a note
        :param title: title of the note
        :param notebook_name: name of the notebook which the note belongs to
        :param tag_name: name of the tag to be added
        :raises NoteTagError: if adding fails
        :return: True if adding is successful, False otherwise
        """
        try:
            # Try to get the note
            try:
                note = self.note_service.get_note(title, notebook_name)
            except NoteError as e:
                raise e
            note_id = note["id"]
            # Try to get the tag
            try:
                tag = self.tag_service.get_tag(tag_name)
            except TagError as e:
                raise e
            tag_id = tag["id"]
            # Try to add the tag to the note
            self.__note_tag_model.add_tag_to_note(note_id, tag_id)
            return True
        except (
            NoteError,
            TagError,
            ValidationError,
            DuplicateNoteTagError,
            NoteNotFoundError,
            TagNotFoundError,
            DatabaseError,
            Exception
        ) as e:
            raise NoteTagError(
                f"Failed to add tag {tag_name} to note {title} in notebook {notebook_name}: {str(e)}"
            )

    def get_tags_for_note(self, title, notebook_name):
        """
        Get all tags associated with a note
        :param title: title of the note
        :param notebook_name: name of the notebook which the note belongs to
        :raises NoteTagError: if retrieval fails
        :return: list of tag names associated with the note
        """
        try:
            # Try to get the note
            try:
                note = self.note_service.get_note(title, notebook_name)
            except NoteError as e:
                raise e
            note_id = note["id"]
            return self.__note_tag_model.get_tags_for_note(note_id)
        except (NoteError, ValidationError, NoteNotFoundError, DatabaseError, Exception) as e:
            raise NoteTagError(
                f"Failed to get tags for note {title} in notebook {notebook_name}: {str(e)}"
            )
            
    def get_notes_for_tag(self, tag_name):
        """
        Get all notes associated with a tag
        :param tag_name: name of the tag
        :raises NoteTagError: if retrieval fails
        :return: list of notes associated with the tag
        """
        try:
            # Try to get the tag
            try:
                tag = self.tag_service.get_tag(tag_name)
            except TagError as e:
                raise e
            tag_id = tag["id"]
            note_ids =  self.__note_tag_model.get_notes_for_tag(tag_id)
            notes = [self.__note_model.get_note(note_id) for note_id in note_ids]
            return notes
        except (TagError, ValidationError, TagNotFoundError, DatabaseError, Exception) as e:
            raise NoteTagError(f"Failed to get notes for tag {tag_name}: {str(e)}")

    def remove_tag_from_note(self, title, notebook_name, tag_name):
        """
        Remove a tag from a note
        :param title: title of the note
        :param notebook_name: name of the notebook which the note belongs to
        :param tag_name: name of the tag to be removed
        :raises NoteTagError: if removal fails
        :return: True if removal is successful, False otherwise
        """
        try:
            # Try to get the note
            try:
                note = self.note_service.get_note(title, notebook_name)
            except NoteError as e:
                raise e
            note_id = note["id"]
            # Try to get the tag
            try:
                tag = self.tag_service.get_tag(tag_name)
            except TagError as e:
                raise e
            tag_id = tag["id"]
            # Remove the tag from the note
            self.__note_tag_model.remove_tag_from_note(note_id, tag_id)
            return True
        except (
            NoteError,
            TagError,
            ValidationError,
            NoteNotFoundError,
            TagNotFoundError,
            DatabaseError,
            Exception
        ) as e:
            raise NoteTagError(
                f"Failed to remove tag {tag_name} from note {title} in notebook {notebook_name}: {str(e)}"
            )

    def remove_all_tags_for_note(self, title, notebook_name):
        """
        Remove all tags associated with a note
        :param title: title of the note
        :param notebook_name: name of the notebook which the note belongs to
        :raises NoteTagError: if removal fails
        :return: True if removal is successful, False otherwise
        """
        try:
            # Try to get the note
            try:
                note = self.note_service.get_note(title, notebook_name)
            except NoteError as e:
                raise e
            note_id = note["id"]
            # Remove all tags associated with the note
            self.__note_tag_model.remove_all_tags_for_note(note_id)
            return True
        except (
            NoteError,
            ValidationError,
            NoteNotFoundError,
            DatabaseError,
            Exception
        ) as e:
            raise NoteTagError(
                f"Failed to remove all tags for note {title} in notebook {notebook_name}: {str(e)}"
            )

    def remove_all_notes_for_tag(self, tag_name):
        """
        Remove all notes associated with a tag
        :param tag_name: name of the tag
        :raises NoteTagError: if removal fails
        :return: True if removal is successful, False otherwise
        """
        try:
            # Try to get the tag
            try:
                tag = self.tag_service.get_tag(tag_name)
            except TagError as e:
                raise e
            tag_id = tag["id"]
            # Remove all notes associated with the tag
            self.__note_tag_model.remove_all_notes_for_tag(tag_id)
            return True
        except (
            TagError,
            ValidationError,
            TagNotFoundError,
            DatabaseError,
            Exception
        ) as e:
            raise NoteTagError(f"Failed to remove all notes for tag {tag_name}: {str(e)}")