from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.utils.repositories import SQLAlchemyRepository
from app.models.payments import Payment
from app.models.parking import Parking
from app.models.cars import Car


class PaymentRepository(SQLAlchemyRepository):
    model = Payment

    async def find_by_user_id(self, user_id: int, successful_only: bool = False) -> Sequence[Payment]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by_parking_id(self, parking_id: int) -> Sequence[Payment]:
        stmt = select(self.model).where(self.model.parking_id == parking_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by_payment_id(self, payment_id: int) -> Sequence[Payment]:
        stmt = select(self.model).where(self.model.id == payment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all_payments(self, successful_only: bool = False) -> Sequence[Payment]:
        stmt = select(self.model)
        if successful_only:
            stmt = stmt.where(self.model.transaction_type == Payment.TransactionType.CREDIT)
        result = await self.session.execute(stmt)
        return result.scalars().all()
     

    async def find_by_license_plate(self, license_plate: str) -> list[Payment]:
        stmt = (
            select(Payment)
            .join(Parking)
            .join(Car)
            .options(
                joinedload(Payment.parking).joinedload(Parking.car)
            )
            .where(Car.license_plate == license_plate)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
        

    async def add_one(self, payment_dict: dict) -> Payment:
        new_payment = Payment(**payment_dict)
        self.session.add(new_payment)
        await self.session.commit()
        return new_payment
