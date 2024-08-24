from typing import Sequence

from sqlalchemy import select
from app.utils.repositories import SQLAlchemyRepository
from app.models.payments import Payment


class PaymentRepository(SQLAlchemyRepository):
    model = Payment

    async def find_by_user_id(self, user_id: int) -> Sequence[Payment]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by_parking_id(self, parking_id: int) -> Sequence[Payment]:
        stmt = select(self.model).where(self.model.parking_id == parking_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_one(self, payment_dict: dict) -> Payment:
        new_payment = Payment(**payment_dict)
        self.session.add(new_payment)
        await self.session.commit()
        return new_payment
