from app.models.rate import Rate
from app.utils.repositories import SQLAlchemyRepository


class RateRepository(SQLAlchemyRepository):
    model = Rate
