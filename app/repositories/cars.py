from app.models.cars import Car
from app.utils.repositories import SQLAlchemyRepository


class CarsRepository(SQLAlchemyRepository):
    model = Car
