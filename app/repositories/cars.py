from sqlalchemy import select
from app.utils.repositories import SQLAlchemyRepository
from app.models.cars import Car


class CarsRepository(SQLAlchemyRepository):
    model = Car

    async def find_by_owner_id(self, owner_id: int) -> list[Car]:
        stmt = select(self.model).where(self.model.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
