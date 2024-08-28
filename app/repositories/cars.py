from sqlalchemy import select
from app.utils.repositories import SQLAlchemyRepository
from app.models.cars import Car


class CarsRepository(SQLAlchemyRepository):
    """Repository class for managing Car objects in the database.

    Inherits from:
        SQLAlchemyRepository: Base repository class providing common database operations.
    """
    model = Car

    async def find_by_owner_id(self, owner_id: int) -> list[Car]:
        """Finds all cars associated with a specific owner ID.

        Args:
            owner_id (int): The ID of the owner.

        Returns:
            list[Car]: A list of Car objects.
        """
        stmt = select(self.model).where(self.model.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
