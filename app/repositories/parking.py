from sqlalchemy import select
from app.utils.repositories import SQLAlchemyRepository
from app.models.parking import Parking


class ParkingRepository(SQLAlchemyRepository):
    model = Parking

    async def find_all_parkings(self, active_only: bool = False) -> list[Parking]:
        stmt = select(self.model)
        if active_only:
            stmt = stmt.where(self.model.is_active == True)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by_owner_id(self, owner_id: int) -> list[Parking]:
        stmt = select(self.model).where(self.model.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
