from app.models.rate import Rate
from app.utils.repositories import SQLAlchemyRepository


class RateRepository(SQLAlchemyRepository):
    """Repository class for managing Rate objects in the database.

    Inherits from:
        SQLAlchemyRepository: Base repository class providing common database operations.
    """
    model = Rate
