from sqlalchemy import select
from app.utils.repositories import SQLAlchemyRepository
from app.models.payments import Payment

class PaymentRepository(SQLAlchemyRepository):
    model = Payment

    async def find_all_payments(self, successful_only: bool = False) -> list[Payment]:
        stmt = select(self.model)
        if successful_only:
            stmt = stmt.where(self.model.is_successful == True)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by_user_id(self, user_id: int) -> list[Payment]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by_parking_id(self, parking_id: int) -> list[Payment]:
        stmt = select(self.model).where(self.model.parking_id == parking_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
