from application.models.tag_model import TagModel

class TagService:
    def __init__(self, db):
        self.tag_model = TagModel(db)