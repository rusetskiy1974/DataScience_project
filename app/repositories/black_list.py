from app.models.black_list import BlackList
from app.utils.repositories import SQLAlchemyRepository


class BlackListRepository(SQLAlchemyRepository):
    """Repository class for managing BlackList objects in the database.

    Inherits from:
        SQLAlchemyRepository: Base repository class providing common database operations.
    """
    model = BlackList